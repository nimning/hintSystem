



our %pool = (
	"000" => "You’re planning a study of vacation spending. From a past study, you have reason to believe that spending plans are normally distributed with σ = $600. You survey 500 people for study and conduct a hypothesis test for it.",
	"001" => "A sample of Alzheimer's patients is tested to assess the amount of time in stage IV sleep. It has been hypothesized that individuals suffering from Alzheimer's disease may spend less time per night in the deeper stages of sleep. Number of minutes spent is Stage IV sleep is recorded for sixty-one patients. The sample produced a mean of 48 minutes (S=14 minutes) of stage IV sleep over a 24 hour period of time.",#"Gasoline pumped from a supplier’s pipeline is supposed to have an octane rating of 87.5. To test this, a sample was taken on 13 consecutive days and the octane measured in a lab.",
	"010" => "",
	"011" => "You’re planning a survey to see what fraction of people who live in Virgil would take the bus if the county added a route between Greek Peak and downtown Cortland via routes 392 and 215. You will random do survey with 100 people about it. Make a hypothesis test whether you are 95% confidence that more than 20% people like to take bus.",
#			"In World War II, a prisoner of war flipped a coin 10,000 times and recorded 5,067 heads. If the coin was fair, it should turn up 50% heads in the long run. Test whether the coin was fair, at the 0.05 level of significance.",
#			"You’ve read that two thirds of Americans believe in angels. You want to see whether that’s true at TC3, so you take a random sample of 100 TC3 students and you find that 61 of them believe in angels. Construct a hypothesis test whether more than 60% of TC3 students believe in angels.",
	"100" => "",
	"101" => "In a large elementary school, you select two age-matched groups of students. Group 1 of 30 students follows the normal schedule. Group 2 of 30 students (with parents’ permission) spends 30 minutes a day learning to play a musical instrument. You want to show that learning a musical instrument makes a student less likely to get into trouble. You consider a student in trouble if s/he was sent to the principal’s office at any time during the year.",
	"110" => "Last week, you showed that 42% of TV viewers of 950 people you surveyed watched American Idol. You conducted a survey whether people watched American Idol this week for 1000 people and 400 people said ”yes”. Conducted a hypothesis test for whether more people watch American Idol this week than last week.",
#			"In World War II, a prisoner of war flipped a coin 10,000 times and recorded 5,067 heads and another one flipped a coin 5000 times and recorded 2800. Conduct a hypothesis test for the coin 1 has more probability to get tail than coin 2."),
	"111" => "",
);

our %anwsers = (
	"000" => "One Population, Means in the C+E Model, Known Variance",
	"001" => "One Population, Means in the C+E Model, Unknown Variance",
	"010" => "One Population, The Proportion in the Binomial Model, Exact for n small",
	"011" => "One Population, The Proportion in the Binomial Model, Approximate for n Large",
	"100" => "Two Population, Means Difference in C+E Model, Equal Variances",
	"101" => "Two Population, Means Difference in C+E Model, NOT Equal Variances",
	"110" => "Two Population, The Proportion in the Binomial Model, Test of the Equality of Two Proportions",
	"111" => "Two Population, The Proportion in the Binomial Model, Test of the Difference of Two Proportions",
);


our %cianwsers = (
	"000*" => "One Population, Means, Known Variance",
	"001*" => "One Population, Means, Unknown Variance",
	"01**" => "One Population, The Proportion",
	"1000" => "Two Population, Independent, Means Difference, Equal Variances",
	"1010" => "Two Population, Independent, Means Difference, NOT Equal Variances",
	"10*1" => "Two Population, Dependent, Means Difference",
	"11**" => "Two Population, The Proportion",
);


# our %ans2s = (
	# "A" => "000",
	# "B" => "001",
	# "C" => "010",
	# "D" => "011",
	# "E" => "100",
	# "F" => "101",
	# "G" => "110",
	# "H" => "111",
# );




our %hint = (
	"1" => "Is there one population or two populations?",
#	"2" => "Which hypothesis test this problem requires?",
);

our %hintOptions = (
	"0" => "One population",
	"1" => "Two populations",
	#"010" => "Hypothesis test for Means",
	#"011" => "Hypothesis test for Proportion",
);
