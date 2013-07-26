# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import os,pickle
pickle_dir=os.environ['WWAH_PICKLE']

BT = pickle.load(open(pickle_dir+'/BehavioralStatistics.pkl','rb'))
B=BT['BehaviourStatistics']

TT=pickle.load(open(pickle_dir+'/problemTexts.pkl','rb'))
Texts=TT['ProblemTexts']

LT=pickle.load(open(pickle_dir+'/ProcessedLogs.pkl','rb'))
G=LT['GroupedDataFrame']
g=G[('xiz080', 'Assignment4')]

mean_times=B['time'].groupby([B['assignment'],B['part']]).mean()
mean_tries=B['tries'].groupby([B['assignment'],B['part']]).mean()
print mean_times[mean_times>10]

# <markdowncell>

# ## Clearly Assignment5, part13 was one of the hardest problems in the quarter.
# 
# We now want to find the text for this problem and examples of students that struggled with it

# <codecell>

assignment='Assignment5'
student='jmc001'
problem=2
part=7

# <codecell>

def extract_history(assignment='Assignment5', problem=2, part=7, student='jmc001'):
    frame=G[(student,assignment)]

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
    
T=extract_history()
parts=T.groupby('part_no')
l=len(parts)

# <codecell>

i=0
summary=[]   # text representing answer attempts
attempts=[]  # number of attempts for this part
time_length=[]  # length of time spent on this part
SorF=['failure','sucess']
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
            line ='** '+line
        text+=line
        a_i+=1
    summary.append(text)
    i+=1
for s in summary:
    print s

# <codecell>

import pandas
FT=Texts
FT.keys()

# <codecell>

FT[['Assignment','problem']].head()

# <codecell>

selector=(FT['Assignment']==assignment) & (FT['problem']==problem)
texts=FT.ix[selector,'text'].values[0]
len(texts)

# <codecell>

filename='.'.join((assignment,str(problem),str(part),student,'org'))
filename

# <codecell>

#output_dir=os.environ['WWAH_OUTPUT']
output_dir='/Users/yoavfreund/projects/Webwork.Improvement.Project/Demo_for_utube/data/OutputFiles'
f=open(output_dir+'/'+filename,'wb')
for i in range(l):
    print >>f,texts[i]
    print >>f,('* Answers of student %s. %2d attempts lasting %3.1f minutes, ending in %s'\
              % (student,attempts[i],time_length[i],final_correct[i]))
    print >>f,summary[i]
f.close()
    

# <codecell>


