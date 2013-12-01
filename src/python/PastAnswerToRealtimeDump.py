#!/usr/bin/env python
import sys, os
from datetime import datetime
from tornado.template import Template

''' Takes a mysql dump from a WebWork past_answer table, and transforms it
    into an attempt-per-part dump.  In the past_answer type dump, each line
    corresponds to a problem.
    In the attempt-per-part type dump (like the realtime analysis dumps), 
    each line corresponds to a single expression entered into a single box
    '''


def timestamp_to_string(timestamp):
    d = datetime.fromtimestamp(timestamp)
    return d.strftime('%Y-%m-%d %H:%M:%S')

def problem_attempt_to_part_attempt(line):
    split_line = line.strip().split('\t')
    id, course, user, assignment, problem, pg_path, timestamp, correctness = \
        split_line[:8]
    expressions = [expr.strip('\\') for expr in split_line[8:-2]]
    if len(expressions) != len(correctness):
        return None
    timestamp_str = timestamp_to_string(int(timestamp))
    
    part_attempt_lines = []
    for i,correct in enumerate(correctness):
        expr = expressions[i]
        part_id = 'PastAnswer%d'%(i + 1)
        part_attempt_lines.append(
            '\t'.join(['1',assignment,problem,part_id,
                user,pg_path,correct,expr,timestamp_str])
        )

    return part_attempt_lines

if __name__ == '__main__':
    if not 'MYSQL_DUMP_DIR' in os.environ:
        print 'Run source setup_mysql_dump.sh in the src root dir'
    past_answers_path = os.path.join(os.environ['MYSQL_DUMP_DIR'],'UCSD_CSE103_past_answer.txt')
    part_attempt_output_path = os.path.join(os.environ['MYSQL_DUMP_DIR'],'UCSD_CSE103_part_attempt.txt')
    with open(past_answers_path,'r') as in_f:
        with open(part_attempt_output_path,'w') as out_f:
            for line in in_f:
                part_attempt_lines = problem_attempt_to_part_attempt(line)
                if not part_attempt_lines is None:
                    for l in part_attempt_lines:
                        out_f.write(l+'\n')
