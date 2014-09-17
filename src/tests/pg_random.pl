#!/usr/bin/env perl

use Module::Load;
use lib '/opt/webwork/pg/lib';
use lib '/opt/webwork/webwork2/lib';

my $filename = '/opt/webwork/pg/macros/PGbasicmacros.pl';

use PGrandom;

my $seed = 1234;
my $r1 = new PGrandom($seed);

my $x = $r1->random(1,5,1);
print "Random Number: ";
print $x;
print "\n"
