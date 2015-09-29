#Files#

* create_hint_databases.sh: Take in class name. Will create hint database tables for new class set. Needs to be run when creating a new homework set.
* save_answers.py: Run with 'python save_answers.py -c <course_name> -s <set_id>'. Create/Update two database tables, 'correct_answers' and 'user_variables'. Needs to be run when a new set is created or new problems are added to problem set.
* past_answer_to_answers_by_part.py: Create table 'answers_by_part' for CSE103_Fall2015. Needs to be running constantly to basically split up the answers per question into answers per part. This is controlled by an upstart init file at /etc/init/past-answer-daemon.conf on server.



#Database Overview #
There are 10 tables associated with each course (eg with tables named UCSD_CSE103_...):
* past_answer: Expressions entered by students, with timestamps.  
* set: Problem sets
* set_user: Problem sets assigned to users 
* permission: Access levels associated with users.  
* setting: Configuration parameters for the course
* problem_user: Problem data associated with a user.    
* key: Not sure 
* problem: Problems (with paths to source)
* password: Hashed passwords of every user account
* user: Users/instuctors assigned to the course 


## past_answer ##
* Description: Stores attempts by users to answer questions.  The expressions entered in text boxes are stored in answer_string, and the correctness is stored in scores.   
### user_id ###
* Example: wentao
### timestamp ###
* Example: 1371175363
* Description: Unix timestamp to 1 second accuracy
### comment_string ###
### source_file ###
* Example: setTestPreparation/events8_hint.pg
### answer_string ###
* Example: 123\t
### scores ###
* Example: 0
* Description: A bit-vector indicating which submitted answers were correct.  The bits in this vector correspond to the tab-separated expressions in answer_string.  
### course_id ###
* Example: UCSD_CSE103
### problem_id ###
* Example: 2
### set_id ###
* Example: TestPreparationCB
### answer_id ###
* Example: 1


## set ##
### time_limit_cap ###
* Example: 0
### hide_work ###
* Example: N
### set_header ###
* Example: defaultHeader
### version_time_limit ###
### attempts_per_version ###
### assignment_type ###
### version_last_attempt_time ###
### visible ###
* Example: 1
### problems_per_page ###
### versions_per_interval ###
### answer_date ###
* Example: 1387062000
### open_date ###
* Example: 1349114520
### hardcopy_header ###
* Example: defaultHeader
### enable_reduced_scoring ###
* Example: 0
### restrict_ip ###
* Example: No
### time_interval ###
### due_date ###
* Example: 1387062000
### description ###
### version_creation_time ###
### restricted_login_proctor ###
### hide_score ###
* Example: N
### problem_randorder ###
### relax_restrict_ip ###
* Example: No
### hide_score_by_problem ###
### hide_hint ###
### set_id ###
* Example: TestPreparationCB


## set_user ##
* Description: as you might expect, set x user
### time_limit_cap ###
### hide_work ###
### set_header ###
### version_time_limit ###
### attempts_per_version ###
### assignment_type ###
### version_last_attempt_time ###
### visible ###
### problems_per_page ###
### versions_per_interval ###
### user_id ###
* Example: melkherj
### answer_date ###
### psvn ###
* Example: 4
### open_date ###
### hardcopy_header ###
### enable_reduced_scoring ###
### restrict_ip ###
### time_interval ###
### due_date ###
### description ###
### version_creation_time ###
### restricted_login_proctor ###
### hide_score ###
### problem_randorder ###
### relax_restrict_ip ###
### hide_score_by_problem ###
### hide_hint ###
### set_id ###
* Example: TestPreparationCB


## permission ##
### user_id ###
* Example: melkherj
### permission ###
* Example: 10
* Description: 10 is probably admin privilege, there was a permission level 20 associated with scheaman for some reason.  


## setting ##
Configuration variables for the course
### name ###
* Example: db_version
### value ###
* Example: 3.1415926


## problem_user ##
* Description: Statistics about user attempts at problems.  This table references both the problem and user tables.  
### status ###
* Example: 0
### sub_status ###
* Example: 0
### user_id ###
* Example: melkherj
### num_correct ###
* Example: 0
### attempted ###
* Example: 0
### value ###
### num_incorrect ###
* Example: 0
### source_file ###
### flags ###
### last_answer ###
### problem_seed ###
* Description: Each problem x user could have a random seed for adding randomness to the problem generated.   
* Example: 2107
### problem_id ###
* Example: 1
### set_id ###
* Example: TestPreparationCB
### max_attempts ###


## key ##
### timestamp ###
* Example: 1375711520
### key_not_a_keyword ###
* Example: UvY7vnI6HAxeVeWDOE55zu1j1rE4G4zD
### user_id ###
* Example: gage


## problem ##
### value ###
* Example: 1
### source_file ###
* Example: setTestPreparation/events5_hint.pg
### flags ###
### problem_id ###
* Example: 1
### set_id ###
* Example: TestPreparationCB
### max_attempts ###
* Example: 1


## password ##
### password ###
* Example: 9JaI2GDutCHx2
### user_id ###
* Example: melkherj


## user ##
### status ###
* Example: C
### comment ###
### first_name ###
* Example: Matthew
### last_name ###
* Example: Elkherj
### user_id ###
* Example: melkherj
### student_id ###
* Example: melkherj
### section ###
### recitation ###
### email_address ###
* Example: melkherj@ucsd.edu


