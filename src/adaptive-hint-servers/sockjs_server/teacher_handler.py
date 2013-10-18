from tornado import gen
import logging

from _base_handler import _BaseSockJSHandler
from hint_rest_api import HintRestAPI
from student_session import StudentSession
from teacher_session import TeacherSession

logger = logging.getLogger(__name__)

class TeacherSockJSHandler(_BaseSockJSHandler):
    """Teacher SockJS connection handler

    This class handles messages received from each teacher client.

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
        @gen.engine
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

                # perform work in another thread
                yield gen.Task(self._perform_teacher_join,
                               teacher_id,
                               student_id,
                               course_id,
                               set_id,
                               problem_id)

                # shorthand
                ts = self.teacher_session

                logger.info("Teacher: %s joined"%ts.teacher_id)
            except:
                logger.exception("Exception in teacher_join handler")
                self.session.close()

        @self.add_handler('list_students')
        @gen.engine
        def handle_list_students(self, args):
            """Handler for 'list_students'

            Requests a list of all active students.

            """
            yield gen.Task(self._perform_list_students)
            
        @self.add_handler('add_hint')
        @gen.engine
        def handle_add_hint(self, args):
            """Handler for 'add_hint'

            Add a hint to a student's client.

            args
            ----
              location : string
                Hint location

              hint_id : string
                Hint  ID
                
              hint_html_template : string
                HTML template
              
            """
            try:
                location = args['location']
                hint_id = args['hint_id']
                hint_html_template = args['hint_html_template']

                # shorthand
                ts = self.teacher_session

                yield gen.Task(self._perform_assign_hint,
                               location,
                               hint_id,
                               hint_html_template)
                
                logger.info("%s: add_hint"%ts.teacher_id)
                
            except:
                logger.exception("Exception add_hint")

        @self.add_handler('remove_hint')
        @gen.engine
        def handle_remove_hint(self, args):
            """Handler for 'remove_hint'

            Remove a hint from a student's client.

            args
            ----
              location : string
                Hint location

              hintbox_id : string
                Hint answer box ID
                
            """
            try:
                location = args['location']
                hintbox_id = args['hintbox_id']
                
                # shorthand
                ts = self.teacher_session

                yield gen.Task(self._perform_unassign_hint,
                               location,
                               hintbox_id)
                
                logger.info("%s: remove_hint"%ts.teacher_id)
                
            except:
                logger.exception("Exception remove_hint")


        @self.add_handler('request_student')
        def handle_request_student(self, args):
            """Handler for 'request_student'

            Request to help a student
            
            args
            ----
              student_id : string
              course_id : string
              set_id : string
              problem_id : string
            """
            try:
                ts = self.teacher_session
                
                student_id = args['student_id']
                course_id = args['course_id']
                set_id = args['set_id']
                problem_id = args['problem_id']
                
                self.teacher_session.request_student(student_id,
                                                     course_id,
                                                     set_id,
                                                     problem_id)

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
              student_id : string
              course_id : string
              set_id : string
              problem_id : string

            """
            try:
                ts = self.teacher_session
                
                student_id = args['student_id']
                course_id = args['course_id']
                set_id = args['set_id']
                problem_id = args['problem_id']

                self.teacher_session.release_student(student_id,
                                                     course_id,
                                                     set_id,
                                                     problem_id)

                # send student lists
                self.send_unassigned_students(ts.list_unassigned_students())
                self.send_my_students(ts.list_my_students())

                logger.info("%s: release_student"%ts.teacher_id)
                
            except:
                logger.exception("Exception handling 'release_student'")

        @self.add_handler('get_student_info')
        @gen.engine
        def handle_get_student_info(self, args):
            """Handler for 'get_student_info' """
            try:
                ts = self.teacher_session
                yield gen.Task(self._perform_get_student_info)
                logger.info("%s: get_student_info"%ts.teacher_id)    
            except:
                logger.exception("Exception handling 'get_student_info'")
 
    ################################################################
    # Tasks                                                        #
    ################################################################
    def _perform_teacher_join(self, teacher_id, student_id,
                              course_id, set_id, problem_id,
                              callback=None):     
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

        # done
        callback()


    def _perform_list_students(self, callback=None):
        ts = self.teacher_session
        
        # send student lists
        self.send_unassigned_students(ts.list_unassigned_students())
        self.send_my_students(ts.list_my_students())

        # done
        callback()


    def _perform_assign_hint(self, location, hint_id,
                             hint_html_template, callback=None):

        # shorthand
        ts = self.teacher_session

        # get the student_id and other info
        if ts.student_hashkey is not None:
            (student_id, course_id, set_id, problem_id) = ts.student_hashkey

            # Call the rest api
            assigned_hintbox_id = HintRestAPI.assign_hint(student_id,
                                                          course_id,
                                                          set_id,
                                                          problem_id, 
                                                          location,
                                                          hint_id,
                                                          hint_html_template)
            
            # Find the student session and update its view
            ss = StudentSession.get_student_session(student_id,
                                                    course_id,
                                                    set_id,
                                                    problem_id)
            if ss is not None:
                ss.update_hints()

            # Update teacher's view
            ts.update_hints()

        # done
        callback()

    def _perform_unassign_hint(self, location, hintbox_id,
                               callback=None):
        # shorthand
        ts = self.teacher_session

        if ts.student_hashkey is not None:
            (student_id, course_id, set_id, problem_id) = ts.student_hashkey
            HintRestAPI.unassign_hint(course_id, hintbox_id)

            # Find the student session and update its view
            ss = StudentSession.get_student_session(student_id,
                                                    course_id,
                                                    set_id,
                                                    problem_id)            
            if ss is not None:
                ss.update_hints()

            # Update teacher's view
            ts.update_hints()
                
        # done
        callback()

    def _perform_get_student_info(self, callback=None):
        ts = self.teacher_session
        if ts.student_hashkey is not None:
            (student_id, course_id, set_id, problem_id) = ts.student_hashkey
            info = ts.student_info(student_id,
                                   course_id,
                                   set_id,
                                   problem_id)
        
            self.send_student_info(info)
        
        # done
        callback()

    ################################################################
    # SockJS helpers                                               #
    ################################################################

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
