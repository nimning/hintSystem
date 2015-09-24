'''
make_function takes a function source string as input and returns a pointer to the executable function

Parameters: 
        name: name of the function (should be consistent with the name used in the code)
        code: A string containing the code

Returns:
        if type==function: a pointer to the executable function
        if type==str: An error message
'''
import sys
import StringIO

def make_function(name,code):
    #locals().pop(name,'clearing keypair')
    try:
        bytecode=compile(source=code,filename='filter source code',mode='exec')
        env={}

        stdout = sys.stdout  #keep a handle on the real standard output
        #sys.stdout = StringIO.StringIO() #Choose a file-like object to write to
        print 'test1'
        exec(bytecode,env)
        print 'test2'
        
        print 'env keys=',env.keys()

    except SyntaxError, e:
        message='Syntax error:  line=%d, offset=%d text=%s'%(e.lineno,e.offset,e.text)
        return message
    
    if env.has_key(name):
        return env[name],env
    else:
        return 'code failed to generate function named '+name

    
if __name__=="__main__":  
    code="""
#from string import *
def f(x):
    print 'from inside',globals().keys()
    return x**2
"""
    A,env=make_function('f',code)
    if type(A)==str:
        print A
    else:
        old_stdout=sys.stdout
        sys.stdout=StringIO.StringIO()
        env['A']=A
        exec('x=A(2)',env)
        stdout_dump=sys.stdout.getvalue()
        sys.stdout=old_stdout
        print A, type(A)
        print 'stdout_dump=|%s|'%stdout_dump
        print 'returned value=',env['x']
    

    