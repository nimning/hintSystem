from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as pp
import operator
import os

answer_log = '../answer_log_assignment8.txt'
assignment_filter = 'Assignment8'
minute_threshold = 10 #how long a student can sit idle before it is counted
save_figure = True
print_top_n_students = 0 #ranked by how much time they spent
# as a new session
export_directory = 'HistogramsTimeSpent/%s'%assignment_filter
os.mkdir(export_directory)

def plot_time_spent_histogram(student_minutes, title):
    '''Given a list of the time spent by each student in minutes, 
        save a histogram to a file with the given title'''
    fig = pp.figure(1)
    fig.clf()
    try:
        pp.hist(student_minutes,bins=40)
    except:
        import pdb
        pdb.set_trace()
    pp.xlabel('minutes')
    pp.ylabel('students')
    pp.title('Time spent per student on %s'%title)
    fig.savefig(export_directory+'/time_spent_histogram_%s.png'%title,dpi=600)

def line_to_timestamp(line):
    '''Converts a line of the WebWork answer_log to a unix timestamp'''
    formatted_timestamp = line.split(']')[0][1:]
    try:
        return int(datetime.strptime(formatted_timestamp,
            '%a %b %d %H:%M:%S %Y').strftime('%s'))
    except:
        raise Exception("Couldn't extract timestamp from line:\n%s"%line)
    
def line_to_user(line):
    return line.split('|')[1]

def line_to_assignment(line):
    return line.split('|')[2]

def line_to_question(line):
    return int(line.split('|')[3])

#Parse answer_log file into a reasonable format
last_user_login = defaultdict(lambda:-10000)
user_time_spent = defaultdict(lambda:0)
user_question_time_spent = defaultdict(lambda:0)
lines = open(answer_log,'r').readlines()
lines = [line for line in lines if len(line.strip()) >= 1]
for i,line in enumerate(lines):
    timestamp = line_to_timestamp(line)
    user = line_to_user(line)
    assignment = line_to_assignment(line)
    question = line_to_question(line)
    if assignment == assignment_filter:
        #user was active during the past 3 minutes
        time_diff = timestamp - last_user_login[user]
        if time_diff < 60*minute_threshold:
            user_time_spent[user] += time_diff
            user_question_time_spent[(user,question)] += time_diff
    last_user_login[user] = timestamp


#plot and save histogram of student time spent
#time spent per student on the entire assignment (in minutes) 
assignment_student_minutes = [t/float(60) for t in user_time_spent.values()]
if save_figure:
    plot_time_spent_histogram(assignment_student_minutes, assignment_filter)
questions = set(k[1] for k in user_question_time_spent.keys())
questions = sorted(list(questions))
#time spent per student on each question of the assignment (in minutes) 
for question in questions:
    time_spent = defaultdict(lambda:0)
    for (student, q) in user_question_time_spent.keys():
        if q == question:
            time_spent[student] += user_question_time_spent[(student, question)]
    question_student_minutes = [t/float(60) for t in time_spent.values()]
    if save_figure:
        plot_time_spent_histogram(question_student_minutes, assignment_filter+'_question%d'%question)

sorted_student_times = sorted(((u,t) for (u,t) in user_time_spent.iteritems()), key=operator.itemgetter(1))
if print_top_n_students > 0:
    top_n_students  = sorted_student_times[-print_top_n_students:]
else:
    top_n_students  = []
for (user,time) in top_n_students:
    hours = time/3600
    minutes = (time-hours*3600)/60
    seconds = time-hours*3600-minutes*60
    print '%s spent %d:%d:%d'%(user, hours, minutes, seconds)
