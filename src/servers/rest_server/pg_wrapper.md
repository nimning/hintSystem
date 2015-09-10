Python interfaces to PG [\[pg_wrapper.py\]](pg_wrapper.py)
----------------------------------------------------
#### PG rendering
```python
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
```
*Implementation details:* ``render_pg`` makes a call to a perl script ``scripts/renderPG.pl`` 
which is a variant of ``renderProblem.pl``. Once the html is generated, ``render_pg`` 
parses the html and returns only the problem part. 


#### Answer checking
```python
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
       This function blocks until the answer checking process is complete.
       It is not recommended to call this function from the main thread. 
    """
```
*Implementation details:* ``checkanswer`` makes a call to a perl script ``scripts/checkanswer.pl``
that performs the following tasks.

1.  Generate a html from the PG file (same as ``renderProblem.pl``)
2.  Fill in the POST data form (i.e. answers) and submit the form to webwork server.
3.  Parse the response from the server that contains the answer results. 

Once the perl script returns, ``checkanswer`` parses the output and put the results into a python dictionary.
