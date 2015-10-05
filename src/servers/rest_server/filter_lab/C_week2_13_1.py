'''
For 2014, week2, problem 13, part 1.
Give hints based on students' attempts
'''
from FindMatchingSubexpressions import find_matches 
import T_week2_13_1

def C_week2_13_1(answer, attempt):
    print 'attempt', attempt
    final_pairs=find_matches(answer,attempt)
    
    #default hint
    hint = T_week2_13_1.T_week2_13_1()
    
    #if nothing mathches, hint is set to the default hint
    if len(final_pairs) == 0:
        print "nothing mathches"
        hint = T_week2_13_1.T_week2_13_1()
    # Something is matched
    else:
        matchDict = {};
        for node,value,ans_piece,attempt_piece in final_pairs:
            matchDict[node] = [value, ans_piece, attempt_piece]
        
        #if the final value, 2^n which corresponds to the root node, is correct 
        if 'R' in matchDict:
            ansPiece = matchDict['R'][1]
            attPiece = matchDict['R'][2]
            
            #if expresssion is not equal, give the correct expression
            if ansPiece != attPiece:
                hint = 'Your answer {0} is correct, it could also be written as {1}'(attPiece, ansPiece)
            # get everything correct
            else:
                hint = 'You get all correct! Great job!'
        else:
            # only have 2
            if 'R.0' in matchDict:
                attPiece = matchDict['R.0'][2]
                hint = 'Your subexpression {0} is correct, however it is just the size of outcome space for flipping one coin'
        
    return hint;