import re
import logging
logger = logging.getLogger(__name__)
import json

def regex_match_filter(args, df, previous_hint_assignments, trigger_cond):
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
    if (len(df) > 1):
        previous_answer = df.iloc[-2].answer_string
        m = re.search(trigger_cond, previous_answer)
        if m:
            return True
    return False
