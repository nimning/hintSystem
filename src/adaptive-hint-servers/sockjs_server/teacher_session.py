import logging
import datetime
import time

from student_session import StudentSession
from hint_rest_api import HintRestAPI

DEFAULT_TIMEOUT = 60 # minutes

def _datetime_to_timestamp(dt):
    return time.mktime(dt.timetuple())

def _hashkey_to_student(hashkey):
    (student_id, course_id, set_id, problem_id) = hashkey
    for ss in StudentSession.active_sessions:
        if (ss.student_id == student_id and
            ss.course_id == course_id and
            ss.set_id == set_id and
            ss.problem_id == problem_id):
            return ss        
    return None

def _extract_student_info(ss):
    return { 'student_id': ss.student_id,
             'course_id': ss.course_id,
             'set_id': ss.set_id,
             'problem_id': ss.problem_id,
             'pg_file': ss.pg_file,
             'pg_seed': ss.pg_seed,
             'hints': ss.hints,
             'answers': ss.answers,
             'current_answers': ss.current_answers }

class TeacherSession(object):
    """Teacher session state

    Class variables
    ---------------
      active_sessions : set of TeacherSession
        Set of all connected teachers

      student_assignment : dict
        Mapping from students to teachers 

    Properties
    ----------
      teacher_id : string
        Teacher ID

      _sockjs_handler : StudentSockJSHandler
        SockJS handler
        
    """
    active_sessions = set()
    student_assignment = {}
        
    def __init__(self, teacher_id, sockjs_handler, student_id=None,
                 course_id=None, set_id=None, problem_id=None):
        self.teacher_id = teacher_id
        self._sockjs_handler = sockjs_handler
        
        # student assigned to this instance
        self.student_id = student_id
        self.course_id = course_id
        self.set_id = set_id
        self.problem_id = problem_id
            
    def request_student(self, student_id, course_id, set_id, problem_id):
        """Try to add a student with the session id to the set"""
        hashkey = (student_id, course_id, set_id, problem_id)
        if hashkey not in TeacherSession.student_assignment:
            timeout = (datetime.datetime.now() +
                       datetime.timedelta(minutes=DEFAULT_TIMEOUT))
            TeacherSession.student_assignment[hashkey] = (self.teacher_id,
                                                          timeout)

    def release_student(self, student_id, course_id, set_id, problem_id):
        """Remove a student with the session id from the set"""
        hashkey = (student_id, course_id, set_id, problem_id)
        if (hashkey in TeacherSession.student_assignment and
            TeacherSession.student_assignment[hashkey][0] == self.teacher_id):
            del TeacherSession.student_assignment[hashkey]

    def add_hint(self, student_id, course_id, set_id, problem_id, location,
                 hint_id, hint_html_template):
        """Add a hint to user_problem_hint DB

        *Blocked until complete*
        """
        timestamp = _datetime_to_timestamp(datetime.datetime.now())
        assigned_hintbox_id = HintRestAPI.assign_hint(student_id,
                                                   course_id,
                                                   set_id,
                                                   problem_id, 
                                                   location,
                                                   hint_id,
                                                   hint_html_template)
        return timestamp, assigned_hintbox_id

    def remove_hint(self, student_id, course_id, set_id, problem_id,
                    location, hintbox_id):
        """Remove a hint to user_problem_hint DB

        *Blocked until complete*
        """
        HintRestAPI.unassign_hint(course_id, hintbox_id)

    def list_my_students(self):
        """List all my students"""
        student_list = []
        now = datetime.datetime.now()           
        for hashkey in TeacherSession.student_assignment.keys():
            (teacher_id, timeout) = TeacherSession.student_assignment[hashkey]
            # Release students that are timed-out.
            if timeout < now:
                del TeacherSession.student_assignment[hashkey]
            elif teacher_id == self.teacher_id:
                # check if the student is still connected
                ss = _hashkey_to_student(hashkey)
                if ss is not None:
                    student_list.append({
                        'session_id': ss.session_id,
                        'student_id': ss.student_id,
                        'course_id': ss.course_id,
                        'set_id': ss.set_id,
                        'problem_id': ss.problem_id,
                        'hints': ss.hints,
                        'answers': ss.answers
                        })
        return student_list

    def list_unassigned_students(self):
        """List all unassigned students"""
        student_list = []
        for ss in list(StudentSession.active_sessions):
            hashkey = (ss.student_id, ss.course_id,
                       ss.set_id, ss.problem_id)            
            if hashkey not in TeacherSession.student_assignment:
                student_list.append({
                    'session_id': ss.session_id,
                    'student_id': ss.student_id,
                    'course_id': ss.course_id,
                    'set_id': ss.set_id,
                    'problem_id': ss.problem_id,
                    'hints': ss.hints,
                    'answers': ss.answers
                    })
        return student_list

    def student_info(self, student_id, course_id, set_id, problem_id):
        info = {}
        for ss in StudentSession.active_sessions:
            if (ss.student_id == student_id and
                ss.course_id == course_id and
                ss.set_id == set_id and
                ss.problem_id == problem_id):
                info = _extract_student_info(ss)
                break
        return info

    def notify_answer_update(self, extended_answer_status):
        """Called when there is an answer update"""
        student_id = extended_answer_status['student_id']
        course_id = extended_answer_status['course_id']
        set_id = extended_answer_status['set_id']
        problem_id = extended_answer_status['problem_id']

        # send updated student info to the teacher
        if (student_id == self.student_id and
            course_id == self.course_id and
            set_id == self.set_id and
            problem_id == self.problem_id):
            info = self.student_info(student_id, course_id, set_id, problem_id)

            # do not send empty
            if len(info) > 0:
                self._sockjs_handler.send_student_info(info)
        
    def notify_hint_update(self, extended_hint):
        """Called when there is a hint update"""
        student_id = extended_hint['student_id']
        course_id = extended_hint['course_id']
        set_id = extended_hint['set_id']
        problem_id = extended_hint['problem_id']
        
        # send updated student info to the teacher
        if (student_id == self.student_id and
            course_id == self.course_id and
            set_id == self.set_id and
            problem_id == self.problem_id):
            info = self.student_info(student_id, course_id, set_id, problem_id)

            # do not send empty
            if len(info) > 0:
                self._sockjs_handler.send_student_info(info)

    def notify_student_join(self, ss):
        """Called when a student has joined"""
        if (ss.student_id == self.student_id and
            ss.course_id == self.course_id and
            ss.set_id == self.set_id and
            ss.problem_id == self.problem_id):
            self._sockjs_handler.send_student_info(_extract_student_info(ss))
        elif (self.student_id is None):
            # no student associated, must be the console
            self._sockjs_handler.send_my_students(self.list_my_students())
            self._sockjs_handler.send_unassigned_students(
                self.list_unassigned_students())
            
    def notify_student_left(self, ss):
        if (ss.student_id == self.student_id and
            ss.course_id == self.course_id and
            ss.set_id == self.set_id and
            ss.problem_id == self.problem_id):
            # send empty info
            self._sockjs_handler.send_student_info({})
