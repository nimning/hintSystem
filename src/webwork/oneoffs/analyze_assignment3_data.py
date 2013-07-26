from operator import itemgetter
from webwork.preprocess_webwork_logs import WebWork
import pickle, os, sys
from collections import defaultdict
import matplotlib.pyplot as pl
import numpy as np
from webwork.cluster_exprs import parse_expr_to_set
from webwork.oneoffs.filter_sub_expressions import min_overlap
import random
import simplejson as json
import yaml

def simplify_attempt_dict(attempt_dict):
    ''' Given an attempt dict, strip off fields not needed for a demo, 
        and add fields for showing/hiding problem parts '''
    # Delete unnecessary keys
    for key in ['user','time','overeager']:
        attempt_dict.pop(key,None)
    attempt_dict['hide'] = []
    attempt_dict['show'] = []
    return attempt_dict

def get_subexprs(session):
    ''' Return a list of indices (i,j) such that the expression corresponding to 
      the i'th attempt of the session is contained in the j'th expression: ie the 
      features from preprocessing exprs[i] are a subset of the features from 
      exprs[j] '''
    exprs = [attempt_dict['expr'] for attempt_dict in session]
    n = len(exprs)
    # Preprocess all expressions to sets of features
    parsed_exprs = map(parse_expr_to_set, exprs)
    return  [
      (i,j) for i,p in enumerate(parsed_exprs) for j,q in enumerate(parsed_exprs)
        
        if    len(p & q) == len(p) #All features in p are in q
          and len(p) > 8 # p is sufficiently complex: '4' isn't interesting
          and len(q) > len(p) # q is more complex than p 
          and session[i]['part'] < session[j]['part'] 
          and session[j]['part'] - session[i]['part'] <= 8 # we assume dependencies
            # won't involve expressions separated by a large number of parts
    ]

def pretty_print_attempt(attempt_dict,print_user=False,out_stream=None):
    ''' Pretty a simple attempt, with time taken, correctness, the part, and the expression entered 
        Optionally print the user, or specify an alternative output stream to stdout'''
    user = attempt_dict['user'] if print_user else ''
    correct = 'T' if attempt_dict['correct'] else ' '
    output_str = '%10s %5d %1d %s       %30s\n' % \
        (user,attempt_dict['timedelta'],attempt_dict['part'],correct,attempt_dict['expr'])
    if out_stream is None:
        return output_str
    else:
        out_stream.write(output_str)

def filter_group_user_attempts(webwork, part_filter=lambda _: True):
    ''' Given a webwork object, produce a dictionary of attempts sorted by time and grouped by user 
        Since the attempts are sorted by time, we can add to each attempt additional attributes: timedelta
        and overeager
        <timedelta>: For a single user, the difference between an attempt and the previous attempt by that user.  
            We define timedelta for the first attempt by a user as 0
        <overeager>: For a single user, whether that user failed to answer a later part, after failing to answer
            an earlier part.  See implementation for details '''
    # Assignment 3 part attempts
    assignment3_attempts = []
    for (user,(assignment,problem,part)),attempts in webwork.user_part_attempts.iteritems():
        for time,correct,expr in attempts:
            if part_filter(assignment,problem,part):
                # A dictionary storing attempt info
                attempt_dict = dict( [(name,eval(name)) for name in ['user','time','part','correct','expr']] )
                assignment3_attempts.append(attempt_dict)
    # Group attempts by user
    assignment3_user_attempts = defaultdict(list)
    for attempt_dict in assignment3_attempts:
        assignment3_user_attempts[attempt_dict['user']].append(attempt_dict)
    # Sort attempts for each user by timestamp
    for user in assignment3_user_attempts.keys():
        assignment3_user_attempts[user] = sorted(assignment3_user_attempts[user],key=lambda d:d['time'])
    # Produce time diffs instead of timestamps: this allows us to find parts where students struggled
    # Also mark whether this part was answered out of order
    for user in assignment3_user_attempts.keys():
        attempts = assignment3_user_attempts[user]
        attempts[0]['timedelta'] = 0
        attempts[0]['overeager'] = (not attempts[0]['correct']) \
             and attempts[0]['part'] > 0
        for i,attempt_dict in enumerate(attempts[1:]):
            attempt_dict['timedelta'] = attempt_dict['time'] - attempts[i]['time']
            # An attempt is overeager if it is incorrect, and an attempt
            # at a previous part was also incorrect
            attempt_dict['overeager'] = (not attempt_dict['correct']) and \
                (attempt_dict['part'] > attempts[i]['part']) and \
                (not attempts[i]['correct'])
    return assignment3_user_attempts

def split_list(l, begin_list=lambda _:False, end_list=lambda _:False):
    ''' Split list 'l' into sublists.  A new sublist is started with 'item' 
            when begin_next(item)==True, or a previous list is ended with 'item'
            if end_list(item) == True
        Return a list of lists, such that the flattenned list of lists forms
            'l' 
        begin_list takes priority over end_list: if both return True for an 
            item, a new list is started '''
    sublists = []
    sublist = []
    for item in l:
        if begin_list(item):
            sublists.append(sublist)
            sublist = [item]
        elif end_list(item):
            sublists.append(sublist+[item])
            sublist = []
        else:
            sublist.append(item)
    # Add last sublist if necessary
    if len(sublist) > 0:
        sublists.append(sublist)
    return sublists

if __name__ == '__main__':
    # Load the yaml config file
    with open('../../config.yaml','r') as f:
        config = yaml.load(f)
    pickled_log_filename = os.path.join(config['Data path'],
        config["pickled WebWork log relative path"])

    webwork = pickle.load(open(pickled_log_filename,'rb'))
    user_attempt_dicts = filter_group_user_attempts(webwork, part_filter=
        (lambda assignment,problem,part: assignment == 'Assignment2' and
            problem == 1) )
    sessions = [session for attempt_dicts in user_attempt_dicts.values()
        for session in split_list(attempt_dicts, 
            lambda attempt_dict: attempt_dict['timedelta'] > 20*60) ]
    # For each session, and each part answered in that session, compute time 
    # taken 
    time_spent = defaultdict(int)
    for i,session in enumerate(sessions):
        for attempt_dict in session[1:]:
            time_spent[(i,attempt_dict['part'])] += attempt_dict['timedelta']
    sorted_time_spent = sorted(time_spent.iteritems(),
        key=lambda ((i,j),count): -count)
    # Plot the cumulative time spent over part/sessions.  This can be used
    # To indicate how many hints students need to be given to significantly
    # decrease overall time spent
#    cumulative_time_spent = np.cumsum(map(itemgetter(1),sorted_time_spent))
#    pl.plot(cumulative_time_spent / float(cumulative_time_spent[-1]))
#    pl.xlabel("(part,session) index")
#    pl.ylabel("Proportion of total student time spent")
    
    # We observe that log(item#) ~proportional to~ time spent, where each item#
    # referse to a (session, part) pair
    # Thus the following plot is approximately linear:
    # pl.plot(np.log(range(len(times))),times)

    # Pretty print attempts at the same part in a session where a student
    # spent a lot of time
#    for ((session_num,part),_) in sorted_time_spent:
#        print '#'*80
#        print 'session %d, part %d'%(session_num,part)
#        for attempt_dict in sessions[session_num][1:]:
#            if attempt_dict['part'] == part:
#                pretty_print_attempt(attempt_dict, out_stream=sys.stdout)
#        print ''

    # Export sessions where students wasted a large amount of time on one
    # part
#    expensive_sessions = [sessions[session_num][1:] for 
#        ((session_num,part),_) in sorted_time_spent[:20] ]
#    # Remove/add some keys to the attempt_dict's of each session
#    expensive_sessions = [map(simplify_attempt_dict, session) for session in
#        expensive_sessions]
#    # By default, show all parts in a session in the first attempt_dict
#    for session in expensive_sessions:
#        session_parts = [attempt_dict['part'] for attempt_dict in session]
##        min_part = min(session_parts)
#        min_part = 0
#        max_part = max(session_parts)
#        session[0]['show'] = range(min_part, max_part+1)
#    print json.dumps(expensive_sessions)





# Pretty print all sessions
#for i,session in enumerate(sessions):
#    print '#'*28+'  %4d %15s  '%(i,session[0]['user'])+'#'*28
#    for attempt_dict in session:
#        pretty_print_attempt(attempt_dict, out_stream=sys.stdout)
#    print '\n'

# Export plots of attempt times for each session
for i,session in enumerate(sessions):
    user = session[0]['user']
    
    correct_times_np = np.array([attempt_dict['time'] 
        for attempt_dict in session if attempt_dict['correct']]) \
            - session[0]['time']
    correct_parts_np = np.array([attempt_dict['part'] 
        for attempt_dict in session if attempt_dict['correct']])
    incorrect_times_np = np.array([attempt_dict['time'] 
        for attempt_dict in session if not attempt_dict['correct']]) \
            - session[0]['time']
    incorrect_parts_np = np.array([attempt_dict['part'] 
        for attempt_dict in session if not attempt_dict['correct']])
    
    pl.ylim((0,50))
    minutes = 120 #Two hours
    pl.xlim((0,minutes*60)) 
    # Put a minute-marking every minutes_delta minutes
    minutes_delta = 10
    pl.xticks(range(0,minutes*60,minutes_delta*60),
        range(0,minutes,minutes_delta))
    pl.xlabel('minutes')
    pl.ylabel('part number')
    if correct_times_np.shape[0] > 0:
        pl.scatter(correct_times_np, correct_parts_np, 
            color='green',label='correct')
    if incorrect_times_np.shape[0] > 0:
        pl.scatter(incorrect_times_np, incorrect_parts_np, 
            color='red', label='incorrect')
    pl.legend()
#    pl.title('Attempt times for a session with user '+user)
#    pl.savefig('session_attempt_times/%s_%d.png'%(user,i))
    # Anonymize
    pl.title('Attempt times for a session %d'%i)
    pl.savefig('session_attempt_times/%d.png'%i)
    pl.clf()


#timedeltas_np = np.array([attempt_dict['timedelta'] for attempt_dict in user_attempts.values()[0]]); pl.hist(timedeltas_np,bins=40)

# Pretty print all attempts, grouped by session
#for (user,attempts) in assignment3_user_attempts.iteritems():
#    print '                  %s                   \n'%user
#    for attempt_dict in attempts:
#        pretty_print_attempt(attempt_dict,sys.stdout)
#    print '\n'

##Get a list of all attempts.  Each attempt is a dictionary with keys:
## user, time, part, correct, expr, timedelta, overeager
#attempt_dicts = [attempt_dict for attempts in assignment3_user_attempts.values() for attempt_dict in attempts]
#
#################################################################################
## Print statistics about the time taken per part
#################################################################################
## Get a numpy array of all times taken per part
#timedeltas_np = np.array([attempt_dict['timedelta'] for attempt_dict in attempt_dicts])
## Print statistics about the distribution of time taken per attempt
#print \
#    '### Statistics about the time taken per attempt ###'
#print ''
#print '       total: numer of attempts = %6d, time taken = %8d' % \
#    (timedeltas_np.shape[0], timedeltas_np.sum())
# <3min
#filtered_timedeltas = timedeltas_np < 60*3
#print '       <3min: numer of attempts = %6d, time taken = %8d' % \
#    (filtered_timedeltas.sum(), timedeltas_np[filtered_timedeltas].sum())
## >3min <20min
#filtered_timedeltas = ((timedeltas_np > 60*3) & (timedeltas_np < 60*20))
#print '>3min,<20min: numer of attempts = %6d, time taken = %8d' % \
#    (filtered_timedeltas.sum(), timedeltas_np[filtered_timedeltas].sum())
## >20min
#filtered_timedeltas = timedeltas_np > 60*20
#print '      >20min: numer of attempts = %6d, time taken = %8d' % \
#    (filtered_timedeltas.sum(), timedeltas_np[filtered_timedeltas].sum())

################################################################################
# Pretty print overeager students attempts to a file 
################################################################################
#pl.hist(timedeltas_np[timedeltas_np < 60*20],bins=40)
#difficult_attempt_dicts = [attempt_dict for attempt_dict in attempt_dicts if attempt_dict['overeager'] and attempt_dict['timedelta'] > 60*3 and attempt_dict['timedelta'] < 60*20 and len(attempt_dict['expr'].strip()) > 0]
#with open('overeager_attempts.txt','w') as f:
#    for attempt_dict in difficult_attempt_dicts:
#        pretty_print_attempt(attempt_dict,print_user=True,out_stream=f)
 
