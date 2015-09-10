#!/usr/bin/env python

import nltk
import threading
import webbrowser
import BaseHTTPServer
import SimpleHTTPServer
import simplejson as json
import os, sys
from scipy import stats
import numpy as np
from preprocess_text_file import preprocess_text_file
import sklearn.ensemble
import random
from pprint import pprint
import pickle
from webwork.cluster_exprs import preprocess_exprs
from webwork.preprocess_webwork_logs import WebWork
from sklearn.cluster import KMeans

FILE = 'client.html'
PORT = 9000 

def row_mode(matrix):
    ''' Get the mode of each row in the matrix, return a numpy array'''
    if len(matrix.shape) == 1: #It's a vector, not a matrix
        axis = None
    else:
        axis = 1
    return stats.mode(matrix, axis=axis)[0]

def uniformity(vector):
    ''' Returns the proportion of vector values equal to the mode '''
    n = float(vector.shape[0]) #vector has shape (n,), not (n,1)
    mode = row_mode(vector)
    return  (vector == mode).sum()/n

class ActiveLearner:
    def __init__(self,X,model):
        self.model = model
        self.X = X
        self.reset()

    def generate_new_batch(self,size=1):
        ''' Generate the next list of examples to be labelled 
            Returns None if every example has been labelled '''
        unlabelled_indices = np.nonzero(self.labels == -1)[0]
        if size > len(unlabelled_indices): #All examples have been labelled
            self.batch = []
            self.predicted_labels = []
            return None
        if self.batch is None:
            self.batch = random.sample(unlabelled_indices, size)
            self.predicted_labels = [0]*len(self.batch)
        else:
            estimator_predictions = np.zeros( shape=(self.X.shape[0], 
                len(self.model.estimators_)) )
            for j,estimator in enumerate(self.model.estimators_):
                estimator_predictions[:,j] = estimator.predict(self.X)
            print int(np.log(self.X.shape[0]))
            kmeans = KMeans(k=max(int(np.log(self.X.shape[0])), 2*size))
            kmeans.fit(estimator_predictions)
            centroids = kmeans.cluster_centers_
            for i,c in enumerate(estimator_predictions):
                sys.stdout.write('%40s '%examples[i])
                for e in c:
                    sys.stdout.write('%d '%e)
                print ''
            # Rank centroids by non-uniformity: we want labelled centroids with 
            # the least uniform predictions
            uncertain_centroids = sorted(centroids, 
                key=lambda c:-uniformity(c))[:size]
            self.batch = []
            for i,centroid in enumerate(uncertain_centroids):
                index, est = max( enumerate(estimator_predictions), 
                    key = lambda (i,e): (e == centroid).sum())
                self.batch.append(index)
        return self.batch

    def label_batch(self, labels):
        ''' Save human labels from the last batch of examples '''
        for index,label in zip(self.batch,labels):
            self.labels[index] = label
       
    def train_model(self):
        ''' Based on the labelling so far, update the model '''
        is_labelled = self.labels != -1
        self.model.fit(self.X[is_labelled,:], self.labels[is_labelled])

    def predict_all_examples(self):
        ''' Return the prediction of the current classifier on all examples '''
        return self.model.predict(X).tolist()

    def reset(self):
        ''' Reset human labels and model '''
        # A label of -1 indicates the example has not been labelled yet
        # Initially, no examples have been labelled
        self.labels = np.array([-1]*self.X.shape[0])
        self.batch = None
        

class TestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
 
    def do_POST(self):
        # Get client data
        length = int(self.headers.getheader('content-length'))        
        data_string = self.rfile.read(length)
        client_data = json.loads(data_string)
        if client_data == {}:
            # This is the clustering defined by the human labelling.  It does not
            #  include expressions labelled by the classifier
            predicted_labels = active_learner.predict_all_examples()
            cluster = [example for i,example in enumerate(examples)
                    if predicted_labels[i] == 1]
            print cluster
            active_learner.reset()
        if not active_learner.batch is None:
            active_learner.label_batch(client_data)
            active_learner.train_model()
         
        # Create response object
        active_learner.generate_new_batch(size=10)
        batch_examples = [examples[i] for i in active_learner.batch]
        response = [{'example':example,'label':label}
            for example,label in zip(batch_examples,active_learner.predicted_labels)]
        # Serialize and send response
        self.wfile.write(json.dumps(response))

def start_server():
    """Start the server."""
    server_address = ("", PORT)
    server = BaseHTTPServer.HTTPServer(server_address, TestHandler)
    server.serve_forever()

if __name__ == "__main__":
    ###  Load and preprocess examples ###
    # WebWork examples from some part
    webwork = pickle.load(open(os.path.join(sys.argv[1],'pickled_data'),'rb'))
    examples = [expr for _,_, expr in webwork.part_attempts[('Assignment3',1,0)] ]
    X = preprocess_exprs(examples)
    #
#    (examples, X) = preprocess_text_file(sys.argv[1])

    active_learner = ActiveLearner(X,sklearn.ensemble.RandomForestClassifier())
    print 'http://localhost:%s/%s' % (PORT, FILE)
    start_server()

