import logging

from common import ActiveClients, _BaseConnection, pack_message

class TeacherConnection(_BaseConnection):
    """Teacher SockJS connection

    This class handles messages received from the teacher clients.

    A new handler for a message can be defined as follows:

    def __init__(self, *args, **kwargs):
        
        ...

        @self.add_handler('new_message')
        def handle_new_message(self, args):
            pass

        ...

    Attributes:
        teacher_id : string
           Teacher ID
    """ 
    
    def __init__(self, *args, **kwargs):
        super(TeacherConnection, self).__init__(*args, **kwargs)
        self.teacher_id = ''
        
        @self.add_handler('signin')
        def handle_signin(self, args):
            """Handler for 'signin'

            'signin' is sent from the client as the first message
            after the connection has established. The message contains
            the client information.
            
            """
            try:
                self.teacher_id = args['teacher_id']
                ActiveClients.teachers.add(self)
                logging.info("%s signed in"%self.teacher_id)
            except KeyError:
                self.session.close()

        @self.add_handler('list_students')
        def handle_list_student(self, args):
            """Handler for 'list_students'

            Requests a list of all active students.
            
            """
            names = [s.student_id for s in ActiveClients.students]
            self.send(pack_message('student_list', names))

        @self.add_handler('send_hint')
        def handle_send_hint(self, args):
            """Handler for 'send_hint'

            Send a hint to a student's client.
            
            """
            try:
                student_id = args.get('student_id','')
                hint = args.get('hint_html','')
                
                for student in ActiveClients.students:
                    # DEBUG: only students in 'demo' course
                    if student.course_id != 'demo':
                        continue
                    
                    if student_id == student.student_id:
                        student.send(pack_message('hint', args))
            except Exception:
                pass
                                        
    def on_open(self, info):
        """Callback for when a teacher is connected"""
        logging.info("%s connected"%info.ip)
                        
    def on_close(self):
        """Callback for when a teacher is disconnected"""
        ActiveClients.teachers.remove(self)
        if len(self.teacher_id) > 0:
            logging.info("%s disconnected"%self.teacher_id)
        else:
            logging.info("%s disconnected"%self.session.conn_info.ip)

