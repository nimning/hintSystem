#!/usr/bin/env python

import re
import sys

def get_parts_answers(pg_filename):
    '''Given the path to some pg file, break the file into parts by
        expression boxes, returning the answers and question part 
        descriptions '''

    with open(pg_filename,'r') as f:
        pg_file = f.read()
    # Strip off headers/end of pg file, just keep the middle content 
    #  from BEGIN_PGML -> END_PGML
    pg_file_body = pg_file[ pg_file.index('BEGIN_PGML')+len('BEGIN_PGML') :
        pg_file.rindex('END_PGML') ]
    pg_file_parts = re.split('\[\_*\]',pg_file_body) #Split by [____...__]
    answers = []
    parts = [] #After removing {<answer>} from the beginning of parts
    for i in range(len(pg_file_parts)-1):
        answer_index = pg_file_parts[i+1].index('}')
        answer = pg_file_parts[i+1][:answer_index].strip('{}')
        pg_file_parts[i+1] = pg_file_parts[i+1][answer_index+1:].strip('.\n')
        parts.append(pg_file_parts[i])
        answers.append(answer)
    return (parts, answers)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('usage: %s <pg filename>\n'%sys.argv[0])
        sys.exit(1)
    parts, answers = get_parts_answers(sys.argv[1])
