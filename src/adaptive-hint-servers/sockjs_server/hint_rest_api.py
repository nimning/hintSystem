from HTMLParser import HTMLParser
import json
import requests
import logging
import base64
import re

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
    def checkanswer(pg_file, pg_seed, psvn, boxname, value):
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
        params = { 'pg_file' : pg_file, 'seed' : pg_seed, 'psvn': psvn,
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
    def set_psvn(student_id, course_id, set_id):
        """
          Returns:
            An integer of the problem set version number.
        """
        base_url = HintRestAPI._baseurl
        params = { 'course': course_id,
                   'set_id': set_id,
                   'user_id': student_id }
        psvn = requests.get(base_url + '/set_psvn',
                            params=params).text
        return int(psvn)

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

    @staticmethod
    def apply_hint_filters(user_id, course, set_id, problem_id, pg_id):
        ''' Call the "run_hint_filters" API call.  This determines what
            hints should be assigned to this particular user/box.
            Then call a function to assign the hint to this user at the given
            box (given by course/set/problem/pg id) '''
        base_url = HintRestAPI._baseurl
        params = {'user_id':user_id,
            'course':course,
            'set_id':set_id,
            'problem_id':problem_id,
            'pg_id':pg_id
        }
        r = requests.get(base_url+'/run_hint_filters', params=params)
        hint_ids = r.json()
        # Assign hints that pass some filter
        for hint_id in hint_ids:
            HintRestAPI.render_html_assign_hint(user_id, course, set_id,
                    problem_id, pg_id, hint_id)
        return hint_ids

    @staticmethod
    def render_html_assign_hint(user_id, course, set_id,
                    problem_id, pg_id, hint_id):
        ''' rows in the assigned hint table store the rendered html associated
            with the hint.
            here we call REST API's to render the hint with the given id,
            then send the rendered hint along with its location to the
            assign_hint API '''
        base_url = HintRestAPI._baseurl
        # GET /hint
        r = requests.get(base_url+'/hint', params={'course':course,  'hint_id':hint_id}).json()
        pg_text = '%s\n%s\n%s'%(r['pg_header'], r['pg_text'], r['pg_footer'])
        # GET /problem_seed
        seed = requests.get(base_url+'/problem_seed', params={'course':course,
            'set_id':set_id, 'problem_id': problem_id, 'user_id':user_id}).json()
        pg_text = base64.b64encode(pg_text)
        params={'pg_file':pg_text, 'seed':seed}
        # GET /render
        r = requests.post(base_url+'/render', data={'pg_file':pg_text,
            'seed':seed}).json()
        h = r['rendered_html']
        # Clean up rendering
        div_match = re.compile(r'^.*<div',flags=re.MULTILINE)
        h = div_match.sub('<div', h).strip().replace('AnSwEr0001', 'HINTBOXID')
        h = h + '<div style="clear:left;">' + \
            '<input type="radio" name="feedback_' + \
            'HINTBOXID' + '" value="too hard">Too hard' + \
            '<input type="radio" name="feedback_' + \
            'HINTBOXID'  + '" value="easy but unhelpful">Easy but unhelpful' + \
            '<input type="radio" name="feedback_' + \
            'HINTBOXID' + '" value="helpful">Helpful' + \
            '</div>'
        # POST to /assigned_hint
        params = {'user_id':user_id, 'course':course,
                  'set_id':set_id, 'problem_id':problem_id, 'pg_id':pg_id,
                  'hint_id':hint_id, 'hint_html_template':h}
        r = requests.post(base_url+'/assigned_hint', data=params)
