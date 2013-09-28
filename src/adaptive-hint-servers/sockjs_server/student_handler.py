from tornado import gen
import logging
import base64

from hint_rest_api import HintRestAPI
from _base_handler import _BaseSockJSHandler
from student_session import StudentSession
from teacher_session import TeacherSession

logger = logging.getLogger(__name__)

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
                                
                logger.info("Student: %s joined"%student_id)
            except:
                logger.exception("Exception in student_join handler")
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

                logger.info("%s updated %s to %s"%(
                    ss.student_id, boxname, value))
            except:
                logger.exception('Exception in student_answer handler')


        @self.add_handler('hint_feedback')
        def handle_hint_feedback(self, args):
            """Handler for 'hint_feedback'

            args
            ----
              * hintbox_id
              * feedback
            """
            try:
                # read args
                hintbox_id = args['hintbox_id']
                feedback = args['feedback']

                # shorthand
                ss = self.student_session
                
                logger.info("%s updated feedback for %s to %s"%(
                    ss.student_id, hintbox_id, feedback))
            except:
                logger.exception('Exception in hint_feedback handler')
                

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
        
        # get PG file path
        if ss.pg_file is None:
            ss.pg_file = HintRestAPI.pg_path(ss.course_id,
                                             ss.set_id,
                                             ss.problem_id)
            
        # get problem seed
        if ss.pg_seed is None:
            ss.pg_seed = HintRestAPI.problem_seed(ss.student_id,
                                                  ss.course_id,
                                                  ss.set_id,
                                                  ss.problem_id)
                                
        # add to active student list.
        StudentSession.active_sessions.add(ss)

        # send assigned hints.
        self.send_hints(ss.hints)

        # send previously entered answers.
        self.send_answer_status(ss.current_answers)

        # notify the teachers that a student has joined.
        for ts in TeacherSession.active_sessions:
            ts.notify_student_join(ss)

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
        answer_status = {}
        
        # check problem answer
        if boxname.startswith('AnSwEr'):
            answer_status = HintRestAPI.checkanswer(ss.pg_file,
                                                    ss.pg_seed,
                                                    boxname,
                                                    value)         
        # check hint answer
        elif boxname.startswith('Hint'):
            # get hint pg
            hint = HintRestAPI.hint(ss.course_id, int(boxname[4:]))
            
            pg_file = base64.b64encode(
                hint['pg_header'] + '\n' +
                hint['pg_text'] + '\n' +
                hint['pg_footer'])

            # check using temporary boxname 'AnSwEr0001' 
            answer_status = HintRestAPI.checkanswer(pg_file,
                                                    ss.pg_seed,
                                                    'AnSwEr0001',
                                                    value)
            # set boxname to the hint boxname
            answer_status['boxname'] = boxname
            
        # unknown box name    
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
                'student_id': ss.student_id,
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

        # Make sure we don't send the solution to the student
        #  and we will only send statuses of the 'Hint' boxes.
        clean_answer_statuses = []
        for answer in answer_statuses:
            if answer['boxname'].startswith('Hint'):
                answer = answer.copy()
                answer.pop('correct_value', None)
                clean_answer_statuses.append(answer)
            
        self.send_message('answer_status', clean_answer_statuses)


    def send_hints(self, hints):
        """Send a list of hints to the client"""
        if not isinstance(hints, list):
            hints = [hints,]
        self.send_message('hints', hints)

                     
    def on_open(self, info):
        """Callback for when a student is connected"""
        logger.info("%s connected"%info.ip)

        
    def on_close(self):
        """Callback for when a student is disconnected"""
        ss = self.student_session

        # Remove the session from active list
        StudentSession.active_sessions.remove(ss)

        # notify teachers
        for ts in TeacherSession.active_sessions:
            ts.notify_student_left(ss)

        if len(ss.student_id) > 0:
            logger.info("%s left"%ss.student_id)
                
        logger.info("%s disconnected"%self.session.conn_info.ip)
            
