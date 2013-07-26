#!/usr/bin/env python
"""
The script reads .def files that list the .pg files for each assignment.
It reads each of the .pg files, finds the blocks that corresponds to the PGML text 
and extracts it.
It then iterates through each block and finds the parts that correspond to questions boxes of the form
"[_____]{answer}". The generated Table that is pickled has the following form:
{'Assignment': list of the names of the assignment def file.
'problem': list of the indexes of the problem in the assignment
'text': list of lists of blocks (one list of blocks for each problem) each block contains:
   {'line': the number of line in the block,
    'start','end': the beginning and end of the question box (inside the line)
    'match': the text of the match. (in the form "[_____]{answer}")
   }
"""
import re,os,pandas,pickle
from glob import glob
from copy import deepcopy
from termcolor import colored, cprint

def find_question_windows(pgml):
    """
    Find the locations of the question boxes, color them and put the part index in the [___]
    add some highlight color and Repartition the text so that it is broken after each box
    """
    # combine all of the blocks in pgml into a single long string.
    Text=''
    for block in pgml:
        for line in block:
            Text+=line
        Text+='-------------------------------------------------------------\n'

    # Partition the long string (Text) into parts according to the
    # locations of the question Blocks
    part=1
    s0=0
    newtext=[]
    for match in re.finditer(r'\[_*\]\{.*?\}',Text):
        pre=Text[s0:match.start()]
        box=match.group(0)
        submatch=re.match(r'(\[_*\])(\{.*?\})',box)
        #print submatch.groups()
        # use '*' emphasis for org-mode
        highlight=('*[%3d]' % part) + submatch.group(2)+'*'
        newtext.append(('* Part %3d\n' % part)+pre+highlight)
        part+=1
        s0=match.end()
    if(s0+1<len(Text)): 
        newtext.append(Text[s0:])
    return newtext

#-------------  Main  -------------------------------

dir=os.environ['WWAH_PG']
os.chdir(dir)

BeginEndPairs=[{'begin':'TEXT(PGML::Format','end':'END_PGML','type':'pgml'},\
               {'begin':'BEGIN_PGML','end':'END_PGML','type':'pgml'}]
Table={'Assignment':[], 'problem':[], 'text':[]}
def_files=glob('setAssignment?.def')
for ass_no in range(len(def_files)):
    assignment=def_files[ass_no]
    file=open(assignment,'r')

    # Extract 'Assignment(\d)' from 'setAssignment(\d).def'
    matchAssignment=re.match(r'setAssignment(\d).def',assignment)
    if matchAssignment:
        assignment='Assignment'+matchAssignment.group(1)
        print 'Assignment name=',assignment
    else:
        raise Exception('Assignment name does not match pattern:'+assignment)
        
    lines=file.readlines()
    start=False; pg_list=[]
    for line in lines:
        if start:
            e=line.split(',')
            if len(e)>1:
                pg_list.append(e[0])
        else:
            if line.find('problemList')>-1:
                start=True

    for problem in range(len(pg_list)):
        file=pg_list[problem]
        if not os.path.exists(file):
            print 'ERROR: did not find file "%s" associated with "%s" problem: %d'\
                    % (file,pg_list[ass_no],problem+1)
        else:
            print 'Processing file ',file, ' in ',assignment

        pg_file=open(pg_list[problem],'r')
        lines=pg_file.readlines()
        pgml_blocks=[]
        TEXT=False
        format_i=-1
        for line in lines:
            if not TEXT:      # Look for start of text
                if format_i ==-1:    # find the type of begin/end that is used in this file
                    for ii in range(len(BeginEndPairs)):
                        if line.find(BeginEndPairs[ii]['begin'])>-1:
                            format_i=ii
                            current_block=''
                            TEXT = True
                            break
                else:
                    if line.find(BeginEndPairs[format_i]['begin'])>-1:   #look for start of known type
                        current_block=''
                        TEXT=True
            else:
                if line.find(BeginEndPairs[format_i]['end'])>-1:     # Look for end
                    pgml_blocks.append(current_block)
                    TEXT=False
                else:
                    current_block +=line      #regular markdown line
        
        pgml_blocks=find_question_windows(pgml_blocks)
        Table['Assignment'].append(assignment)
        Table['problem'].append(problem+1)
        Table['text'].append(pgml_blocks)
        print 'found ',len(pgml_blocks),'of sizes',[len(b) for b in pgml_blocks]

print 'starting pickle'
pickle_dir=os.environ['WWAH_PICKLE']
pickle.dump({'ProblemTexts':pandas.DataFrame(Table)},\
            open(pickle_dir+'/problemTexts.pkl','wb'),\
            protocol=pickle.HIGHEST_PROTOCOL)
print 'finished pickle'

