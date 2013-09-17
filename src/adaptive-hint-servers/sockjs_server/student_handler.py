from tornado import gen, httpclient
import logging
import json
import urllib

from _base_handler import _BaseSockJSHandler
from student_session import StudentSession

CHECKANSWER_API = 'http://127.0.0.1:4351/checkanswer'
        
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
                # create a new instace of StudentSession
                self.student_session = StudentSession(args['session_id'],
                                                      args['student_id'],
                                                      args['course_id'],
                                                      args['set_id'],
                                                      args['problem_id'],
                                                      self)
                
                # shorthand
                ss = self.student_session
                
                # TODO: these should be obtained from DB instead
                if ss.pg_file is None:
                    ss.pg_file = args.get('pg_file', None)

                if ss.pg_seed is None:
                    ss.pg_seed = args.get('pg_seed', None)
                
                # add the student session to the list
                StudentSession.active_sessions.add(ss)

                # send previoud hints
                self.send_hints(ss.hints.values())

                # send previous answers
                self.send_answer_status(ss.answers.values())

                logging.info("Student: %s joined"%ss.student_id)
            except:
                logging.exception("Exception in student_join handler")
                self.session.close()
                
        @self.add_handler('student_answer')
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
                if ss.course_id == 'demo':
                    if len(value) > 0:
                        if boxname.startswith('AnSwEr'):
                            self._perform_checkanswer(boxname, value)
                        else:
                            self._perform_checkanswer_hint(boxname, value)
            except:
                logging.exception('Exception in student_answer handler')


    def _perform_checkanswer_hint(self, boxname, value):
        # TODO: implement this
        import random
        answer_status = { 'boxname': boxname,
                          'entered_value': value }
        if random.random() < 0.5:
            answer_status['is_correct'] = True
        else:
            answer_status['is_correct'] = False
                            
        # update session
        self.student_session.answers[boxname] = answer_status
        
        # send the status to client
        self.send_answer_status([answer_status,])

            
    @gen.engine
    def _perform_checkanswer(self, boxname, value):
        """
          Returns 'answer_status' that contains the following arguments:
            * boxname
            * is_correct
            * error_msg
            * correct_value
            * entered_value
        """
        ss = self.student_session
        
        http_client = httpclient.AsyncHTTPClient()
        # Hacky way to get PG path
        # TODO: get pg_file and pg_seed from DB
        path_prefix = ('/opt/webwork/libraries/' +
                       'webwork-open-problem-library/OpenProblem')
        pg_file = path_prefix + ss.pg_file
        pg_seed = 123
        
        post_data = { 'pg_file' : pg_file,
                      'seed' : pg_seed,
                      boxname : value }
        
        response = yield http_client.fetch(CHECKANSWER_API,
                                           method='POST',
                                           headers=None,
                                           body=urllib.urlencode(post_data))
        
        result_json = json.loads(response.body)[boxname]
        answer_status = { 'boxname': boxname,
                          'is_correct': result_json['is_correct'],
                          'error_msg': result_json['error_msg'],
                          'correct_value': result_json['correct_value'],
                          'entered_value': value }

        # update session data
        ss.update_answer(boxname,answer_status)
        
        # send the status to client
        self.send_answer_status([answer_status,])

        
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

        # save state of the session
        ss.save_session()

        # Remove the session from active list
        StudentSession.active_sessions.remove(ss)

        if len(ss.student_id) > 0:
            logging.info("%s left"%ss.student_id)
        
        logging.info("%s disconnected"%self.session.conn_info.ip)
            
