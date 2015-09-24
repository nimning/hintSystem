file=open('CSE103_Fall14_Week2_problem13_part4.txt','r');
ID=file.readline()
answer=file.readline()
print 'answer=',answer
count =0
for line in file.readlines():
    count+=1
    if count>10: break
    params=json.loads(line);
    attempt,att_parse_tree,att_eval_tree,answer,answer_parse_tree,answer_eval_tree,variables = params
    #print 'answer before substitution',answer
    answer=substit(answer,variables)
    #print 'answer after substitution',answer
    attempt_flat=flatten(att_eval_tree)
    answer_flat =flatten(answer_eval_tree)
    #print attempt_flat
    #print answer_flat
    if attempt_flat==None or answer_flat==None:
        print 'Eval tree== None or parsing error ------------------------------'
        print str(params)
        break

    Class=classify_final_value(attempt_flat,answer_flat)
    if Class=='correct' or Class=='int':
        #print Class
        continue

    print "attempt={:<40} answer={:<40}".format(attempt,answer)
    hint= find_common(attempt,attempt_flat,answer,answer_flat)
    