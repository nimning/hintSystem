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
from auth import require_auth
from multiprocessing import Process, Pipe, Queue, current_process
from StringIO import StringIO

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

def parse_eval(string):
    expr = parse_webwork(string)
    if expr:
        try:
            etree = eval_parsed(expr)
            return expr, etree
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
        try:
            user_vars = dict(self.variables_df[self.variables_df['user_id']==user_id][['name', 'value']].values.tolist())
            return user_vars
        except:
            return {}

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
            include_finished=0
            Response:
                ...
            '''
        # Get correct answers
        self.answer_exps = {}
        course = self.get_argument('course')
        set_id = self.get_argument('set_id')
        problem_id = self.get_argument('problem_id')
        part_id = int(self.get_argument('part_id'))
        include_finished = (int(self.get_argument('include_finished', 1)) == 1)

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
        if len(self.variables_df) == 0:
            logger.warn("No user variables saved for assignment %s, please run the save_answers script", set_id)
            # raise tornado.web.HTTPError(500)
        answer_re = re.compile('\[__+\]{(?:Compute\(")?(.+?)(?:"\))?}')
        answer_boxes = answer_re.findall(pg_file)
        self.part_answer = answer_boxes[part_id-1]
        self.answer_tree = parse_webwork(self.part_answer)

        # Get attempts by part
        if include_finished:
            query = '''SELECT * from {course}_answers_by_part
            WHERE set_id="{set_id}" AND problem_id = {problem_id}
            AND part_id={part_id};
            '''.format(course=course, set_id=set_id, problem_id=problem_id,
                       part_id=part_id)
        else:
            # This self join query idea comes from http://stackoverflow.com/a/4519302/90551
            # You can do this more clearly with subqueries but it's super slow
            query = '''SELECT abp.* FROM {course}_answers_by_part as abp
            LEFT JOIN {course}_answers_by_part AS abp2
            ON abp.problem_id = abp2.problem_id AND abp.set_id = abp2.set_id
            AND abp.part_id = abp2.part_id AND abp.user_id = abp2.user_id AND abp2.score = '1'
            WHERE abp.set_id='{set_id}' AND abp.problem_id={problem_id}
            AND abp.part_id={part_id} AND abp2.user_id IS NULL;
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
                    if a['user_id'] not in correct_terms_map[str(sorted(correct_terms))][a['answer_string']]:
                        correct_terms_map[str(sorted(correct_terms))][a['answer_string']].append(a['user_id'])

        out = {}
        out['correct'] = correct_terms_map
        out['correct_terms'] = sorted(all_correct_terms)
        out['incorrect'] = incorrect_terms_map
        out['answer_tree'] = str(self.answer_tree)
        self.write(json.dumps(out, default=serialize_datetime))

def filtered_answers(answers, correct_string, correct_tree,
                     user_vars, filter_function_string, pipe, queue):
    import os
    import sys
    import StringIO
    import tempfile
    USER_ID=1009

    tempdir = tempfile.mkdtemp()
    os.chown(tempdir, USER_ID, -1)
    os.chroot(tempdir)
    os.setuid(USER_ID)

    class QueueStringIO(StringIO.StringIO):
        def __init__(self, queue, *args, **kwargs):
            StringIO.StringIO.__init__(self, *args, **kwargs)
            self.queue = queue
        def flush(self):
            self.queue.put(self.getvalue())
            self.truncate(0)

    selected_answers = []
    out = QueueStringIO(queue)
    sys.stderr = sys.stdout = out

    t1 = set(locals().keys()) | set(['t1'])
    try:
        exec filter_function_string in globals(), locals()
        t2 = set(locals().keys())
        logger.debug("New locals: %s", t2-t1)
        for thing in (t2-t1):
            logger.debug(locals()[thing])
        for a in answers:
            user_id = a['user_id']
            student_vars = dict(user_vars[user_vars['user_id']==user_id].values.tolist())
            # This function must be defined by the exec'd code
            ret = answer_filter(a['string'], a['parsed'], a['evaled'], correct_string, correct_tree, a['correct_eval'], student_vars)
            if ret:
                selected_answers.append({'user_id': user_id, 'answer_string': a['string']})
    except Exception, e:
        logger.error("Error in filter function: %s", e)
        print e
    pipe.send(selected_answers)
    out.flush()
    return

def get_source(course, set_id, problem_id):
    source_file = conn.query('''select source_file from {course}_problem
            where problem_id={problem_id} and set_id="{set_id}";
        '''.format(course=course, set_id=set_id, problem_id=problem_id))[0]['source_file']
    pg_path = os.path.join(webwork_dir, 'courses', course, 'templates', source_file)
    with open(pg_path, 'r') as fin:
        pg_file = fin.read()
        return pg_file
    
# GET /filter_answers?
class FilterAnswers(JSONRequestHandler, tornado.web.RequestHandler):
    def vars_for_student(self, user_id):
        try:
            user_vars = dict(self.variables_df[self.variables_df['user_id']==user_id][['name', 'value']].values.tolist())
            return user_vars
        except:
            return {}

    def answer_for_student(self, user_id):
        user_vars = self.vars_for_student(user_id)
        key = frozenset(user_vars.iteritems())
        answer = self.answer_exps.get(key)
        if answer:
            return answer
        else:
            etree = eval_parsed(self.answer_tree, user_vars)
            self.answer_exps[key] = etree
            return etree

    @require_auth()
    def post(self):
        self.answer_exps = {}
        course = self.get_argument('course')
        set_id = self.get_argument('set_id')
        problem_id = int(self.get_argument('problem_id'))
        part_id = int(self.get_argument('part_id'))
        include_finished = (int(self.get_argument('include_finished', 1)) == 1)
        filter_function = self.get_argument('filter_function')

        pg_file = get_source(course, set_id, problem_id)
        # name  problem_id set_id   user_id  value
        user_variables = conn.query('''SELECT * from {course}_user_variables
        WHERE set_id="{set_id}" AND problem_id = {problem_id};
        '''.format(course=course, set_id=set_id, problem_id=problem_id))
        self.variables_df = pd.DataFrame(user_variables)
        if len(self.variables_df) == 0:
            logger.warn("No user variables saved for assignment %s, please run the save_answers script", set_id)
        # Matches answers with Compute() and without in separate groups
        # TODO Make this a utility function
        answer_re = re.compile('\[__+\]{(?:(?:Compute\(")(.+?)(?:"\))(?:.*)|(.+?))}')
        answer_boxes = answer_re.findall(pg_file)
        self.part_answer = answer_boxes[part_id-1][0] or answer_boxes[part_id-1][1]

        self.answer_tree = parse_webwork(self.part_answer)

        # Get attempts by part
        if include_finished:
            query = '''SELECT * from {course}_answers_by_part
            WHERE set_id="{set_id}" AND problem_id = {problem_id}
            AND part_id={part_id};
            '''.format(course=course, set_id=set_id, problem_id=problem_id,
                       part_id=part_id)
        else:
            # This self join query idea comes from http://stackoverflow.com/a/4519302/90551
            # You can do this more clearly with subqueries but it's super slow
            query = '''SELECT abp.* FROM {course}_answers_by_part as abp
            LEFT JOIN {course}_answers_by_part AS abp2
            ON abp.problem_id = abp2.problem_id AND abp.set_id = abp2.set_id
            AND abp.part_id = abp2.part_id AND abp.user_id = abp2.user_id AND abp2.score = '1'
            WHERE abp.set_id='{set_id}' AND abp.problem_id={problem_id}
            AND abp.part_id={part_id} AND abp2.user_id IS NULL;
            '''.format(course=course, set_id=set_id, problem_id=problem_id,
                       part_id=part_id)
        answers = conn.query(query)

        student_answers = []

        for a in answers:
            # {'user_id': u'acpatel', 'timestamp': datetime.datetime(2014, 10, 12, 2, 10, 19), 'id': 284488L, 'score': u'1', 'answer_string': u'C(55,6)', 'part_id': 2L, 'problem_id': 10L, 'set_id': u'Week2', 'answer_id': 199326L}
            user_id = a['user_id']
            ans = self.answer_for_student(user_id)

            ptree, etree = parse_eval(a['answer_string'])
            if ptree and etree:
                student_answers.append({'string': a['answer_string'], 'parsed': ptree, 'evaled': etree, 'user_id': user_id, 'correct_eval': ans})

        parent, child = Pipe()
        queue = Queue()
        p = Process(target=filtered_answers, args=(student_answers, self.part_answer, self.answer_tree, self.variables_df, filter_function, child, queue))
        p.start()
        p.join(timeout=5)

        logger.debug('Done waiting')
        if p.is_alive():
            logger.warn("Function took too long, we killed it.")
            p.terminate()
        matches = parent.recv()

        if not queue.empty():
            output = queue.get()
        else:
            output=""
        out = {
            'output': output,
            'matches': matches
        }
        self.write(json.dumps(out))
