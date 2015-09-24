def classify_final_value(attempt_flat,answer_flat):
    """ Written by Yoav Freund, Sat Sep 19 17:09:48 PDT 2015
    classifies the final value as: correct,parse_error,int, not_int
    """
    
    att_final_value=attempt_flat[0]['val']
    ans_final_value=answer_flat[0]['val']
    
    if att_final_value==ans_final_value:
        return 'correct'
    if isinf(att_final_value):
        return "inf"
    if int(att_final_value)!=att_final_value:
        return "not int"
    else:
        return "int"