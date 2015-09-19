"""
This module is responsible for managing and executing the filters used in the adaptive hints System
"""
#class filter_bank():
#    __init__(filter_table='an SQL table', helpers_file='filter_helpers.py'):
#    """ load the filters into a filters table and the filter helpers into an environment"""
#    pass

import logging
logger = logging.getLogger(__name__)

import sys
import json
from TimeoutError import timeout # a decorator that creates a time-out interrupt for a given function.
import StringIO

def add_filter(name,code,env):
    '''
    make_filter takes a function source string as input and returns a pointer to the executable function

    parameters:
       code: a string containing the code of the function
       name: the name of the function (has to be consistent with the code)
       env: the environment to which the compiled function will be added.

    return value:
       if string: the string is an error message
       else:
          env: the environment given as parameter with the filter added
    '''

    try:
        bytecode=compile(source=code,filename='filter source code',mode='exec')

        exec(bytecode,env) # running this bytecode creates the function, it does not run it.

    except SyntaxError, e:
        message='Syntax error:  line=%d, offset=%d text=%s'%(e.lineno,e.offset,e.text)
        return message
    
    if env.has_key(name):
        return env
    else:
        return 'code failed to generate function named '+name

@timeout(1)  # does not support less than 1 sec
def exec_filter(filtername,env,input):
    try:
        #old_stdout=sys.stdout
        #sys.stdout=StringIO.StringIO()
        env['input']=input
        print 'input= ',input
        print 'before ',env.keys()
        exec('output=%s(input)'%filtername,env)
        print 'after ',env.keys()
        #stdout_dump=sys.stdout.getvalue()
        #sys.stdout=old_stdout
    except Exception, e:
        print 'error =',e
    return 'hint string','This is a fake printout'
    # return env['output'],stdout_dump

    
if __name__=="__main__": 
    code="""def answer_filter(params):
    #import json
    #answer_string, parse_tree, eval_tree, correct_string, correct_tree, correct_eval, user_vars = params
    #print json.dumps(params)
    print params.keys()
    return 'a hint'
"""
    env=add_filter('answer_filter',code,{})
    print env.keys()
    logger.debug('made the filter')
    file=open('filter_lab/Problem8Attempts.json','r');
    answer=json.loads(file.readline())['answer']
    print 'answer=',answer
    for line in file.readlines():
        params=json.loads(line);
        hint,output = exec_filter(filter,env,params)
        print 'hint=',hint
        print 'stdout=',output,
        break
        
