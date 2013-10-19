import logging
import datetime
import time
from threading import Thread

from hint_rest_api import HintRestAPI

logger = logging.getLogger(__name__)

def _datetime_to_timestamp(dt):
    return time.mktime(dt.timetuple())

class StudentSession(object):
    """Provides an interface to each student session connected.

    Class variables
    ---------------
     all_sessions : dict of StudentSession
        All student sessions
    
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
       Current answers on the student's browser

     _sockjs_handler : StudentSockJSHandler
       SockJS handler
     
    """
    all_sessions = dict()

    @staticmethod
    def get_student_session(student_id, course_id, set_id, problem_id):
        hashkey = (student_id, course_id, set_id, problem_id)
        return StudentSession.all_sessions.get(hashkey, None) 

    @staticmethod
    def update_student_session(ss):
        hashkey = (ss.student_id, ss.course_id, ss.set_id, ss.problem_id)
        StudentSession.all_sessions[hashkey] = ss

    def __init__(self, session_id, student_id, course_id,
                 set_id, problem_id, sockjs_handler):
        self.session_id = session_id
        self.student_id = student_id
        self.course_id = course_id
        self.set_id = set_id
        self.problem_id = problem_id
        self.pg_file = None
        self.pg_seed = None
        self.summary = None
        self._sockjs_handler = sockjs_handler
        # internal cache
        self._answers = None
        self._hints = None
        

    @property
    def hints(self):
        if self._hints is None:
            self._hints = HintRestAPI.get_user_problem_hints(self.student_id,
                                                             self.course_id,
                                                             self.set_id,
                                                             self.problem_id)
        return self._hints
    
    @property
    def answers(self):
        if self._answers is None:
            self._answers = HintRestAPI.get_realtime_answers(self.student_id,
                                                             self.course_id,
                                                             self.set_id,
                                                             self.problem_id)
        return self._answers

    @property
    def current_answers(self):
        answer_dict = {}
        # recontruct the current answers
        for answer in self.answers:
            answer_dict[answer['boxname']] = answer        
        return answer_dict.values()

    def update_hints(self):
        """Update the hints displayed on the client"""
        try:            
            # invalidate internal cache
            self._hints = None
            if self._sockjs_handler is not None:
                self._sockjs_handler.send_hints(self.hints)
                self._sockjs_handler.send_answer_status(self.current_answers)

            # update summary in another thread
            Thread(target=self.update_summary).start()

        except:
            logging.exception("Exception in update_hints()")

    def update_answer(self, boxname, answer_status):
        """Update an answer box """
        # update current answer
        HintRestAPI.post_realtime_answer(self.student_id,
                                         self.course_id,
                                         self.set_id,
                                         self.problem_id,
                                         answer_status)
                    
        # invalidate internal cache
        self._answers = None

        # update summary in another thread
        Thread(target=self.update_summary).start()

    def update_summary(self):
        solved = {}
        total_tries = {}
        recent_tries = {}
        time_lastincorrect = None
        current_time = _datetime_to_timestamp(datetime.datetime.now())
        for answer in self.answers:
            if answer['boxname'].startswith('AnSwEr'):
                part = answer['boxname']
                solved[part] = answer['is_correct']
                if not answer['is_correct']:
                    time_lastincorrect = answer['timestamp']
                    total_tries[part] = total_tries.get(part, 0) + 1
                    # recent = 15 minute
                    if ((current_time - answer['timestamp']) < 15 * 60):
                        recent_tries[part] = recent_tries.get(part, 0) + 1

        problem_solved = all(solved.values())
        sum_total_tries = 0
        sum_recent_tries = 0
        for part in solved:
            if not solved[part]:
                sum_total_tries += total_tries.get(part, 0)
                sum_recent_tries += recent_tries.get(part, 0)

        time_lasthint = None
        if len(self.hints) > 0:
            time_lasthint = self.hints[-1]['timestamp']

        if problem_solved:
            time_lastincorrect = None
            sum_total_tries = None
            sum_recent_tries = None

        self.summary = { 'student_id': self.student_id,
                         'course_id': self.course_id,
                         'set_id': self.set_id,
                         'problem_id': self.problem_id,
                         'is_online': (self._sockjs_handler is not None),
                         'problem_solved' : problem_solved,
                         'total_tries' : sum_total_tries,
                         'recent_tries' : sum_recent_tries,
                         'time_lastincorrect' : time_lastincorrect,
                         'time_lasthint' : time_lasthint }

