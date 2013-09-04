#!/usr/bin/env python
import os,pandas,pickle,sys
import numpy as np

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

    def print_struggles(self,assignment,mintries=3,lines=10):
        """report the problem parts in a given assignment on which the
        students spent most of their time.

        """
        B=self.B
        BA1= B[B['assignment']==assignment]
        BA1H=BA1[BA1['tries']>mintries-1]
        Summary=BA1H[['problem_no','part_no','user','tries','time']].sort(['problem_no','part_no'])
        self.Summary=Summary
        groupedSummary=Summary.groupby(['problem_no','part_no'])
        part_statistics=groupedSummary.agg({'user':np.size,
                                            'tries':np.sum,
                                            'time':np.sum}).sort('time', ascending=False)
        
        print 'index\t(problem,part)\tno. of students\t\ttotal tries\ttotal time'
        self.struggles_table=[]
        for i in range(lines):
            row=part_statistics.iloc[i:i+1].to_dict()
            key=row['user'].keys()[0]
            users=row['user'].values()[0]
            tries=row['tries'].values()[0]
            time=row['time'].values()[0]
            self.struggles_table.append({'key':key,'users':users,'tries':tries,'time':time})
            print '%1d)\t   %s\t\t   %2d\t\t   %3d\t\t   %5.2f' % (i+1,key, users, tries, time)

    def list_students(self,line,lines=10):
        ProblemPart=self.struggles_table[line-1]
        (problem,part)=ProblemPart['key']
        print 'problem=%d,part=%d' % (problem,part)
        Summary=self.Summary
        Summary = Summary[Summary['problem_no']==problem]
        Summary = Summary[Summary['part_no']==part]
        print Summary.sort('tries', ascending=False).head(lines)
        return (problem,part)

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
        T=self.extract_history(assignment, problem, part, student)
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
            a_i=0; text='** All but last attempt\n\n'
            for row in g[1].iterrows():
                line=('| %2d:'%a_i)+('| %3d | %4.1f | %s | %s |' % tuple(row[1].values)+'\n')
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

        # combine logs and problem texts and output to a file generate
        # a file using extended markdown - pandoc markdown.  make
        # students answers into a horizontal table with ~5 answers per
        # row.  It would be great if the size of the display windows
        # would be limited and the reviewer can scroll through them.
        # Make the display the hint and the original text in web editor frames.

        # use github markdown, translate to HTML using 
        
        # pandoc -f markdown_github -t html -o github.html github.md 

        # Use the ACE embedded editor so that tutors can write hints
        # and make changes to current problem.

        output_dir=os.environ['WWAH_OUTPUT']
        filename='.'.join((assignment,str(problem),str(part),student,'md'))
        f=open(output_dir+'/'+filename,'wb')
        for i in range(len(attempts)):
            print >>f,"```\n"+texts[i]+"\n```"
            print >>f,('* Answers of student %s. %2d attempts lasting %3.1f minutes, ending in %s'\
                      % (student,attempts[i],time_length[i],final_correct[i]))
            print >>f,summary[i]
        f.close()
        print 'generated file: ',output_dir+'/'+filename,

if __name__=='__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Create a org file detailing the actions of students that struggled with a problem')
    parser.add_argument('-a','--assignment', required=True)
    parser.add_argument('-m','--mintries', type=int, default=3
                        ,help='the minimal number of tries for a user/part to be considered (default=3)')
    parser.add_argument('-l','--lines', type=int, default=10
                        ,help='the number of output lines generated (default=3)')
    parser.add_argument('-p','--problem',type=int ,default=-1)
    parser.add_argument('-r','--part',type=int ,default=-1)

    args = vars(parser.parse_args())


    # Three phase interaction:
    # 1) give statistics on hardest parts of assignment
    R=reportStruggles()
    print 'The hardest parts of %s are:' % args['assignment']
    lines_no=args['lines']
    R.print_struggles(args['assignment'],mintries=args['mintries'],lines=lines_no)

    # 2) Select part to dig into - get list of students that struggled with those parts.
    import readline
    line = input('choose one of the lines above (1 to '+str(lines_no)+'): ')

    while line>lines_no or line<1:
        print 'you entered',line,'which is outside the range [1,',lines_no,']'
        line=input('try again: ')

    (problem,part) = R.list_students(line)
        
    # 3) Choose a student : generate org file(s) that shows how students struggled, and has space to define hints.

    student=raw_input("type in student's id :")
    R.generate_report(args['assignment'],problem,part,student)

