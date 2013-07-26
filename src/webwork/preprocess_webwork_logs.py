#!/usr/bin/env python

import pickle
import datetime
from collections import defaultdict
import operator
import os, sys
import re
import numpy as np

class WebWork:
    def __init__(self, webwork_log_dir):
        self.load_webwork_answer_logs(webwork_log_dir)
        self.get_user_part_attempts()
        self.get_part_attempts()
        self.get_user_attempts()
        self.get_all_attempts()


    def __getstate__(self):
       return (self.student_answers, self.user_part_attempts, 
            self.part_attempts, self.user_attempts, self.all_attempts)
        

    def __setstate__(self, state):
       (self.student_answers, self.user_part_attempts, self.part_attempts, 
            self.user_attempts, self.all_attempts) = state



    def load_webwork_answer_logs(self,webwork_log_dir):
        '''Given a directory containing student answer log files 
           from WebWork, load the answers in a dictionary mapping
    
           (student, problem set, problem #) -> 
              [ (timestamp, [correct/incorrect ...], [expressions, ...]), 
                 ...]
    
           student_answers is a dictionary.  
           The values in this dictionary give particular submissions 
           for a problem, sorted by timestamp.  '''
            
        #    '''This parses the last part of the 5-part student answer line.  
        #Eg: '111    1347593286  1/13    1/4 1/52'.
        #        The first part should be a correcness bit vector 
        #      (may be missing)Given a student answer of the form 
        # There is some overlap in log files.  Load lines from all log files, 
        #   then unique on stripped lines
        log_lines = set([])
        for log_filename in os.listdir(webwork_log_dir):
            if not 'log' in log_filename:
                continue
            with open(os.path.join(webwork_log_dir,log_filename),'r') as log_file:
                for line in log_file.readlines():
                    line = re.sub('[\r\n\0]','',line)
                    if len(line.strip()) > 0: #Skip blank lines
                        log_lines.add(line)
        
        # After uniqueing on lines, preprocess answer submissions into a clean, 
        #   baseline data format.  Further reformatting can be done from here.  
        # An example of a log file line with an explanation of fields:
        # [Thu Sep 13 23:28:06 2012] |melkherj|Combinatorics|5|111    1347593286  1/13    1/4 1/52
        # [<webwork timestamp>] |<user>|<problem set|<problem #>|<correctness bitvector> <answer part 1> <answer part 2> <answer part 3>
        self.student_answers = defaultdict(lambda:[])
        for i,line in enumerate(log_lines):
            # Split line into 5 parts, spliting by |
            (timestamp_str, user, problem_set, problem_num, correctness_answer) = line.split('|',4)
            # Process each of the 5 parts into a canonical format
            timestamp = self.parse_webwork_timestamp(timestamp_str.strip())
            problem_num = int(problem_num)
            #For some reason, a very small number (~4 total) of answers
            # are not marked as correct/incorrect in the log files
            if correctness_answer[0] != '0' and correctness_answer[0] != '1':
                continue
            spl = correctness_answer.split('\t')
            #There are ~15 cases where answers are completely missing
            if len(spl) < 3: 
                continue
            (correctness_str, timestamp2_str, answer_str) = \
                correctness_answer.split('\t',2)
            correctness = [(c=='1') for c in correctness_str]
            # There is no answer after the last tab
            answer = answer_str.split('\t')[:-1]
            timestamp2 = int(timestamp2_str)
            # There are ~11 cases where the number of correctness bits
            # doesn't match up to the number of answers for that question
            if (len(correctness) != len(answer)):
                continue
            # The two timestamps shouldn't be off by more than two seconds
            assert(abs(timestamp - timestamp2) <= 2)
            self.student_answers[(user, problem_set, problem_num)].append( (timestamp, correctness, answer) )
        
        for key in self.student_answers.keys():
            #Sort each student answer for each problem by timestamp
            self.student_answers[key] = sorted(self.student_answers[key],
                key=operator.itemgetter(0))

        self.student_answers = dict(self.student_answers)


    def parse_webwork_timestamp(self,timestamp_str):
        '''Converts a WebWork timestampm string in the format [Thu Sep 13 23:28:06 2012] to a unix timestamp integer, PST'''
        try:
            #Remove '[' and ']' characters
            timestamp_str = timestamp_str.replace('[','')
            timestamp_str = timestamp_str.replace(']','')
            timestamp = datetime.datetime.\
                strptime(timestamp_str, '%a %b %d %H:%M:%S %Y')
            #3 hour time delta: subtrace to convert EST->PST
            delta = datetime.timedelta(seconds=3600*3)
            timestamp -= delta
            return int(timestamp.strftime('%s'))
        except:
            print timestamp_str
            raise
    
    
    def number_problem_parts(self, problem):
        '''Given a problem set and problem number, return the median number
               of parts of the problem over all student attempts 

            '''
        
        # A list of lists of attempts for the given problem
        problem_attempts = [ attempts
            for (user,problem_set,problem_num),attempts in self.student_answers.iteritems()
                if (problem_set, problem_num) == problem]
        # The number of parts for each attempt for this problem
        n_problem_parts = [len(attempt[2]) for attempts in problem_attempts
            for attempt in attempts]
        return np.median(n_problem_parts)
       
    
    def get_user_part_attempts(self):
        '''Given student answers of the form returned from the function
           'load_webwork_answer_logs' above, return students attempts in the
           form 
           
             (user,part) -> [(timestamp,correctness,expression), ...]
    
           where part = (problem set, problem number, problem part)
           In the process of converting to this form, attempts by students 
           with #parts that doesn't match the median number of parts for 
           attempts for a particular question, are ignored.  
           '''
        self.user_part_attempts = defaultdict(lambda:[])
        last_part_expr = defaultdict(lambda:'') #a mapping from user/problems
            # to the last expression analyzed.  This is used to keep from
            # duplicating expressions
            # Note that '' is the "haven't answered yet" expression
        # For each user/problem, get the list of attempts
        for ((user,problem_set,problem_num),attempts) \
                in self.student_answers.iteritems():
            problem = (problem_set,problem_num)
            n_problem_parts = self.number_problem_parts(problem)
            # For each attempt, get the list of parts
            for (timestamp,correctness,exprs) in attempts:
                if len(exprs) == n_problem_parts:
                    for part,(correct,expr) in enumerate(zip(correctness,exprs)):
                        problem_part = (problem[0],problem[1],part)
                        if expr != last_part_expr[user,problem_part]:
                            # A new answer was submitted by user
                            last_part_expr[user,problem_part] = expr
                            self.user_part_attempts[user,problem_part].append(
                                (timestamp,correct,expr))
        for user_part in self.user_part_attempts.keys():
           # For each user_part, sort the list of attempts by timestamp
            self.user_part_attempts[user_part] = \
                sorted(self.user_part_attempts[user_part],key=operator.itemgetter(0))
        self.user_part_attempts = dict(self.user_part_attempts) 
 
    def get_part_attempts(self):
        ''' Given part_attempts in the form returned from user_part_attempts, 
            return a list of attempts per problem part:  
            
            part -> [(timestamp, correctness, expression), ...]
    
            '''
        self.part_attempts = defaultdict(list)
        for (_,part),attempts in self.user_part_attempts.iteritems():
            for attempt in attempts:
                self.part_attempts[part].append(attempt)
        for part in self.part_attempts.keys():
            # For each part, sort the list of attempts by timestamp
            self.part_attempts[part] = \
                sorted(self.part_attempts[part],key=operator.itemgetter(0))
        
    
    def get_user_attempts(self):
        ''' Given part_attempts in the form returned from user_part_attempts, return
            a list of attempts per user:
#            
            user -> [(timestamp, correctness, expression), ...]
    
            '''
        self.user_attempts = defaultdict(list)
        for (user,_),attempts in self.user_part_attempts.iteritems():
            for attempt in attempts:
                self.user_attempts[user].append(attempt)
        for user in self.user_attempts.keys():
            # For each part, sort the list of attempts by timestamp
            self.user_attempts[user] = \
                sorted(self.user_attempts[user],key=operator.itemgetter(0))
    
    def get_all_attempts(self):
        ''' Given user_part_attempts in the form returned from user_part_attempts, 
            return a list of every attempt:
            [(timestamp, correctness, expression), ...]
    
            '''
        self.all_attempts = [attempt 
            for per_user_attempts in self.user_part_attempts.values() 
                for attempt in per_user_attempts]
        self.all_attempts = sorted(self.all_attempts,key=operator.itemgetter(0))
   
 
    def get_correctness_sequence(self, attempts):
        '''Given a list of attempts, extract the correctness bit sequence.
           This is the list of true/false, whether the user got the 
           question parts correct'''
        return [ c for _,c,_ in attempts]

    
if __name__ == '__main__':
    webwork = pickle.load(open(os.path.join(sys.argv[1],'pickled_data'),'rb'))
#    webwork = WebWork(sys.argv[1])
    incorrect_attempt_times = [time 
        for time,correct,_ in webwork.all_attempts if not correct]
    time_parts = dict( (time,part) 
        for part,attempts in webwork.part_attempts.iteritems()
            for time,_,_ in attempts)
    clustered_attempt_times = {}
    last_time = -1
    cluster_size = 1
    for time in incorrect_attempt_times:
        #Another incorrect attempt was made within the same minute
        if time <= last_time + 60: 
            cluster_size += 1
        else:
            clustered_attempt_times[time] = cluster_size
            cluster_size = 1
        last_time = time
    bad_attempt_times = [time for time,n_attempts in clustered_attempt_times.iteritems() if n_attempts > 7]
    part_hardness = defaultdict(int)
    for time in bad_attempt_times:
        part_hardness[time_parts[time]] += 1
#    hard_parts = dict( ((time%10000000/10000), time_parts[time]) for time in bad_attempt_times )
#    hard_parts = sorted(hard_parts.iteritems())
