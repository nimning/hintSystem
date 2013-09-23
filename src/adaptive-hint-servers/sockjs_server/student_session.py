import logging
import datetime
import time
from threading import Thread

from session_storage import SessionStorage
from fake_db import FakeDB

def _datetime_to_timestamp(dt):
    return time.mktime(dt.timetuple())

class StudentSession(object):
    """Provides an interface to each student session connected.

    Class variables
    ---------------
      active_sessions : set of StudentSession
        Set of all connected students

      storage : SessionStorage
        Storage for resuming from disconnection
    
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
       PG file path on the server
       
     pg_seed : int
       Random seed

     hints : list
       Hints assigned to the student

     answers : list
       Student's answers (past and current) with timestamps

     current_answers : list
       Current answers on student's browser

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
        self.pg_file = None
        self.pg_seed = None
        self._sockjs_handler = sockjs_handler

    @property
    def hints(self):
        return FakeDB.get_hints(self.student_id,
                                self.course_id,
                                self.set_id,
                                self.problem_id)
    
    @property
    def answers(self):
        return FakeDB.get_answers(self.student_id,
                                  self.course_id,
                                  self.set_id,
                                  self.problem_id)

    @property
    def current_answers(self):
        answer_dict = {}
        # recontruct the current answers
        for answer in self.answers:
            answer_dict[answer['boxname']] = answer        
        return answer_dict.values()

    def reload_hints(self):
        """Update the hints displayed on the client"""
        def _perform_send_hints():
            self._sockjs_handler.send_hints(self.hints)
            
        Thread(target=_perform_send_hints).start()

    def update_answer(self, boxname, answer_status):
        """Update an answer box

        *Blocked until complete*

        Returns
        -------
          timestamp of the updated answer.
        """
        # Insert a timestamp
        answer_status['timestamp'] = _datetime_to_timestamp(
            datetime.datetime.now())

        # update current answer
        FakeDB.add_answer(self.student_id,
                          self.course_id,
                          self.set_id,
                          self.problem_id,
                          answer_status)

        return answer_status['timestamp']
