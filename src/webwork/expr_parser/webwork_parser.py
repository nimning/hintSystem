import sys,os
import pickle
import ply.lex as lex
import ply.yacc as yacc
from math import factorial

"""
Parsing webwork expressions
written by Matt Elkherj, Yoav Freund

The main method is:

parse_webwork - returns a tree, represented as nested tuples.
Where expression is a string containing what should be a valid webwork answer (otherwise an exception is thrown).
Example: parse_webwork('C(32,5) - C(20,5)')
Answer: ('+', ('C', 32, 5), ('-', ('C', 20, 5)))
"""

associative_ops = ['*','+']

def reduce_associative(tree):
    ''' Given a tree of nested operations, group nested associative operations into a single tuple.  
        For example:

        >> reduce_associative(  ('*',('*',1,2),3)  )
#        ('*', 1, 2, 3)
        '''
    if type(tree) == tuple:
        #reduce subtrees
        subtrees = list(map(reduce_associative, tree[1:]))
        op = tree[0]
        if op in associative_ops:
            subtrees2 = [op]
            for t in subtrees:
                if (type(t) == tuple) and (t[0] == op):
                    subtrees2 += list(t[1:])
                else:
                    subtrees2.append(t)
            return tuple(subtrees2)
        else:
            return tuple([op]+subtrees)
    else:
        return tree

def flatten_list(L):
    """ Flatten a hierarchical list into one level """
    if not isinstance(L, tuple):
        #print 'flatten_list, non-tuple',L
        return L
    elif len(L)==1:
        #print 'flatten_list, len 1 tuple',L
        return flatten_list(L[0])
    elif L[0][0]!='list':
        #print 'flatten_list, header is not "list"',L
        return L
    else:
        #print 'flatten_list, real list ',L
        items=[]
        for i in range(1,len(L)):
            items=items+[flatten_list(L[i])]
        return items

class WebworkParseException(Exception):
    pass

def handle_comma_separated_number(expr):
    ''' Handles numbers of the form 1,234,562.09842 or 1,234,562 returning the 
         numeric value 
         returns None if the expression is not of this form '''
    expr_without_commas = ''.join( (c for c in expr if c != ',') )
    if len(expr) == len(expr_without_commas):
        return None
    else:
        try:
            return int(expr_without_commas)
        except (TypeError, ValueError):
            try:
                return float(expr_without_commas)
            except (TypeError, ValueError):
                return None

tokens = (
    'CHOOSE', 'VARIABLE', 'NUMBER', 'PLUS','MINUS','TIMES','DIVIDE', 'LPAREN','RPAREN','FACTORIAL', 'LSET', 'RSET','COMMA','EXP', 'LBRACKET', 'RBRACKET'
    )

# Tokens
t_CHOOSE    = r'C'
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_FACTORIAL = r'!'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_EXP       = r'\^|(\*\*)'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_LSET      = r'\{'
t_RSET      = r'\}'
t_COMMA     = r'\,'
t_VARIABLE  = r'[A-BD-Za-z]+[0-9]*'

def t_NUMBER(t):
    r'\d*\.?\d+E?(\+|\-)?\d*'
    try:
        t.value = int(t.value)
    except ValueError:
        try:
            t.value = float(t.value)
        except ValueError:
            raise WebworkParseException("Trouble parsing float %s", t.value)
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    raise WebworkParseException(
        "Illegal character '%s'" % t.value[0])

expr_tree = None

# Parsing rules
precedence = (
    ('left','LIST'),
    ('left','PLUS'),
    ('nonassoc','UMINUS'),
    ('left','TIMES'),
    ('left','IMPL_TIMES'),
    ('left','EXP'),
    ('left','FACTORIAL'),
    ('right','CHOOSE')
    )

def p_statement_expr_list(t):
    '''statement : expression
                 | factor
                 | list
                 '''
    global expr_tree
    expr_tree = t[1]

def add_header(t): # append the span of the expression to the header
    #print 'add_header got:',t[0]
    return ((t[0][0],t.lexspan(0)),)+t[0][1:]

def p_expression_ops(t):
    '''expression : expression PLUS factor  %prec PLUS
                  | factor PLUS factor      %prec PLUS
                  | expression MINUS factor %prec PLUS
                  | factor MINUS factor     %prec PLUS
                  '''
    if t[2] == '+'  : t[0] = ('+',t[1],t[3])
    elif t[2] == '-': t[0] = ('-',t[1],t[3])
    t[0]=add_header(t)

def p_factor_ops(t):
    '''factor : factor TIMES factor    %prec TIMES
                | factor DIVIDE factor %prec TIMES
                | factor EXP factor    %prec EXP
                  '''
    if t[2] == '*': t[0] = ('*',t[1],t[3])
    elif t[2] == '/': t[0] = ('/', t[1], t[3])
    elif t[2] == '^' or t[2] == '**': t[0] = ('^',t[1],t[3])
    t[0]=add_header(t)

def p_expression_implicit_times(t):
    '''factor : factor factor %prec IMPL_TIMES'''
    t[0] = ('*',t[1],t[2])
    t[0]=add_header(t)

def p_expression_uminus(t):
    'factor : MINUS factor %prec UMINUS'
    t[0] = ('-',t[2])
    t[0]=add_header(t)

def p_expression_factorial(t):
    'factor : factor FACTORIAL %prec FACTORIAL'
    t[0] = ('!',t[1])
    t[0]=add_header(t)
        
def p_expression_choose(t):
    'factor : CHOOSE LPAREN list RPAREN %prec CHOOSE'
    list=flatten_list(t[3][1:])
    #print 'p_expression_choose', list
    t[0] = ('C',list[0],list[1])
    t[0]=add_header(t)

def p_expression_group(t):
    '''factor : LPAREN expression RPAREN
              | LBRACKET expression RBRACKET 
              | LPAREN factor RPAREN
              | LBRACKET factor RBRACKET 
              '''
    t[0] = t[2]
    # t[0]=add_header(t)

def p_expression_set(t):
    '''factor : LSET list RSET
                | LSET expression RSET
                | LSET RSET '''
    if len(t) == 4:
        t[0] = ('{}',t[2])
    else:
        t[0] = ('{}',[])
    t[0]=add_header(t)

def p_expression_tuple(t):
    'factor : LPAREN list RPAREN'
    t[0] = ('()',t[2])
    t[0]=add_header(t)


def p_nonempty_list(t):
    ''' list  : expression COMMA
              | list expression COMMA
              | list expression 
              | factor COMMA
              | list factor COMMA
              | list factor %prec LIST '''
    #print 'nonempty_list:',len(t),
    #for i in range(len(t)):
    #    print 't[%1d]='%i, t[i],';',
    #print
                   
    if len(t) == 3 and t[2] == ',':                #eg 1,
        t[0] = ('list',(t[1],))
    elif len(t) == 4 or len(t) == 3:               #eg ...1, or ...1
        t[0] = ('list',t[1] + (t[2],))
    t[0]=add_header(t)

def p_expression_number_variable(t):
    '''factor    : NUMBER
                 | VARIABLE '''
    t[0] = t[1]
#   t[0]=(t[0],t.lexspan(0))

def p_error(t):
    if t is None:
        raise WebworkParseException('Syntax error')
    else:
        raise WebworkParseException("Syntax error at '%s'" % t)


# Start lex and yacc
lex.lex()
yacc.yacc()

# set up debugging.
# Set up a logging object
# import logging
# print 'setting up logging'
# logging.basicConfig(
#     level = logging.DEBUG,
#     filename = "parselog.txt",
#     filemode = "w",
#     format = "%(filename)10s:%(lineno)4d:%(message)s"
# )
# log = logging.getLogger()

#lex.lex(debug=True,debuglog=log,errorlog=log)
#yacc.yacc(debug=True,debuglog=log,errorlog=log)



def parse_webwork(expr):
    global expr_tree
    parsed = handle_comma_separated_number(expr)
    if parsed is None: #didn't match comma_separated_number, so parse expr
        yacc.parse(expr,tracking=True,debug=log)
        parsed = expr_tree
    return parsed
#    return reduce_associative(parsed)

#if __name__ == '__main__':
#    webwork = pickle.load(open(os.path.join(sys.argv[1],'pickled_data'),'rb'))
#    exprs = [expr for _,_,expr in webwork.all_attempts]
#    parse_webwork(exprs[0])

if __name__ == '__main__':
    string=sys.argv[1]
    print 'input:::',string
    tree=parse_webwork(string)
    print 'output:::',tree
