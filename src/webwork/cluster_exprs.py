#!/usr/bin/env python
import math
import numpy as np
import nltk
import sys, os
from sklearn.cluster import KMeans
from collections import defaultdict
from webwork.preprocess_webwork_logs import WebWork
from webwork.expr_parser.webwork_parser import parse_webwork,WebworkParseException
import pickle
from pprint import pprint
from operator import itemgetter
import simplejson as json
import split_webwork_pg
from sklearn.decomposition import NMF, PCA

def is_float(s):
    ''' Check whether the string can be converted to a floating point '''
    try:
        float(s)
        return True
    except ValueError:
        return False

n = 4 #the n in ngram, or path length in type_tree_paths
K = 10 #the k in kmeans
webwork_data_path = '/home/melkherj/education_project/data/cse103_original_data/WebWork'
webwork_pg_filename = '/home/melkherj/education_project/data/problem_3_1_analysis/problem_text/problem.pg'
problem = ('Assignment3',1)
#part = 21)
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
        return list
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
        return list(tree_paths(tree,n,trivial_leaf_mapper)) + \
            list(tree_paths(tree,n,type_leaf_mapper))
    except WebworkParseException:
        return None


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

if __name__ == '__main__':
    parts = {}
    
    part_texts, part_answers = split_webwork_pg.get_parts_answers(webwork_pg_filename)
    webwork = pickle.load(open(os.path.join(webwork_data_path,'pickled_data'),'rb'))
    problem_part_attempts = [(part,attempts) for part,attempts in 
        webwork.part_attempts.iteritems() if part[0] == problem[0] 
        and part[1] == problem[1]]
    for part_index, attempts in problem_part_attempts:
        part_index = part_index[-1] #part_index is originally of the form: ('Assignment3', 1, 30)
        if part_index >= 7:
            continue
        exprs = [expr for _,c,expr in attempts 
            if ((correctness_filter == c) or (correctness_filter is None)) 
            and len(expr.strip()) > 0 and (not preprocessor(expr) is None)]
        X = preprocess_exprs(exprs)
        # Cluster using KMeans, and decide on cluster using BIC score
        scores = []
        bic_scores = []
        (n, d) = X.shape
        all_vars = []
        bic_score_parts = []
        last_bic_score = None #-Inf
        is_decreasing = False
        for K in range(30,31): #range(1,min(len(exprs),300),10):
            model = KMeans(k=K)
            model.fit(X)
            labels = model.predict(X)
            clusters = defaultdict(list)
            for i,label in enumerate(labels):
                clusters[int(label)].append(exprs[i])
            # Compute BIC score, and break accordingly
            clusters_n = [len(c) for c in clusters.values()]
            log_prod = sum([c*math.log(c) for c in clusters_n])
            var = kmeans_cluster_var(X, model)
            n_parameters = (K-1 + d*K + 1)
            try:
                bic_score = -n/2.0*math.log(2*math.pi) - n*d/2.0*math.log(var) - (n-K)/2.0 + log_prod - n*math.log(n) -n_parameters/2.0*math.log(n) 
                bic_score_parts.append((-n/2.0*math.log(2*math.pi),- n*d/2.0*math.log(var),- (n-K)/2.0, log_prod,- n*math.log(n), -n_parameters/2.0*math.log(n)))
                bic_scores.append(bic_score)
                # BIC scores need to be decreasing twice in a row 
                if bic_score < last_bic_score:
                    if is_decreasing:
                        break
                    is_decreasing = True
                last_bic_score = bic_score
            except ValueError:
                break
        X_k = model.transform(X)
        centroids = [exprs[int(i)] for i in X_k.argmin(axis=0)]
        ordered_clusters = [clusters[i] for i in range(model.k)]
        # Sort clusters by length
        sorted_clusters_centroids = sorted(zip(ordered_clusters,centroids), key=lambda (cluster,_):-len(cluster))
        sorted_clusters = map(itemgetter(0),sorted_clusters_centroids)
        sorted_centroids = map(itemgetter(1),sorted_clusters_centroids)
        sorted_cluster_lens = map(len,sorted_clusters)
        top_K = (k for k,cumsum in enumerate(np.cumsum(sorted_cluster_lens)) 
                if cumsum >= 0.9*n).next()
        part = {}
        part['clusters'] = dict((str(i),cluster) 
            for i,cluster in enumerate(sorted_clusters[0:top_K]))
        part['centroids'] = dict((str(i),centroid) 
            for i,centroid in enumerate(sorted_centroids[0:top_K]))
        part['text'] = part_texts[part_index]+'%s'
        part['answer'] = part_answers[part_index]
        part['name'] = 'part%d'%part_index
        part['dependencies_OR'] = {}
        part['cluster_groups'] = {}
        # By default, add a "numbers" expression cluster
        part['cluster_groups']['numbers'] = [i 
            for i,centroid in enumerate(sorted_centroids[0:top_K]) 
            if is_float(centroid)]
        parts[part_index] = part
    parts_ordered = [part for _,part in sorted(parts.iteritems(),key=itemgetter(0))]
    
    with open('expr_clusters.json','w') as f:
        json.dump(parts_ordered, f, sort_keys=True)
