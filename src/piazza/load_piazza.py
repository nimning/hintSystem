import datetime
import json
import sys, os
import nltk
import matplotlib.pyplot as pl
from collections import defaultdict

difficult_part = (5,2,6)

def process_timestamp(timestamp_str):
    '''Given a timestamp string of the form 2012-09-13T05:17:40Z, convert
           to a unix timestamp

    '''
    timestamp = datetime.datetime.strptime(timestamp_str,'%Y-%m-%dT%H:%M:%SZ')
    return int(timestamp.strftime('%s'))

def piazza_tokenize(text):
    '''Tokenize using a standard english word tokenizer, but split "words" of
       the form XYZ123 into XYZ 123.  Eg: Assignment1 => Assignment 1
       '''
    #First Step: standard tokenizer
    words1 = nltk.word_tokenize(text)
    # Second step: split XXX123 => XYZ 123
    words2 = []
    for word in words1:
        word.replace('#','')
        for i,c in enumerate(word):
            if not c.isalpha():
                break
        if i == len(word) - 1: #Word is all A-Za-z
            words2.append(word.lower())
        else:
            words2.append(word[:i].lower())
            # Remote '#' symbol
            words2.append(word[i:].lower())
    return words2

def int_or_none(s):
    try:
        return int(s)
    except ValueError:
        return None

if __name__ == '__main__':
    # A list of piazza posts
    with open(os.path.join(sys.argv[1],'class_content.json'),'r') as f:
        posts = json.load(f)
  
    # A list of words that indicate which assignment/part we're talking about
    with open(os.path.join(sys.argv[1],'assignment_part_words.txt'),'r') as f:
        assignment_words = set([line.strip() for line in f.readlines()])
     
    # Dictionary of content keyed by time created 
    all_content = {}
    for post in posts:
        for main_revision in post['history']:
            time = process_timestamp(main_revision['created'])
            content = main_revision['content']
            all_content[time] = content
        
        for child_post in post['children']:
            if 'history' in child_post:
                for child_revision in child_post['history']:
                    time = process_timestamp(child_revision['created'])
                    content = child_revision['content']
                    all_content[time] = content

    pset_words = set(['assignment','hw','homework'])
    problem_words = set(['question', 'number', 'problem'])
    part_words = set(['parts','part'])
    part_times = {}
    assignment_content = []
    for time,content in all_content.iteritems():
        pset = None
        problem = None
        part = None
        words = piazza_tokenize(content)
        for i,word in enumerate(words):
            # The word contains a digit, preceded by "assignment", "part", etc
            if i > 0 and all(map(lambda c:c.isdigit(), word)) \
                and words[i-1] in assignment_words:
                if words[i-1] in pset_words:
                    pset = int_or_none(word)
                elif words[i-1] in problem_words:
                    problem = int_or_none(word)
                elif words[i-1] in part_words:
                    part = int_or_none(word)
        t = (time%10000000)/10000
        if problem == difficult_part[1] and t > 925 and t < 950:
            print content
#        part_times[time] = (pset,problem,part)

#    hard_parts = sorted([((time%10000000)/10000, s,q,p,) for time,(s,q,p) in part_times.iteritems() if not q is None])
#    for time_part in hard_parts:
#        print time_part


    # Get a list of words that may indicate we're talking about an assignment  
#    assignment_words = []
#    for content in all_content.values():
#        words = piazza_tokenize(content)
#        for i,word in enumerate(words):
#            if i < len(words)-1 and \
#                any(map(lambda c:c.isdigit(), words[i+1])):
#                    assignment_words.append(word)
#
#    word_dist = nltk.FreqDist( [word for content in all_content.values() 
#        for word in piazza_tokenize(content)] )
 
