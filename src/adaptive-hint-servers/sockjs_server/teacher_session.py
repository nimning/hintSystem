import logging
import datetime
import time

from student_session import StudentSession
from fake_db import FakeDB

def _datetime_to_timestamp(dt):
    return time.mktime(dt.timetuple())

# TODO: change some of the fields
def _student_info(session_ids):
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

    def __init__(self, teacher_id, sockjs_handler):
        self.teacher_id = teacher_id
        self._sockjs_handler = sockjs_handler
        
    def request_student(self, session_id):
        """Try to add a student with the session id to the set"""
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
        return _student_info(student_list)

    def list_unassigned_students(self):
        """List all unassigned students"""
        student_list = []
        for ss in list(StudentSession.active_sessions):
            if ss.session_id not in TeacherSession.student_assignment:
                student_list.append(ss.session_id)
        return _student_info(student_list)

    def notify_answer_update(self, extended_answer_status):
        """Called when there is an answer update"""
        session_id = extended_answer_status['session_id']
        course_id = extended_answer_status['course_id']
        set_id = extended_answer_status['set_id']
        problem_id = extended_answer_status['problem_id']
        if TeacherSession.student_assignment[session_id] == self.teacher_id:
            self._sockjs_handler.send_student_info(session_id,
                                                   course_id,
                                                   set_id,
                                                   problem_id)

    def notify_hint_update(self, extended_hint):
        """Called when there is a hint update"""
        session_id = extended_hint['session_id']
        course_id = extended_hint['course_id']
        set_id = extended_hint['set_id']
        problem_id = extended_hint['problem_id']
        if TeacherSession.student_assignment[session_id] == self.teacher_id:
            self._sockjs_handler.send_student_info(session_id,
                                                   course_id,
                                                   set_id,
                                                   problem_id)

    def notify_student_join(self):
        """Called when a student has joined"""
        self._sockjs_handler.send_my_students(self.list_my_students())
        self._sockjs_handler.send_unassigned_students(
            self.list_unassigned_students())
