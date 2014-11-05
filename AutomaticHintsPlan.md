# Brief architecture overview

## REST Server
* Path: `src/adaptive-hint-servers/rest_server`
* interface with the webwork mysql database, performs some computations as well.
* filters should run in here
* Deployment detail: multiple processes are run because the mysql driver is blocking, nginx serves as a reverse proxy for the individual processes

## SockJS Server
* Path: `src/adaptive-hint-servers/sockjs_server`
* Handles realtime communication between clients and the server
** For students:
*** their answers are transmitted to the SockJS server (when they stop typing)
*** when hints are assigned, a command is sent to the student's browser to insert the hint
*** Also gets hint feedback, POSTs it to the REST server
** For instructors:
*** When browsing a student's view, they can get the student's current answers inserted if the student is online
*** To assign hints, the command must be sent to the SockJS server (see teacher_handler.py:add_hint)
*** Also tracks who is taking care of a student/which students are not being viewed

## adaptive_hints.js (student client)
* Path: `src/adaptive-hints-clients/webwork_js/adaptive_hints.js`
* Does the monitoring of students and handles commands to send hints
* Important limitation: Only active while the student is on the page, i.e. when the page reloads (eg. form submit) we can't do anything
** Solution: Scan the webwork database for new submissions

## Past answers daemon
* Path: `src/python/past_answers_to_answers_by_part.py`
* Converts webwork's past_answer table (containing all parts to a question) to one which has the answers for each part in separate rows
* Initially was a script which ran on a cron job, then became a daemon which runs constantly with a short sleep time.

# Timeline of events for assigning hints automatically:

1. Student submits a question [adaptive_hints.js]
2. Past answers daemon splits it up into parts, notifies SockJS server of the new answer (via a websocket)
3. SockJS server runs hint filters (by calling REST Server) on the part answer
4. If any filters match, assign the hint to the student (call REST server)
  * If the function returns a string instead of just True, interpret that as the hint PGML.
5. SockJS server needs to also notify the student's client that a new hint has been assigned (which is why the SockJS server needs to call the REST server to run filters, wait for response, then assign the hints - only it knows about student's currently active sessions)

# Automatic hint related architecture

## Filter functions
* Signature is `def answer_filter(answer_string, parse_tree, eval_tree, correct_string, correct_tree, correct_eval, user_vars)`
* Database table is created in `src/python/create_filter_functions.py` (uses sqlalchemy just because it's more readable and easier than piping an SQL file into a database shell)
* Currently the code is stored in a database field, needs to be stored on disk
* When filters are updated, a github repository should also be updated (can start with manual)
* Currently associated with a set and problem, but there's a dummy set for generic filters.
* Since the assigned\_hint table requires a hint\_id to assign the hints, there's a dummy hint created for each filter function, in case we want to return the PGML in a string ourselves.

# TODOS

- [ ] Store filter functions in a folder on disk
- [ ] Loading/Saving filter functions
Preferably use an intelligent directory hierarchy based on the course/set/problem_id
- [ ] Create database table to record which filter functions are assigned to which part and which hint
- [ ] Create UI for picking which filter function to assign to a problem part and a hint (may be optional if the function generates PGML for a hint, in which case we'd use the dummy hint ID)
- [ ] REST server needs an API call to run all assigned filter functions for a given part answer
- [ ] SockJS server needs to handle the notification of a new student answer from the past answer daemon and run the assigned filters (`daemon_handler.py`)
- [ ] Only run filters if a student has spent some minimum amount of time and/or attempts
- [ ] Once any filters have returned True/a PGML string, assign those hints to the user
- [ ] Notify the student's client to insert the new hint into the student's page
- [ ] Send hints to students who match a filter function after running the function via the TA interface


# Random bugfixes
- [ ] Hints don't use the psvn when rendering, so some variables might be seeded incorrectly (affects multi-part questions where there are multiple problems using the psvn as the same random seed across problems)
- [ ] Group hint sending does not use the pg_seed properly either
- [ ] Show hints which have been inserted for students who are not online (need to load assigned hints from the REST_server instead of SockJS if the student does not have an active SockJS session)
