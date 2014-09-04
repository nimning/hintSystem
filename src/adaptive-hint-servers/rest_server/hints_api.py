import tornado
import json
import tornado.ioloop
import tornado.web
import logging

from tornado.template import Template
from convert_timestamp import utc_to_system_timestamp
from process_query import ProcessQuery, conn
from hint_filters.AllFilters import hint_filters
from operator import itemgetter
import pandas as pd

logger = logging.getLogger(__name__)

class UserProblemHints(ProcessQuery):
    """ /user_problem_hints """

    def _add_header_footer(self, rows):
        ''' Add header footer and convert timestamps '''
        rows = self.add_header_footer(rows)
        for row in rows:
            row['timestamp'] = utc_to_system_timestamp(
                row['timestamp'])
        return rows
    
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
                    "pg_file_path": "/opt/path/compoundProblem.pg",
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
                {{course}}_assigned_hint.assigned as timestamp,
                {{course}}_assigned_hint.pg_id,
                {{course}}_assigned_hint.hint_html,
                {{course}}_assigned_hint.id as assigned_hint_id,
                {{course}}_hint.set_id as original_set_id,
                {{course}}_hint.problem_id as original_problem_id
            from {{course}}_hint, {{course}}_assigned_hint
            where 
                {{course}}_assigned_hint.user_id="{{user_id}}"        AND
                {{course}}_assigned_hint.hint_id={{course}}_hint.id   AND
                {{course}}_assigned_hint.set_id="{{set_id}}"          AND 
                {{course}}_assigned_hint.problem_id={{problem_id}}  '''
        self.process_query(query_template, 
            dehydrate=self._add_header_footer)
       

class Hint(ProcessQuery):
    """ /hint """

    def set_default_headers(self):
        # Allows X-site requests
        super(ProcessQuery, self).set_default_headers()
        self.add_header("Access-Control-Allow-Methods", "PUT,DELETE")

    def delete(self):
        '''  For helping the instructor delete hints
            
            Sample arguments:
            hint_id=1
            course="CompoundProblems"

            With return 0
        '''
        query_template = '''
           update {{course}}_hint set deleted=true
             where id={{hint_id}} '''
        self.process_query(query_template, write_response=False)

    def _add_header_footer(self, response):
        self.args['set_id'] = response[0]['set_id']
        self.args['problem_id'] = response[0]['problem_id']
        return self.add_header_footer(response)[0]
    
    def get(self):
        '''  For helping the instructor read hints
            
            Sample arguments:
            hint_id=1
            course="CompoundProblems"

            With return [{"pg_text": "what is 1+1?  [____]{2}", 
                "author": "melkherj"}]
        '''
        query_template = '''
            select pg_text, author, set_id, problem_id
            from {{course}}_hint 
            where id={{hint_id}} and (NOT deleted)'''
        self.process_query(query_template, dehydrate=self._add_header_footer)

    def post(self):
        ''' For helping the instructor add hints 
            Sample arguments:
            course="CompoundProblems"
            pg_text="This might help you.  3+3=? [____]{6}"
            author="melkherj"
            set_id="compoundProblemExperiments"
            problem_id=1

            With return 6   (the id of the row created)'''
        query_template = '''insert into {{course}}_hint 
            (pg_text, author, set_id, problem_id) values 
            ("{{pg_text}}", "{{author}}", "{{set_id}}", "{{problem_id}}") 
        '''
        self.process_query(query_template, write_response=False)

    def put(self):
        ''' For helping the instructor update hints 
            Sample arguments:
            course="CompoundProblems"
            pg_text="This might help you.  3+3=? [____]{6}"
            hint_id=6

            With return 6   (the id of the row created)'''
        query_template = '''UPDATE {{course}}_hint 
            SET pg_text="{{pg_text}}" WHERE id={{hint_id}}
        '''
        self.process_query(query_template, write_response=False)

       

class AssignedHint(ProcessQuery):
    """ /assigned_hint """

    def replace_hint_html_id(self, assigned_id):
        assigned_hintbox_id = "AssignedHint%05d"%assigned_id

        # replace 'HINTBOXID with the actual hintbox id
        self.args['hint_html'] = self.args['hint_html_template'].replace(
            'HINTBOXID',
            assigned_hintbox_id)

        self.args['id'] = assigned_id
        query_template = '''update {{course}}_assigned_hint
            set hint_html="{{hint_html}}"
            where id={{id}}'''
        
        query_rendered = Template(query_template).generate(**self.args)
        conn.execute(query_rendered)
        return assigned_hintbox_id
    
    def post(self):
        ''' For helping the instructor assign hints 
            Sample arguments:
            course="CompoundProblems",
            set_id="compoundProblemExperiments",
            problem_id=1,
            pg_id="a",
            hint_id=6,
            user_id="melkherj", 
            hint_html_template="melkherj", 

            With return None '''
        query_template = '''insert into {{course}}_assigned_hint 
            (set_id, problem_id, pg_id, hint_id, user_id, hint_html) values
            ("{{set_id}}", {{problem_id}}, 
            "{{pg_id}}", "{{hint_id}}", "{{user_id}}", "{{hint_html_template}}")
            '''
        self.process_query(query_template,
                           post_process=self.replace_hint_html_id, 
                           write_response=False)

    def get(self):
        ''' 
            Sample arguments:
            course="CompoundProblems",
            set_id="compoundProblemExperiments",
            problem_id=1,
            assigned_hint_id=10
            '''
        query_template = '''
            select {{course}}_hint.pg_text         
            from {{course}}_hint, {{course}}_assigned_hint
            where 
                {{course}}_assigned_hint.id={{assigned_hint_id}}  AND
                {{course}}_assigned_hint.hint_id={{course}}_hint.id '''
        self.process_query(query_template,
                           dehydrate=lambda x: self.add_header_footer(x)[0])
        

    def delete(self):
        query_template = '''
           delete from {{course}}_assigned_hint
           where id={{assigned_hint_id}}'''
        self.process_query(query_template, write_response=False)
        

class HintFeedback(ProcessQuery):
    """ /hint_feedback """
    
    def post(self):
        ''' For logging student feedback of a hint

            Sample arguments:
            course="CompoundProblems",
            assigned_hint_id=1,
            feedback="very useful"

            Returning: 
       '''
        query_template = '''
            insert into {{course}}_assigned_hint_feedback
                (assigned_hint_id, feedback) values
                ( {{assigned_hint_id}}, "{{feedback}}" )
        '''
        self.process_query(query_template, write_response=False)
    

class ProblemHints(ProcessQuery):
    """ /problem_hints """

    def get(self):
        ''' 
            For listing all hints for a problem (for instructors)
            that could be reused for other students:

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
            select {{course}}_hint.id as hint_id,
                   {{course}}_hint.pg_text,
                   {{course}}_hint.author,
                   {{course}}_hint.set_id,
                   {{course}}_hint.problem_id
            from {{course}}_hint left outer join {{course}}_assigned_hint
            on {{course}}_assigned_hint.hint_id={{course}}_hint.id
            where 
            (
              (
                {{course}}_assigned_hint.set_id="{{set_id}}"        AND
                {{course}}_assigned_hint.problem_id={{problem_id}}
              ) OR (
                {{course}}_hint.set_id="{{set_id}}"                 AND
                {{course}}_hint.problem_id={{problem_id}}
              )
            )
            AND (NOT {{course}}_hint.deleted )
            group by {{course}}_hint.id
        '''
        self.process_query(query_template, dehydrate=self.add_header_footer)


class RunHintFilters(ProcessQuery):
    ''' Given a user and problem part (a particular box where expressions are
        entered), scan HintFilter's and assignment/answer histories to 
        determine whether a hint should be assigned to this user/box '''

    def check_hint_assignment(self, rows):
        ''' Given the course, user_id, set_id, problem_id, and pg_id, 
            return a pandas DataFrame containing the rows in the mysql 
            realtime_past_answers table that match the given args
             '''
        # Convert the context of the student struggling on the particular part
        # to a pandas DataFrame
        df = pd.DataFrame(rows) 
        # Go through each entry in the assigned_hint_filter table.  
        # Find matches for 
        query_template = ''' select {{course}}_hint_filter.filter_name, 
                {{course}}_assigned_hint_filter.hint_id
            from {{course}}_hint_filter, {{course}}_assigned_hint_filter
            where
                {{course}}_assigned_hint_filter.hint_filter_id
                    = {{course}}_hint_filter.id
        ''' 
        query_rendered = Template(query_template).generate(**self.args)
        hint_filters_dict = dict( (f.__name__, f) for f in hint_filters)
        assigned_hint_filters = conn.query(query_rendered)
        hint_ids_to_assign = set([]) 
        for assigned_hint_filter in assigned_hint_filters:
            filter_name = assigned_hint_filter['filter_name']
            hint_id = assigned_hint_filter['hint_id']
            hint_filter = hint_filters_dict[filter_name]
            self.args['hint_id'] = hint_id
            # Get a list of other places the hint has been assigned
            query_template = '''
                select {{course}}_assigned_hint.*
                from {{course}}_hint, {{course}}_assigned_hint
                where {{course}}_assigned_hint.hint_id={{course}}_hint.id 
                    and {{course}}_hint.id = {{hint_id}}
            '''
            query_rendered = Template(query_template).generate(**self.args)
            previous_hint_assignments = conn.query(query_rendered)
            if hint_filter(self.args, df, previous_hint_assignments):
                hint_ids_to_assign.add(hint_id)
        return list(hint_ids_to_assign)

 
    def get(self):
        query_template = ''' select * from {{course}}_realtime_past_answer 
            where set_id="{{set_id}}" and 
            problem_id={{problem_id}} and 
            pg_id="{{pg_id}}" and 
            user_id="{{user_id}}"
        '''
        self.process_query(query_template, dehydrate=self.check_hint_assignment)

class HintFilter(ProcessQuery):
    
    def filter_names_to_list(self, rows):
        return [row['filter_name'] for row in rows]

    def get(self):
        query_template = ''' select filter_name from {{course}}_hint_filter '''
        self.process_query(query_template, dehydrate=self.filter_names_to_list)
    
    def post(self):
        query_template = ''' insert into {{course}}_hint_filter 
            (filter_name) values ("{{filter_name}}") '''
        self.process_query(query_template, write_response=False)

class AssignedHintFilter(ProcessQuery):

    def get(self):
        query_template = ''' select {{course}}_hint_filter.filter_name, 
            {{course}}_assigned_hint_filter.hint_id
            from {{course}}_hint_filter, {{course}}_assigned_hint_filter
            where {{course}}_assigned_hint_filter.hint_filter_id = 
                {{course}}_hint_filter.id
        '''
        self.process_query(query_template)

    def post(self):
        # insert ignore inserts only if there is not already a matching element
        query_template = ''' insert ignore into {{course}}_assigned_hint_filter
            (hint_filter_id, hint_id) values 
            ( (select id from {{course}}_hint_filter 
                       where filter_name="{{filter_name}}"), 
              {{hint_id}})
        '''
        self.process_query(query_template, write_response=False)
