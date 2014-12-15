.. _architecture:

=============
Architecture Overview
=============

The Webwork Adaptive Hints system is comprised of several components which
coordinate together to provide an overview of student performance in Webwork
and send hints automatically to students who are struggling.

1. REST Server

   * Path: `src/adaptive-hint-servers/rest_server`
   * interface with the webwork mysql database, performs some computations as well.
   * filters should run in here
   * Deployment detail: multiple processes are run because the mysql driver is blocking, nginx serves as a reverse proxy for the individual processes

2. SockJS Server

   * Path: `src/adaptive-hint-servers/sockjs_server`
   * Handles realtime communication between clients and the server

     * For students:

       * their answers are transmitted to the SockJS server (when they stop typing)
       * when hints are assigned, a command is sent to the student's browser to insert the hint
       * Also gets hint feedback, POSTs it to the REST server

     * For instructors:

       * When browsing a student's view, they can get the student's current answers inserted if the student is online
       * To assign hints, the command must be sent to the SockJS server (see teacher_handler.py:add_hint)
       * Also tracks who is taking care of a student/which students are not being viewed

3. Teacher UI

   * Client side interface built using AngularJS (1.2)

4. Student Client (embedded in Webwork)

   * Path: `src/adaptive-hints-clients/webwork_js/adaptive_hints.js`
   * Monitors student answers and handles commands to send hints
   * Important limitation: Only active while the student is on the page, i.e. when the page reloads (eg. form submit) we can't do anything

     * Solution: Scan the webwork database for new submissions

5. Past answers daemon

   * Path: `src/python/past_answers_to_answers_by_part.py`
   * Converts webwork's past_answer table (containing all parts to a question) to one which has the answers for each part in separate rows
   * Initially was a script which ran on a cron job, then became a daemon which runs constantly with a short sleep time.
