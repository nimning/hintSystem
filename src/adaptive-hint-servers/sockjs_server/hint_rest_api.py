from tornado import httpclient
from tornado.httputil import url_concat
from HTMLParser import HTMLParser
import urllib
import json
import requests

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
        http_client = httpclient.HTTPClient()
        baseurl = HintRestAPI._baseurl
        response = http_client.fetch(baseurl + '/checkanswer',
                                     method='POST',
                                     headers=None,
                                     body=urllib.urlencode({
                                         'pg_file' : pg_file,
                                         'seed' : pg_seed,
                                         boxname : value 
                                         }))
        result_json = json.loads(response.body)[boxname]
        answer_status = { 'boxname': boxname,
                          'is_correct': result_json['is_correct'],
                          'error_msg': result_json['error_msg'],
                          'entered_value': value,
                          'correct_value': result_json['correct_value']
                          }
        return answer_status

    @staticmethod
    def problem_seed(student_id, course_id, set_id, problem_id):
        """
          Returns:
            An integer of the random seed.
        """
        http_client = httpclient.HTTPClient()
        baseurl = HintRestAPI._baseurl
        url = url_concat(baseurl + '/problem_seed',
                         { 'course': course_id,
                           'set_id': set_id,
                           'problem_id': problem_id,
                           'user_id': student_id
                           })
        response = http_client.fetch(url)
        return int(response.body)
    
    @staticmethod
    def pg_path(course_id, set_id, problem_id):
        """
          Returns:
            A string representing the path to the pg file.
        """
        http_client = httpclient.HTTPClient()
        baseurl = HintRestAPI._baseurl
        url = url_concat(baseurl + '/pg_path',
                         { 'course': course_id,
                           'set_id': set_id,
                           'problem_id': problem_id
                           })
        response = http_client.fetch(url)
        return json.loads(response.body)
            
    @staticmethod
    def hint(course_id, hint_id):
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
        http_client = httpclient.HTTPClient()
        baseurl = HintRestAPI._baseurl
        url = url_concat(baseurl + '/hint',
                         { 'course': course_id,
                           'hint_id': hint_id
                           })
        response = http_client.fetch(url)
        return json.loads(response.body)

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
                'hintbox_id' : 'Hint%05d'%row['hint_id'],
                'location' : row['pg_id'],
                'hint_html' : p.unescape(row['hint_html']) })
        return hints
 
    @staticmethod
    def assign_hint(student_id, course_id, set_id,
                    problem_id, location, hintbox_id, hint_html):
        base_url = HintRestAPI._baseurl
        hint_id = int(hintbox_id[4:])
        params = {'user_id':student_id, 'course':course_id,
                  'set_id':set_id, 'problem_id':problem_id, 'pg_id':location, 
                  'hint_id':hint_id, 'hint_html':hint_html}
        r = requests.post(base_url+'/assigned_hint', data=params)

    @staticmethod
    def unassign_hint(student_id, course_id, set_id, problem_id,
                      location, hintbox_id):
        pass
            
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
