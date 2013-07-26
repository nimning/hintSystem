import os,pandas,pickle,sys

class reportStruggles:

    def __init__(self):
        pickle_dir=os.environ['WWAH_PICKLE']

        def load_pickle(pickle_file):
            print 'reading ',pickle_file
            sys.stdout.flush()
            return pickle.load(open(pickle_dir+pickle_file,'rb'))

        self.BT = load_pickle('/BehavioralStatistics.pkl')
        self.B=self.BT['BehaviourStatistics']

        self.TT= load_pickle('/problemTexts.pkl')
        self.Texts=self.TT['ProblemTexts']

        self.LT = load_pickle('/ProcessedLogs.pkl')
        self.G=self.LT['GroupedDataFrame']

        print 'done reading pickle files'

    def find_struggles(self):
        B=self.B
        grouped=B.groupby(['assignment','problem_no','part_no'])
        mean_times=grouped['time'].mean()
        mean_tries=grouped['tries'].mean()
        return (mean_times, mean_tries)

    def extract_history(self,assignment, problem, part, student):
        frame=self.G[(student,assignment)]

        frame=frame[frame['problem_no']==problem]
        frame=frame[frame['part_no']<=part]
        frame=frame[frame['answer_state']=='!=']
        frame=frame.sort(columns=['part_no','time'])
        frame['time']=(frame['time']-frame['time'].values[0])/60.0
        triplets=frame[['part_no','time','correct','answer']]
        if len(triplets)==0:
            return None
        else:
            return triplets
    
    def generate_report(self,assignment, problem, part, student):
        """Generate a report for a particular (user,assignment) pair.  The
        report consists of the PG text up to each question box,
        followed by the list of attempts to answer made by the
        student.  The output is a sequence of multi-line strings the
        are meant to be printed and then viewed in emac in org-mode

        """
        T=extract_history(self,assignment, problem, part, student)
        parts=T.groupby('part_no')

        if parts==None:
            return None

        # extract the relevant parts of the student's log
        i=0
        summary=[]   # text representing answer attempts
        attempts=[]  # number of attempts for this part
        time_length=[]  # length of time spent on this part
        SorF=['failure','success']
        final_correct=[] # indicates if the final attempt is correct
        for g in parts:
            att_no=len(g[1])
            attempts.append(att_no)
            gt=g[1]['time'].values
            time_length.append(gt[-1]-gt[0])
            fin=SorF[int(g[1]['correct'].values[-1])]
            final_correct.append(fin)
            a_i=0; text='** All but last attempt\n'
            for row in g[1].iterrows():
                line=(' %2d:'%a_i)+('\t%3d\t%4.1f\t%s\t%s' % tuple(row[1].values)+'\n')
                if  a_i==att_no-1:
                    line ='** '+line # make last line easily accessible in org-mode
                text+=line
                a_i+=1
            summary.append(text)
            i+=1
    
        # extract the relevant problem texts
        FT=self.Texts
        selector=(FT['Assignment']==assignment) & (FT['problem']==problem)
        texts=FT.ix[selector,'text'].values[0]

        # combine logs and problem texts and output to a file
        output_dir=os.environ['WWAH_OUTPUT']
        filename='.'.join((assignment,str(problem),str(part),student,'org'))
        f=open(output_dir+'/'+filename,'wb')
        for i in range(len(texts)):
            print >>f,texts[i]
            print >>f,('* Answers of student %s. %2d attempts lasting %3.1f minutes, ending in %s'\
                      % (student,attempts[i],time_length[i],final_correct[i]))
            print >>f,summary[i]
        f.close()
