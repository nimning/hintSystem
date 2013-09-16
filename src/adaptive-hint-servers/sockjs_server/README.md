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


### Messages handled by the student server

<table>
  <tr>
    <th>Message</th>
    <th>Arguments</th>
    <th>Description</th>
    <th>Notes</th>
  </tr>
    <tr>
        <td>
<pre>
student_join
</pre>
        </td>
        <td>
<pre>
{ 
  'session_id': '7GPWHBoRc...',
  'student_id': 'scheaman',
  'course_id': 'demo',
  'set_id': 'sandbox',
  'problem_id': '1'
} 
</pre>
        </td>
        <td>
        Notifies the server that a student is connected.  
        </td>
        <td>
        The server resumed the previous session with the client using 'session_id'.
        </td>
    </tr>
    <tr>
        <td>
<pre>
student_answer
</pre>
        </td>
        <td>
<pre>
{
  'boxname': 'AnSwEr0001',
  'value': '123'
} 
</pre>
        </td>
        <td>
        Notifies the server that an answer box has been updated. 
        </td>
        <td>
        The server will send back 'answer_status' message 
        once the answer checking process is complete.
        </td>
    </tr>
</table>


### Messages handled by the student client

<table>
  <tr>
    <th>Message</th>
    <th>Arguments</th>
    <th>Description</th>
    <th>Notes</th>
  </tr>
    <tr>
        <td>
<pre>
hints
</pre>
        </td>
        <td>
<pre>
[{ 
  'hintbox_id': 'Hint1183',
  'location': 'AnSwEr0001',
  'hint_html': '...'
},...] 
</pre>
        </td>
        <td>
        Requests the client to display the hints.
        </td>
        <td>
        In the current implementation, existing hints on the browser are removed prior to
        inserting the new hints. The server needs to send all of the hints.
        </td>
    </tr>
    <tr>
        <td>
<pre>
answer_status
</pre>
        </td>
        <td>
<pre>
[{
  'boxname': 'AnSwEr0001',
  'entered_value': '123',
  'is_correct': False,
  'error_msg': ''
},...] 
</pre>
        </td>
        <td>
        Requests the client to update the answer boxes.
        </td>
        <td>
        -
        </td>
    </tr>
</table>


### Messages handled by the teacher server

<table>
  <tr>
    <th>Message</th>
    <th>Arguments</th>
    <th>Description</th>
    <th>Notes</th>
  </tr>
    <tr>
        <td>
<pre>
teacher_join
</pre>
        </td>
        <td>
<pre>
{ 
  'teacher_id': 'scheaman'
} 
</pre>
        </td>
        <td>
        Notifies the server that a teacher is connected.
        </td>
        <td>
        -
        </td>
    </tr>
    <tr>
        <td>
<pre>
list_students
</pre>
        </td>
        <td>
<pre>
{}
</pre>
        </td>
        <td>
        Requests the list of connected students from the server.
        </td>
        <td>
        The server will response with 'student_list'.
        </td>
    </tr>
    <tr>
        <td>
<pre>
add_hint
</pre>
        </td>
        <td>
<pre>
{
  'session_id': '8Qa12ad1...',
  'course_id': 'demo',
  'set_id': 'sandbox',
  'problem_id': '1',
  'location': 'AnSwEr0001',
  'hintbox_id': 'Hint1231',
  'hint_html': '...'
}
</pre>
        </td>
        <td>
        Give a new hint to a student identified by her 'session_id'
        </td>
        <td>
        -
        </td>
    </tr>
</table>


### Messages handled by the teacher client

<table>
  <tr>
    <th>Message</th>
    <th>Arguments</th>
    <th>Description</th>
    <th>Notes</th>
  </tr>
    <tr>
        <td>
<pre>
student_list
</pre>
        </td>
        <td>
<pre>
[{ 
  'session_id': '7GPWHBoRc...',
  'student_id': 'scheaman',
  'course_id': 'demo',
  'set_id': 'sandbox',
  'problem_id': '1',
  'hints': { ... },
  'answers': { ... },
  'pg_file': '/opt/webwork/...',
  'pg_seed': 1234
},...] 
</pre>
        </td>
        <td>
        A list of connected students and their information.
        </td>
        <td>
        This is the response to 'list_student' message.
        </td>
    </tr>
</table>



