"""Webwork DB API"""
import os.path
from process_query import ProcessQuery, conn
from webwork_config import webwork_dir
from tornado.template import Template

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

# GET /UserProblemHints?
class UserProblemAnswers(ProcessQuery):
    def get(self):
        ''' For showing the instructor student attempts at a problem

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
                {{course}}_past_answer.answer_id,
                {{course}}_past_answer.scores,
                {{course}}_past_answer.answer_string
            from {{course}}_past_answer
            where 
                {{course}}_past_answer.set_id="{{set_id}}"        AND
                {{course}}_past_answer.problem_id={{problem_id}}   AND
                {{course}}_past_answer.user_id="{{user_id}}"
        '''
        self.process_query(query_template)
 

# GET /RealtimeProblemAnswer?
class RealtimeProblemAnswer(ProcessQuery):
    def add_problem_source(self, args):
        query_template = '''select source_file from {{course}}_problem
            where {{course}}_problem.set_id     = "{{set_id}}" AND
                  {{course}}_problem.problem_id = {{problem_id}} '''
        query_rendered = Template(query_template).generate(**args) 
        print query_rendered
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
        self.process_query(query_template, hydrate = self.add_problem_source,
            verbose=True, write_response=False)
