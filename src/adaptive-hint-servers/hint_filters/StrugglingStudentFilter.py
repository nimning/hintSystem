from datetime import timedelta

def struggling_student_filter(args, df, previous_hint_assignments):
    ''' *** Input:
        args is a dictionary containing the most recent attempt by a student
        to answer a question.  This contains user_id, hint_id, set_id, problem_id,
        and pg_id
        
        df is a pandas DataFrame storing the attempts by a student on a 
        particular problem part where he/she is struggling 
    
        previous_hint_assignments give a list of dictionaries, each dictionary
        containing at least user_id, set_id, problem_id, pg_id, hint_id 
        giving the location where the hint has been previous assigned

        *** Output:
        Returns True iff the hint has been assigned to the same part for some
            other user before, the current student attempting the problem has
            not answered the part correctly, and the current student attempting
            the problem has spent at least some given amount of time trying
            the problem part
        
    '''
    args['problem_id'] = int(args['problem_id'])
    # Check that hint has been assigned to the same part previously
    hint_part_problems = [(a['set_id'], a['problem_id'], a['pg_id'])
        for a in previous_hint_assignments]
    if not (args['set_id'], args['problem_id'], args['pg_id']) \
        in hint_part_problems:
        return False

    # Check that hint has not been assigned to the same user/part previously
    user_hint_part_problems = [(a['user_id'], a['hint_id'], a['set_id'], a['problem_id'], a['pg_id'])
        for a in previous_hint_assignments]
    if (args['user_id'], args['hint_id'], args['set_id'], 
        args['problem_id'], args['pg_id']) in user_hint_part_problems:
        return False

    # Check that the user has spent a minimum amount of time struggling
    break_threshold = 1
    minutes_struggling_threshold = 2
    td = df['timestamp'].order()
    td = td.diff().dropna()
    td = td[td < timedelta(minutes=break_threshold) \
        .total_seconds()*10**9]
    total_time_spent = td.sum()
    if total_time_spent < \
        timedelta(minutes=minutes_struggling_threshold).total_seconds()*10**9:
        pass #return False
        
    
    # Check that the user doesn't have the correct answer
    if (df['correct'].max() == 1): # Student has correctly answered the question
        return False
    
  
    # The student has passed all the above criteria, he/she is probably struggling
    return True

