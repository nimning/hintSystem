import sys,os
import pickle
import ply.lex as lex
import ply.yacc as yacc
from math import factorial

"""
Parsing webwork expressions
written by Matt Elkherj, Yoav Freund

The main two methods are:
parse_webwork(expression), compute_webwork(expression)
Where expression is a string containing what should be a valid webwork answer (otherwise an exception is thrown).

parse_webwork - returns a tree, represented as nested tuples.
Example: parse_webwork('C(32,5) - C(20,5)')
Answer: ('+', ('C', 32, 5), ('-', ('C', 20, 5)))

compute_webwork - returns the numeratical value of the expression
Example:  compute_webwork('C(32,5) - C(20,5)')
Answer:  185872L
"""

associative_ops = ['*','+']
parse_output=''

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
    r'\d*\.?\d+'
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

# Build the lexer
lex.lex()

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

def p_expression_ops(t):
    '''expression : expression PLUS factor  %prec PLUS
                  | factor PLUS factor      %prec PLUS
                  | expression MINUS factor %prec PLUS
                  | factor MINUS factor     %prec PLUS
                  '''
    #global parse_output
    if parse_output=='parse':
        if t[2] == '+'  : t[0] = ('+',t[1],t[3])
        elif t[2] == '-': t[0] = ('+',t[1],('-',t[3]))
    else:
        if t[2] == '+'  : t[0] = t[1]+t[3]
        elif t[2] == '-': t[0] = t[1]-t[3]

def p_factor_ops(t):
    '''factor : factor TIMES factor    %prec TIMES
                | factor DIVIDE factor %prec TIMES
                | factor EXP factor    %prec EXP
                  '''
    #global parse_output
    if parse_output=='parse':
        if t[2] == '*': t[0] = ('*',t[1],t[3])
        elif t[2] == '/': t[0] = ('*',t[1],('/',t[3]))
        elif t[2] == '^' or t[2] == '**': t[0] = ('^',t[1],t[3])
    else:
        if t[2] == '*': t[0] = t[1]*t[3]
        elif t[2] == '/': t[0] = t[1]/t[3]
        elif t[2] == '^' or t[2] == '**': t[0] = t[1]**t[3]

def p_expression_implicit_times(t):
    '''factor : factor factor %prec IMPL_TIMES'''
    #global parse_output
    if parse_output=='parse':
        t[0] = ('*',t[1],t[2])
    else:
        t[0] = t[1]*t[2]

def p_expression_uminus(t):
    'factor : MINUS factor %prec UMINUS'
    #global parse_output
    if parse_output=='parse':
        t[0] = ('-',t[2])
    else:
        t[0]=-t[2]

def p_expression_factorial(t):
    'factor : factor FACTORIAL %prec FACTORIAL'
    #global parse_output
    if parse_output=='parse':
        t[0] = ('!',t[1])
    else:
        t[0]=factorial(t[1])
        
def p_expression_choose(t):
    'factor : CHOOSE LPAREN list RPAREN %prec CHOOSE'
    #global parse_output
    if parse_output=='parse':
        lst = t[3]
        t[0] = tuple(['C']+lst)
    else:
        (m,n) = t[3]
        t[0] = factorial(m)/(factorial(n)*factorial(m-n))

def p_expression_group(t):
    '''factor : LPAREN expression RPAREN
              | LBRACKET expression RBRACKET 
              | LPAREN factor RPAREN
              | LBRACKET factor RBRACKET 
              '''
    t[0] = t[2]

def p_expression_set(t):
    '''factor : LSET list RSET
                | LSET expression RSET
                | LSET RSET '''
    if len(t) == 4:
        t[0] = ('{}',t[2])
    else:
        t[0] = ('{}',[])

def p_expression_tuple(t):
    'factor : LPAREN list RPAREN'
    t[0] = ('()',t[2])


def p_nonempty_list(t):
    ''' list  : expression COMMA
              | list expression COMMA
              | list expression 
              | factor COMMA
              | list factor COMMA
              | list factor %prec LIST '''
    if len(t) == 3 and t[2] == ',':                #eg 1,
        t[0] = [t[1],]
    elif len(t) == 4 or len(t) == 3:               #eg ...1, or ...1
        t[0] = t[1] + [t[2],]

def p_expression_number_variable(t):
    '''factor    : NUMBER
                 | VARIABLE '''
    t[0] = t[1]

def p_error(t):
    if t is None:
        raise WebworkParseException('Syntax error')
    else:
        raise WebworkParseException(
            "Syntax error at '%s'" % t.value)

yacc.yacc()

def parse_webwork(expr):
    global parse_output
    parse_output='parse'
    global expr_tree
    parsed = handle_comma_separated_number(expr)
    if parsed is None: #didn't match comma_separated_number, so parse expr
        yacc.parse(expr)
        parsed = expr_tree
    return reduce_associative(parsed)

def compute_webwork(expr):
    global parse_output
    parse_output='compute'
    global expr_tree
    parsed = handle_comma_separated_number(expr)
    if parsed is None: #didn't match comma_separated_number, so parse expr
        yacc.parse(expr)
        parsed = expr_tree
    return parsed

if __name__ == '__main__':
    webwork = pickle.load(open(os.path.join(sys.argv[1],'pickled_data'),'rb'))
    exprs = [expr for _,_,expr in webwork.all_attempts]
    parse_webwork(exprs[0])
