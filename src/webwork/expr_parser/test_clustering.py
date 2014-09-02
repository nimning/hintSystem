import webwork_parser
import pandas as pd
import json
from zss import simple_distance

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
    print "Parsing", a[part]
    if df.scores[i][part] == '0':
        # Only consider incorrect answers
        try:
            expr = webwork_parser.parse_webwork(a[part])
            n = TupleNode(expr)
            trees.append(n)
            print expr
            if len(trees) > 1:
                print n.edit_distance(trees[0])
            except webwork_parser.WebworkParseException:
                pass

print len(trees)
