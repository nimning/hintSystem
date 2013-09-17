import logging

from _base_handler import _BaseSockJSHandler
from student_session import StudentSession

class TeacherSockJSHandler(_BaseSockJSHandler):
    """Teacher SockJS connection handler

    This class handles messages received from the teacher clients.

    A new handler for a message can be defined as follows:

    def __init__(self, *args, **kwargs):        
        ...
        @self.add_handler('new_message')
        def handle_new_message(self, args):
            pass
        ...

    Properties
    ----------
        teacher_id : string
           Teacher ID
           
    """ 
    def __init__(self, *args, **kwargs):
        super(TeacherSockJSHandler, self).__init__(*args, **kwargs)
        self.teacher_id = ''
        
        @self.add_handler('teacher_join')
        def handle_teacher_join(self, args):
            """Handler for 'teacher_join'

            'teacher_join' is sent from the client as the first message
            after the connection has established. The message contains
            the client information.

            args
            ----
              teacher_id : string
                Teacher ID
            """
            try:
                self.teacher_id = args['teacher_id']
                logging.info("Teacher: %s joined"%self.teacher_id)
            except:
                logging.exception("Exception in teacher_join handler")
                self.session.close()

        @self.add_handler('list_students')
        def handle_list_student(self, args):
            """Handler for 'list_students'

            Requests a list of all active students.

            args
            ----
              course_id : string
                Webwork course ID
            
            """
            # TODO: filter session using 'course_id'
            sessions = [{ 'session_id': ss.session_id,
                          'student_id': ss.student_id,
                          'course_id': ss.course_id,
                          'set_id': ss.set_id,
                          'problem_id': ss.problem_id,
                          'hints': ss.hints,
                          'answers': ss.answers,
                          'pg_file': ss.pg_file,
                          'pg_seed': ss.pg_seed }
                        for ss in StudentSession.active_sessions]
            self.send_message('student_list', sessions)

        @self.add_handler('add_hint')
        def handle_add_hint(self, args):
            """Handler for 'add_hint'

            Add a hint to a student's client.

            args
            ----
              session_id : string
                Webwork Session ID

              course_id : string
                Webwork course ID
              
              set_id : string
                Webwork set ID
                
              problem_id : string
                Webwork problem ID

              location : string
                Hint location

              hintbox_id : string
                Hint answer box ID
                
              hint_html : string
                HTML snippet of the hint
              
            """
            try:
                session_id = args['session_id']
                course_id = args['course_id']
                set_id = args['set_id']
                problem_id = args['problem_id']
                location = args['location']
                hintbox_id = args['hintbox_id']
                hint_html = args['hint_html']
                
                for ss in StudentSession.active_sessions:
                    if (session_id == ss.session_id and
                        course_id == ss.course_id and
                        set_id == ss.set_id and
                        problem_id == ss.problem_id):
                        ss.add_hint(hintbox_id, location, hint_html)
            except:
                logging.exception("Exception add_hint")
