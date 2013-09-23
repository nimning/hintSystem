from tornado import httpclient
from tornado.httputil import url_concat
import logging
import datetime
import time
import json

from student_session import StudentSession
from fake_db import FakeDB

REST_SERVER = 'http://127.0.0.1:4351'
PROBLEM_SEED_API = REST_SERVER + '/problem_seed'
PG_PATH_API = REST_SERVER + '/pg_path'

def _datetime_to_timestamp(dt):
    return time.mktime(dt.timetuple())

def _active_students(session_ids):
    student_set = set(session_ids)
    info = []
    for ss in StudentSession.active_sessions:
        if ss.session_id in student_set:
            info.append({ 'session_id': ss.session_id,
                          'student_id': ss.student_id,
                          'course_id': ss.course_id,
                          'set_id': ss.set_id,
                          'problem_id': ss.problem_id,
                          'hints': ss.hints,
                          'answers': ss.answers,
                          'current_answers': ss.current_answers,
                          'sockjs_active': (ss._sockjs_handler is not None)
                          })
    return info


class TeacherSession(object):
    """Teacher session state

    Class variables
    ---------------
      active_sessions : set of TeacherSession
        Set of all connected teachers

      student_assignment : dict
        Mapping from students to teachers 

      storage : SessionStorage
        Storage for resuming from disconnection

    Properties
    ----------
      teacher_id : string
        Teacher ID

      _sockjs_handler : StudentSockJSHandler
        SockJS handler
        
    """
    active_sessions = set()
    student_assignment = {}
    _hints_cache = {}
    _answers_cache = {}
    _session_id_cache = {}

    def student_info(self, student_id, course_id, set_id, problem_id):
        hashkey = (student_id, course_id, set_id, problem_id)
        
        if hashkey in TeacherSession._hints_cache:
            hints = TeacherSession._hints_cache[hashkey]
        else:
            hints = FakeDB.get_hints(student_id, course_id, set_id,
                                     problem_id)
            
        if hashkey in TeacherSession._answers_cache:
            answers = TeacherSession._answers_cache[hashkey]
        else:
            answers = FakeDB.get_answers(student_id, course_id, set_id,
                                         problem_id)
        current_answers = {}
        for answer in answers:
            current_answers[answer['boxname']] = answer

        # get PG file path
        http_client = httpclient.HTTPClient()
        url = url_concat(PG_PATH_API, {
            'course': course_id,
            'set_id': set_id,
            'problem_id': problem_id
            })
        response = http_client.fetch(url)
        pg_file = json.loads(response.body)
            
        # get problem seed
        url = url_concat(PROBLEM_SEED_API, {
            'course': course_id,
            'set_id': set_id,
            'problem_id': problem_id,
            'user_id': student_id
            })
        response = http_client.fetch(url)
        pg_seed = int(response.body)
        
        info = {
            'student_id': student_id,
            'course_id': course_id,
            'set_id': set_id,
            'problem_id': problem_id,
            'pg_file': pg_file,
            'pg_seed': pg_seed,
            'hints': hints,
            'answers': answers,
            'current_answers': current_answers,
            }
        return info
        
    def __init__(self, teacher_id, sockjs_handler):
        self.teacher_id = teacher_id
        self._sockjs_handler = sockjs_handler
        
    def request_student(self, session_id):
        """Try to add a student with the session id to the set"""
        
        for ss in StudentSession.active_sessions:
            if ss.session_id == session_id:
                TeacherSession._session_id_cache[ss.student_id] = ss.session_id
        
        if session_id not in TeacherSession.student_assignment:
            TeacherSession.student_assignment[session_id] = self.teacher_id

    def release_student(self, session_id):
        """Remove a student with the session id from the set"""
        if (session_id in TeacherSession.student_assignment and
            TeacherSession.student_assignment[session_id] == self.teacher_id):
            del TeacherSession.student_assignment[session_id]

    def add_hint(self, student_id, course_id, set_id, problem_id,
                 location, hintbox_id, hint_html):
        """Add a hint to user_problem_hint DB

        *Blocked until complete*
        """
        timestamp = _datetime_to_timestamp(datetime.datetime.now())
        hint = hint = { 'timestamp': timestamp,
                        'hint_html': hint_html,
                        'location': location,
                        'hintbox_id': hintbox_id }
        FakeDB.add_hint(student_id, course_id, set_id, problem_id, hint)
        return timestamp

    def remove_hint(self, student_id, course_id, set_id, problem_id,
                    location, hintbox_id):
        """Remove a hint to user_problem_hint DB

        *Blocked until complete*
        """
        FakeDB.remove_hint(student_id, course_id, set_id, problem_id,
                           location, hintbox_id)

    def list_my_students(self):
        """List all my students"""
        student_list = []
        for session_id in TeacherSession.student_assignment.keys():
            if TeacherSession.student_assignment[session_id] == self.teacher_id:
                student_list.append(session_id)
        return _active_students(student_list)

    def list_unassigned_students(self):
        """List all unassigned students"""
        student_list = []
        for ss in list(StudentSession.active_sessions):
            if ss.session_id not in TeacherSession.student_assignment:
                student_list.append(ss.session_id)
        return _active_students(student_list)

    def notify_answer_update(self, extended_answer_status):
        """Called when there is an answer update"""
        session_id = extended_answer_status['session_id']
        student_id = extended_answer_status['student_id']
        course_id = extended_answer_status['course_id']
        set_id = extended_answer_status['set_id']
        problem_id = extended_answer_status['problem_id']

        # invalidate cache
        hashkey = (student_id, course_id, set_id, problem_id)
        TeacherSession._answers_cache.pop(hashkey, None)

        # send updated student info to the teacher
        if (session_id in TeacherSession.student_assignment and
            TeacherSession.student_assignment[session_id] == self.teacher_id):
            info = self.student_info(student_id, course_id, set_id, problem_id)
            self._sockjs_handler.send_student_info(info)
        
    def notify_hint_update(self, extended_hint):
        """Called when there is a hint update"""
        student_id = extended_hint['student_id']
        course_id = extended_hint['course_id']
        set_id = extended_hint['set_id']
        problem_id = extended_hint['problem_id']

        # TODO: improve this
        session_id = TeacherSession._session_id_cache[student_id]

        # invalidate cache
        hashkey = (student_id, course_id, set_id, problem_id)
        TeacherSession._hints_cache.pop(hashkey, None)

        # send updated student info to the teacher
        if (session_id in TeacherSession.student_assignment and
            TeacherSession.student_assignment[session_id] == self.teacher_id):
            info = self.student_info(student_id, course_id, set_id, problem_id)
            self._sockjs_handler.send_student_info(info)


    def notify_student_join(self):
        """Called when a student has joined"""
        self._sockjs_handler.send_my_students(self.list_my_students())
        self._sockjs_handler.send_unassigned_students(
            self.list_unassigned_students())
