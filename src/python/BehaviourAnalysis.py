#!/usr/bin/env python

import pandas, sys, os
import numpy as np
import pickle
from copy import deepcopy

class BehaviourAnalysis:
    def __init__(self,filename):
        print 'starting to load',filename
        Dict=pickle.load(open(filename,'rb'))
        self.__dict__=Dict
        print 'finished loading, loaded',self.__dict__.keys()

    def measure_effort(self,key):
        Ga=self.GroupedDataFrame[key]
        Dtimes={}
        Danswers={}
        Dcorrect={}
        Dproblem_no={}
        Dpart_no={}

        last_answer_correct=False
        group_by_counter=dict(list(Ga.groupby('counter')))

        part_keys=group_by_counter.keys()
        part_keys=sorted(part_keys)
        for k in part_keys:
            group = group_by_counter[k]
            #take the first entry of the parameters that don't change inside a group.
            Assignment,problem_no,part_no=group[['Assignment','problem_no','part_no']].values[0,:]
            problem_no=int(problem_no); part_no=int(part_no)
            #print '%d,%s\t%d\t%d' % (k,Assignment,problem_no,part_no)
            table=group[['time','answer','correct']].values
            prev_answer=''
            answers=[]
            times=[]
            corrects=[]
            prev_time=0
            for i in range(len(table)):
                time,answer,correct=table[i]
                correct=int(correct)
                # ignore entries where the answer did not change.
                if answer!=prev_answer:
                    prev_answer=answer
                    if i==0:
                        times.append(time)
                    else:
                        times.append(time-prev_time)
                    prev_time=time

                    answers.append(answer)
                    corrects.append(correct)
                    if correct==1: 
                        break
            l=len(times)
            if l>0:
                times = np.array(times)
                times /=60.0
            Dtimes[k]=times
            Danswers[k]=answers
            Dcorrect[k]=corrects
            Dproblem_no[k]=[problem_no]*l
            Dpart_no[k]=[part_no]*l
        return Dtimes,Danswers,Dcorrect,Dproblem_no,Dpart_no

    def analyze_all(self):
        frame={'user':[],'assignment':[],'start_time':[],\
               'final_correct':[],'tries':[],'problem_no':[],'part_no':[],'time':[]}
        self.Effort_Table=pandas.DataFrame(frame)
        count=0
        total=len(self.GroupedDataFrame)
        for key in sorted(self.GroupedDataFrame.keys()):
            print '\r',key,'%d/%d = %4.1f percent                ' % (count,total,100.0*(count+0.0)/total),
            sys.stdout.flush()
            count +=1
            Dtimes,Danswers,Dcorrect,Dproblem_no,Dpart_no = self.measure_effort(key)
            l=len(Dtimes)
            block=deepcopy(frame)
            for k in sorted(Dtimes.keys()):
                if len(Dtimes[k])>0:
                    block['user'].append(key[0])
                    block['assignment'].append(key[1])
                    block['start_time'].append(Dtimes[k][0])
                    block['final_correct'].append(Dcorrect[k][-1])
                    block['tries'].append(len(Dtimes[k]))
                    block['problem_no'].append(Dproblem_no[k][0])
                    block['part_no'].append(Dpart_no[k][0])
                    if len(Dtimes[k])>1:
                        block['time'].append(sum(Dtimes[k][1:]))
                    else:
                        block['time'].append(0.0)
            self.Effort_Table=self.Effort_Table.append(pandas.DataFrame(block))
            #print 'Effort_Table length=',len(self.Effort_Table),'table length=',len(block['time'])
        print '\n finished'

    def pickle(self,filename):
        """
        Create a pickle file with the desired table
        """
        print 'starting pickle'
        pickle.dump({'BehaviourStatistics':self.Effort_Table},\
                    open(filename,'wb'),\
                    protocol=pickle.HIGHEST_PROTOCOL)
        print 'finished pickle'
        
if __name__=='__main__':
    pickle_dir=os.environ['WWAH_PICKLE']
    B=BehaviourAnalysis(pickle_dir+'/ProcessedLogs.pkl')

    print "-------------- Processing all ---------------------"

    B.analyze_all()
    import os
    pickle_dir=os.environ['WWAH_PICKLE']
    B.pickle(pickle_dir+'/BehavioralStatistics.pkl')

    # OLD CODE

    # key= ('djdawson', 'Assignment3')
    # Dtimes,Danswers,Dcorrect,Dproblem_no,Dpart_no = B.measure_effort(key)
    # correctness=[' - ','VVV']
    # print key
    # for k in sorted(Dtimes.keys()):
    #     T=Dtimes[k]
    #     A=Danswers[k]
    #     C=Dcorrect[k]

    #     if(len(T)<3): continue  # ignore parts where the student made at most 2 tries.

    #     print '------------------------------------------- part no. ',k

    #     for i in range(len(T)):
    #         print '%3d: %s  time=%4.1f, answer=%s' % (i,correctness[C[i]],T[i],A[i])
    
    #     print 'Total time spent=%4.1f minutes' % sum(T[1:])
