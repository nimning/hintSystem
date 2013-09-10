from tornado import gen, httpclient
import logging
import json

from common import ActiveClients, _BaseConnection, pack_message

class StudentConnection(_BaseConnection):
    """Student SockJS Connection

    This class handles messages received from the student clients.

    A new handler for a message can be defined as follows:

    def __init__(self, *args, **kwargs):
        
        ...

        @self.add_handler('new_message')
        def handle_new_message(self, args):
            pass

        ...

    Attributes:
        student_id : string
           Student ID
        course_id : string
           Course ID
        set_id : string
           Problem set ID
        problem_id : string
           Problem ID
        problem_body : string
           HTML of the current problem
    """ 
   
    def __init__(self, *args, **kwargs):
        super(StudentConnection, self).__init__(*args, **kwargs)
        self.student_id = ''
        self.course_id = ''
        self.set_id = ''
        self.problem_id = ''
        self.problem_body = ''
        self.pg_file = ''

        @self.add_handler('signin')
        def handle_signin(self, args):
            """Handler for 'signin'

            'signin' is sent from the client as the first message
            after the connection has established. The message contains
            the client information.

            When 'signin' is received, the following tasks are performed.
              * Update information about the client e.g. student_id, problem_id.
              * Broadcast 'student_joined' to the active teachers.

            More detail:
              https://github.com/yoavfreund/Webwork_AdaptiveHints/tree/master/
              src/adaptive-hint-servers/sockjs_server#student-client---server
            
            """
            try:
                # required 
                self.student_id = args['student_id']
                self.course_id = args['course_id']
                self.set_id = args['set_id']
                self.problem_id = args['problem_id']

                # optional
                self.problem_body = args.get('problem_body', '')
                self.pg_file = args.get('pg_file', '')

                # Arguments are OK. Add this student to the list.
                ActiveClients.students.add(self)
                logging.info("%s signed in"%self.student_id)
                
                # Broadcast 'student_joined' to teachers
                self.broadcast(ActiveClients.teachers,
                               pack_message('student_joined', args))
            except KeyError:
                self.session.close()
                
        @self.add_handler('newstring')
        def handle_newstring(self, args):
            """Handler for 'newstring'

            'newstring' is sent from the client when one of the answer boxes
            is updated.

            When a 'newstring' is received, the following tasks are performed.
              * Forward the message to active teachers.
              * Initiate answer checking routines.

            More detail:
              https://github.com/yoavfreund/Webwork_AdaptiveHints/tree/master/
              src/adaptive-hint-servers/sockjs_server#student-client---server
            """
            boxname = args['boxname']
            value = args['value']
            logging.info("%s updated %s to %s"%(self.student_id,
                                                boxname,
                                                value))

            # DEBUG: Check the answers
            if (self.course_id == 'demo'):
                if len(value) > 0: 
                    if boxname.startswith('AnSwEr'):
                        self.perform_checkanswer(args)
                    else:
                        self.perform_checkanswer_hint(args)
            
            # broadcast 'newstring' to teachers
            self.broadcast(ActiveClients.teachers,
                           pack_message('newstring', args))


    def perform_checkanswer_hint(self, args):
        import random
        result = { 'boxname': args['boxname'] }

        if random.random() < 0.5:
            result['is_correct'] = True
            self.send(pack_message('answer_status', result))
        else:
            result['is_correct'] = False
            self.send(pack_message('answer_status', result))
            

    @gen.engine
    def perform_checkanswer(self, args):
        import urllib
        http_client = httpclient.AsyncHTTPClient()
        # Hacky way to get PG path
        path_prefix = '/opt/webwork/libraries/webwork-open-problem-library/OpenProblem'
        post_data = {
            'pg_file' : path_prefix + self.pg_file,
            'seed' : 123,   
            }
        post_data[args['boxname']] = args['value']
        body = urllib.urlencode(post_data)
        response = yield http_client.fetch("http://localhost:4351/checkanswer",
                                           method='POST',
                                           headers=None,
                                           body=body)
        result_json = json.loads(response.body)[args['boxname']]
        # parse the reponse
        result = { 'boxname': args['boxname'],
                   'is_correct': result_json['is_correct'],
                   'error_msg': result_json['error_msg'],
                   'correct_value': result_json['correct_value']
                   }
        self.send(pack_message('answer_status', result))
        
    def on_open(self, info):
        """Callback for when a student is connected"""
        logging.info("%s connected"%info.ip)
                        
    def on_close(self):
        """Callback for when a student is disconnected

        Also sends 'student_left' message to active teachers.
        
        """
        ActiveClients.students.remove(self)
        if len(self.student_id) > 0:
            logging.info("%s disconnected"%self.student_id)
        else:
            logging.info("%s disconnected"%self.session.conn_info.ip)
            
        # Broadcast 'student_left' to teachers
        args = { 'student_id': self.student_id }
        self.broadcast(ActiveClients.teachers,
                       pack_message('student_left', args))
