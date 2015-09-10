#!/usr/bin/env python

import pandas, glob, sys, os, traceback
import numpy as np
from string import strip
import pickle
import matplotlib.pyplot as pl
from matplotlib.backends.backend_pdf import PdfPages

class ProcessLogs:

    #DataFrame=pandas.DataFrame()     # raw data
    #DedupFrame=pandas.DataFrame()    # deduped and sorted data
    #ExpandedFrame=pandas.DataFrame() # problems broken into parts
    #G=pandas.DataFrame()             # ExpandedFrame groups according to user and assignment.

    """Transform a directory of webwork log file into a pandas DataFrame
    and store it as a pkl file Expects one parameters: the path to the
    directory with the log files (they need to have the extension
    '.txt')
    """
    def __init__(self,path,is_dir=True):
        """read all of the log files in a given directory, parse their
        content, and concatanate them into a single DataFrame.  path: a
        path to the directory where all the log files reside. The
        current assumption is that the log files are all those whose
        extension is '.txt'
        is_dir=True means the given path <path> is to a directory
        else the path refers to a single file
        """
        self.time_gap_threshold=1200  # 20 minutes in seconds
        self.DataFrame=pandas.DataFrame()     # raw data

        Table={'string_time':[],'user':[],'Assignment':[],'problem_no':[],'correctness':[],'time':[],'answers':[]}
        if is_dir:
            filenames=glob.glob(path+'/*.txt')
        else:
            filenames = [path]
        if len(filenames)==0:
            sys.exit('Found no files matching '+path+'/*.txt')
        errors=open('ProcessingErrors.txt','wb')
        for filename in filenames:
            lines=0
            bad_lines=0
            file=open(filename,'r')
            for line in file.readlines():
                lines +=1
                try:
                    line_parts= line.split('|',4)
                    answer_parts =line_parts[4].split('\t')
                    line_parts=[strip(p) for p in line_parts]
                    if len(line_parts)<5 or len(answer_parts)<3:
                        raise Exception('missing elements in line')
                    answer_parts=[strip(p) for p in answer_parts]
                    # convert the elements that need to formatted
                    line_parts[3]=int(line_parts[3])     # problem_no
                    correctness=answer_parts[0]
                    answer_parts[1]=int(answer_parts[1]) # time
                    answers=tuple([strip(a) for a in answer_parts[2:]])
                    # everything looks ok, append new value to each column of the table
                    Table['string_time'].append(line_parts[0])
                    Table['user'].append(line_parts[1])
                    Table['Assignment'].append(line_parts[2])
                    Table['problem_no'].append(line_parts[3])
                    Table['correctness'].append(correctness)
                    Table['time'].append(answer_parts[1])
                    Table['answers'].append(answers)
                except Exception as e:
                    bad_lines +=1
                    errors.write('%s line no:%d: ' % (filename,lines))
                    errors.write(line)
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback.print_exception(exc_type, exc_value, exc_traceback,
                                              limit=2, file=errors)

            tmp=pandas.DataFrame(Table)
            self.DataFrame=self.DataFrame.append(tmp)
            print 'file: %s: read %d lines, out of which %d were bad' % (filename,lines,bad_lines)

    def dedup(self):
        """
        Sort, remove duplicates
        """
        self.DataFrame=self.DataFrame.sort(['time'])
        self.DedupFrame=self.DataFrame.drop_duplicates(cols=['string_time','user'])
        self.DedupFrame['time'] -= self.DedupFrame.ix[0,'time']
        # plot(DedupFrame.ix[start:,'time']) # useful in a notebook

    def expand_into_parts(self):
        """
        Each problem is made out of several parts. we partition the rows in 
        """
        count=0
        # define the keys of the expanded dataframe with a row for each problem part
        # replicated = copied as is
        # new = added in ExpandedFrame
        replicated=['Assignment','problem_no','string_time','time','user']
        new=['correct','answer','part_no']
        all_vars=replicated+new
        CE={} # a dictionary of columns from which ExpandedFrame will be constructed.
        for v in all_vars: CE[v]=[]

        for (Index,row) in self.DedupFrame.iterrows():
            template=dict(row[replicated])
            answers=row['answers']
            correctness=row['correctness']
            no_of_parts=min(len(answers),len(correctness))
            # create, in E, a row for each of the question parts.
            E={'correct':[0]*no_of_parts,\
               'answer':[0]*no_of_parts,\
               'part_no':range(1,no_of_parts+1)\
            }
            for k in template.keys():
                E[k]=[template[k]]*no_of_parts
            for i in range(no_of_parts):
                E['correct'][i]=correctness[i]
                E['answer'][i]=answers[i]
            for v in all_vars:
                CE[v]+=E[v]
                count+=1
                if count % 10000==0: print count,len(CE['user']),'\r',
        self.ExpandedFrame=pandas.DataFrame(CE)

    def map_to_counter(self):
        """find a mapping between problem_no and part_no to a globally
        consistent index called "counter" Add a "counter" column to
        the table.

        """
        self.G=dict(list(self.ExpandedFrame.groupby(['user','Assignment'])))

        print "finding the problems and parts in each assignment"
        ALL=pandas.DataFrame()
        for g in self.G.keys():
            block=self.G[g]
            Q=block[['Assignment','problem_no','part_no']]
            ALL=ALL.append(Q)
            ALL=ALL.drop_duplicates()
            ALL=ALL.sort(['Assignment','problem_no','part_no'])
            Indexes=ALL.groupby(ALL['Assignment'])

        print "creating a dictionary that maps from ['Assignment','problem_no','part_no'] to counter"
        D=dict(list(Indexes))
        self.C_dict={}   # A mapping from assignment,problem_no,part_no to counter
        for k in D.keys():
            l=len(D[k])
            D[k]['counter']=range(1,l+1)
            List=D[k][['Assignment','problem_no','part_no','counter']].values
            for (Assignment,problem_no,part_no,counter) in List:
                key='%s,%d,%d' % (Assignment,problem_no,part_no)
                self.C_dict[key]=counter

        print "Define a new column called 'counter' \n"
        def map2counter(r):
            key='%s,%d,%d' % tuple(r[['Assignment','problem_no','part_no']].values)
            return self.C_dict[key]
        for g in self.G.keys():
            print '\r                                        \r adding column "counter" to ',g,
            sys.stdout.flush()
            self.G[g]['counter']=self.G[g].apply(map2counter,1)

    def find_breaks(self):
        """
        We define some time threshold (currently 20 minutes) as indicating the the student took a break from working on the HW.
        We reduce gaps larger than the threshold to the threshold and create an additional column to store the size of the gaps
        """
        for key in self.G.keys():
            t=self.G[key]['time'].values
            t-= t[0]
            gaps=t[1:]-t[:-1]
            locs=np.array([(gaps[i] if gaps[i]>self.time_gap_threshold else 0) for i in range(len(gaps))])
            steps=np.cumsum(locs)
            self.G[key]['time']=np.insert(t[1:]-steps,0,0)
            self.G[key]['break']=np.insert(locs,0,0)
    
    def identify_changes(self):
        """
        Add a column the G indicating when the user entered a new answer
        """
        for key in self.G.keys():
            block=self.G[key]
            last_answer={}

            answer=block['answer'].values
            counter=block['counter'].values

            d=[0]*len(block.index)
            # classify each answer to one of three categories:
            # '' = empty (no answer given)
            # '=' = answer same as in the last try (probably left with no change)
            # '!=' = answer is different from the previous one
            for i in range(len(block.index)):
                # check if answer is the same as the previous or is different or new.
                d[i]='!='
                if answer[i]=='':
                    d[i]=''
                elif counter[i] in last_answer.keys():
                    if answer[i]==last_answer[counter[i]]:
                        d[i]='='
                last_answer[counter[i]]=answer[i]    
            self.G[key]['answer_state']=d

    def process(self):
        """execute all processing steps after initialization and before
        pickling.
        """
        print 'Starting with DataFrame, length=',len(self.DataFrame.index)
        self.dedup()
        print 'finished dedup, length of DedupFrame =',len(self.DedupFrame.index)
        self.expand_into_parts()
        print 'finished expanding into parts, length of ExpandedFrame =',len(self.ExpandedFrame.index)
        self.map_to_counter()
        print 'finished adding counter column'
        self.find_breaks()
        print 'finished updating time and adding break column'
        self.identify_changes()
        print 'finished adding answer_state column'


    def pickle(self,filename):
        """
        Create a pickle file with the desired table
        """
        print 'starting pickle'
        pickle.dump({'GroupedDataFrame':self.G,\
                     'time_gap_threshold':self.time_gap_threshold,\
                     'Problem_parts':self.C_dict},\
                    open(filename,'wb'),\
                    protocol=pickle.HIGHEST_PROTOCOL)
        print 'finished pickle'

if __name__=='__main__':
    if (len(sys.argv) == 1) and ('WWAH_LOGS' in os.environ.keys()):
        input_path=os.environ['WWAH_LOGS']
        P=ProcessLogs(input_path) # instantiatiate a class object and read in the log files.
    elif len(sys.argv) > 1 and ('MYSQL_DUMP_DIR' in os.environ.keys()):
        input_path = os.path.join(os.environ['MYSQL_DUMP_DIR'],sys.argv[1])
        P=ProcessLogs(input_path, is_dir=False) # instantiatiate a class object and read in the log files.
    else:
        print 'Execute "source setup.sh" from the root directory'
        sys.exit(0)
    print 'Log input path=',input_path
    P.process()
    if len(sys.argv) > 2:
        output_path = os.path.join(os.environ['WWAH_PICKLE'],sys.argv[2])
    else:
        output_path = os.environ['WWAH_PICKLE']+'/ProcessedLogs.pkl'
    P.pickle(output_path)
