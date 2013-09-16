from tornado import gen, httpclient
import logging
import json
import urllib

from common import ActiveSockJSClients, _BaseSockJSHandler, pack_message

CHECKANSWER_API = 'http://127.0.0.1:4351/checkanswer'
        
class StudentSockJSHandler(_BaseSockJSHandler):
    """
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
        super(StudentConnection, self).__init__(*args, **kwargs)
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
              src/adaptive-hint-servers/sockjs_server#student-client---server

            args
            ----
              * session_id (req)
              * student_id (req)
              * course_id (req)
              * set_id (req)
              * problem_id (req)
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
                
                # add the student session to the active client list
                ActiveSockJSClients.students.add(self)
                logging.info("%s signed in"%self.student_id)
                
                # also relay 'student_join' to teachers
                for teacher in ActiveSockJSClients.teachers:
                    teacher.send(pack_message('student_join', args))
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
              * boxname (req)
              * value (req)
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
                            answer_status = self._perform_checkanswer(args)
                        else:
                            answer_status = self._perform_checkanswer_hint(args)
                            
                        # update session
                        ss.answers[boxname] = answer_status

                        # send the status to client
                        self.send_answer_status([answer_status,])

            except:
                logging.exception('Exception in student_answer handler')

                
    def _perform_checkanswer_hint(self, boxname, value):
        import random
        result = { 'boxname': boxname,
                   'entered_value': value }
        if random.random() < 0.5:
            result['is_correct'] = True
        else:
            result['is_correct'] = False

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
        http_client = httpclient.AsyncHTTPClient()
        # Hacky way to get PG path
        # TODO: get pg_file and pg_seed from DB
        path_prefix = ('/opt/webwork/libraries/' +
                       'webwork-open-problem-library/OpenProblem')
        pg_file = path_prefix + self.student_session.pg_file
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
                          'correct_value': result_json['correct_value']
                          'entered_value': value }
        return answer_status

                    
    def send_answer_status(self, answer_statuses):
        if not isinstance(answer_statuses, list):
            answer_statuses = [answer_statuses,]
        self.send(pack_message('answer_status', answer_statuses))


    def send_hints(self, hints):
        if not isinstance(hints, list):
            hints = [hints,]
        self.send(pack_message('hints', hints))


    def on_open(self, info):
        """Callback for when a student is connected"""
        logging.info("%s connected"%info.ip)

                        
    def on_close(self):
        """Callback for when a student is disconnected

        Also sends 'student_left' message to active teachers.
        
        """
        ss = self.student_session

        # save state of the session
        ss.save_session()

        # Remove the session from active list
        ActiveClients.students.remove(ss)
        
        if len(ss.student_id) > 0:
            logging.info("%s disconnected"%ss.student_id)
        else:
            logging.info("%s disconnected"%self.session.conn_info.ip)
            
        # Send 'student_left' to active teachers
        args = { 'session_id': ss.session_id,
                 'student_id': ss.student_id,
                 'course_id': ss.course_id,
                 'set_id': ss.set_id,
                 'problem_id': ss.problem_id }

        for teacher in ActiveSockJSClients.teachers:
            teacher.send(pack_message('student_left', args))
