import logging

from common import ActiveClients, _BaseConnection, pack_message

class TeacherConnection(_BaseConnection):
    """Teacher SockJS connection"""
    
    def __init__(self, *args, **kwargs):
        super(TeacherConnection, self).__init__(*args, **kwargs)
        self.teacher_id = ''
        
        @self.add_handler('signin')
        def handle_signin(self, args):
            try:
                teacher_id = args['teacher_id']
                # Arguments are OK. Add this teacher to the list.
                self.teacher_id = teacher_id
                ActiveClients.teachers.add(self)
                logging.info("%s signed in"%self.teacher_id)
            except KeyError:
                self.session.close()

        @self.add_handler('list_students')
        def handle_list_student(self, args):
            """
            """
            names = [s.student_id for s in ActiveClients.students]
            self.send(pack_message('student_list', names))

        @self.add_handler('send_hint')
        def handle_send_hint(self, args):
            hint = "<div>hint</div>"
            self.broadcast(ActiveClients.students,
                           pack_message('hint', hint))
            
        @self.add_handler('render_hint')
        def handle_render_hint(self, args): pass
            
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

        
