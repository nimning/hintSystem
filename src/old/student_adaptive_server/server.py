#!/usr/bin/env python

import yaml
import threading
import webbrowser
import BaseHTTPServer
import SimpleHTTPServer
import simplejson as json
import os, sys
from webwork.expr_parser.webwork_parser import parse_webwork,WebworkParseException
from webwork.cluster_exprs import preprocessor_parsing

''' The first command line argument gives a json file containing problem 
    and hint data to serve up.  '''

def preprocess_expr(expr):
    ''' Produce a set of features (tuples) from mathematical expressions '''
    feature_list = preprocessor_parsing(expr)
    if feature_list is None:
        return set([])
    else:
        return set(feature_list)

class TestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    _problem_data = None
    _student_session = None
    client_state = {}
        
    def problem_data(self):
        ''' Load the data from the json file, or return a cached version
            of this data if it hasn't yet been loaded '''
        if self._problem_data is None:
            with open(problem_data_filename,'r') as f:
                self._problem_data = json.load(f)
        return self._problem_data

    def student_session(self):
        if self._student_session is None:
            with open(student_session_path, 'r') as f:
                self._student_session = json.load(f)[student_session_id]
        return self._student_session
 
    def do_POST(self):
        # Get client data
        length = int(self.headers.getheader('content-length'))        
        data_string = self.rfile.read(length)
        client_data = json.loads(data_string)
        # Create response object
        self.student_session()
        self.wfile.write(json.dumps(self._student_session))

def start_server():
    """Start the server."""
    server_address = ("", PORT)
    server = BaseHTTPServer.HTTPServer(server_address, TestHandler)
    server.serve_forever()

if __name__ == "__main__":
    # Load the yaml config file
    with open('../config.yaml','r') as f:
        config = yaml.load(f)
    
    # Set path/port variables used by the server
    FILE = config['Server configuration']['html file to serve']
    PORT = config['Server configuration']['port']
    problem_data_filename = os.path.join(config['Data path'],
        config['WebWork problem json relative path'])
    student_session_path = os.path.join(config['Data path'],
        config['Student session data']['relative path'])
    student_session_id = config['Student session data']['session id']
   
    # Start the server 
    print 'http://localhost:%s/%s' % (PORT, FILE)
    start_server()

