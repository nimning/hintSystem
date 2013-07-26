#
#  Data used by compoundProblem2.pg that can be copied
#  to the templates/macros directory where the instructor
#  can edit it.
#
#  Change the $parts variable to the part that is
#  currently active (reopen the homework set to let
#  the students continue to work on the problem if
#  the set closed before you provide the second
#  part).
#
#  The $isProfessor variable is used to determine
#  who gets to have a "go back to part 1" button.
#

$parts = 1;
$isProfessor = ($studentLogin eq 'dpvc' || $studentLogin eq 'professor');
