from HTMLParser import HTMLParser
import json
import requests
import logging

logger = logging.getLogger(__name__)
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

class HintRestAPI(object):
    """Provides an interface to the Hint ReSTful APIs"""
    
    _baseurl = "http://127.0.0.1:4351"

    @staticmethod
    def setBaseUrl(baseurl):
        HintRestAPI._baseurl = baseurl

    @staticmethod
    def checkanswer(pg_file, pg_seed, boxname, value):
        """
          Returns:
            { 'boxname' : 'AnSwEr0001',
              'is_correct' : False,
              'error_msg' : '',
              'entered_value' : '123',
              'correct_value' : '567'
            }
        """
        base_url = HintRestAPI._baseurl
        params = { 'pg_file' : pg_file,
                   'seed' : pg_seed,
                   boxname : value }
        result_json = requests.post(base_url + '/checkanswer',
                                    data=params).json()
        answer_status = {}
        if boxname in result_json:
            result_json = result_json[boxname]
            answer_status = { 'boxname': boxname,
                              'is_correct': result_json['is_correct'],
                              'error_msg': result_json['error_msg'],
                              'entered_value': value,
                              'correct_value': result_json['correct_value'] }
        return answer_status

    @staticmethod
    def problem_seed(student_id, course_id, set_id, problem_id):
        """
          Returns:
            An integer of the random seed.
        """
        base_url = HintRestAPI._baseurl
        params = { 'course': course_id,
                   'set_id': set_id,
                   'problem_id': problem_id,
                   'user_id': student_id }
        seed = requests.get(base_url + '/problem_seed',
                            params=params).text
        return int(seed)
    
    @staticmethod
    def pg_path(course_id, set_id, problem_id):
        """
          Returns:
            A string representing the path to the pg file.
        """
        base_url = HintRestAPI._baseurl
        params = { 'course': course_id,
                   'set_id': set_id,
                   'problem_id': problem_id }
        return requests.get(base_url + '/pg_path',
                            params=params).json()
            
    @staticmethod
    def hint(course_id, set_id, problem_id, assigned_hint_id):
        """
          Returns:
            {
              ...
              'pg_text' : 'Hint body',
              'pg_header' : 'DOCUMENT(); ...',
              'pg_footer' : '...ENDDOCUMENT();'
              ...
            }
        """
        base_url = HintRestAPI._baseurl
        params =  { 'course': course_id,
                    'set_id': set_id,
                    'problem_id': problem_id,
                    'assigned_hint_id': assigned_hint_id }
        return requests.get(base_url + '/assigned_hint',
                            params=params).json()

    @staticmethod
    def get_user_problem_hints(student_id, course_id, set_id, problem_id):
        base_url = HintRestAPI._baseurl
        params = {'user_id':student_id, 'course':course_id,
                  'set_id':set_id, 'problem_id':problem_id}
        rows = requests.get(base_url+'/user_problem_hints',
                            params=params).json()

        p = HTMLParser()
        hints = []
        for row in rows:
            hints.append({
                'hintbox_id' : 'AssignedHint%05d'%row['assigned_hint_id'],
                'location' : row['pg_id'],
                'hint_html' : p.unescape(row['hint_html']),
                'timestamp' : row['timestamp'] })
        return hints
 
    @staticmethod
    def assign_hint(student_id, course_id, set_id,
                    problem_id, location, hint_id, hint_html_template):
        base_url = HintRestAPI._baseurl
        params = {'user_id':student_id, 'course':course_id,
                  'set_id':set_id, 'problem_id':problem_id, 'pg_id':location, 
                  'hint_id':hint_id, 'hint_html_template':hint_html_template}
        r = requests.post(base_url+'/assigned_hint', data=params)

    @staticmethod
    def unassign_hint(course_id, hintbox_id):
        base_url = HintRestAPI._baseurl
        params = {'course': course_id,
                  'assigned_hint_id': int(hintbox_id[-5:])}
        r = requests.delete(base_url+'/assigned_hint', params=params)
            
    @staticmethod
    def get_realtime_answers(student_id, course_id,
                             set_id, problem_id):
        base_url = HintRestAPI._baseurl
        params = {'user_id':student_id, 'course':course_id,
                  'set_id':set_id, 'problem_id':problem_id}
        r = requests.get(base_url+'/realtime_user_problem_answers',
                         params=params)
        rows = r.json()
        # Change the API spec for one of the client or server
        # TODO: change client or API calls to be consistent.
        #       This row rewriting shouldn't happen
        for row in rows:
            row['boxname'] = row['pg_id']
            row['error_msg'] = u''
            row['entered_value'] = row['answer_string']
            row['is_correct'] = (row['correct'] == 1)
            row['timestamp'] = float(row['timestamp'])
        return rows 

    @staticmethod
    def post_realtime_answer(student_id, course_id,
                             set_id, problem_id, answer_status):
        base_url = HintRestAPI._baseurl
        params = {'user_id': student_id,
                  'course': course_id,
                  'set_id': set_id,
                  'problem_id': problem_id,
                  'pg_id': answer_status['boxname'],
                  'correct': answer_status['is_correct'],
                  'answer_string': answer_status['entered_value']}
        r = requests.post(base_url+'/realtime_problem_answer',
                          data=params)

    @staticmethod
    def post_hint_feedback(course_id, assigned_hint_id, feedback):
        base_url = HintRestAPI._baseurl
        params = {'course': course_id,
                  'assigned_hint_id': assigned_hint_id,
                  'feedback': feedback}
        r = requests.post(base_url+'/hint_feedback', data=params)
        
