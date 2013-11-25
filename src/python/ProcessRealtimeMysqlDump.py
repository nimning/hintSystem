#!/usr/bin/env python

from datetime import datetime
import pandas as pd
from collections import defaultdict
import pickle, os
import sys; sys.path.append('/opt/Webwork_AdaptiveHints/src/python')
from PlotTiming import PlotTiming
import numpy as np


mysql_dump_filename = 'UCSD_CSE103_realtime_past_answer.txt'
pickle_out_filename = 'ProcessedLogs.pkl'
mysql_dump_dir = os.environ['WWAH_LOGS']
pickle_out_dir = os.environ['WWAH_PICKLE']
mysql_dump_abspath = os.path.join(mysql_dump_dir, mysql_dump_filename)
pickle_out_abspath = os.path.join(pickle_out_dir, pickle_out_filename)

### TODO DELETEME
### THIS IS A DUPLICATE OF THE FUNCTION IN ProcessLogs.py
def find_breaks(G, time_gap_threshold):
    for key in G.keys():
        t=G[key]['time'].values
        t-= t[0]
        gaps=t[1:]-t[:-1]
        locs=np.array([(gaps[i] if gaps[i]>time_gap_threshold else 0) for i in range(len(gaps))])
        steps=np.cumsum(locs)
        G[key]['time']=np.insert(t[1:]-steps,0,0)
        G[key]['break']=np.insert(locs,0,0)
    return G
     
### END TODO DELETEME

with open(mysql_dump_abspath, 'r') as f:
    lines = f.readlines()

rows = defaultdict(list)

for line in lines:
    try:
        _, set_id, problem_id, pg_id, user_id, _, correct, answer_string, timestamp = line.split('\t')
    except ValueError:
        continue
    timestamp = datetime.strptime(timestamp.strip(), '%Y-%m-%d %H:%M:%S')
#    webwork_timestamp = timestamp.strftime('%a %b %d %H:%M:%S %Y')
#    unix_timestamp = int(timestamp.strftime('%s'))
    problem_id = int(problem_id)
    # Remove non-digits, then convert to int
    pg_id = int(  ''.join( (c for c in pg_id if c.isdigit()))   )
    rows['Assignment'].append(set_id)
    rows['problem_no'].append(problem_id)
    rows['part_no'].append(pg_id)
    rows['user'].append(user_id)
    rows['correct'].append(correct == '1')
    rows['answer'].append(answer_string)
    rows['timestamp'].append(timestamp)

rows['time'] = [int(t.strftime('%s')) for t in rows['timestamp']]
df = pd.DataFrame(rows, index=pd.DatetimeIndex(rows['timestamp']))
keys = dict(df.groupby(['Assignment','problem_no','part_no']).size()).keys()
C = dict(( ((a,prob,part),prob*20+part) for (a,prob,part) in keys ))
G = dict(list(df.groupby(['user', 'Assignment'])))
time_gap_threshold=1200
G = find_breaks(G, time_gap_threshold)
for k in G.keys():        
    G[k]['counter'] = [C[tuple(row)] 
        for row in G[k][['Assignment', 'problem_no','part_no']].values]
    G[k]['answer_state'] = '!='

with open(pickle_out_abspath, 'w') as f:
    pickle.dump(
        {'GroupedDataFrame':G,
         'time_gap_threshold':time_gap_threshold,
         'Problem_parts':C,
         'FullRealtimeDataFrame':df},
        f,
        protocol=pickle.HIGHEST_PROTOCOL
    )

#plotTiming = PlotTiming(pickle_out_abspath)
#plotTiming.plot()

