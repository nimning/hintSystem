#!/usr/bin/perl -w

################################################################################
# WeBWorK Online Homework Delivery System
# Copyright © 2000-2007 The WeBWorK Project, http://openwebwork.sf.net/
# $CVSHeader: webwork2/clients/renderProblem.pl,v 1.4 2010/05/11 15:44:05 gage Exp $
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of either: (a) the GNU General Public License as published by the
# Free Software Foundation; either version 2, or (at your option) any later
# version, or (b) the "Artistic License" which comes with this package.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See either the GNU General Public License or the
# Artistic License for more details.
################################################################################

=head1 NAME

webwork2/clients/renderProblem.pl

This script will take a file and send it to a WeBWorK daemon webservice
to have it rendered.  The result is split into the basic HTML rendering
and evaluation of answers and then passed to a browser for printing.

The formatting allows the browser presentation to be interactive with the 
daemon running the script webwork2/lib/renderViaXMLRPC.pm

Rembember to configure the local output file and display command !!!!!!!!

=cut

use strict;
use warnings;


##################################################
#  configuration section for client
##################################################

# Use address to WeBWorK code library where WebworkClient.pm is located.
use lib '/opt/webwork/webwork2/lib';
#use Crypt::SSLeay;  # needed for https
use WebworkClient;
use MIME::Base64 qw( encode_base64 decode_base64);

our ($XML_URL, $FORM_ACTION_URL, $XML_PASSWORD, $XML_COURSE, %credentials);

$XML_URL         = 'http://webwork.cse.ucsd.edu';
$FORM_ACTION_URL = 'http://webwork.cse.ucsd.edu/webwork2/html2xml';
$XML_PASSWORD    = 'xmlwebwork';
$XML_COURSE      = 'nonexisting_course';

%credentials = (
    userID    => "scheaman",
    password  => "scheaman",
    courseID  => "CompoundProblems",
);


use constant DISPLAYMODE   => 'images'; #  jsMath  is another possibilities.

our @COMMANDS = qw( listLibraries  renderProblem ); #listLib  readFile tex2pdf 


##################################################
# end configuration section
##################################################


##################################################
# input/output section
##################################################



our $rh_result;

die "Usage: $0 <PG file> <random seed>\n" if @ARGV < 2;

my $fileName = $ARGV[0];
my $problemSeed = $ARGV[1];

open(my $input_fh, "<", $fileName) || die "Can't open $fileName: $!";
my $source = join('', <$input_fh>);

############################################
# Build client
############################################
our $xmlrpc_client = new WebworkClient (
    url              =>  $XML_URL,
    form_action_url  =>  $FORM_ACTION_URL,
    displayMode      =>  DISPLAYMODE(),
    site_password    =>  $credentials{site_password},
    courseID         =>  $credentials{courseID},
    userID           =>  $credentials{userID},
    session_key      =>  $credentials{session_key},
);
 
$xmlrpc_client->encodeSource($source);
 
my $input = { 
    userID           =>  $credentials{userID}||'',
    session_key	     =>  $credentials{session_key}||'',
    courseID   	     =>  $credentials{courseID}||'',
    courseName       =>  $credentials{courseID}||'',
    password         =>  $credentials{password}||'',	
    site_password    =>  $credentials{site_password}||'',
    envir            =>  $xmlrpc_client->environment(),
 };


$input->{envir}->{fileName} = $fileName;

# set the random seed
$input->{envir}->{problemSeed} = $problemSeed;


#xmlrpcCall('renderProblem');
our $output;
our $result;
if ($result = $xmlrpc_client->xmlrpcCall('renderProblem', $input) )    {
    $output = $xmlrpc_client->formatRenderedProblem;  
} else {
    print "\n\n ERRORS in renderProblem \n\n";
    $output = $xmlrpc_client->{output};  # error report
}

# set seed value
my $oldseed = "name=\"problemSeed\" value=\"1234\"";
my $newseed = "name=\"problemSeed\" value=\"$problemSeed\"";

$output =~ s/$oldseed/$newseed/g;

print $output;

##################################################
# end input/output section
##################################################

1;
