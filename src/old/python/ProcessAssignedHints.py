#!/usr/bin/env python

from datetime import datetime
import pandas as pd
from collections import defaultdict
import pickle, os
import sys; sys.path.append('/opt/Webwork_AdaptiveHints/src/python')
from PlotTiming import PlotTiming
import numpy as np

if len(sys.argv) > 1 and ('MYSQL_DUMP_DIR' in os.environ.keys()):
    mysql_dump_abspath = os.path.join(os.environ['MYSQL_DUMP_DIR'],sys.argv[1])
else:
    print 'Execute "source setup.sh" from the root directory'
    sys.exit(0)
if len(sys.argv) > 2:
    pickle_out_abspath = os.path.join(os.environ['WWAH_PICKLE'],sys.argv[2])
else:
    pickle_out_abspath = os.environ['WWAH_PICKLE']+'/ProcessedAssignedHints.pkl'

with open(mysql_dump_abspath, 'r') as f:
    lines = f.readlines()

rows = defaultdict(list)

last_line = ''
for line in lines:
    # Ignore the current line of the sql dump if the previous line continues onto
    # this line
    if (len(last_line) > 0) and (last_line.rstrip()[-1] == '\\'):
        last_line = line
        continue
    try:
        assigned_hint_id,assignment,problem,part,user, \
            hint_id,_,_ = line.split('\t')
    except ValueError:
        continue
    # Remove non-digits, then convert to int
    assigned_hint_id = int(  ''.join( (c for c in assigned_hint_id 
        if c.isdigit()))   )
    part_id = int(  ''.join( (c for c in part if c.isdigit()))   )

    rows['assigned_hint_id'].append(int(assigned_hint_id)+1000)
    rows['assignment'].append(assignment)
    rows['problem_no'].append(int(problem))
    rows['part_no'].append(int(part_id))
    rows['user'].append(user)
    rows['hint_no'].append(int(hint_id))
    last_line = line

df = pd.DataFrame(rows,index=rows['hint_no'])
with open(pickle_out_abspath, 'w') as f:
    pickle.dump(df, f, protocol=pickle.HIGHEST_PROTOCOL)

