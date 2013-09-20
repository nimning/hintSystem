import logging
import datetime
import time

from session_storage import SessionStorage

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

     hints : dict
       Hints given in this session (readonly)
       
     answers : dict
       Current answers on student's browser (readonly)

     past_answers : list
       Student's past (including current) answers with timestamps (readonly)

     _sockjs_handler : StudentSockJSHandler
       SockJS handler
     
    """
    active_sessions = set()

    # Session storage with 30 minutes time-out
    storage = SessionStorage(timeout=30)
    
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
        self._hints = {}
        self._answers = {}
        self._past_answers = []

    @property
    def hints(self):
        return self._hints
    
    @property
    def answers(self):
        return self._answers

    @property
    def past_answers(self):
        return self._past_answers

    def add_hint(self, hintbox_id, location, hint_html):
        """Adds a hint"""
        hint = { 'timestamp': _datetime_to_timestamp(datetime.datetime.now()),
                 'hint_html': hint_html,
                 'location': location,
                 'hintbox_id': hintbox_id }
        self._hints[hintbox_id] = hint
        self._sockjs_handler.send_hints(self.hints.values())
        logging.info("Add a hint to %s"%(self.session_id))
        
    def remove_hint(self, hintbox_id):
        """Removes a hint"""
        del self._hints[hintbox_id]
        self._sockjs_handler.send_hints(self._hints.values())
        logging.info("Remove a hint from %s"%(self.session_id))

    def update_answer(self, boxname, answer_status):
        """Update an answer box"""

        # Insert a timestamp
        answer_status['timestamp'] = _datetime_to_timestamp(
            datetime.datetime.now())

        # update current answer
        self._answers[boxname] = answer_status

        # Update past_answer as well
        self._past_answers.append(answer_status)
        
