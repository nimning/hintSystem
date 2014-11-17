from process_query import conn
import pandas as pd
from webwork_config import webwork_dir
import re
from Eval_parsed import eval_parsed
import logging
logger = logging.getLogger(__name__)


def get_user_vars(course, set_id, problem_id):
    '''
    Gets user specific PG variables from the webwork database
    '''
    user_variables = conn.query('''SELECT * from {course}_user_variables
    WHERE set_id="{set_id}" AND problem_id = {problem_id};
    '''.format(course=course, set_id=set_id, problem_id=problem_id))
    variables_df = pd.DataFrame(user_variables)
    if len(variables_df) == 0:
        logger.warn("No user variables saved for assignment %s, please run the save_answers script", set_id)
    return variables_df


def vars_for_student(df, user_id):
    '''
    Selects the variables for a given user from a dataframe containing all users' variables
    '''
    try:
        user_vars = dict(df[df['user_id'] == user_id][['name', 'value']].
                         values.tolist())
        return user_vars
    except:
        return {}


def answer_for_student(df, user_id, answer_tree):
    '''
    Evaluates an answer parse tree for a specific user
    '''
    user_vars = vars_for_student(df, user_id)
    etree = eval_parsed(answer_tree, user_vars)
    return etree
