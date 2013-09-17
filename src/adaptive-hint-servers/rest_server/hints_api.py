import tornado
import json
import tornado.ioloop
import tornado.web

from process_query import ProcessQuery

# GET /user_problem_hints?
class UserProblemHints(ProcessQuery):

    def get(self):
        ''' For rendering hints in the student page.  

            Sample arguments:
            course="CompoundProblems",
            user_id="melkherj", 
            set_id="compoundProblemExperiments",
            problem_id=2

            Returning: [{"pg_text": "My name is Mr Hint", "pg_id": "b"}] '''
        query_template = '''
            select {{course}}_hint.pg_id, {{course}}_hint.pg_text 
            from {{course}}_assigned_hint, {{course}}_hint 
            where 
                {{course}}_assigned_hint.user_id="{{user_id}}"        AND
                {{course}}_assigned_hint.hint_id={{course}}_hint.id   AND
                {{course}}_hint.set_id="{{set_id}}"                   AND 
                {{course}}_hint.problem_id={{problem_id}}'''
        self.process_query(query_template)
       

class Hint(ProcessQuery):

    def get(self):
        '''  For helping the instructor read hints
            
            Sample arguments:
            course="CompoundProblems"
            hint_id=2

            With return [{"pg_text": "My name is Mr Hint", "pg_id": "b", 
                "problem_id": 2, "set_id": "compoundProblemExperiments"}] '''
        query_template = '''
            select set_id, problem_id, pg_id, pg_text
            from {{course}}_hint 
            where id={{hint_id}} '''
        self.process_query(query_template)

    def post(self):
        ''' For helping the instructor add hints 
            Sample arguments:
            course=course, 
            pg_id="b",
            set_id="compoundProblemExperiments",
            problem_id=2,
            pg_text="What is [`x^2+4x+2`]?"

            With return None '''
        query_template = '''insert into {{course}}_hint 
            (pg_id, problem_id, set_id, pg_text) values
            ("{{pg_id}}", {{problem_id}}, "{{set_id}}", "{{pg_text}}") '''
        self.process_query(query_template, write_response=False)
       
# GET /problem_hints?

class ProblemHints(ProcessQuery):
    def get(self):
        ''' 
            For listing all hints for a problem (for instructors) that could be reused for other students:

            Sample arguments:
            course="CompoundProblems", 
            set_id="compoundProblemExperiments",
            problem_id=2

            Response: [
                {"pg_text": "My name is Mr Hint", "pg_id": "b"}, 
                {"pg_text": "What is [`x^2+4x+2`]?", "pg_id": "b"}, 
                {"pg_text": "some new problem text!", "pg_id": "b"}, 
                {"pg_text": "some new problem text!", "pg_id": "b"}, 
                {"pg_text": "some new problem text!", "pg_id": "b"}, 
                {"pg_text": "More hints for you dear", "pg_id": "b"}
            ]
            '''
        query_template = '''
            select pg_id, pg_text
            from {{course}}_hint 
            where set_id="{{set_id}}" AND problem_id={{problem_id}} ''' 
        self.process_query(query_template)
        

if __name__ == "__main__":
    
    application = tornado.web.Application([
        (r"/user_problem_hints", UserProblemHints),
        (r"/hint", Hint),
        (r"/problem_hints", ProblemHints),
        ])
    
    application.listen(8420)
    tornado.ioloop.IOLoop.instance().start()

