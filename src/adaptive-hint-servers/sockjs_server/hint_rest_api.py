from tornado import httpclient
from tornado.httputil import url_concat
import urllib
import json

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
