from tornado import gen, httpclient
from tornado.httputil import url_concat
import logging
import json
import urllib
import base64

from _base_handler import _BaseSockJSHandler
from student_session import StudentSession
from teacher_session import TeacherSession

REST_SERVER = 'http://127.0.0.1:4351'
CHECKANSWER_API = REST_SERVER + '/checkanswer'
PROBLEM_SEED_API = REST_SERVER + '/problem_seed'
PG_PATH_API = REST_SERVER + '/pg_path'
HINTS_API = REST_SERVER + '/hint'

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
        @gen.engine
        def handle_student_join(self, args):
            """Handler for 'student_join'

            'student_join' is sent from the client as the first message
            after the connection has been established. The message also
            includes the client information.
              
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

                # yield and call _perform_student_join
                yield gen.Task(
                    self._perform_student_join,
                    session_id,
                    student_id,
                    course_id,
                    set_id,
                    problem_id)
                                
                logging.info("Student: %s joined"%student_id)
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
                # read args
                boxname = args['boxname']
                value = args['value']

                # shorthand
                ss = self.student_session
        
                # yeild and perform checkanswer
                yield gen.Task(self._perform_checkanswer,
                               boxname,
                               value)

                logging.info("%s updated %s to %s"%(
                    ss.student_id, boxname, value))
            except:
                logging.exception('Exception in student_answer handler')

    def _perform_student_join(self, session_id, student_id, course_id,
                              set_id, problem_id, callback=None):
        """
          Returns a new instance of StudentSession
        """
        # create an instance of StudentSession
        self.student_session = StudentSession(session_id,
                                              student_id,
                                              course_id,
                                              set_id,
                                              problem_id,
                                              self)

        # shorthand
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
                                
        # add to active student list.
        StudentSession.active_sessions.add(ss)

        # send assigned hints.
        self.send_hints(ss.hints)

        # send previously entered answers.
        self.send_answer_status(ss.current_answers)

        # notify the teachers that a student has joined.
        for ts in TeacherSession.active_sessions:
            ts.notify_student_join()

        # done
        callback()


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

        answer_status = {}
        
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
            
        # check hint answer
        elif boxname.startswith('Hint'):
            # get hint pg
            url = url_concat(HINTS_API, {
                'course': ss.course_id,
                'hint_id': int(boxname[4:])
                })
            response = http_client.fetch(url)
            hint = json.loads(response.body)
            
            pg_file = base64.b64encode(
                hint['pg_header'] + '\n' +
                hint['pg_text'] + '\n' +
                hint['pg_footer'])
            
            response = http_client.fetch(CHECKANSWER_API,
                                         method='POST',
                                         headers=None,
                                         body=urllib.urlencode({
                                             'pg_file' : pg_file,
                                             'seed' : ss.pg_seed,
                                             'AnSwEr0001' : value 
                                             }))
            
            result_json = json.loads(response.body)['AnSwEr0001']
            answer_status = { 'boxname': boxname,
                              'is_correct': result_json['is_correct'],
                              'error_msg': result_json['error_msg'],
                              'entered_value': value }
        else:
            raise ValueError('Boxname must begin with AnSwEr or Hint')

        # post-process the answer status
        if len(answer_status) > 0:
            # update the database
            timestamp = ss.update_answer(boxname, answer_status)
        
            # send the status to client
            self.send_answer_status([answer_status,])

            # also send status to teachers
            ext_ans = {
                'session_id': ss.session_id,
                'course_id': ss.course_id,
                'set_id': ss.set_id,
                'problem_id': ss.problem_id,
                'timestamp': timestamp,
                'boxname': boxname,
                'is_correct': answer_status['is_correct'] }

            for ts in TeacherSession.active_sessions:
                ts.notify_answer_update(ext_ans)

        # done
        callback()


    def send_answer_status(self, answer_statuses):
        """Send a list of answer statuses to the client"""
        if not isinstance(answer_statuses, list):
            answer_statuses = [answer_statuses,]
        self.send_message('answer_status', answer_statuses)


    def send_hints(self, hints):
        """Send a list of hints to the client"""
        if not isinstance(hints, list):
            hints = [hints,]
        self.send_message('hints', hints)

                     
    def on_open(self, info):
        """Callback for when a student is connected"""
        logging.info("%s connected"%info.ip)

        
    def on_close(self):
        """Callback for when a student is disconnected"""
        ss = self.student_session

        # Remove the session from active list
        StudentSession.active_sessions.remove(ss)

        if len(ss.student_id) > 0:
            logging.info("%s left"%ss.student_id)
                
        logging.info("%s disconnected"%self.session.conn_info.ip)
            
