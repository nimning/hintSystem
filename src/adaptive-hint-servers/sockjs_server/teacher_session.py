import logging

from student_session import StudentSession
from session_storage import SessionStorage

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
                          'pg_file': ss.pg_file,
                          'pg_seed': ss.pg_seed,
                          'hints': ss.hints,
                          'answers': ss.answers,
                          'past_answers': ss.past_answers,
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

      students : set
        Session IDs of students associated with this teacher.

      _sockjs_handler : StudentSockJSHandler
        SockJS handler
        
    """
    active_sessions = set()
    student_assignment = {}

    # Session storage with 24 hours time-out
    storage = SessionStorage(timeout=60*24)

    def __init__(self, teacher_id, sockjs_handler):
        self.teacher_id = teacher_id
        self._sockjs_handler = sockjs_handler
        self.students = set()
        
    def _remove_timedout_students(self):
        """Remove timed-out students from the student set"""
        for session_id in list(self.students):
            if StudentSession.storage.is_timedout(session_id):
                self.students.remove(session_id)

    def request_student(self, session_id):
        """Try to add a student with the session id to the set"""
        if session_id not in TeacherSession.student_assignment:
            TeacherSession.student_assignment[session_id] = self.teacher_id

    def release_student(self, session_id):
        """Remove a student with the session id from the set"""
        if (session_id in TeacherSession.student_assignment and
            TeacherSession.student_assignment[session_id] == self.teacher_id):
            del TeacherSession.student_assignment[session_id]

    def my_students(self):
        """List all my students"""
        student_list = []
        for session_id in list(TeacherSession.student_assignment):
            if TeacherSession.student_assignment[session_id] == self.teacher_id:
                if StudentSession.storage.is_timedout(session_id):
                    del TeacherSession.student_assignment[session_id]
                else:
                    student_list.append(session_id)
        return _student_info(student_list)

    def unassigned_students(self):
        """List all unassigned students"""
        student_list = []
        for ss in list(StudentSession.active_sessions):
            if ss.session_id not in TeacherSession.student_assignment:
                student_list.append(ss.session_id)
        return _student_info(student_list)

    def answer_update(self, extended_answer_status):
        """Send 'answer_update' message"""
        self._sockjs_handler.send_answer_update(extended_answer_status)

    def hint_update(self, extended_hint):
        """Send 'hint_update' message"""
        self._sockjs_handler.send_hint_update(extended_hint)

