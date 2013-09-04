## Transport Layer

To unify the low level communication and provide checking we will a
Socket class, both on the javascript side and on the server side. The
socket provide the infrastructure for sending JSON packets back and
forth.
The Socket class supports the following public methods:

* *Open*(server-address, @NewCallBack, @StatusCallBack): opens a connection
to the server.
 * @NewCallBack is a pointer to a subroutine that is called when a new
   packet is available from the server.
 * @StatusCallBack points to a subroutine that is called when an valid
   acknowledgement is recieved from the other side or if repeated
   attempts to connect have failed (according to some retry policy).
* *Send* (packet): sends a JSON packet.
* *Close*: close the connection

## Client
The client will be written in JavaScript and use the BackBone
Model-View pattern.

*Yoav:* As I am ignorant about JavaScript, I will not attempt a
detailed description here, but just give a high-level description of
the needed functionality.

* *Parse HTML:* Send The HTML to the server and get back a modified
   HTML. The Modified HTML has ID's associated with each of the
   question-answer pairs. (By having this Parsing done on the server
   we make sure that there is no mismatch between the server and the
   client. I need to check with Gage, but the HTML might be cached on
   the server, in which case only an index would have to be sent to
   the hint server).
* *HeartBeat:* each client sends a "heartbeat" packet to the server
   every 10 seconds or so. This way the server knows which clients are
   active. From the "Ack" reply of the server the client knows whether
   or not it has a working connection to the hints server.
* *Capture Keystrokes:* The script will listen for keystrokes on each
   of the boxes (both of original questions and of hints). When
   keystrokes are captured, they will be sent to the server every 5
   seconds (not waiting for the <CR>)
* *Insert hints:* When the script recieves a hint, together with an
   index that defines the location. It inserts the hint in the
   appropriate place and starts a new listener for the answer.
* *Submit:* The final evaluation of the answers will be performed just
   as it is now - when the user presses the "submit" button. However,
   to allow continuity this submit is intercepted by the script which
   send the appropriate "POST" to the webwork server.

## Server
Unlike the client, the server maintains a large number of
connections. It does not initiate opening connections, but responds to
incoming open requests.

As the server might need to serve many students and TAs/Tutors at the
same time, we plan to use multiple threads, each thread servicing
multiple connections.

Each thread uses a separate port, I will refer to them as port0,port1
etc. Port0 is special in that it is where the connection is initiated,
the other ports are used for actual communication. 

Server_Transport consists of the following classes:
* ConnectionListener: listens on port0 for requests for a new
  connection. Upon recieving a request, either assigns it to an
  existing StudentServer or TAServer, or starts a new student server on a new port.

* StudentState: a data structure holding the student's state.
  * Current PG file
  * Current HTML 
  * Keystrokes (timestamped)
  * Hints recieved (timestamped)
  
* StudentServer: A class for handling updates to the student
  state. Each student server uses a separate port for communicating and a
  list of StudentState instances that it manages.

* TAState: The list of students that the TA is currently helping. A
  pointer to the StudentState for each of those.
  
* TAServer: Similar to StudentServer, but for TA's

## Implementation

<https://github.com/sunsern/adaptive-hint>

<https://github.com/sunsern/adaptive-hint/blob/master/README.md>
