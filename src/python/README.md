How to run the scripts
======================

In order to generate the plots and the error report you need to follow
the following steps:

0. Setup a directory structure for the analysis 
   (we should write code in setup.sh for doing that).
   
1. In the root directory of "src" do "source setup.sh" to set the
   pointers to the directories.
2. Use the file manager in WebWork to Download the log files. Go to
   the root directory and from there to "logs". The files you want are
   named "answer\_log*" put the files in $WWAH_LOGS and append ".txt"
   to their names.
3. From the same root directory of webwork, archive and download the
   directory "templates", which contains all of the .pg files. unpack
   the directory into $WWAH_DATA and name the directory
   "course\_webwork\_data"
4. Go to the directory $WWAH_SRC. Suppose the assignment that you are
   interested in is called "Assignment1". Run the following commands:

No parameters:
./ProcessLogs
./ParsingPGfiles.py
./BehaviourAnalysis.py

Get Parameters, use the flag -h to get a description of the
parameters.

./reportStruggles.py > reportFile.txt
./PlotTiming.py -a Assignment1

reportStruggles will list the problems/parts that were the most
difficult for the students. The directory 
$WWAH_OUTPUT/Assignment1 will contain plots and .org files detailing
what the struggling students did.


### Need to move to model where the Assignemnt number is always
    specified.
	
	
