import sys
import nltk
import numpy as np

def preprocess_text_file(filename):
    '''Given a text file with filename 'filename', preprocess it into a 
       bag-of-words matrix of counts X.  Only words that appear at least
       5 times in the corpus are counted.  
       
       Returns: (lines of the file, bag-of-words model)
       '''    
    with open(filename,'r') as f:
        lines = f.readlines()
    vocab_dist = nltk.FreqDist( 
        (word for line in lines for word in line.split()) )
    vocab_list = [word 
        for word,count in dict(vocab_dist).iteritems() if count > 5]
    vocab_list = sorted(vocab_list)
    vocab_hash = dict((s,i) for i,s in enumerate(vocab_list) )
    X = np.zeros( shape=(len(lines),len(vocab_list)) )
    for i,line in enumerate(lines):
        for word in line.split():
            if word in vocab_hash:
                X[i,vocab_hash[word]] += 1
    return lines, X

if __name__ == '__main__':            
    (lines, X) = preprocess_text_file(sys.argv[1])
