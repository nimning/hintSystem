Adaptive Hint Server API
========================

Repository: <https://github.com/sunsern/adaptive-hint>

Figures:
* [Yoav's Detailed](https://www.lucidchart.com/documents/edit/4ed8-1c14-521f9e44-a155-55720a00def9)
* [From meeting](https://docs.google.com/a/eng.ucsd.edu/drawings/d/1HiSdIF7rpkZbfcE_XsuMBfa0AkQFA43FERyPJBVB1Zo/edit)
* [Sunsern's figure](https://docs.google.com/drawings/d/19nmZt2Dzaz0_3F8tUUwOE_SmPAN_-e9J-Xx3GqYPA24/edit?usp=sharing)


Resource [server/rest_server.py]
---------------------------------
#### PG Resources / Matt
  - ```POST /pg``` -- Retrieve PG source from a path 

#### Hint Resources /Matt
  - ```GET /hints/:pg_id``` -- Retrieve hints associated with the given pg_id
  - ```POST /hints/:pg_ig``` -- Add hints to the given pg_id
  - ```DELETE /hints/:hint_id``` -- Delete a hint

#### Render / Sunsern
  - ```POST /render``` -- Render HTML from PG

#### Check Answer / Sunsern
  - ```POST /checkanswer``` -- Check answers with PG


Communication API [server/sockjs_server.py]
---------------------------------------
A valid message must have the following format:
```
message = JSON.stringify({
  'command': 'some_command',
  'arguments': { 
    'arg1': 'some_text',
    'arg2': 123
  }
});
```

To send a message to the server, 
```
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
