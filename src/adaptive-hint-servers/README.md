### Production
```
/etc/init.d/hint-sockjs-4350 {start|restart|stop}
/etc/init.d/hint-rest-7250 {start|restart|stop}
/etc/init.d/hint-rest-7251 {start|restart|stop}
/etc/init.d/hint-rest-7252 {start|restart|stop}
/etc/init.d/hint-rest-7253 {start|restart|stop}
/etc/init.d/hint-rest-7254 {start|restart|stop}
```

### How to run test servers
```
python rest_server/rest_server.py --port=1234
python sockjs_server/sockjs_server.py --port=4321 --rest_port=1234
```

### Known issues

* Webwork /html2xml service does not return the correct answer when the correct answer is "0". For example,

```
DOCUMENT();

loadMacros(
  "PGstandard.pl",
  "PGML.pl",
  "MathObjects.pl",
  "Parser.pl",
  "PGunion.pl",
  "PGcourse.pl",
  "PGchoicemacros.pl",
);

TEXT(beginproblem());
BEGIN_PROBLEM();

##############################################

$isProfessor = ($studentLogin eq 'yoav.freund' || $studentLogin eq 'professor');
Context("Interval");
$showPartialCorrectAnswers = 1; # show student the correct part of their answer.

BEGIN_PGML

Is 1 a prime? (1 = yes, 0 = no) [____]{0}

END_PGML

END_PROBLEM();
ENDDOCUMENT();
```
   The main webwork does not have this bug.
  
