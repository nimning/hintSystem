import logging
import datetime

from student_session import StudentSession
from hint_rest_api import HintRestAPI

DEFAULT_TIMEOUT = 60 # minutes
logger = logging.getLogger(__name__)
    
def _extract_student_info(ss):
    return { 'student_id': ss.student_id,
             'course_id': ss.course_id,
             'set_id': ss.set_id,
             'problem_id': ss.problem_id,
             'pg_file': ss.pg_file,
             'pg_seed': ss.pg_seed,
             'hints': ss.hints,
             'answers': ss.answers,
             'current_answers': ss.current_answers,
             'is_online': (ss._sockjs_handler is not None) }

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

      student_hashkey : hashable

      _sockjs_handler : StudentSockJSHandler
        SockJS handler
        
    """
    active_sessions = set()
    student_assignment = {}
        
    def __init__(self, teacher_id, sockjs_handler,
                 student_id, course_id, set_id, problem_id):
        self.teacher_id = teacher_id
        self._sockjs_handler = sockjs_handler
        self.student_hashkey = None
        
        if (student_id is not None and
            course_id is not None and
            set_id is not None and
            problem_id is not None):
            self.student_hashkey = (student_id,
                                    course_id,
                                    set_id,
                                    problem_id)


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
                (student_id, course_id, set_id, problem_id) = hashkey
                ss = StudentSession.get_student_session(student_id,
                                                        course_id,
                                                        set_id,
                                                        problem_id)
                if ss is not None:
                    student_list.append(ss.summary)
        return student_list

    def list_unassigned_students(self):
        """List all unassigned students"""
        student_list = []
        for hashkey in StudentSession.all_sessions.keys():
            if hashkey not in TeacherSession.student_assignment:
                (student_id, course_id, set_id, problem_id) = hashkey
                ss = StudentSession.get_student_session(student_id,
                                                        course_id,
                                                        set_id,
                                                        problem_id)
                if ss is not None:
                    student_list.append(ss.summary)
                    
        # filter out students who already solved the problems
        student_list = [student for student in student_list
                        if not student['problem_solved']]
        
        return student_list

    def update_hints(self):
        if self.student_hashkey is not None:
            (student_id, course_id, set_id, problem_id) = self.student_hashkey
            info = self.student_info(student_id,
                                     course_id,
                                     set_id,
                                     problem_id)
            self._sockjs_handler.send_student_info(info)


    def student_info(self, student_id, course_id, set_id, problem_id):
        ss = StudentSession.get_student_session(student_id,
                                                course_id,
                                                set_id,
                                                problem_id)
        if ss is not None:
            return _extract_student_info(ss)
            
        return {}

    def notify_answer_update(self, ss):
        """Called when there is an answer update"""
        if self.student_hashkey is not None:
            (student_id, course_id, set_id, problem_id) = self.student_hashkey
            # notification is for me?
            if (student_id == ss.student_id and
                course_id == ss.course_id and
                set_id == ss.set_id and
                problem_id == ss.problem_id):
                info = self.student_info(student_id,
                                         course_id,
                                         set_id,
                                         problem_id)
                self._sockjs_handler.send_student_info(info)
        
    def notify_student_join(self, ss):
        """Called when a student has joined"""
        if self.student_hashkey is not None:
            (student_id, course_id, set_id, problem_id) = self.student_hashkey
            # notification is for me?
            if (student_id == ss.student_id and
                course_id == ss.course_id and
                set_id == ss.set_id and
                problem_id == ss.problem_id):
                info = self.student_info(student_id,
                                         course_id,
                                         set_id,
                                         problem_id)
                self._sockjs_handler.send_student_info(info)
            
    def notify_student_left(self, ss):
        """Called when a student has left"""
        # do nothing
