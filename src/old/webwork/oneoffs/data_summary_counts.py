import yaml
import pickle
import os 
from webwork.preprocess_webwork_logs import WebWork

# Load the yaml config file
with open('../../config.yaml','r') as f:
    config = yaml.load(f)
pickled_log_filename = os.path.join(config['Data path'],
    config["pickled WebWork log relative path"])
webwork = pickle.load(open(pickled_log_filename,'rb'))

# Calculate and print WebWork data statistics.  
# Eg number of assignments, users, ...
n_assignments = len(set([assignment for (assignment,_,_) in webwork.part_attempts.keys()]))
n_problems = len(set([(assignment,problem) for (assignment,problem,_) in webwork.part_attempts.keys()]))
n_parts = len(webwork.part_attempts.keys())
n_attempts = len(webwork.all_attempts)
n_users = len(webwork.user_attempts)

print 'Students: %d'%len(webwork.user_attempts)
print 'Assignments: %d'%n_assignments
print 'Average problems/assignment: %d, Total problems: %d' % \
    (n_problems/n_assignments, n_problems)
print 'Average parts/problem: %d, Total parts: %d' % \
    (n_parts/n_problems, n_parts)
print 'Average attempts per user per part: %d, Total attempts: %d' % \
    (n_attempts/(n_parts*n_users), n_attempts)

