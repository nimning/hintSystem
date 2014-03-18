#!/usr/bin/env python
import math
import numpy as np
import nltk
import sys, os
from sklearn.cluster import KMeans
from collections import defaultdict
sys.path.append(os.environ['WWAH_SRC'])
#from webwork.preprocess_webwork_logs import WebWork
from webwork.expr_parser.webwork_parser import parse_webwork,WebworkParseException
import pickle
from pprint import pprint
from operator import itemgetter
import simplejson as json
from sklearn.decomposition import NMF, PCA
import pickle
from collections import Counter
from scipy.stats import pearsonr
import random

assignment = 'Assignment10.18.13'
problem = 1
n_parts = 7

def is_float(s):
    ''' Check whether the string can be converted to a floating point '''
    try:
        float(s)
        return True
    except ValueError:
        return False

n = 4

correctness_filter = None #Filter by correct/incorrect expressions.  
def leaf_mapper(leaf):
    trivial_leaf_mapper(leaf)
def preprocessor(expr):
    return preprocessor_parsing(expr)
#None tells not to filter by correctness 

def parse_expr_to_set(expr):
    ''' Produce a set of features (tuples) from mathematical expressions '''
    feature_list = preprocessor_parsing(expr)
    if feature_list is None:
        return set([])
    else:
        return set(feature_list)

def ngrams(s, n):
    '''Generate all <n>grams from string s'''
    ngram_strs = []
    for i in range(len(s)-n+1):
        ngram_strs.append(s[i:i+n])
    return ngram_strs

def trivial_leaf_mapper(leaf):
    if type(leaf) == list:
        return tuple([',']+leaf)
    else:
        return leaf

def type_leaf_mapper(leaf):
    return type(leaf)

def tree_paths(tree,n,leaf_mapper):
    paths = set([])
    if type(tree) != tuple: #leaf node
        paths.add( (leaf_mapper(tree), ) ) #Just the node forms a path    
    else:
        child_paths = set([])
        for child_tree in tree[1:]:
            child_paths |= tree_paths(child_tree,n,leaf_mapper)
        for child_path in child_paths:
            if len(child_path) < n:
                paths.add( (tree[0],) + child_path)
        paths.add( (tree[0],) )
        paths |= child_paths
    return paths

def clean_expr(expr):
    for c in ['(',')',' ']: #Remove theses characters
        expr = expr.replace(c,'')
    return expr

def preprocessor_ngram(expr):
    expr = clean_expr(expr)
    return ngrams(expr,n)

def preprocessor_parsing(expr):
    try:
        tree = parse_webwork(expr)
        return list(tree_paths(tree,n,type_leaf_mapper))+ list(tree_paths(tree,n,trivial_leaf_mapper))
    except WebworkParseException:
        return []


def preprocess_expr(expr, vocab_hash):
    '''Map a mathematical expression to a bag-of-words vector of ngram counts
        '''
    dist = nltk.FreqDist( (vocab_hash[word] for word in preprocessor(expr) if word in vocab_hash) )
    v = np.zeros(shape=(1,len(vocab_hash)))
    for i,count in dict(dist).iteritems():
        v[0,i] = 1 #count
    return v

def preprocess_exprs(exprs):
    vocab_dist = nltk.FreqDist( (word for expr in exprs
        for word in preprocessor(expr)))
    vocab_list = [word for word,count in dict(vocab_dist).iteritems() if count > 5]
    vocab_list = sorted(vocab_list)
    vocab_hash = dict((s,i) for i,s in enumerate(vocab_list))
    
    X = np.zeros(shape=(len(exprs),len(vocab_list)))
    for i,expr in enumerate(exprs):
        X[i,:] = preprocess_expr(expr,vocab_hash)
    return X

def kmeans_cluster_var(X, model):
    ''' Same as model.score '''
    centroids = model.cluster_centers_
    var = 0
    for x,label in zip(X,model.labels_):
        diff = x - centroids[label,:]
        var += np.dot(diff,diff)
    return var

def cluster_expr_series(series, k):
    if len(series) > k:
        exprs = series.values.tolist()
        X = preprocess_exprs(exprs)
        model = KMeans(n_clusters=k)
        return model.fit_predict(X)
    else:
        return [0]*len(series)

def cluster_expr_dataframe(df, k):
    ''' Add a column 'expr_cluster' to the data frame '''
    df['expr_cluster'] = df.groupby(['Assignment','problem_no','part_no'],
        as_index=False)['answer'].transform(
        lambda exprs:cluster_expr_series(exprs,k))
    return df

def cluster_exprs(exprs, k):
    ''' Given a list of mathematical expressions as strings, parse and 
        use KMeans clustering to group these into k groups 
        Return a list of expression groups '''
    model = KMeans(n_clusters=k)
    X = preprocess_exprs(exprs)
    labels = model.fit_predict(X)
    groups = defaultdict(list) #a list of lists of length k, for storing expression clusters
    for label, expr in zip(labels, exprs):
        groups[label].append(expr)
    return groups.values()

def user_clusters(df, users):
    ''' Given a dataframe <df> with 'user' and 'expr_cluster' columns, 
        and a list of users, return a numpy array the same size as <users>
        
        Each element of the numpy array gives for the corresponding element
        in <users> the expr_cluster most commonly associated with that
        user in <df> '''
    user_clusters = np.zeros(shape=(len(users),))
    for i,user in enumerate(users):
        cluster_counts = df[df['user'] == user].groupby('expr_cluster').size()
        if len(cluster_counts) == 0:
            user_clusters[i] = -1
        else:
            user_clusters[i] = cluster_counts.index[np.argmax(cluster_counts)]
    return user_clusters

if __name__ == '__main__':
    # Load full realtime table data frame
    pickle_dir=os.environ['WWAH_PICKLE']
    if len(sys.argv) > 1:
        input_path = os.path.join(pickle_dir,sys.argv[1])
    else:
        input_path = pickle_dir+'/ProcessedLogs.pkl'
    with open(input_path,'r') as f:
        df = pickle.load(f)['FullRealtimeDataFrame']
