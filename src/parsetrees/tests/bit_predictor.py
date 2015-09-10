#!/usr/bin/env python

import sys
from webwork.bit_predictor import BitPredictor
from webwork.preprocess_webwork_logs import WebWork
import unittest

class BasicUnitTests(unittest.TestCase):
    def setUp(self):
        self.predictor = BitPredictor(gamma=0.90)
 
    def test_online_predict_bits(self):
        bits = [True,False,True,True,False,True,False]
    
        prediction, accuracy = self.predictor.online_predict_bits(bits)
        assert(prediction == [True,True,False,True,True,True,True])
        assert(accuracy == 3.0/7)

    def test_online_predict_grouped_bits(self):
        bit_sequences = [ 
            [True,False,True], [False,False,False], [True,True]
        ]
        prediction, accuracy = self.predictor.online_predict_grouped_bits(bit_sequences)
        assert(prediction == [
            [True, True, False], [True, False, False], [True, True]
        ])
        assert(accuracy == 5.0/8)

if __name__ == '__main__':
    unittest.main()
    webwork = WebWork(sys.argv[1])
