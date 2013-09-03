Adaptive Hint Server API
========================

Repository: <https://github.com/sunsern/adaptive-hint>


Resource [server/rest_server.py]
---------------------------------
#### PG Resources
  - ```POST /pg``` -- Retrieve PG source from a path 

#### Hint Resources
  - ```GET /hints/:pg_id``` -- Retrieve hints associated with the given pg_id
  - ```POST /hints/:pg_ig``` -- Add hints to the given pg_id
  - ```DELETE /hints/:hint_id``` -- Delete a hint

#### Render
  - ```POST /render``` -- Render HTML from PG

#### Check Answer
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

#### Student commands
  - ```userinfo``` -- Update student's info 
  - ```keypressed``` -- Send a keystroke
  - ```checkanswer``` -- Check answers
  
#### Teacher command
  - ```list_students``` -- List all connected students
  - ```send_hint``` -- Send a hint to a student
