import webwork_parser
import pandas as pd
import numpy as np
import json
from zss import simple_distance
import random
from collections import defaultdict

cache_hits = 0
cache_misses = 0
class ExpressionNode(object):
    """An expression tree class with proper getters for the zss module to
    function.

    """
    def __init__(self, tp):
        self.data = tp
        self.dist_cache = {}
        if isinstance(tp, tuple):
            self.label = tp[0]
            self.children = [ExpressionNode(x) for x in tp[1:]]
        else:
            self.label = tp
            self.children = []

    @classmethod
    def from_string(cls, string):
        """
        Creates expression tree from a string.

        Throws webwork_parser.WebworkParseException on failure
        """
        data = webwork_parser.parse_webwork(string)
        return cls(data)

    def __str__(self):
        if self.children:
            return '(' + str(self.label) + ' ' +' '.join([str(x) for x in self.children]) + ')'
        else:
            return str(self.label)

    def __repr__(self):
        return '<ExpressionNode %s>' % str(self)

    @staticmethod
    def to_json(node):
        return str(node)

    @staticmethod
    def get_children(node):
        """Getter method for zss"""
        return node.children

    @staticmethod
    def get_label(node):
        """Getter method for zss"""
        return node.label

    def edit_distance(self, other_tree):
        """
        Returns the Zhang-Sasha edit distance between another tree, as
        implemented in zss
        """
        global cache_hits
        global cache_misses
        cached_dist = self.dist_cache.get(str(other_tree))
        if cached_dist:
            cache_hits += 1
            return cached_dist
        else:
            cache_misses += 1
            d = simple_distance(self, other_tree,
                                ExpressionNode.get_children, ExpressionNode.get_label)
            self.dist_cache[other_tree] = d
            other_tree.dist_cache[self] = d
            return d

    @staticmethod
    def distance_function(node1, node2):
        return node1.edit_distance(node2)

def cluster_cost(medoid, cluster):
    """
    Computes the total edit distance from a medoid to the elements in
    its cluster

    """
    costs = [x.edit_distance(medoid) for x in cluster]
    return sum(costs)

def assign_clusters(data, medoids):
    clusters = defaultdict(list)
    for expr in data:
        if expr not in medoids:
            dists = [x.edit_distance(expr) for x in medoids]
            min_dist_i = np.argmin(dists)
            min_medoid = medoids[min_dist_i]
            clusters[min_medoid].append(expr)
    return clusters

def k_medoids(data, k):
    """
    K Medoids Algorithm

    1. Initialize: randomly select k of the n data points as the medoids
    2. Associate each data point to the closest medoid.
    3. For each medoid m
      1. For each non-medoid data point o
        1. Swap m and o and compute the total cost of the configuration

    4. Select the configuration with the lowest cost.
    Repeat steps 2 to 4 until there is no change in the medoid.
    """
    medoids = random.sample(data, k)
    medoids_changed = True
    while medoids_changed:
        medoids_changed = False
        clusters = assign_clusters(data, medoids)
        # Assign each data point to closest cluster
        print '=== Start Loop ==='
        while any([len(c)==0 for c in clusters.values()]):
            clusters = assign_clusters(data, medoids)
            # Replace empty cluster medoids
            for m, c in clusters.iteritems():
                if len(c)==0:
                    medoids.remove(m)
                    print "Removing", str(m), "since its cluster was empty"
                    new_m = random.sample(data, 1)
                    while str(new_m) in [str(x) for x in medoids]:
                        # Don't readd duplicate medoids
                        new_m = random.sample(data, 1)
                    medoids.append(new_m)
        for m,c in clusters.iteritems():
            print str(m), len(c)
        print '==== Finished Initial Cluster Assignment ===='
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
                print 'Old medoid was ', medoid, ', New', new_medoid
                print 'Old cost', current_cost,  ', New cost', costs[min_cost_i]
        medoids = clusters.keys()
        print '=== End Loop ===', medoids_changed
        print medoids
        return clusters
    
if __name__ == '__main__':
    with open('poker_cond2_1.pg.json', 'r') as f:
        data = json.load(f)

    df = pd.DataFrame(data['past_answers'])

    answers = df.answer_string.str.split('\t')

    trees = []
    part = 0
    for i, a in answers.iteritems():
        if df.scores[i][part] == '0':
            # Only consider incorrect answers
            try:
                n = ExpressionNode.from_string(a[part])
                trees.append(n)
            except webwork_parser.WebworkParseException:
                pass

    print len(trees), 'incorrect expressions parsed'
    clusters = k_medoids(trees, 10)
    json_clusters = {}
    for m, c in clusters.iteritems():
        json_clusters[str(m)] = c
    with open('k_medoid_clusters.json', 'w') as f:
        json.dump(json_clusters, f, default=ExpressionNode.to_json, indent=4)
    print cache_hits
    print cache_misses
