import subprocess
import os
import re
import urllib
import logging
import xmlrpclib
import base64
logger = logging.getLogger(__name__)

# scripts' location
_SCRIPTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'scripts')
_RENDERPG = os.path.join(_SCRIPTDIR,'renderPG.pl')
_CHECKANSWER = os.path.join(_SCRIPTDIR,'checkanswer.pl')

xmlrpc_url = 'http://192.168.33.10/mod_xmlrpc'
server = xmlrpclib.ServerProxy(xmlrpc_url)
user = 'scheaman'
password = 'scheaman'
course = 'CompoundProblems'

def render_pg_xmlrpc(pg_file, seed=1234, psvn=1234):
    ''' Renders an HTML snippet from a given PG file.
    Uses python's xmlrpclib instead of separate perl script

    Args:
       pg_file : string
         Path to the PG file
       seed : int
         Random seed
    Return:
       A string containing the HTML snippet, or None if there is an error.

    '''
    pg_file = os.path.abspath(pg_file)
    with open(pg_file, 'r') as fin:
        problem_text = fin.read()
    args = {'envir':
            {'fileName': pg_file, 'problemSeed': int(seed), 'displayMode':'images', 'psvn': psvn},
            'source': base64.b64encode(problem_text),
            'userID': user, 'password': password, 'courseID': course}
    res=server.WebworkXMLRPC.renderProblem(args)
    logger.debug(res['compute_time'])
    html = base64.b64decode(res['text'])
    return html

def render_pg(pg_file, seed=1234):
    """Render a HTML snippet from a given PG file.

    Args:
       pg_file : string
         Path to the PG file
       seed : int
         Random seed
         
    Return:
       A string containing the HTML snippet, or None if there is an error.

    Notes:
       This function blocks until the PG generation process is complete.
       It is not recommended to call this function from the main thread.
    """
    try:
        pg_file = os.path.abspath(pg_file)
        # spawn another process and call renderPG.pl
        process = subprocess.Popen([_RENDERPG, pg_file, str(seed)],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        # block until done
        process.wait()
        
        # read stdout, stderr
        out, err = process.communicate()

        # check for any error 
        if len(out) == 0 or len(err) > 0:
            return None

        # parse PG output
        problem = re.search(r'<form.*?>(.*?)<input type="hidden" name="answersSubmitted" value="1">',
                            out, re.DOTALL).group(1)
        
        return problem
            
    except Exception:
        return None


def checkanswer(pg_file, answers, seed=1234):
    """Check answers with a given PG file.

    Args:
       pg_file : string
         Path to the PG file
       answers : dict
         Dictionary with the answers e.g.
            { 'AnSwEr0001' : '123',
              'AnSwEr0002' : 'x' }
       seed : int
         Random seed
         
    Return:
       A dictionary containing results e.g.
            { 'AnSwEr0001' : { 'entered_value' : '123',
                               'correct_value' : '50',
                               'is_correct' : False,
                               'error_msg' : '' },
              'AnSwEr0002' : { 'entered_value' : 'x',
                               'correct_value' : '10',
                               'is_correct' : False,
                               'error_msg' : 'Your answer isn't a number
                               (it looks like a formula that returns a number)' } }
                               
       or None if there is an error.                        
   
    Notes:
       This function blocks until the PG generation process is complete.
       It is not recommended to call this function from the main thread.
    """
    try:
        pg_file = os.path.abspath(pg_file)

        answer_str = urllib.urlencode(answers)

        # spawn another process and call checkanswer.pl
        process = subprocess.Popen([_CHECKANSWER, pg_file, str(seed), answer_str],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        # block until done
        process.wait()
        
        # read stdout, stderr
        out, err = process.communicate()

        if len(out) == 0 or len(err) > 0:
            return None

        # parse PG output
        table = re.search(r'ANSWERS <table.*?>(.*?)</table>', out, re.DOTALL).group(1)
        rows = re.findall(r'<tr>(.*?)</tr>', table, re.DOTALL)

        p_td = re.compile(r'<td>(.*?)</td>', re.DOTALL)
        p_key = re.compile(r'Prob: (\d+)')
        p_correct_val = re.compile(r'Correct answer is (.*)', re.DOTALL)
        p_err = re.compile(r'<i>(.*?)</i>', re.DOTALL)

        results = {}
        for row in rows:
            cols = p_td.findall(row)
            key = p_key.search(cols[0]).group(1)
            entered_value = cols[1].strip()
            if entered_value == '&nbsp;':
                entered_value = ''
            is_correct = (cols[2].strip() == "Correct")
            correct_value = p_correct_val.search(cols[3]).group(1).strip()
            error = p_err.search(cols[4]).group(1)
            results["AnSwEr%04d"%(int(key))] = { 'entered_value' : entered_value,
                                                'correct_value' : correct_value,
                                                'is_correct' : is_correct,
                                                'error_msg' : error }
        
        return results
            
    except Exception:
        import traceback
        traceback.print_exc()
        return None
    
    
def test():
    print '#'*50
    print render_pg(os.path.join(_SCRIPTDIR,'BayesBurglary.pg'))
    print '#'*50
    print render_pg(os.path.join(_SCRIPTDIR,'generalizedCombination1.pg'))
    print '#'*50
    print checkanswer(os.path.join(_SCRIPTDIR,'BayesBurglary.pg'),
                      { 'AnSwEr0001' : '12' ,
                        'AnSwEr0002' : 'x'})
    print '#'*50
    print checkanswer(os.path.join(_SCRIPTDIR,'generalizedCombination1.pg'),
                      { 'AnSwEr0001' : '55' ,
                        'AnSwEr0002' : '21'})

    print '#'*50
    print checkanswer(os.path.join(_SCRIPTDIR,'generalizedCombination1.pg'),
                      { 'AnSwEr0001' : '55' ,
                        'AnSwEr0002' : '21'},
                      seed=42)

    print '#'*50
    print checkanswer(os.path.join(_SCRIPTDIR,'test.pg'),
                      { 'AnSwEr0001' : '1' },
                      seed=42)



if __name__ == "__main__":
    test()
