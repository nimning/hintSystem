Architecture of the hint-server
===============================

## **DB** Database ##
### Tables: ###
1. Hints: pgml snippets.
2. Activity log: student,Assignment,problem,part,text-typed
3. Everything that Webwork stores in the database.

## **JS** Client side program (javascript) ##
After initiation, parses the page and identifies the locations of the
answer boxes. It then:

1. (Optional) _Focus Control_ Allows the student to type into boxes
only after the previous boxes have been filled.
2. The client sends a JSON message to the AJAX server at least once a
minute, sending a JSON message, which contains a time stamp and the ID
of the current page that the user is working on. When the user types,
the updates are more frequent (every 10 seconds) and the JSON message
contains the user's keystrokes since the last message.  In response,
the server sends a JSON getting new hints if any. At the least, it is
a mutual live signal. If page is hidden (for example, the browser is
on another tab), the javascript should not send anything.
3. Sends the keystrokes the user types back to the _AJAX_ server.
4. Recieves hints from server, displays them, Optionally moves the
focus point to the hint answer box [^1]

## **AJAX** server side that communicates with the javascript client ##
* The server program will be written in python and will run on the same
machine as the webwork server.
* There should be a separate thread running for each student that is
logged in.
* The server decides whether and which hint based on:
 1. The page presented and the box being worked on.
 2. The student's profile.
 3. The keystrokes entered.
 4. the amount of time the student spent on working on the box.
 5. A proposed hint by an Instructor/TA.
* The hint is sent back to the client.
* When an answer is typed in, the server passes it on to the answer
  parser, and, if the answer is incorrect, passes it also to the
  pattern matcher for mistakes.

## Changes to WebWork ##
This should be restricted to adding a line or two to the header of
each html page, which instantiates the javascript program and
potentially passes it an index identifying the page.

## Hint Authoring This is a separate application, which runs on the
machines of the Instructor, the TA's, and the tutors. It maintains a
queue of students that have been struggling with a particular part of
a particular question for at least 10 minutes. The instructor can then
get a summary of what the student did on the current problem, and
choose an existing hint to show to the user or write a new hint, which
can have an associated question and answer box. This hint authoring
program will be based on Mike Gage's
[standalone question renderer](https://github.com/mgage/standalone-question-renderer.git)
The hint snippets will be placed in the database. Rules will be
associated with the different hints as described above. For example
the hint "Please write the expression and not just the final result"
or "malformed expression" can be used for almost all questions, based
on simple rules.


* * * * *
[^1]: It is an interesting question whether or not the student would
benefit from being limited to one box at a time. Might foster more
rigorous thinking or it might aggrevate the students. It might be
better to allow the students to have the hints be only for the benefit
of the student, not an added challenge. We probably should have
configuration parameters to control these options.

