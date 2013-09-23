## Files
- [sockjs_server.py](sockjs_server.py) -- Main entry point for the SockJS server.
- [student_handler.py](student_handler.py) -- Handler for student connections (via ``\student``).
- [teacher_handler.py](teacher_handler.py) -- Handler for teach connections (via ``\teacher``).
- [student_session.py](student_session.py) -- Provides an interface to each student's session information.
- [session_storage.py](session_storage.py) -- Storage for storing session information.
- [_base_handler.py](_base_handler.py) -- A base handler class for both student and teacher.

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
    <tr>
        <td>
<pre>
hint_feedback
</pre>
        </td>
        <td>
<pre>
{
  'hintbox_id': 'Hint0001',
  'feedback': 'Helpful'
} 
</pre>
        </td>
        <td>
        Notifies the server that a feedback box has changed. 
        </td>
        <td>
        *Not Yet Implemented*
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
  'teacher_id': 'TA_1',
  ('student_id': 'scheaman',)*
  ('course_id': 'demo',)*
  ('set_id': 'sandbox',)*
  ('problem_id': '1')*
} 
</pre>
        </td>
        <td>
        Notifies the server that a teacher is connected.
        </td>
        <td>
        * are optional.
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
{
  'course_id': 'demo'
}
</pre>
        </td>
        <td>
        Requests the list of connected students from the server.
        </td>
        <td>
        The server will response with 'unassigned_students' and 'my_students'.
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
  'student_id': 'scheaman',
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
        Assign a hint to a student
        </td>
        <td>
        -
        </td>
    </tr>
    <tr>
        <td>
<pre>
remove_hint
</pre>
        </td>
        <td>
<pre>
{
  'student_id': 'scheaman',
  'course_id': 'demo',
  'set_id': 'sandbox',
  'problem_id': '1',
  'location': 'AnSwEr0001',
  'hintbox_id': 'Hint1231',
}
</pre>
        </td>
        <td>
        Remove a hint from a student
        </td>
        <td>
        -
        </td>
    </tr>
    <tr>
        <td>
<pre>
request_student
</pre>
        </td>
        <td>
<pre>
{
  'session_id': '8Qa12ad1...',
}
</pre>
        </td>
        <td>
        Request to help the student identified by the session_id.
        </td>
        <td>
        The server will response with 'unassigned_students' and 'my_students'.
        </td>
    </tr>
     <tr>
        <td>
<pre>
release_student
</pre>
        </td>
        <td>
<pre>
{
  'session_id': '8Qa12ad1...',
}
</pre>
        </td>
        <td>
        Release the student identified by the session_id to unassigned pool.
        </td>
        <td>
        The server will response with 'unassigned_students' and 'my_students'.
        </td>
    </tr>
    <tr>
        <td>
<pre>
get_student_info
</pre>
        </td>
        <td>
<pre>
{
  'student_id': 'scheaman',
  'course_id': 'demo',
  'set_id': 'sandbox',
  'problem_id': '1'
}
</pre>
        </td>
        <td>
        Get a student info of a specified student
        </td>
        <td>
        The server will response with 'student_info'.
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
unassigned_students
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
  'hints': [ ... ],
  'answers': [ ... ]
},...] 
</pre>
        </td>
        <td>
        A list of students in the unassigned pool.
        </td>
        <td>
        -
        </td>
    </tr>
    <tr>
        <td>
<pre>
my_students
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
  'hints': [ ... ],
  'answers': [ ... ]
},...] 
</pre>
        </td>
        <td>
        A list of students assigned to the client.
        </td>
        <td>
        -
        </td>
    </tr>
    <tr>
        <td>
<pre>
student_info
</pre>
        </td>
        <td>
<pre>
{ 
  'student_id': 'scheaman',
  'course_id': 'demo',
  'set_id': 'sandbox',
  'problem_id': '1',
  'pg_file': '/opt/path/problem.pg',
  'pg_seed': 123,
  'hints': [ ... ],
  'answers': [ ... ],
  'current_answers': { ... }
}
</pre>
        </td>
        <td>
        Student-Problem information
        </td>
        <td>
        This is the response to 'get_student_info' or whenever there are changes.
        </td>
    </tr>
</table>



