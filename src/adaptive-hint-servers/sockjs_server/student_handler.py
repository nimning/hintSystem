from tornado import gen, httpclient
from tornado.httputil import url_concat
import logging
import json
import urllib

from _base_handler import _BaseSockJSHandler
from student_session import StudentSession
from teacher_session import TeacherSession
from session_storage import SessionStorage

CHECKANSWER_API = 'http://127.0.0.1:4351/checkanswer'
PROBLEM_SEED_API = 'http://127.0.0.1:4351/problem_seed'
PG_PATH_API = 'http://127.0.0.1:4351/pg_path'
        
class StudentSockJSHandler(_BaseSockJSHandler):
    """Student SockJS connection handler
    
    This class handles messages received from the student clients.

    A new handler for a message can be defined as follows:

    def __init__(self, *args, **kwargs):   
        ...
        @self.add_handler('new_message')
        def handle_new_message(self, args):
            pass
        ...

    Properties
    ----------
      student_session : StudentSession
        The corresponding instance of StudentSession.
      
    """

    def __load_session(self, session_id, course_id, set_id, problem_id):
        self.student_session = StudentSession.storage.\
                               load(session_id, (course_id, set_id, problem_id))
        
    def __save_session(self):
        ss = self.student_session
        StudentSession.storage.save(ss.session_id,
                                    (ss.course_id, ss.set_id, ss.problem_id),
                                    self.student_session)    
        
    def __init__(self, *args, **kwargs):
        super(StudentSockJSHandler, self).__init__(*args, **kwargs)
        self.student_session = None

        @self.add_handler('student_join')
        def handle_student_join(self, args):
            """Handler for 'student_join'

            'student_join' is sent from the client as the first message
            after the connection has been established. The message also
            includes the client information.

            When 'student_join' is received, the following tasks are performed:
              * Update session information e.g. student_id, problem_id.
              * Relay 'student_join' to all active teachers.
              
            More detail:
              https://github.com/yoavfreund/Webwork_AdaptiveHints/tree/master/
              src/adaptive-hint-servers/sockjs_server#messages-handled-
              by-the-student-server
            
            args
            ----
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
            """
            try:
                # read args
                session_id = args['session_id']
                student_id = args['student_id']
                course_id = args['course_id']
                set_id = args['set_id']
                problem_id = args['problem_id']
                
                # try to resume session
                self.__load_session(session_id, course_id, set_id, problem_id)

                # check if loaded successfully
                if self.student_session is None:
                    # create a new instace of StudentSession
                    self.student_session = StudentSession(session_id,
                                                          student_id,
                                                          course_id,
                                                          set_id,
                                                          problem_id,
                                                          self)
                else:
                    # update sockjs handler
                    self.student_session._sockjs_handler = self
                
                # shorthand
                ss = self.student_session
                                
                # add to active student list
                StudentSession.active_sessions.add(ss)

                # send previous hints
                self.send_hints(ss.hints.values())

                # send previous answers
                self.send_answer_status(ss.answers.values())

                logging.info("Student: %s joined"%ss.student_id)
            except:
                logging.exception("Exception in student_join handler")
                self.session.close()
                
        @self.add_handler('student_answer')
        @gen.engine
        def handle_student_answer(self, args):
            """Handler for 'student_answer'

            'student_answer' is sent from the client when one of the answer
            boxes is updated.

            When a 'newstring' is received, the following tasks are performed.
              * Forward the message to active teachers.
              * Initiate answer checking routines.

            More detail:
              https://github.com/yoavfreund/Webwork_AdaptiveHints/tree/master/
              src/adaptive-hint-servers/sockjs_server#student-client---server

            args
            ----
              * boxname
              * value
            """
            try:
                ss = self.student_session
        
                boxname = args['boxname']
                value = args['value']
                logging.info("%s updated %s to %s"%(
                    ss.student_id, boxname, value))

                # TODO: Only monitor message from demo course
                if ss.course_id == 'demo' and len(value) > 0:
                    answer_status = yield gen.Task(self._perform_checkanswer,
                                                   boxname,
                                                   value)
                    # update session data
                    ss.update_answer(boxname, answer_status)
        
                    # send the status to client
                    self.send_answer_status([answer_status,])

                    # also send status to teachers
                    ans = ss.answers[boxname]
                    ext_ans = {
                        'session_id': ss.session_id,
                        'course_id': ss.course_id,
                        'set_id': ss.set_id,
                        'problem_id': ss.problem_id,
                        'timestamp': ans['timestamp'],
                        'boxname': ans['boxname'],
                        'entered_value': ans['entered_value'],
                        'is_correct': ans['is_correct'] }
                    for ts in TeacherSession.active_sessions:
                        ts.answer_update(ext_ans)
                    
            except:
                logging.exception('Exception in student_answer handler')

            
    def _perform_checkanswer(self, boxname, value, callback=None):
        """
          Returns 'answer_status' that contains the following arguments:
            * boxname
            * is_correct
            * error_msg
            * correct_value
            * entered_value
        """
        ss = self.student_session
        http_client = httpclient.HTTPClient()
            
        # get PG file path
        if ss.pg_file is None:
            url = url_concat(PG_PATH_API, {
                'course': ss.course_id,
                'set_id': ss.set_id,
                'problem_id': ss.problem_id
                })
            response = http_client.fetch(url)
            ss.pg_file = json.loads(response.body)
            
        # get problem seed
        if ss.pg_seed is None:
            url = url_concat(PROBLEM_SEED_API, {
                'course': ss.course_id,
                'set_id': ss.set_id,
                'problem_id': ss.problem_id,
                'user_id': ss.student_id
                })
            response = http_client.fetch(url)
            ss.pg_seed = int(response.body)

        # check problem answer
        if boxname.startswith('AnSwEr'):
            response = http_client.fetch(CHECKANSWER_API,
                                         method='POST',
                                         headers=None,
                                         body=urllib.urlencode({
                                             'pg_file' : ss.pg_file,
                                             'seed' : ss.pg_seed,
                                             boxname : value 
                                             }))
            
            result_json = json.loads(response.body)[boxname]
            answer_status = { 'boxname': boxname,
                              'is_correct': result_json['is_correct'],
                              'error_msg': result_json['error_msg'],
                              'entered_value': value }

            return callback(answer_status)
        
        else:
            # TODO: Implement this
            import random
            answer_status = { 'boxname': boxname,
                              'entered_value': value }
            if random.random() < 0.5:
                answer_status['is_correct'] = True
            else:
                answer_status['is_correct'] = False

            return callback(answer_status)

        
    def send_answer_status(self, answer_statuses):
        if not isinstance(answer_statuses, list):
            answer_statuses = [answer_statuses,]
        self.send_message('answer_status', answer_statuses)


    def send_hints(self, hints):
        if not isinstance(hints, list):
            hints = [hints,]
        self.send_message('hints', hints)

                     
    def on_open(self, info):
        """Callback for when a student is connected"""
        logging.info("%s connected"%info.ip)

        
    def on_close(self):
        """Callback for when a student is disconnected"""
        ss = self.student_session

        if ss is not None:
            # Remove the session from active list
            StudentSession.active_sessions.remove(ss)

            # remove reference to this handler
            ss._sockjs_handler = None

            # save session
            self.__save_session()

            if len(ss.student_id) > 0:
                logging.info("%s left"%ss.student_id)
                
        logging.info("%s disconnected"%self.session.conn_info.ip)
            
