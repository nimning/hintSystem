"""Webwork DB API"""
import os.path
from process_query import ProcessQuery
from webwork_config import webwork_dir

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

        
