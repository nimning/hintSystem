from webwork.preprocess_webwork_logs import WebWork
import pickle,os,sys
from collections import defaultdict
from operator import itemgetter

webwork = pickle.load(open(os.path.join(sys.argv[1],'pickled_data'),'rb'))
user_correct = defaultdict(int)
user_total = defaultdict(int)
for (user,(assignment,_,_,)),attempts in webwork.user_part_attempts.iteritems():
    if assignment == 'Assignment1' or assignment=='Assignment2':   
        for _,correct,_ in attempts:
            user_correct[user] += correct
            user_total[user] += 1
user_accuracy = defaultdict(float)
for user in user_total.keys():
    user_accuracy[user] = float(user_correct[user])/user_total[user]
for user,accuracy in sorted(user_accuracy.iteritems(),key=itemgetter(1)):
    print '%s %0.3f'%(user,accuracy)
