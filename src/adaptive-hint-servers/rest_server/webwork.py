"""Webwork DB API"""
import os.path
from process_query import ProcessQuery, conn
from webwork_config import webwork_dir
from tornado.template import Template
from convert_timestamp import utc_to_system_timestamp
from json_request_handler import JSONRequestHandler
import tornado.web
import json
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial

# GET /problem_seed?
class ProblemSeed(ProcessQuery):
    def get(self):
        ''' 
            To render problems, we need to get the seed from that problem.  

            Sample arguments:
            course="CompoundProblems", 
            set_id="compoundProblemExperiments",
            problem_id=2
            user_id="melkherj"

            Response: 
                2225
            '''
        query_template = '''
            select problem_seed from {{course}}_problem_user 
            where 
                problem_id={{problem_id}} and 
                user_id="{{user_id}}" and 
                set_id="{{set_id}}";
        '''
        self.process_query(query_template,
            dehydrate=lambda rows: rows[0]["problem_seed"])


# GET /pg_path?
class ProblemPGPath(ProcessQuery):
    def get(self):
        ''' 
            Get the path to the PG file of a given problem
            
            Sample arguments:
            course="CompoundProblems", 
            set_id="compoundProblemExperiments",
            problem_id=2

            Response: 
             "/opt/webwork/courses/demo/.../setCounting/counting1.pg"
             
            '''
        # extract course from the arguments
        course_name = self.get_argument('course')

        query_template = '''
            select source_file from {{course}}_problem 
            where 
                problem_id={{problem_id}} and 
                set_id="{{set_id}}";
        '''

        def _dump_pg_path(mysql_rows):
            if len(mysql_rows) > 0:
                return os.path.join(webwork_dir,
                                    'courses',
                                    course_name,
                                    'templates',
                                    mysql_rows[0]["source_file"])
            else:
                return ''
            
        self.process_query(query_template, dehydrate=_dump_pg_path)


# GET /pg_file?
class ProblemPGFile(ProcessQuery):
    def initialize(self):
        # Allows X-site requests
        self.set_header("Access-Control-Allow-Origin", "*")

    def get(self):
        ''' 
            Get the content of the PG file of a given problem
            
            Sample arguments:
            course="CompoundProblems", 
            set_id="compoundProblemExperiments",
            problem_id=2

            Response: 
             "DOCUMENT();\n ... ENDDOCUMENT();\n\n"
             
            '''

        def _dump_pg_file(mysql_rows):
            if len(mysql_rows) > 0:
                pg_path = os.path.join(webwork_dir,
                                       'courses',
                                       course_name,
                                       'templates',
                                       mysql_rows[0]["source_file"])
                with open(pg_path, 'r') as fin:
                    return fin.read()
            else:
                return ''
        

        # extract course from the arguments
        course_name = self.get_argument('course')

        query_template = '''
            select source_file from {{course}}_problem 
            where 
                problem_id={{problem_id}} and 
                set_id="{{set_id}}";
        '''
        self.process_query(query_template, dehydrate=_dump_pg_file)

# GET /realtime_user_problem_answers?
class RealtimeUserProblemAnswers(ProcessQuery):
    def serialize_timestamp(self, rows):
        for row in rows:
            # From utc to local system time
            row['timestamp'] = utc_to_system_timestamp(row['timestamp'])
        return rows

    def get(self):
        ''' For showing the instructor student attempts at a problem, in 
                realtime

            Sample arguments:
            course="CompoundProblems",
            user_id="melkherj", 
            set_id="compoundProblemExperiments",
            problem_id=1

            Returning: 
                [{"scores": "11", "answer_string": "1\t2\t", "answer_id": 5}]
       '''

        query_template = '''
            select 
                {{course}}_realtime_past_answer.id,
                {{course}}_realtime_past_answer.pg_id,
                {{course}}_realtime_past_answer.source_file,
                {{course}}_realtime_past_answer.correct,
                {{course}}_realtime_past_answer.answer_string,
                {{course}}_realtime_past_answer.timestamp
            from {{course}}_realtime_past_answer
            where 
                {{course}}_realtime_past_answer.set_id="{{set_id}}"        AND
                {{course}}_realtime_past_answer.problem_id={{problem_id}}  AND
                {{course}}_realtime_past_answer.user_id="{{user_id}}"
        '''
        self.process_query(query_template, dehydrate=self.serialize_timestamp)
 

# GET /RealtimeProblemAnswer?
class RealtimeProblemAnswer(ProcessQuery):
    def add_problem_source(self, args):
        query_template = '''select source_file from {{course}}_problem
            where {{course}}_problem.set_id     = "{{set_id}}" AND
                  {{course}}_problem.problem_id = {{problem_id}} '''
        query_rendered = Template(query_template).generate(**args) 
        rows = conn.query(query_rendered)
        if len(rows) == 1:
            args['source_file'] = rows[0]['source_file']
        else:
            args['source_file'] = None
        return args

    
    def post(self):
        ''' For logging real-time student answers to problems

            Sample arguments:
            course="CompoundProblems",
            set_id="compoundProblemExperiments",
            problem_id=1
            pg_id="a"
            user_id="melkherj", 
            correct=1
            answer_string="x^2+4x"

            Returning:
        '''
        query_template = '''
            insert into {{course}}_realtime_past_answer
                (set_id, problem_id, pg_id, user_id, source_file, correct, 
                    answer_string) values
                ( "{{set_id}}", {{problem_id}}, "{{pg_id}}", "{{user_id}}", 
                    "{{source_file}}", {{correct}}, 
                    "{{answer_string}}" )
        '''
        self.process_query(query_template, hydrate = 
            self.add_problem_source, write_response=False)


# GET /set_ids?
class SetIds(ProcessQuery):
    def get(self):
        ''' 
            List set ids.  

            Sample arguments:
            course="CompoundProblems", 

            Response: 
                ["set_1", "set_2", ...]
            '''
        query_template = '''
            select set_id from {{course}}_set
            order by open_date desc; 
        '''
        self.process_query(query_template,
                           dehydrate=lambda rows: [x['set_id'] for x in rows])

# GET /sets?
class Sets(ProcessQuery):
    def get(self):
        ''' 
            List sets.  

            Sample arguments:
            course="CompoundProblems", 

            Response: 
                [{"set_1"}, {"set_2"}, ...]
            '''
        query_template = '''
            select set_id, open_date, due_date, answer_date  from {{course}}_set
            order by open_date desc; 
        '''
        self.process_query(query_template)

# GET /problems?
class Problems(JSONRequestHandler, tornado.web.RequestHandler):
    def get(self):
        ''' 
            List problems.  

            Sample arguments:
            course="CompoundProblems", 
            set_id="Assignment1"
            Response: 

            '''
        course = self.get_argument('course')
        set_id = self.get_argument('set_id')

        query = '''
            SELECT p.problem_id, p.source_file, p.value,
            COUNT(a.answer_id) AS attempt_count
            FROM {0}_problem AS p
            LEFT OUTER JOIN {0}_past_answer AS a
            ON a.set_id = p.set_id AND a.problem_id = p.problem_id
            WHERE p.set_id = %s
            GROUP BY COALESCE(a.problem_id, p.problem_id)
            ORDER BY problem_id ASC; '''.format(course)
        logger.debug(query)
        result = conn.query(query, set_id)

        hints_query = ''' SELECT p.problem_id, COUNT(h.id) as hint_count
        FROM {0}_problem as p LEFT OUTER JOIN {0}_hint as h
        ON h.set_id = p.set_id AND h.problem_id = p.problem_id AND h.deleted = 0
        WHERE p.set_id = %s
        GROUP BY COALESCE(h.problem_id, p.problem_id)
        ORDER BY problem_id ASC;
        '''.format(course)
        hints = conn.query(hints_query, set_id)
        logger.debug(hints)
        for i in range(len(result)):
            result[i]['hint_count'] = hints[i]['hint_count']
        logger.debug(result)
        self.write(json.dumps(result))

# GET /export_problem_data?
class ExportProblemData(JSONRequestHandler, tornado.web.RequestHandler):
    def get(self):
        '''
        Export all data about a problem
        '''
        course = self.get_argument('course')
        set_id = self.get_argument('set_id')
        problem_id = self.get_argument('problem_id')
        query = 'SELECT * from {0}_problem WHERE set_id = %s AND problem_id = %s'.format(course)
        result = conn.query(query, set_id, problem_id)[0]
        pg_path = result['source_file']
        with open(os.path.join(webwork_dir, 'courses', course, 'templates', pg_path), 'r') as f:
            pg_file_contents = f.read()

        out = {}
        out['pg_file'] = pg_file_contents
        out['filename'] = pg_path
        past_answers = conn.query(
            'SELECT * from {0}_past_answer where set_id = %s AND problem_id = %s'.format(course),
            set_id, problem_id)

        out['past_answers'] = past_answers

        realtime_past_answers = conn.query(
            'SELECT * from {0}_realtime_past_answer where set_id = %s AND problem_id = %s'.format(course),
            set_id, problem_id)

        out['realtime_past_answers'] = realtime_past_answers

        hints = conn.query(
            'SELECT * from {0}_hint where set_id = %s AND problem_id = %s'.format(course),
            set_id, problem_id)
        out['hints'] = hints

        assigned_hints = conn.query(
            'SELECT * from {0}_assigned_hint where set_id = %s AND problem_id = %s'.format(course),
            set_id, problem_id)
        out['assigned_hints'] = assigned_hints

        hint_feedback = conn.query(
            'SELECT {0}_assigned_hint_feedback.* from {0}_assigned_hint_feedback INNER JOIN {0}_assigned_hint ON {0}_assigned_hint_feedback.assigned_hint_id = {0}_assigned_hint.id WHERE {0}_assigned_hint.set_id = %s AND {0}_assigned_hint.problem_id = %s'.format(course),
            set_id, problem_id)
        out['hint_feedback'] = hint_feedback
        self.write(json.dumps(out, default=serialize_datetime))
