#!/usr/bin/env python

from webwork_parser import parse_webwork
from Eval_parsed import eval_parsed, Collect_numbers, parse_and_collect_numbers
from datetime import timedelta
import re
import logging
logger = logging.getLogger(__name__)

def expression_value_filter(args, df, previous_hint_assignments, trigger_cond):
    ''' *** Input:
        args is a dictionary containing the most recent attempt by a student
        to answer a question.  This contains user_id, hint_id, set_id, problem_id,
        and pg_id

        df is a pandas DataFrame storing the attempts by a student on a
        particular problem part where he/she is struggling

        previous_hint_assignments give a list of dictionaries, each dictionary
        containing at least user_id, set_id, problem_id, pg_id, hint_id
        giving the location where the hint has been previous assigned

        trigger_cond is a string in the form "HAS ____ & HAS ____ & MISSING ____"
        where the blanks represent mathematical expressions that are present or
        absent from the student's answer.

        *** Output:
        Returns True iff the
    '''
    user_id = args['user_id']
    # TODO: Check the part where the hint is supposed to be assigned
    # Don't reassign the same hint to the same user
    if any([x['user_id'] == user_id for x in previous_hint_assignments]):
        return False

    last_answer_string = df.iloc[-1].answer_string
    answer_numbers = parse_and_collect_numbers(last_answer_string)

    conditions = [s.strip() for s in trigger_cond.split("&")]
    for c in conditions:
        cond_type, exp = re.split('\s+', c, 1)
        parse_tree = parse_webwork(exp)
        eval_tree = eval_parsed(parse_tree)
        logger.debug(eval_tree)
        if type(eval_tree[0]) == tuple:
            result = eval_tree[0][1]
        else:
            result = eval_tree[0]
        if cond_type == 'HAS':
            if result not in answer_numbers:
                return False
        elif cond_type == 'MISSING':
            if result in answer_numbers:
                return False
    return True
