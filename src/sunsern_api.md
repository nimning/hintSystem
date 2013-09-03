adaptive-hint
=============

Requirements
------------
```
sockjs-tornado==1.0.0
tornado==3.1.1
```

rest_server.py
--------------
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


sockjs_server.py
----------------
#### Student commands
  - ```userinfo``` -- Update student's info 
  - ```keypressed``` -- Send a keystroke
  - ```checkanswer``` -- Check answers
  
#### Teacher command
  - ```list_students``` -- List all connected students
  - ```send_hint``` -- Send a hint to a student
