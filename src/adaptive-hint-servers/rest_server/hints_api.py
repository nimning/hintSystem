import tornado
import json
import tornado.ioloop
import tornado.web

from process_query import ProcessQuery, conn
from get_header_footer import get_header, get_footer

# GET /user_problem_hints?
class UserProblemHints(ProcessQuery):

    def add_header_footer(self, response):
        print self.args['course']
        relative_filename_query = \
            "select source_file from %s_problem;" % self.args['course']
        relative_filename = conn.query(relative_filename_query) \
            [0]['source_file']
        pg_file_path = '/opt/webwork/courses/%s/templates/%s' % \
            (self.args['course'], relative_filename)
        with open(pg_file_path, 'r') as f:
            pg_file_str = f.read()
            header = get_header(pg_file_str)
            footer = get_header(pg_file_str)
            
        for row in response:
            row['pg_header'] = header
            row['pg_footer'] = footer
            row['pg_file_path'] = pg_file_path
        return response

    def get(self):
        ''' For rendering assigned hints in the student page.  

            Sample arguments:
            course="CompoundProblems",
            user_id="melkherj", 
            set_id="compoundProblemExperiments",
            problem_id=1

            Returning: [
                {
                    "hint_id": 3,
                    "assigned_hint_id": 1, 
                    "pg_footer": "...",
                    "pg_header": "...",
                    "pg_file_path": "/opt/webwork/courses/CompoundProblems/templates/setcompoundproblemexperiments/compoundProblem.pg",
                    "pg_id": "a",
                    "pg_text": "This might help: what is 1+1? [____]{2}"
                },
                ...
            ]
        '''
        query_template = '''
            select 
                {{course}}_hint.pg_text,
                {{course}}_hint.id as hint_id,
                {{course}}_assigned_hint.pg_id,
                {{course}}_assigned_hint.id as assigned_hint_id
            from {{course}}_hint, {{course}}_assigned_hint
            where 
                {{course}}_assigned_hint.user_id="{{user_id}}"        AND
                {{course}}_assigned_hint.hint_id={{course}}_hint.id   AND
                {{course}}_assigned_hint.set_id="{{set_id}}"          AND 
                {{course}}_assigned_hint.problem_id={{problem_id}}'''
        self.process_query(query_template, 
            dehydrate=self.add_header_footer, verbose=True)
       

class Hint(ProcessQuery):

    def delete(self):
        '''  For helping the instructor delete hints
            
            Sample arguments:
            hint_id=1
            course="CompoundProblems"

            With return 0
        '''
        query_template = '''
            delete from {{course}}_hint 
            where id={{hint_id}} '''
        self.process_query(query_template, write_response=False)

    def get(self):
        '''  For helping the instructor read hints
            
            Sample arguments:
            hint_id=1
            course="CompoundProblems"

            With return [{"pg_text": "This might help: what is 1+1?  [____]{2}", 
                "author": "melkherj"}]
        '''
        query_template = '''
            select pg_text, author
            from {{course}}_hint 
            where id={{hint_id}} '''
        self.process_query(query_template)

    def post(self):
        ''' For helping the instructor add hints 
            Sample arguments:
            pg_text="This might help you.  3+3=? [____]{6}"
            author="melkherj"
            course="CompoundProblems"

            With return 6   (the id of the row created)'''
        query_template = '''insert into {{course}}_hint 
            (pg_text, author) values ("{{pg_text}}", "{{author}}") '''
        self.process_query(query_template, write_response=False)
       

class AssignedHint(ProcessQuery):
    
    def post(self):
        ''' For helping the instructor assign hints 
            Sample arguments:
            course="CompoundProblems",
            set_id="compoundProblemExperiments",
            problem_id=1,
            pg_id="a",
            hint_id=6,
            user_id="melkherj", 

            With return None '''
        query_template = '''insert into {{course}}_assigned_hint 
            (set_id, problem_id, pg_id, hint_id, user_id) values
            ("{{set_id}}", {{problem_id}}, 
                    "{{pg_id}}", "{{hint_id}}", "{{user_id}}")
            '''
        self.process_query(query_template, write_response=False)


## GET /problem_hints?
#class ProblemHints(ProcessQuery):
#    def get(self):
#        ''' 
#            For listing all hints for a problem (for instructors) that could be reused for other students:
#
#            Sample arguments:
#            course="CompoundProblems", 
#            set_id="compoundProblemExperiments",
#            problem_id=2
#
#            Response: [
#                {"pg_text": "My name is Mr Hint", "pg_id": "b"}, 
#                {"pg_text": "What is [`x^2+4x+2`]?", "pg_id": "b"}, 
#                {"pg_text": "some new problem text!", "pg_id": "b"}, 
#                {"pg_text": "some new problem text!", "pg_id": "b"}, 
#                {"pg_text": "some new problem text!", "pg_id": "b"}, 
#                {"pg_text": "More hints for you dear", "pg_id": "b"}
#            ]
#            '''
#        query_template = '''
#            select pg_id, pg_text,
#            from {{course}}_hint 
#            where set_id="{{set_id}}" AND problem_id={{problem_id}} ''' 
#        self.process_query(query_template)
