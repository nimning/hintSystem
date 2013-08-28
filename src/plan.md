Relevant information about the design of Webwork2
=================================================
### Information from Mike Gage:

* All of the mechanisms for answering the questions, including PGML, are
in the code in the directory webwork/pg/macros and webwork/pg/lib.
* There are several "bridges" between pg and the outside
world.  One of them is [Webworkwebservice/RenderProblem.pm](https://github.com/openwebwork/webwork2/blob/master/lib/WebworkWebservice/RenderProblem.pm), another is
[webwork2/lib/WeBWorK/ContentGenerator/Problem.pm](https://github.com/openwebwork/webwork2/blob/master/lib/WeBWorK/ContentGenerator/Problem.pm)
The third is the library browser which is in WeBWorK/Utils/Tasks.pm
The last one is the most recent and probably the best written bridge.
I'd like to refactor and rewrite the other two to look more like the
last one.  Also involved are PG.pm and PG/Local.pm
* The main purpose of the outside of the bridge is to build the envir
variable (a large hash) which defines the information available with
the PG world and a to construct a Safe compartment to compile and run
the PG problem. The safe compartment is also passed some other
precompiled programs that it is allowed to use.
* On the PG side, the environment is unpacked in pg/macros/PG.pl and
the basic macros were defined in PGbasicmacros.pl although I have
rewritten many of them to use PGcore.pm instead.  The original code
was perl4 and CGI -- the PGcore modifications take better advantage of
the object orientation in perl5 and the caching of mod_perl.

[Some Documentation about remote rendering](http://webwork.maa.org/wiki/MikeRemoteRendering)

### The JSON webservice in webwork
Webwork includes a json-based webservice. Developed by Peter Staab <pstaab@fitchburgstate.edu>.

The relevant PERL code is in
[webwork2/lib/WebWorkwebservice.pm](https://github.com/openwebwork/webwork2/blob/master/lib/WebworkWebservice.pm) and in the files in the directory  [webwork2/lib/WebWorkwebservice/](https://github.com/openwebwork/webwork2/tree/master/lib/WebworkWebservice)

The implementation uses the [backbone library](http://backbonejs.org/)
Implemetations using backbone seperate between the models and the views.
Yoav believes that the relevant model is [problem.js](https://github.com/openwebwork/webwork2/blob/develop/htdocs/js/lib/models/Problem.js)
and the relevant view [ProblemView.js](https://github.com/openwebwork/webwork2/blob/develop/htdocs/js/lib/views/ProblemView.js)

Note that this code is in the develop branch of the github repository. It is therefor not on our server yet.

Yoav: I would like to identify the PERL files that embed this javascript. I will try to schedule another meeting with Peter Staab.


The code implements both an XML, SOAP and JSON interface.

The skeleton of this API is given here:
[WebworkAPI](https://github.com/whytheplatypus/WeBWorK-API)

It is probably more useful to follow the examples that use this API
here: 

* [ProblemView.js](https://github.com/openwebwork/webwork2/blob/develop/htdocs/js/lib/views/ProblemView.js)
* [LibraryBrowser/](https://github.com/openwebwork/webwork2/tree/master/htdocs/js/apps/LibraryBrowser)
  
*Yoav Question:* where in these javascript is the code for sending
 the JSON query, and where is it specified which webservice routine is
 supposed to recieve and execute the query?

## Example of a multi-part problem using javascript:

Mike Gage has a javascript-based multipart problem (Yoav: I believe this does not use backbone.js)

* [CompoundProblem2.pl](https://github.com/openwebwork/pg/blob/develop/macros/compoundProblem2.pl)
* A deployed .pg file using
  CompoundProblem2:[CompoundproblemExperiments/7](http://webwork.cse.ucsd.edu/webwork2/CompoundProblems/compoundProblemExperiments/7)
  ( You will need an account to have access to these files, send an
  email to yfreund@ucsd.edu )
* [An annotated Example of a .pg file using CompoundProblem.pl](http://webwork.maa.org/wiki/CompoundProblems#.UgeXqGRATYY)
* The main source file for this is (old) is [CompoundProblem.pl](https://github.com/openwebwork/pg/blob/develop/macros/compoundProblem.pl)


Architecture of the hint-server
===============================

The following demo movie on youtube can serve as a rough mockup of the
interface we have in mind:
[YouTube, Adaptive Hints](http://www.youtube.com/watch?v=7KNzBAlh8L0)

## Displaying Hints from the Server
Hints are associated with an answerbox in a problem page.  They are
displayed before the question associated with the box.

PGML files should allow for labels, eg: LABEL "start part 1"
Hints could then be associated with these labels, instead of with just
boxes

* *Yoav* Mike Gage told me that in the new version of pg boxes can be
       associated with labels.

To allow us to associate student histories, pgml snippets, ... with
hint display locations, the HintLocation table is indexed by
the id/assignment/label.

## **AJAX** server side that communicates with the javascript client ##
* The server program will be written in python and will run on the same
machine as the webwork server.

Each user is associated with an entry in the database which stores the
state of the user (logged in, active, working on problem X) etc. Each
process on the server will serve 1-10 users.

* The server decides whether and which hint based on:
 1. The page presented and the box being worked on.
 2. Previous expressions answered, the hint/part answered for, and timestamps
 3. The keystrokes entered.
 4. the amount of time the student spent on working on the box.
 5. A proposed hint by an Instructor/TA.
 6. Other information in the student's profile: grades in previous courses, class year, ...
* The hint is sent back to the client.
* When an answer is typed in, the server passes it on to the answer
  parser, and, if the answer is incorrect, passes it also to the
  pattern matcher for mistakes.

## Changes to WebWork
This should be restricted to adding a line or two to the header of
each html page, which instantiates the javascript program and
potentially passes it an index identifying the page.

## Hint Authoring
This is a separate application, which runs on the
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

Mike Gage will try to create a .dmg file that contains a standalone
server. I have not been successful in installing the standalone server
from git on a mac. (Yoav)

## Next Steps
*Yoav:* Here is my suggestion:

* Expand on compoundProblem2.pm so that:
   1. It uses jQuery/accordion instead of javascript
   2. It communicates with the server to 
	  * send keystrokes and 
	  * recieve *rendered* hint snippets. (using Webworkwebservice/RenderProblem.pm)
   3. Control which elements are seen and which empty boxes can be / have
to be filled.

*Yoav* I have changed the next steps based on what I learned about
 existing parts of webwork2.

*Matt's* last version:
> * Get key functionality with javascript in WebWork pages: 
>     * Get the user, assignment, and problem from the webwork page
>     * Write a javascript function display_after_box(box_index) that adds html before or after the box with the given index.  This script should find a nearby `<br>` or `<p>` tag, and insert here (instead of in the middle of a paragraph).
> * Change the student_adaptive_server/server.py clint/server to adhere to the slightly tweaked client/server protocol
> * Improve expression correctness evaluation: it could be better
> * Install WebWork <-- Done
> * Write hints

* * * * * 

[^1]: It is an interesting question whether or not the student would
benefit from being limited to one box at a time. Might foster more
rigorous thinking or it might aggrevate the students. It might be
better to allow the students to have the hints be only for the benefit
of the student, not an added challenge. We probably should have
configuration parameters to control these options.

[^2]: Why should we send for every key entered, rather than
  faster/slower based on how fast the user is typing?  Using the JSON
  protocol we outlined, communication is still very light.  We'll need
  to profile to ensure computing answer correctness is fast- this is
  probably the greatest issue.  Too much space taken up, or too many
  entries in the answer history database?  Assuming 420 chars per
  minute, a user spends an average of 1 hour per day on WebWork, and
  200 users, this is 420*60*200 = 5M rows in the database.  Our db
  should have no problem handling this.  If we have some scaling issue
  later, we can always send or store less expressions.  We shouldn't
  prematurely optimize though.
  
  *Yoav* The reason I want a package to be sent every minute or so is
  for both client and server to know that the other side is there.
  The reason I don't want each symbol to be sent as a packet is that
  sometimes many characters are types in quick succession, say, when
  the user cuts and pastes a long expression. The caclculation you are
  doing regards *throughput* not *latency*. From the point of view of
  latency, unpacking many small json packets can take a long time.
