import pandas as pd
import pickle

f = pickle.load(open('BehavioralStatistics.pkl','r'))
df = f.values()[0]

index=zip(list(df.assignment), list(df.problem_no), list(df.part_no));

# plan to use linear regression using
# http://docs.scipy.org/doc/numpy-1.4.x/reference/generated/numpy.linalg.lstsq.html#numpy-linalg-lstsq
