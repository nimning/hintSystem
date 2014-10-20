import sys,os
import pickle
import ply.lex as lex
import ply.yacc as yacc
from math import factorial
from webwork_lexer import WebworkLexer

# Set up a logging object
import logging

logging.basicConfig(
    level = logging.WARNING,
    filename = "parselog.txt",
    filemode = "w",
    format = "%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)

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

def node_span(node):
    if type(node)==tuple and type(node[0])==tuple:
        if len(node[0]) == 2: # Parse tree
            return node[0][1]
        elif len(node[0]) == 3: # Evaluation tree
            return node[0][2]

def node_string(node, string):
    if len(node) > 1:
        span = node_span(node)
        return string[span[0]:(span[1]+1)]
    else:
        return str(node[0])

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
        return [L]
    elif len(L)==1:
        #print 'flatten_list, len 1 tuple',L
        return flatten_list(L[0])
    # This line seems to error sometimes, seems like L or L[0] can be an int somehow
    elif L[0][0]!='list':
        #print 'flatten_list, header is not "list"',L
        return [L]
    else:
        #print 'flatten_list, real list ',L
        items=[]
        for i in range(1,len(L)):
            items=items+flatten_list(L[i])
        #print 'returning',items
        return items

def tree_to_s_exp(tree):
    '''Convert an expression parse tree to a lisp-style s-expression'''
    if type(tree) == tuple or type(tree) == list:
        return '('+tree[0][0] + ' ' + ' '.join(tree_to_s_exp(child) for child in tree[1:]) +')'
    else:
        return str(tree)

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

# Parsing rules
precedence = (
    ('left','LIST'),
    ('nonassoc','COMMA'),
    ('left','IMPL_TIMES'),
    ('nonassoc','UMINUS'),
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('left','EXP'),
    ('left','FACTORIAL'),
    ('nonassoc','CHOOSE')
    )

def p_statement_expr_list(p):
    '''statement : expression
                 | factor
                 | list
                 '''
    p[0] = p[1]

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
                | factor DIVIDE factor %prec DIVIDE
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

def p_expression_unbalanced_group(t):
    '''factor : LPAREN expression
              | LBRACKET expression
              | LPAREN factor
              | LBRACKET factor
              '''
    print "Parse Error: Unbalanced Group Operator"
    print t.lexer.lexdata
    print ' '*(t.lexpos(0))+'^'
    raise WebworkParseException('Unbalanced grouping operator in expression: ' + t.lexer.lexdata)

def p_expression_unclosed_choose(t):
    'factor : CHOOSE LPAREN list'
    print "Parse Error: Unclosed Choose"
    print t.lexer.lexdata
    print ' '*(t.lexpos(0))+'^'
    raise WebworkParseException('Unbalanced parentheses in expression: ' + t.lexer.lexdata)

def p_expression_set(t):
    '''factor : LSET list RSET
                | LSET expression RSET
                | LSET RSET '''
    if len(t) == 4:
        list=flatten_list(t[2][1:])
        t[0] = ('{}',tuple(list))
    else:
        t[0] = ('{}',())
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

def p_error(p):
    if p is None:
        raise WebworkParseException('yacc:Syntax error - Empty token')
    else:
        #start,end = p.lexpos
        raise WebworkParseException("yacc:Syntax error at '%s',location=%1d" % (p,p.lexpos))

# def p_error(p):
#     if p==None:
#         print "Syntax error at end of expression"
#     else:
#         print "Syntax error at <<", p,p.lexspan(0),'>>'
#     # Just discard the token and tell the parser it's okay.
#     yacc.token()

# START lex and yacc
lexer = WebworkLexer()
tokens = lexer.tokens
parser = yacc.yacc()

# set up debugging.

#lex.lex(debug=True,debuglog=log,errorlog=log)
#yacc.yacc(debug=True,debuglog=log,errorlog=log)

def parse_webwork(expr):
    parsed = handle_comma_separated_number(expr)
    if parsed is None: #didn't match comma_separated_number, so parse expr
        try:
            parsed = parser.parse(expr,tracking=True,debug=log, lexer=lexer.lexer)
        except  WebworkParseException as e:
            logger.error('||%s|| %s', expr, e)
            parsed=None
        except Exception as e:
            logger.error('||%s|| %s', expr, e)
            parsed = None
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
