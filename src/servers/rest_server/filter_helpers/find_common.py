def find_range(item,flat_tree):
    for entry in flat_tree:
        if item==entry['val']:
            return entry['location']
    return None
    
def find_common(attempt,att_flat,answer,ans_flat):
    "Find sub-expressions common to the attempt and the answer"

    att_set=[x['val'] for x in att_flat if x.has_key('val')]
    answer_set=[x['val'] for x in ans_flat if x.has_key('val')]

    intersection=[x for x in set(att_set) & set(answer_set) if (int(x)!=x) or x>100]
    
    if len(intersection)==0:
        return None
 
    print 'common subexpressions=',str(intersection)
    #print 'attempt=%s, att_eval_tree=%s\n variables=%s,answer=%s,answer_eval_tree=%s'\
    #    %(attempt,str(att_eval_tree),str(variables),answer,str(answer_eval_tree))

    for item in intersection:
        att_range=find_range(item,att_flat)
        ans_range=find_range(item,ans_flat)
        print "attempt subexpression %s is equivalent to answer subexpression %s"\
        %(attempt[att_range[0]:att_range[1]+2],answer[ans_range[0]:ans_range[1]+2])
 
        