Adaptive Hint Server API
========================

Repository: <https://github.com/sunsern/adaptive-hint>

Figures:
* [Yoav's Detailed](https://www.lucidchart.com/documents/edit/4ed8-1c14-521f9e44-a155-55720a00def9)
* [From meeting](https://docs.google.com/a/eng.ucsd.edu/drawings/d/1HiSdIF7rpkZbfcE_XsuMBfa0AkQFA43FERyPJBVB1Zo/edit)
* [Sunsern's figure](https://docs.google.com/drawings/d/19nmZt2Dzaz0_3F8tUUwOE_SmPAN_-e9J-Xx3GqYPA24/edit?usp=sharing)


Python interfaces to PG scripts [\[server/pgwrapper.py\]](https://github.com/sunsern/adaptive-hint/blob/master/server/pgwrapper.py)
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


Resource [\[server/rest_server.py\]](https://github.com/sunsern/adaptive-hint/blob/master/server/rest_server.py)
---------------------------------
#### PG Resources / Matt
  - ```POST /pg``` -- Retrieve PG source from a path 

#### Hint Resources /Matt
  - ```GET /hints/:pg_id``` -- Retrieve hints associated with the given pg_id
  - ```POST /hints/:pg_ig``` -- Add hints to the given pg_id
  - ```DELETE /hints/:hint_id``` -- Delete a hint

#### Render / Sunsern
  - ```POST /render``` -- Render HTML from PG
    - input: ```pg_file=/opt/webwork/.../sample.pg&seed=123```
    - JSON output: 

```
{ 'status': 'OK', 
  'html': '<div>Problem</div>' 
}
```

#### Check Answer / Sunsern
  - ```POST /checkanswer``` -- Check answers with PG
    - input: ```pg_file=/opt/webwork/.../sample.pg&seed=123&AnSwEr0001=42&AnSwEr0002=x```
    - JSON output: 

```json
{ 'status': 'OK', 
  'results': { 
    'AnSwEr0001' : {
      'entered_value': '42',
      'correct_value': '42',
      'is_correct': true,
      'error_msg': ''
    },
    'AnSwEr0002' : {
      'entered_value': 'x',
      'correct_value': '12',
      'is_correct': false,
      'error_msg': 'Your answer isn\'t a number'
    },
  }
}
```

Communication API [\[server/sockjs_server.py\]](https://github.com/sunsern/adaptive-hint/blob/master/server/sockjs_server.py)
---------------------------------------
A valid message must have the following format:
```python
message = JSON.stringify({
  'command': 'some_command',
  'arguments': { 
    'arg1': 'some_text',
    'arg2': 123
  }
});
```

To send a message to the server, 
```python
  sock = new SockJS('http://localhost:1234/student');
  sock.send(message);
```

#### Student client to server
  - Included in each message from the client:
    - user id
    - session key (key in the html file)
  - ```pageinfo``` 
    - HTML [the BODY part]
  - ```newstring```
    - ID of the box in which the string was entered
    - An ascii string.
    - The client needs some logic to decide when to send the string. 
      - Basically: when user start typing in a new box. Or when some time-out occured (10sec)

#### Server to student client
  - ```hint```
    - HTML of hint (just that paragraph (see below))
    - Location to insert the hint. (before paragraph containing id=X)
  
#### Teacher command
  - ```list_students``` -- List all connected students
  - ```send_hint``` -- Send a hint to a student

-----
*Paragraph*: The relevant part of the HTML (the problem body) is partitioned into paragraphs 
according to the answer blocks. The answer block has the form \<input type=text ...id='AnSwEr0003' ... \>
A paragraph consists of the HTML text preceding the answer block, together with the answer block.
