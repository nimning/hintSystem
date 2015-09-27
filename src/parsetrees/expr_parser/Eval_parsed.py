from math import factorial
import linecache
import sys
from webwork_parser import parse_webwork, WebworkParseException, node_string
import traceback
import operator as op
from scipy.stats import norm

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

def is_number(s):
    try:
        float(s)
        return True
    except:
        return False


def ncr(n, r):
    r = min(r, n-r)
    if r == 0: return 1
    numer = reduce(op.mul, xrange(n, n-r, -1))
    denom = reduce(op.mul, xrange(1, r+1))
    return numer/denom

def eval_parsed(e, variables = None):
    """ Evaluate a parsed expression, returns a tree, of the same form as the parse tree. Where each operator 
        is replaced by a binary tuple: (operator,evaluation result)
    
        Still need to write code to handle varibles, lists and sets.
    """
    if variables is None:
        variables = {}
    def get_number(ev):
        #print 'get_number got',ev
        if len(ev)==3 and ev[0]=='X': 
            return ev[1]
        elif len(ev)==1:
            return ev[0]
        else: 
            return ev[0][1]
        
    try:
        #print 'eval_parsed, e="',e,'"'
        if type(e)==type(None):
            return 0
        elif is_number(e)==1:
            return (float(e),)
        elif type(e) == str: # Variable
            if e in variables:
                return (variables[e],)
            else:
                print "Couldn't find", e, "in",variables
                return (e,) # Variables will cause things to break right now
        elif len(e)==2:
            ((f,span),op)=e

            if f=='{}':
                return e  # if element is a list, just return as is.
                          # might need to improve this if we want sets of expressions

            ev=eval_parsed(op, variables)
            v=get_number(ev)
            
            if f=='X':  # X indicates a single number
                ans=v
                return (f,ans,tuple(span))
            elif f=='-':
                ans=-v
            elif f=='!':
                ans=factorial(v)
            elif f=='Q':
                ans= 1-norm.cdf(v)
            else:
                raise Exception('unrecognized unary operator %s in %s'%(f,e))
            return ((f,ans,tuple(span)),ev)
        
        elif len(e)==3:
            ((f,span),op1,op2)=e
            ev1=eval_parsed(op1, variables)
            v1=get_number(ev1)
            ev2=eval_parsed(op2, variables)
            v2=get_number(ev2)
            
            if f=='+':    ans= v1+v2
            elif f=='*':  ans= v1*v2
            elif f=='-':  ans= v1-v2
            elif f=='/':  ans= v1/v2
            elif f=='**': ans= v1**v2
            elif f=='^': ans= v1**v2
            elif f=='C':
                ans= ncr(int(v1), int(v2))
            else:
                raise Exception('unrecognized binary operator %s in %s'%(f,e))
            return ((f,ans,tuple(span)),ev1,ev2)
        else:
            raise Exception('Unrecognized expression form: %s'%e)
    except Exception as ex:
        print 'Eval_parsed Exception:',ex
        traceback.print_exc()
        return None
        #raise WebworkParseException(ex)
        # return ((e[0][0], None, e[0][1]),)


def Collect_numbers(etree):
    T={}
    if type(etree)==int:
        return T
    collection_recursion(T,etree)
    return T

def collection_recursion(T,etree):
    if len(etree)==1:
        T[etree[0]]=etree   # add leaf
    if len(etree)>1:
        T[etree[0][1]]=etree   # add evaluation for non-leaf
        for i in range(1,len(etree)):
            collection_recursion(T,etree[i])

def numbers_and_exps(etree, string):
    numbers = Collect_numbers(etree)
    ret = {k: node_string(v, string) for k, v in numbers.iteritems()}
    return ret

def parse_and_collect_numbers(string):
    try:
        parse_tree = parse_webwork(string)
        eval_tree = eval_parsed(parse_tree)
        eval_numbers = Collect_numbers(eval_tree)
        return set(eval_numbers.keys())
    except:
        return set()

def parse_and_eval(string, variables=None):
    expr = parse_webwork(string)
    if expr:
        try:
            etree = eval_parsed(expr, variables)
            return expr, etree
        except:
            return (None, None)
    else:
        return (None, None)

if __name__=="__main__":
    string=sys.argv[1]
    print 'input:::',string
    tree=parse_webwork(string)
    print 'output:::',tree
    eval_tree=eval_parsed(tree)
    print 'Eval_tree:::',eval_tree
