#!/usr/bin/env python

import sys
from preprocess_webwork_logs import WebWork

class BitPredictor:
   
 
    def __init__(self, gamma=0.95):
        self.gamma = gamma


    def online_predict_bits(self,bits):
        ''' Given a list of true/false values
            
                [T,F,T,...]
    
            Make online predictions of the next bit
            Return the predicted list, and accuracy'''
        prediction = []
        true_so_far = 0
        false_so_far = 0
        for i,bit in enumerate(bits):
            true_so_far = self.gamma*true_so_far
            false_so_far = self.gamma*false_so_far
            prediction.append(true_so_far >= false_so_far)
            true_so_far += bit
            false_so_far += 1 - bit
        n_correct_predictions = sum( (bit==prediction) 
            for (bit,prediction) in zip(bits,prediction) )
        prediction_accuracy = n_correct_predictions/float(len(bits))
    
        return (prediction, prediction_accuracy)
    
    def online_predict_grouped_bits(self,bit_sequences):
        ''' Given groups of bit sequences B1,B2,...,
            make online predictions and compute accuracy for each sequence.  
            Then return overall accuracy: weighted by the lengths of the sequences
            '''
        n_total_bits = sum(len(bits) for bits in bit_sequences)
        overall_accuracy = 0
        sequence_predictions = []
        for bits in bit_sequences:
            (prediction, accuracy) = self.online_predict_bits(bits)
            overall_accuracy += len(bits)*accuracy
            sequence_predictions.append(prediction)
        overall_accuracy = overall_accuracy/n_total_bits
        return sequence_predictions, overall_accuracy
       
     
if __name__ == '__main__':
    webwork = WebWork(sys.argv[1])
    attempts_correctness = webwork.get_correctness_sequence(webwork.all_attempts)
    predictor = BitPredictor()
    (_,baseline_accuracy) = predictor.online_predict_bits(attempts_correctness)
    _, part_accuracy = predictor.online_predict_grouped_bits(
        map(webwork.get_correctness_sequence,webwork.part_attempts.values()) )
    _, user_accuracy = predictor.online_predict_grouped_bits(
        map(webwork.get_correctness_sequence,webwork.user_attempts.values()) )
    all_true_accuracy = sum(c for c in attempts_correctness) \
        /float(len(attempts_correctness))
    print 'Correctness prediction accuracy:'
    print 'All True: %0.3f'%all_true_accuracy
    print 'Online bit predictor        : %0.3f'%baseline_accuracy
    print 'Segmenting by question parts: %0.3f'%part_accuracy
    print 'Segmenting by users         : %0.3f'%user_accuracy
