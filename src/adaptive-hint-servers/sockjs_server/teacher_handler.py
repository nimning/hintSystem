import logging

from _base_handler import _BaseSockJSHandler
from student_session import StudentSession
from teacher_session import TeacherSession
from session_storage import SessionStorage

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
    def __load_session(self, teacher_id):
        self.teacher_session = TeacherSession.storage.load(teacher_id, 1)
        
    def __save_session(self):
        ts = self.teacher_session
        TeacherSession.storage.save(ts.teacher_id, 1, ts)

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

                # try to resume session
                self.__load_session(teacher_id)

                if self.teacher_session is None:
                    # create a new instance of teacher
                    self.teacher_session = TeacherSession(teacher_id, self)
                else:
                    # update sockjs handler
                    self.teacher_session._sockjs_handler = self

                # shorthand
                ts = self.teacher_session

                # add to the active session list
                TeacherSession.active_sessions.add(ts)

                # send student lists
                self.send_unassigned_students(ts.unassigned_students())
                self.send_my_students(ts.my_students())
                
                logging.info("Teacher: %s joined"%ts.teacher_id)
            except:
                logging.exception("Exception in teacher_join handler")
                self.session.close()

        @self.add_handler('list_students')
        def handle_list_student(self, args):
            """Handler for 'list_students'

            Requests a list of all active students.

            """
            ts = self.teacher_session
            
            # send student lists
            self.send_unassigned_students(ts.unassigned_students())
            self.send_my_students(ts.my_students())
            
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

                        # also send status to teachers
                        hint = ss.hints[hintbox_id]
                        ext_hint = {
                            'session_id': ss.session_id,
                            'course_id': ss.course_id,
                            'set_id': ss.set_id,
                            'problem_id': ss.problem_id,
                            'timestamp': hint['timestamp'],
                            'hintbox_id': hint['hintbox_id'],
                            'location': hint['location'] }
                        for ts in TeacherSession.active_sessions:
                            ts.hint_update(ext_hint)
                            
            except:
                logging.exception("Exception add_hint")

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
                self.send_unassigned_students(ts.unassigned_students())
                self.send_my_students(ts.my_students())
            except:
                logging.exception("Exception handling 'request_student'")

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
                self.send_unassigned_students(ts.unassigned_students())
                self.send_my_students(ts.my_students())
            except:
                logging.exception("Exception handling 'release_student'")

    def send_unassigned_students(self, unassigned_students):
        self.send_message('unassigned_students', unassigned_students)

    def send_my_students(self, my_students):
        self.send_message('my_students', my_students)

    def send_answer_update(self, answer_update):
        self.send_message('answer_update', answer_update)
        
    def send_hint_update(self, hint_update):
        self.send_message('hint_update', hint_update)


    def on_open(self, info):
        """Callback for when a teacher is connected"""
        logging.info("%s connected"%info.ip)

        
    def on_close(self):
        """Callback for when a teacher is disconnected"""
        ts = self.teacher_session

        # Remove the session from active list
        TeacherSession.active_sessions.remove(ts)

        # remove reference to this handler
        self._sockjs_handler = None

        # save state of the session
        self.__save_session()

        if len(ts.teacher_id) > 0:
            logging.info("%s left"%ts.teacher_id)
        
        logging.info("%s disconnected"%self.session.conn_info.ip)

            
