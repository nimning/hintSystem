import logging

from _base_handler import _BaseSockJSHandler
from student_session import StudentSession
from teacher_session import TeacherSession

logger = logging.getLogger(__name__)

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
        teacher_session : TeacherSession
           Teacher session
           
    """
    def __init__(self, *args, **kwargs):
        super(TeacherSockJSHandler, self).__init__(*args, **kwargs)
        self.teacher_session = None
                
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
                # read args
                teacher_id = args['teacher_id']

                # optional args
                student_id = args.get('student_id', None)
                course_id = args.get('course_id', None)
                set_id = args.get('set_id', None)
                problem_id = args.get('problem_id', None)

                # create an instance of TeacherSession
                self.teacher_session = TeacherSession(teacher_id,
                                                      self,
                                                      student_id=student_id,
                                                      course_id=course_id,
                                                      set_id=set_id,
                                                      problem_id=problem_id)
                
                # shorthand
                ts = self.teacher_session

                # add to the active session list
                TeacherSession.active_sessions.add(ts)

                # send student lists
                self.send_unassigned_students(ts.list_unassigned_students())
                self.send_my_students(ts.list_my_students())
                
                logger.info("Teacher: %s joined"%ts.teacher_id)
            except:
                logger.exception("Exception in teacher_join handler")
                self.session.close()

        @self.add_handler('list_students')
        def handle_list_student(self, args):
            """Handler for 'list_students'

            Requests a list of all active students.

            """
            ts = self.teacher_session

            # send student lists
            self.send_unassigned_students(ts.list_unassigned_students())
            self.send_my_students(ts.list_my_students())

            #logger.info("%s: list_students"%ts.teacher_id)
            
        @self.add_handler('add_hint')
        def handle_add_hint(self, args):
            """Handler for 'add_hint'

            Add a hint to a student's client.

            args
            ----
              student_id : string
                Webwork student ID

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
                student_id = args['student_id']
                course_id = args['course_id']
                set_id = args['set_id']
                problem_id = args['problem_id']
                location = args['location']
                hintbox_id = args['hintbox_id']
                hint_html = args['hint_html']

                # shorthand
                ts = self.teacher_session

                # TODO: wrap this with Task()
                timestamp = ts.add_hint(
                    student_id, course_id, set_id, problem_id,
                    location, hintbox_id, hint_html)

                # Ask the client to update its view
                for ss in StudentSession.active_sessions:
                    if (student_id == ss.student_id and
                        course_id == ss.course_id and
                        set_id == ss.set_id and
                        problem_id == ss.problem_id):
                        ss.reload_hints()
                        
                # Notify the teachers about the new hint
                ext_hint = {
                    'student_id': student_id,
                    'course_id': course_id,
                    'set_id': set_id,
                    'problem_id': problem_id,
                    'timestamp': timestamp,
                    'hintbox_id': hintbox_id,
                    'location': location }
                for ts in TeacherSession.active_sessions:
                    ts.notify_hint_update(ext_hint)

                logger.info("%s: add_hint"%ts.teacher_id)
                
            except:
                logger.exception("Exception add_hint")

        @self.add_handler('remove_hint')
        def handle_remove_hint(self, args):
            """Handler for 'remove_hint'

            Remove a hint from a student's client.

            args
            ----
              student_id : string
                Webwork student ID

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
                
            """
            try:
                student_id = args['student_id']
                course_id = args['course_id']
                set_id = args['set_id']
                problem_id = args['problem_id']
                location = args['location']
                hintbox_id = args['hintbox_id']
                
                # shorthand
                ts = self.teacher_session

                # TODO: wrap this with Task()
                ts.remove_hint(student_id, course_id, set_id, problem_id,
                               location, hintbox_id)

                # Ask the clients to reload hints
                for ss in StudentSession.active_sessions:
                    if (student_id == ss.student_id and
                        course_id == ss.course_id and
                        set_id == ss.set_id and
                        problem_id == ss.problem_id):
                        ss.reload_hints()
                        
                # notify the teachers about the update
                ext_hint = {
                    'student_id': student_id,
                    'course_id': course_id,
                    'set_id': set_id,
                    'problem_id': problem_id }
                for ts in TeacherSession.active_sessions:
                    ts.notify_hint_update(ext_hint)

                logger.info("%s: remove_hint"%ts.teacher_id)
                
            except:
                logger.exception("Exception remove_hint")


        @self.add_handler('request_student')
        def handle_request_student(self, args):
            """Handler for 'request_student'

            Request to help a student
            
            args
            ----
              session_id : string
                Webwork session id

            """
            try:
                ts = self.teacher_session
                
                session_id = args['session_id']
                self.teacher_session.request_student(session_id)

                # send student lists
                self.send_unassigned_students(ts.list_unassigned_students())
                self.send_my_students(ts.list_my_students())

                logger.info("%s: request_student"%ts.teacher_id)
                
            except:
                logger.exception("Exception handling 'request_student'")

        @self.add_handler('release_student')
        def handle_release_student(self, args):
            """Handler for 'release_student'

            Release a student to the unassigned pool
            
            args
            ----
              session_id : string
                Webwork session id

            """
            try:
                ts = self.teacher_session
                
                session_id = args['session_id']
                self.teacher_session.release_student(session_id)

                # send student lists
                self.send_unassigned_students(ts.list_unassigned_students())
                self.send_my_students(ts.list_my_students())

                logger.info("%s: release_student"%ts.teacher_id)
                
            except:
                logger.exception("Exception handling 'release_student'")

        @self.add_handler('get_student_info')
        def handle_get_student_info(self, args):
            """Handler for 'get_student_info'

            args
            ----
              student_id : string
                Webwork Session ID

              course_id : string
                Webwork course ID
              
              set_id : string
                Webwork set ID
                
              problem_id : string
                Webwork problem ID
            """
            try:
                student_id = args['student_id']
                course_id = args['course_id']
                set_id = args['set_id']
                problem_id = args['problem_id']

                ts = self.teacher_session
                info = ts.student_info(student_id, course_id,
                                       set_id, problem_id)
                self.send_student_info(info) 
                
                logger.info("%s: get_student_info"%ts.teacher_id)    
            except:
                logger.exception("Exception handling 'get_student_info'")


    def send_unassigned_students(self, unassigned_students):
        self.send_message('unassigned_students', unassigned_students)


    def send_my_students(self, my_students):
        self.send_message('my_students', my_students)


    def send_student_info(self, student_info):
        self.send_message('student_info', student_info)


    def on_open(self, info):
        """Callback for when a teacher is connected"""
        logger.info("%s connected"%info.ip)

        
    def on_close(self):
        """Callback for when a teacher is disconnected"""
        ts = self.teacher_session

        if ts is not None:
            # Remove the session from active list
            TeacherSession.active_sessions.remove(ts)

            # remove reference to this handler
            ts._sockjs_handler = None

            if len(ts.teacher_id) > 0:
                logger.info("%s left"%ts.teacher_id)
        
        logger.info("%s disconnected"%self.session.conn_info.ip)
