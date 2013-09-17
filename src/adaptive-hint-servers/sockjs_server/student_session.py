from tornado import httpclient
import logging
import urllib

from session_storage import SessionStorage

storage = SessionStorage(timeout=10)

class StudentSession(object):
    """Provides an interface to each student session connected.

    Class variables
    ---------------
      connected_students : set of StudentSession
        Set of all connected students
    
    Properties
    ----------
     session_id : string
       Webwork session ID
       
     student_id : string
       Webwork student ID
       
     course_id : string
       Webwork course ID
       
     set_id : string
       Webwork set ID
       
     problem_id : string
       Webwork problem ID
              
     pg_file : string
       PG file path on the server [PERSIST]
       
     pg_seed : int
       Random seed [PERSIST]

     _hints : dict
       Hints given in this session [PERSIST]
       
     _answers : dict
       Current answers on student's browser [PERSIST]

     _sockjs_handler : StudentSockJSHandler
       SockJS handler
     
    """

    active_sessions = set()
    
    def __init__(self, session_id, student_id, course_id,
                 set_id, problem_id, sockjs_handler):
        self.session_id = session_id
        self.student_id = student_id
        self.course_id = course_id
        self.set_id = set_id
        self.problem_id = problem_id
        self._sockjs_handler = sockjs_handler

        self.pg_file = storage.load('pg_file',
                                    session_id,
                                    course_id,
                                    set_id,
                                    problem_id)
        
        self.pg_seed = storage.load('pg_seed',
                                    session_id,
                                    course_id,
                                    set_id,
                                    problem_id)

        
        self._hints = storage.load('hints',
                                   session_id,
                                   course_id,
                                   set_id,
                                   problem_id)
        if self._hints is None:
            self._hints = {}

        self._answers = storage.load('answers',
                                     session_id,
                                     course_id,
                                     set_id,
                                     problem_id)
        if self._answers is None:
            self._answers = {}

    @property
    def hints(self):
        return self._hints
    
    @property
    def answers(self):
        return self._answers
        
    def save_session(self):
        """Save session data to storage"""
        storage.save('pg_file',
                     self.session_id,
                     self.course_id,
                     self.set_id,
                     self.problem_id,
                     self.pg_file)

        storage.save('pg_seed',
                     self.session_id,
                     self.course_id,
                     self.set_id,
                     self.problem_id,
                     self.pg_seed)

        storage.save('hints',
                     self.session_id,
                     self.course_id,
                     self.set_id,
                     self.problem_id,
                     self._hints)

        storage.save('answers',
                     self.session_id,
                     self.course_id,
                     self.set_id,
                     self.problem_id,
                     self._answers)

    def add_hint(self, hintbox_id, location, hint_html):
        """Adds a hint"""
        hint = { 'hint_html': hint_html,
                 'location': location,
                 'hintbox_id': hintbox_id }
        self._hints[hintbox_id] = hint
        
        storage.save('hints',
                     self.session_id,
                     self.course_id,
                     self.set_id,
                     self.problem_id,
                     self._hints)

        self._sockjs_handler.send_hints(self.hints.values())
        
    def remove_hint(self, hintbox_id):
        """Removes a hint"""
        del self._hints[hintbox_id]

        storage.save('hints',
                     self.session_id,
                     self.course_id,
                     self.set_id,
                     self.problem_id,
                     self._hints)

        self._sockjs_handler.send_hints(self._hints.values())

    def update_answer(self, boxname, answer_status):
        """Update an answer box"""
        self._answers[boxname] = answer_status

        storage.save('answers',
                     self.session_id,
                     self.course_id,
                     self.set_id,
                     self.problem_id,
                     self._answers)
