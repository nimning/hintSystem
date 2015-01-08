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
   * Important limitation: Only active while the student is on the page,
     i.e. when the page reloads (eg. form submit) we can't do anything

     * Solution: Scan the webwork database for new submissions

5. Past answers daemon

   * Path: `src/python/past_answers_to_answers_by_part.py`
   * Converts webwork's past_answer table (containing all parts to a question)
     to one which has the answers for each part in separate rows
   * Initially was a script which ran on a cron job, then became a daemon which
     runs constantly with a short sleep time.


======
Design Decisions
======

1. AngularJS

   There are many client side application frameworks and libraries which aim to
   make it easier to develop rich interactive clients. Most follow some sort of
   MV*/Model-View-Whatever paradigm where the view in the page is generated
   using a template and some data stored in the model layer. There are many
   options in this space such as Angular, Ember, Backbone, Polymer, Knockout,
   React, Ractive, etc... with different tradeoffs.

   There are a few reasons I chose to use AngularJS.

   * I already had experience with it.
   * Tends to have stronger conventions for organizing your code and splitting
     things into files. Some other frameworks tend to have a more limited scope
     and thus don't necessarily dictate how you should structure the code that
     ties together the model and the view.
   * Stronger conventions should make it easier for new developers to understand
     the organization of a project.
   * Directives aim to allow encapsulating a view and its interactive
     functionality into reusable chunks, though it can be somewhat complicated
     to make them work correctly.
   * Model layer is a regular Javascript object, don't need to use getter/setter
     methods or other special methods to inform the framework that data has
     changed and the view should be updated.
   * The main development team is employed by Google so theoretically it seemed
     more likely to stick around (however, see the last point below)

   Drawbacks of Angular

   * The different components in Angular can be a little confusing to understand
     what they do and how they work; there's a lot of things to learn and a lot
     of jargon which sometimes doesn't mesh with language used outside of the
     project.
   * Directives can be pretty hard to understand at first
   * Weird watcher/scope issues can be hard to debug and understand - the easy
     cases are easier with Angular, but sometimes the harder cases can become
     more confusing.
   * Angular 2.0 was recently announced and has little in common with Angular
     1.x which kind of obsoletes some of the experience gained from using Angular.
   * Performance issues from using dirty checking vs magic setters.

   In hindsight, Google doesn't seem to use AngularJS anywhere important so it
   should have not mattered that Google backs it in some way. Now that they're
   changing the framework so drastically it becomes a little discouraging to
   work with Angular 1.x.

   I would consider something like Facebook's React more strongly now, because
   Facebook actually uses that in prominent places and while it's simpler and
   doesn't do everything Angular does, it's not clear that some of that stuff
   is even necessary.
