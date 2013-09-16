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
       
     hints : set
       Hints given in this session [PERSIST]
       
     answers : dict
       Current answers on student's browser [PERSIST] 
    """
    
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
        
        self.hints = storage.load('hints',
                                  session_id,
                                  course_id,
                                  set_id,
                                  problem_id)
        if self.hints is None:
            self.hints = set()

        self.answers = storage.load('answers',
                                    session_id,
                                    course_id,
                                    set_id,
                                    problem_id)
        if self.answers is None:
            self.answers = {}

        
    def save_session(self):
        """Save session data to storage"""
        storage.save('pg_file',
                     session_id,
                     course_id,
                     set_id,
                     problem_id,
                     self.pg_file)

        storage.save('pg_seed',
                     session_id,
                     course_id,
                     set_id,
                     problem_id,
                     self.pg_seed)

        storage.save('hints',
                     session_id,
                     course_id,
                     set_id,
                     problem_id,
                     self.hints)

        storage.save('answers',
                     session_id,
                     course_id,
                     set_id,
                     problem_id,
                     self.answers)

    def add_hint(self, hintbox_id, location, hint_html):
        """Adds a hint"""
        hint = { 'hint_html': hint_html,
                 'location': location,
                 'hintbox_id': hintbox_id }
        self.hints.add(hint)
        self._sockjs_handler.send_hints()
        
    def remove_hint(self, hintbox_id):
        """Removes a hint"""
        for hint in list(self.hints):
            if hint['hintbox_id'] == hintbox_id:
                self.hints.remove(hint)
        self._sockjs_handler.send_hints()
