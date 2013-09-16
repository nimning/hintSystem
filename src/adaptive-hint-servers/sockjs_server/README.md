## Files
- [sockjs_server.py](sockjs_server.py) -- Starts the SockJS server.
- [student_conn.py](student_conn.py) -- Handler for student connections (via ``\student``).
- [teacher_conn.py](teacher_conn.py) -- Handler for teach connections (via ``\teacher``).
- [common.py](common.py) -- Common code shared between ``student_conn.py`` and ``teacher_conn.py``.

## Messaging API specification

A valid message must be in the following format:
```javascript
message = JSON.stringify({
  'type': 'message_type',
  'arguments': { 
    'arg1': 'some_text',
    'arg2': 123
  }
});
```
To send a message to the server, 
```javascript
  sock = new SockJS('http://webwork.cse.ucsd.edu:1234/student');
  ...
  sock.send(message);
```

### Student [client -> server]

  - ``student_join`` Notifies the server that a student is connected. 

```javascript
{ 
  'type': 'student_join'
  'arguments': {
    'student_id': 'scheaman',
    'course_id': 'demo',
    'set_id': 'sandbox',
    'problem_id': '1',
    'problem_body': '<div>...</div>'
  }
}
```
  - ``student_answer`` Notifies the server that an answer box has been updated.
    - The client needs some logic to decide when to send the string. 
      - When losing focus.
      - When a timeout has been reached. 

```javascript
{ 
  'type': 'student_answer'
  'arguments': {
    'boxname': 'AnSwEr0001',
    'value': '123'
  } 
}
```

### Student [server -> client]
  - ``answer_status`` 
    - List of hints incuding locations, entered value, student feedback, hint_id

  - ``hints`` Inserts a hint to the student's browser
   
```javascript
{ 
  'type': 'hints'
  'arguments': [ {
    'hintbox_id': 'Hint0001',
    'hint_html': '<div>..</div>',
    'location': 'AnSwEr0001'
  }, ... ]
}
```

### Teacher [client -> server]
  - ``list_students`` -- List all connected students
  - ``send_hint`` -- Send a hint to a student

### Teacher [server -> client]
  - ``student_joined`` Received when a student has connected to the server.
  - ``student_left`` Receieved when a student has disconnected.
  - ``student_list`` A reponse to ``list_students``

