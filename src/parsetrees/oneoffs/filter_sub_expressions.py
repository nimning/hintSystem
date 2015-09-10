from webwork.cluster_exprs import *
from operator import itemgetter
import pickle
import numpy as np
import matplotlib.pyplot as pl

''' Filter mathematical expressions by their bit-vector similarity
    to sub-expressions '''

def jaccard(s1,s2):
    union = len(s1 | s2)
    if union == 0:
        return 1
    else:
        return float(len(s1 & s2))/union

def min_overlap(s1,s2):
    min_len = min(len(s1),len(s2))
    if min_len == 0:
        return 1
    else:
        return float(len(s1 & s2))/min_len

if __name__ == '__main__':
    exprs = pickle.load(open('exprs','r'))
    X = np.load(open('X','rb'))['arr_0']
    for part_expr in ['13*12/2','52!/(47!*5!)']:
        min_part_overlaps = map(
            lambda expr:min_overlap(set(preprocessor(expr)),
            set(preprocessor(part_expr))), exprs)
#        pl.plot(sorted(min_part_overlaps))
#        sorted_prep = sorted(enumerate(exprs), 
#            key=lambda (_,expr):
#          )
#        for expr in map(lambda (i,_):exprs[i],sorted_prep[-10:]):
#            print expr
#        print ''
    
