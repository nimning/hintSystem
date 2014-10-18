"""Webwork Answer Parsing API"""
import os.path
from process_query import ProcessQuery, conn
from webwork_config import webwork_dir
from tornado.template import Template
from convert_timestamp import utc_to_system_timestamp
from json_request_handler import JSONRequestHandler
import tornado.web
import json
from datetime import datetime
from webwork_parser import parse_webwork
from Eval_parsed import eval_parsed, Collect_numbers, numbers_and_exps
from webwork import serialize_datetime
from collections import defaultdict
import pandas as pd
import requests
import re

import logging
logger = logging.getLogger(__name__)

def parsed(string):
    expr = parse_webwork(string)
    if expr:
        try:
            etree = eval_parsed(expr)
            nums = Collect_numbers(etree)
            return etree, nums
        except:
            return (None, None)
    else:
        return (None, None)

def part_id_to_box(part_id):
    return "AnSwEr{part:04d}".format(part=int(part_id))

def separate_nums(correct_etree, answer_etree):
    if not correct_etree or not answer_etree:
        return (None,None,None)
    correct_nums = frozenset(correct_etree.keys())
    answer_nums = frozenset(answer_etree.keys())
    return (correct_nums & answer_nums,
            answer_nums - correct_nums)


def get_correct_answers(course, set_id, problem_id, seed):
    base_url = 'http://webwork.cse.ucsd.edu:4351/{0}'
    pg_path = requests.get(base_url.format('pg_path'),
                 params={'course':course, 'set_id':set_id, 'problem_id':problem_id}).json()
    check_answer = requests.post(base_url.format('checkanswer'),
                                 {'pg_file':pg_path, 'seed':seed, 'AnSwEr1':'0'}).json()
    logger.debug(check_answer)
    return {k: v['correct_value'] for k, v in check_answer.iteritems()}

# POST /parse_string?
class ParseString(JSONRequestHandler, tornado.web.RequestHandler):
    def post(self):
        '''
            Parses an expression and returns the parsed data structure.

            Sample arguments:
            expression="1+1"

            Response:
                [['+', [0,2]], 1, 1]
            '''
        expression = self.get_argument('expression')
        etree = parse_webwork(expression)
        if etree:
            self.write(json.dumps(etree))
        else:
            logger.error("Failed to parse expression '%s'", expression)
            self.set_status(400)
            self.write(json.dumps({'error': 'Error parsing expression %s' % expression}))

# GET /grouped_part_answers?
class GroupedPartAnswers(JSONRequestHandler, tornado.web.RequestHandler):
    def vars_for_student(self, user_id):
        user_vars = dict(self.variables_df[self.variables_df['user_id']==user_id][['name', 'value']].values.tolist())
        return user_vars

    def answer_for_student(self, user_id):
        user_vars = self.vars_for_student(user_id)
        key = frozenset(user_vars.iteritems())
        answer = self.answer_exps.get(key)
        if answer:
            return answer
        else:
            etree = eval_parsed(self.answer_tree, user_vars)
            exps = numbers_and_exps(etree, self.part_answer)
            self.answer_exps[key] = exps
            return exps

    def parse_student_answers(self):
        pass

    def correct_terms(self, nums, answer):
        # answer is a mapping of numbers to expressions
        correct_exps = []
        for k in nums:
            if answer.get(k): # Number from student's appears in answer
                correct_exps.append(answer[k])
        return correct_exps

    def get(self):
        '''
            Parses all expressions for a given question

            Sample arguments:
            course='CSE103_Fall14',
            set_id='Week1',
            problem_id=1,
            part_id=1

            Response:
                ...
            '''
        # Get correct answers
        self.answer_exps = {}
        course = self.get_argument('course')
        set_id = self.get_argument('set_id')
        problem_id = self.get_argument('problem_id')
        part_id = int(self.get_argument('part_id'))

        source_file = conn.query('''
            select source_file from {course}_problem
            where
                problem_id={problem_id} and
                set_id="{set_id}";
        '''.format(course=course, set_id=set_id, problem_id=problem_id))[0]['source_file']

        pg_path = os.path.join(webwork_dir, 'courses', course, 'templates', source_file)
        with open(pg_path, 'r') as fin:
            pg_file = fin.read()
        # name  problem_id set_id   user_id  value
        user_variables = conn.query('''SELECT * from {course}_user_variables
        WHERE set_id="{set_id}" AND problem_id = {problem_id};
        '''.format(course=course, set_id=set_id, problem_id=problem_id))
        self.variables_df = pd.DataFrame(user_variables)
        answer_re = re.compile('\[__+\]{(?:Compute\(")?(.+)(?:"\))?}')
        answer_boxes = answer_re.findall(pg_file)
        self.part_answer = answer_boxes[part_id-1]
        self.answer_tree = parse_webwork(self.part_answer)

        # correct_answers = get_correct_answers(course, set_id, problem_id, 1) # last arg is random seed
        # _, correct_nums = parsed(correct_answers[part_id_to_box(part_id)])

        # Get attempts by part
        query = '''SELECT * from {course}_answers_by_part
        WHERE set_id="{set_id}" AND problem_id = {problem_id}
        AND part_id={part_id};
        '''.format(course=course, set_id=set_id, problem_id=problem_id,
                   part_id=part_id)

        answers = conn.query(query)
        all_correct_terms = set()
        correct_terms_map = defaultdict(lambda: defaultdict(list))
        incorrect_terms_map = defaultdict(lambda: defaultdict(list))
        # Parse and evaluate all answers
        for a in answers:
            # {'user_id': u'acpatel', 'timestamp': datetime.datetime(2014, 10, 12, 2, 10, 19), 'id': 284488L, 'score': u'1', 'answer_string': u'C(55,6)', 'part_id': 2L, 'problem_id': 10L, 'set_id': u'Week2', 'answer_id': 199326L}
            user_id = a['user_id']
            ans = self.answer_for_student(user_id)

            if a['score'] != '1':
                etree, nums = parsed(a['answer_string'])
                if etree and nums:
                    correct_terms = self.correct_terms(nums, ans)
                    all_correct_terms |= set(correct_terms)
                    # logger.debug(set(correct_terms))
                    # correct,incorrect = separate_nums(correct_nums, nums)
                    correct_terms_map[str(sorted(correct_terms))][a['answer_string']].append(a['user_id'])
                    # incorrect_terms_map[str(sorted(incorrect))][a['answer_string']].append(a['user_id'])

        out = {}
        out['correct'] = correct_terms_map
        out['correct_terms'] = sorted(all_correct_terms)
        out['incorrect'] = incorrect_terms_map
        out['answer_tree'] = str(self.answer_tree)
        self.write(json.dumps(out, default=serialize_datetime))
