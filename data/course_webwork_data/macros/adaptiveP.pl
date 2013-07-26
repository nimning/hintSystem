package adaptiveP;

use "problemPool.pl"  # ???

our %defaultStatus = (
	times => 0,
	hintUsed => 0,
	initialDist => "***",
	currentDist => "***",
	hint => 0,
	hintS => "*",
);

sub new
{
	my $self = shift; my $class = ref($self) || $self;
	
	my $p = bless
	{
		ans => "110",
		maxDel => 1,
		grader => $main::PG_FLAGS{PROBLEM_GRADER_TO_USE} || \&main::avg_problem_grader,
		@_,
		status => $defaultStatus,
	}, $class;
	
	$p->reset if $main::inputs_ref->{_reset};
	$p->getStatus;
	$p->initial;
	return $p;
}

sub initial
{
	my $self = shift;
	main::install_problem_grader(\&adaptiveP::grader);
	$main::PG_FLAGS{adaptiveP} = $self;
}

sub getStatus
{
	my $self = shift;
	main::RECORD_FORM_LABEL("_del");
	main::RECORD_FORM_LABEL("_reset");
	main::RECORD_FORM_LABEL("_status");
	$self->{status} = $self->decode;
	
	if ($main::inputs_ref->{_del} || 
		($main::inputs_ref->{submitAnswers} && $main::inputs_ref->{submitAnswers} eq "Delete some options"))
	{
		$self->{status}->{hintUsed} += 1;
		$self->{status}->{initialDist} = $self->{status}->{currentDist};
	}
	
	if ($main::inputs_ref->{_hint} || ($main::inputs_ref->{submitAnswers} && $main::inputs_ref->{submitAnswers} eq "hint"))
		{$self->{status}->{hint} = 1;}
}

sub setProblem
{
	my $self = shift;
	# @keys = main::lex_sort(keys(%anwsers));
	# $ans = $self->getNext(@keys);
	if ($self->{status}->{hint} == 0)
		{$self->setOptions();}
	else
	{
		$self->s2hintS();
		my @options = ();
		foreach (main::lex_sort(keys(%hintOptions)))
			{push (@options, %hintOptions->{$_});}
		@{$self->{otherOptions}} = @options;
	}
}

sub setOptions
{
	$self = shift;
	my @options = ();
	my @i = qw (A B C D E F G H);
	foreach (main::lex_sort(keys(%anwsers))) {
		if ($self->ifGET($_)) {
			push (@options, %anwsers->{$_});
			%ans2s->{shift(@i)} = $_;
		}
	}
	
	@{$self->{otherOptions}} = @options;
}

sub question
{
	my $self = shift;
	if ($self->{status}->{hint} == 0)
		{return %pool->{$self->{ans}};}
	else
		{return %pool->{$self->{ans}} ."<br/>" .%hint->{"1"};}
		#return {$self->{status}->{hintS}}}
}

sub answer
{
	my $self = shift;
	if ($self->{status}->{hint} == 0)
		{return %anwsers->{$self->{ans}};}
	else
		{return %hintOptions->{$self->{status}->{hintS}};}
}

sub otherOptions
{
	my $self = shift;
	return $self->{otherOptions};
}

sub getNext
{
	my $self = shift;
	@keys = shift;
	#return @keys[0];
	return "101";
}


sub ifGET {
	my $self = shift;
	my $dist = shift;
	if ($self->cmp( $self->dis($dist, $self->{ans}), $self->{status}->{initialDist}))
		{return 1;}
	else
		{return 0;}
}

sub dis
{
	my $self = shift;
	my $a = shift;
	my $b = shift;
	my $dist = "";
	for ($i = 0; $i < 2; $i++)
	{
		if ((substr($a, $i, 1) eq "*") || (substr($b, $i, 1) eq "*"))
			{substr($dist,$i) = "*";}
		else
		{
			if (substr ($a, $i, 1) eq substr($b, $i, 1))
				{substr($dist, $i) = "1";}
			else
				{substr($dist, $i) = "0";}
		}
	}
	substr($dist, 2) = "*";
	return $dist;
}

sub cmp
{
	my $self = shift;
	my $a = shift;
	my $b = shift;
	my $cmp = 1;
	for ($i = 0; $i < 3; $i++)
	{
		if ((substr ($a, $i, 1) eq "0") && (substr($b, $i, 1) eq "1"))
			{$cmp = 0;}
	}
	return $cmp;
}



	# foreach $key (keys(%{$_[0]->{AnSwEr1}}))
	# {
		# $result->{msg} .= "key=$key,<br/>value=";
		# $result->{msg} .= $_[0]->{AnSwEr1}->{$key}."<br/><br/>";
	# }

sub grader
{
	my $self = $main::PG_FLAGS{adaptiveP};
	my ($result,$state) = &{$self->{grader}}(@_);
	$stuAns = %ans2s->{$_[0]->{AnSwEr1}->{student_ans}} || "***"; # student's answer
	$self->{status}->{currentDist} = $self->dis($stuAns, $self->{ans});
	$self->{status}->{times} += 1;

	# my $label = "<b>Go on to next part</b> (when you submit your answers).";
	# my $par = $main::PAR;
	# $result->{msg} .= qq!$par<input type="checkbox" name="_next" value="next" />$label!;
	# $result->{msg} .= $self->{status}->{currentDist}. "<br/>";
	# $result->{msg} .= $self->cmp( $self->dis($stuAns, $self->{ans}), "11*" ). "<br/>";
	
	# use Data::Dumper;
	$result->{msg} .= Dumper($_[0]->{AnSwEr1});
	
	if ($self->{status}->{currentDist} eq "00*" && $self->{status}->{hint} == 0)
	{
		$result->{msg} .= $self->hintCheckbox("hint",1);
	}
	else
	{
		if ($self->{status}->{times} > 1 && $self->{status}->{delUsedN} < $self->{maxDel} && $self->{status}->{hint} == 0)
		{
			$result->{msg} .= $self->delCheckbox("Delete some options",1);
		}
	}
	
	if ($self->{status}->{hint} == 1 && $result->{score}>0)
	{
		$self->{status}->{hint} = 0;
	}
	# if ($main::inputs_ref->{_del})
	# {
		# $self->{status}->{delUsed} = 1;
		# $result->{msg} .= " delete something ";
	# }
	
	
	# $result->{msg} .= $main::inputs_ref->{_del} ."<br/>";
	
	$result->{msg} .= $self->resetCheckbox("Reset",0);
	
	
	my $data = quoteHTML($self->encode);
	$result->{msg} .= qq!<input type="hidden" name="_status" value="$data" />!;

	return ($result,$state);
}



sub s2hintS
{
	$self = shift;
	$s = $self->{ans};
	$self->{status}->{hintS} = substr($s,0,1);
}








	sub reset {
		my $self = shift;
		$main::inputs_ref->{_status} = $self->encode(\%defaultStatus);
	}
	
	sub resetCheckbox {
		my $self = shift;
		my $label = shift || " <b>Go back to Part 1</b> (when you submit your answers).";
		my $par = shift; $par = ($par ? $main::PAR : '');
		qq'$par<input type="checkbox" name="_reset" value="1" />$label';
	}
	
	sub delButton {
		my $self = shift;
		my $label = quoteHTML(shift || "Go on to Next Part");
		my $par = shift; $par = ($par ? $main::PAR : '');
			$par . qq!<input type="submit" name="previewAnswers" value="$label" !
			. q!onclick="document.getElementById('_del').value=1" />!;
	}
	
	sub delCheckbox {
		my $self = shift;
		my $label = shift || " <b>Go on to next part</b> (when you submit your answers).";
		my $par = shift; $par = ($par ? $main::PAR : '');
		qq'$par<input type="checkbox" name="_del" value="1" />$label';
	}
	
	######################################################################
	#
	#  Encode all the status information so that it can be
	#  maintained as the student submits answers.  Since this
	#  state information includes things like the score from
	#  the previous parts, it is "encrypted" using a dumb
	#  hex encoding (making it harder for a student to recognize
	#  it as valuable data if they view the page source).
	#
	sub encode {
	  my $self = shift; my $status = shift || $self->{status};
	  my @data = (); my $data = "";
	  foreach my $id (main::lex_sort(keys(%defaultStatus))) {push(@data,$status->{$id})}
	  foreach my $c (split(//,join('|',@data))) {$data .= toHex($c)}
	  return $data;
	}

	#
	#  Decode the data and break it into the status hash.
	#
	sub decode {
	  my $self = shift; my $status = shift || $main::inputs_ref->{_status};
	  return {%defaultStatus} unless $status;
	  my @data = (); foreach my $hex (split(/(..)/,$status)) {push(@data,fromHex($hex)) if $hex ne ''}
	  @data = split('\\|',join('',@data)); $status = {%defaultStatus};
	  foreach my $id (main::lex_sort(keys(%defaultStatus))) {$status->{$id} = shift(@data)}
	  return $status;
	}

	#
	#  Hex encoding is shifted by 10 to obfuscate it further.
	#  (shouldn't be a problem since the status will be made of
	#  printable characters, so they are all above ASCII 32)
	#
	sub toHex {main::spf(ord(shift)-10,"%X")}
	sub fromHex {main::spf(hex(shift)+10,"%c")}

	#
	#  Make sure the data can be properly preserved within
	#  an HTML <INPUT TYPE="HIDDEN"> tag.
	#
	sub quoteHTML {
		my $string = shift;
		$string =~ s/&/\&amp;/g; $string =~ s/"/\&quot;/g;
		$string =~ s/>/\&gt;/g;  $string =~ s/</\&lt;/g;
		return $string;
	}