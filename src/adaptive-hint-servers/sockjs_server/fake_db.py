import requests
from HTMLParser import HTMLParser

base_url = 'http://0.0.0.0:4348'

class FakeDB:

    @staticmethod
    def get_hints(student_id, course_id, set_id, problem_id):
        params = {'user_id':student_id, 'course':course_id,
            'set_id':set_id, 'problem_id':problem_id}
        rows = requests.get(base_url+'/user_problem_hints',
            params=params).json()

        p = HTMLParser()
        for row in rows:
            row['hintbox_id'] = 'Hint%05d'%row['hint_id']
            row['location'] = row['pg_id']
            row['hint_html'] = p.unescape(row['hint_html'])
        return rows
 
    @staticmethod
    def add_hint(student_id, course_id, set_id, problem_id, location, hintbox_id,
            hint_html):
        hint_id = int(hintbox_id[4:])
        params = {'user_id':student_id, 'course':course_id,
            'set_id':set_id, 'problem_id':problem_id, 'pg_id':location, 
            'hint_id':hint_id, 'hint_html':hint_html}
        r = requests.post(base_url+'/assigned_hint', data=params)

    @staticmethod
    def remove_hint(student_id, course_id, set_id, problem_id,
                    location, hintbox_id):
        pass
            
    @staticmethod
    def get_answers(student_id, course_id, set_id, problem_id):
        params = {'user_id':student_id, 'course':course_id,
            'set_id':set_id, 'problem_id':problem_id}
        r = requests.get(base_url+'/realtime_user_problem_answers',
            params=params)
        rows = r.json()
        # Change the API spec for one of the client or server
        # TODO change client or API calls to be consistent.  This row rewriting shouldn't happen
        for row in rows:
            row['boxname'] = row['pg_id']
            row['error_msg'] = u''
            row['entered_value'] = row['answer_string']
            row['is_correct'] = (row['correct'] == 1)
            row['timestamp'] = float(row['timestamp'])
        return rows 
#rows

    @staticmethod
    def add_answer(student_id, course_id, set_id, problem_id, answer_status):
        params = {'user_id':student_id, 'course':course_id,
            'set_id':set_id, 'problem_id':problem_id,
            'pg_id':answer_status['boxname'],
            'correct':answer_status['is_correct'],
            'answer_string': int(answer_status['entered_value'])}
        r = requests.post(base_url+'/realtime_problem_answer',
            data=params)
