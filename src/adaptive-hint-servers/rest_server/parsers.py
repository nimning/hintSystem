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
from Eval_parsed import eval_parsed, Collect_numbers
from webwork import serialize_datetime
from collections import defaultdict
import requests
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
            answer_nums - correct_nums,
            correct_nums - answer_nums)


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
        course = self.get_argument('course')
        set_id = self.get_argument('set_id')
        problem_id = self.get_argument('problem_id')
        part_id = self.get_argument('part_id')

        correct_answers = get_correct_answers(course, set_id, problem_id, 1) # last arg is random seed
        _, correct_nums = parsed(correct_answers[part_id_to_box(part_id)])

        # Get attempts by part
        query = '''SELECT * from {course}_answers_by_part
        WHERE set_id="{set_id}" AND problem_id = {problem_id}
        AND part_id={part_id};
        '''.format(course=course, set_id=set_id, problem_id=problem_id,
                   part_id=part_id)

        answers = conn.query(query)

        correct_terms_map = defaultdict(lambda: defaultdict(list))
        incorrect_terms_map = defaultdict(lambda: defaultdict(list))
        missing_terms_map = defaultdict(lambda: defaultdict(list))
        # Parse and evaluate all answers
        for a in answers:
            if a['score'] != 1:
                etree, nums = parsed(a['answer_string'])
                if etree and nums:
                    correct,incorrect,missing = separate_nums(correct_nums, nums)
                    correct_terms_map[str(sorted(correct))][a['answer_string']].append(a['user_id'])
                    incorrect_terms_map[str(sorted(incorrect))][a['answer_string']].append(a['user_id'])
                    missing_terms_map[str(sorted(missing))][a['answer_string']].append(a['user_id'])
        out = {}
        out['correct'] = correct_terms_map
        out['incorrect'] = incorrect_terms_map
        out['missing'] = missing_terms_map
        # parsed_answers = [parsed(a['answer_string']) for a in answers]
        self.write(json.dumps(out, default=serialize_datetime))
