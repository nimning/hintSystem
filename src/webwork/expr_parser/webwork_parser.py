import sys,os
import pickle
import ply.lex as lex
import ply.yacc as yacc


# -----------------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables -- all in one file.
# -----------------------------------------------------------------------------

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
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('left','EXP'),
    ('left','FACTORIAL'),
    ('right','UMINUS'),
    ('right','CHOOSE')
    )

def p_statement_expr_list(t):
    '''statement : expression
                 | list '''
    global expr_tree
    expr_tree = t[1]

def p_expression_ops(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression EXP expression
                  | expression expression '''
    if len(t) == 3: #last case, eg (1)(2)
        t[0] = ('*',t[1],t[2])
    elif t[2] == '+'  : t[0] = ('+',t[1],t[3])
    elif t[2] == '-': t[0] = ('-',t[1],t[3])
    elif t[2] == '*': t[0] = ('*',t[1],t[3])
    elif t[2] == '/': t[0] = ('/',t[1],t[3])
    elif t[2] == '^' or t[2] == '**': t[0] = ('^',t[1],t[3])

def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    t[0] = ('-',0,t[2])

def p_expression_factorial(t):
    'expression : expression FACTORIAL %prec FACTORIAL'
    t[0] = ('!',t[1])

def p_expression_choose(t):
    'expression : CHOOSE LPAREN list RPAREN %prec CHOOSE'
    lst = t[3]
    t[0] = tuple(['C']+lst)

def p_expression_group(t):
    '''expression : LPAREN expression RPAREN
                  | LBRACKET expression RBRACKET '''
    t[0] = t[2]

def p_expression_set(t):
    '''expression : LSET list RSET
                  | LSET expression RSET
                  | LSET RSET '''
    if len(t) == 4:
        t[0] = ('{}',t[2])
    else:
        t[0] = ('{}',[])

def p_expression_tuple(t):
    'expression : LPAREN list RPAREN'
    t[0] = ('()',t[2])

def p_nonempty_list(t):
    ''' list  : expression COMMA
              | list expression COMMA
              | list expression %prec LIST '''
    if len(t) == 3 and t[2] == ',':                #eg 1,
        t[0] = [t[1],]
    elif len(t) == 4 or len(t) == 3:               #eg ...1, or ...1
        t[0] = t[1] + [t[2],]

def p_expression_number_variable(t):
    '''expression : NUMBER
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
    global expr_tree
    parsed = handle_comma_separated_number(expr)
    if parsed is None: #didn't match comma_separated_number, so parse expr
        yacc.parse(expr)
        parsed = expr_tree
    return reduce_associative(parsed)

if __name__ == '__main__':
    webwork = pickle.load(open(os.path.join(sys.argv[1],'pickled_data'),'rb'))
    exprs = [expr for _,_,expr in webwork.all_attempts]
    parse_webwork(exprs[0])
