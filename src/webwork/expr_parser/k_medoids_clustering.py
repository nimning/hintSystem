import webwork_parser
import pandas as pd
import numpy as np
import json
from zss import simple_distance
import random
from collections import defaultdict

class TupleNode(object):
    def __init__(self, tp):
        self.data = tp
        try:
            self.label = tp[0]
            self.children = [TupleNode(x) for x in tp[1:]]
        except TypeError:
            self.label = tp
            self.children = []

    @staticmethod
    def get_children(node):
        return node.children

    @staticmethod
    def get_label(node):
        return node.label

    def edit_distance(self, other_tree):
        return simple_distance(self, other_tree,
                               TupleNode.get_children, TupleNode.get_label)
    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return '<TupleNode %s>' % str(self.data)
with open('poker_cond2_1.pg.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data['past_answers'])

answers = df.answer_string.str.split('\t')

# e3=webwork_parser.parse_webwork('C(6*7*5,5^3)+9/(31+18)')
# print e3

# We want to cluster all incorrect attempts
# For each incorrect attempt:
#  Parse answer expression into tree
#  (Discard unparseable expressions or something)
#  Stick parse tree into a list

trees = []
part = 0
for i, a in answers.iteritems():
    if df.scores[i][part] == '0':
        # Only consider incorrect answers
        try:
            expr = webwork_parser.parse_webwork(a[part])
            n = TupleNode(expr)
            trees.append(n)
        except webwork_parser.WebworkParseException:
            pass

print len(trees)

# K Medoids Algorithm
"""
1. Initialize: randomly select k of the n data points as the medoids
2. Associate each data point to the closest medoid.
3. For each medoid m

    1. For each non-medoid data point o
        1. Swap m and o and compute the total cost of the configuration

4. Select the configuration with the lowest cost.
Repeat steps 2 to 4 until there is no change in the medoid.
"""
k = 10

def cluster_cost(medoid, cluster):
    costs = [x.edit_distance(medoid) for x in cluster]
    return sum(costs)

medoids = random.sample(trees, k)
medoids_changed = True
while medoids_changed:
    medoids_changed = False
    clusters = defaultdict(list)
    # Assign each data point to closest cluster
    print '=== Start round ==='
    for expr in trees:
        if expr not in medoids:
            dists = [x.edit_distance(expr) for x in medoids]
            min_dist_i = np.argmin(dists)
            min_medoid = medoids[min_dist_i]
            clusters[min_medoid].append(expr)
    for medoid in medoids:
        current_cost = cluster_cost(medoid, clusters[medoid])
        print len(clusters[medoid]), ' in cluster ', medoid
        costs = []
        for other in clusters[medoid]:
            c = cluster_cost(other, clusters[medoid]) + \
                other.edit_distance(medoid)
            costs.append(c)
        min_cost_i = np.argmin(costs)
        if costs[min_cost_i] < current_cost:
            cluster = clusters.pop(medoid)
            new_medoid = cluster.pop(min_cost_i)
            cluster.append(medoid)
            clusters[new_medoid] = cluster
            medoids_changed = True
            print medoid, new_medoid
            print costs[min_cost_i]
    medoids = clusters.keys()
    print '=== End round ===', medoids_changed
    print medoids
print clusters
