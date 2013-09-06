import json
import logging

from common import ActiveClients, _BaseConnection

class StudentConnection(_BaseConnection):
    """Student SockJS Connection""" 
   
    def __init__(self, *args, **kwargs):
        super(StudentConnection, self).__init__(*args, **kwargs)
        self.student_id = ''
        self.course_id = ''
        self.set_id = ''
        self.problem_id = ''

        @self.add_handler('signin')
        def handle_signin(self, args):
            try:
                student_id = args['student_id']
                course_id = args['course_id']
                set_id = args['set_id']
                problem_id = args['problem_id']

                # Arguments are OK. Add this student to the list.
                self.student_id = student_id
                self.course_id = course_id
                self.set_id = set_id
                self.problem_id = problem_id
                ActiveClients.students.add(self)
                logging.info("%s signed in"%self.student_id)
                # broadcast 'student_joined' to teachers
                self.broadcast(
                    ActiveClients.teachers,
                    json.dumps({'command': 'student_joined',
                                'arguments': args
                                }))
            except KeyError:
                self.session.close()
                
        @self.add_handler('newstring')
        def handle_newstring(self, args):
            boxname = args['boxname']
            value = args['value']
            logging.info("%s updated %s to %s"%(self.student_id,
                                                boxname,
                                                value))
            # broadcast 'student_joined' to teachers
            self.broadcast(
                ActiveClients.teachers,
                json.dumps({'command': 'newstring',
                            'arguments': args
                            }))


    def on_open(self, info):
        """Callback for when a student is connected"""
        logging.info("%s connected"%info.ip)
                        
    def on_close(self):
        """Callback for when a student is disconnected"""
        ActiveClients.students.remove(self)
        if len(self.student_id) > 0:
            logging.info("%s disconnected"%self.student_id)
        else:
            logging.info("%s disconnected"%self.session.conn_info.ip)
        # broadcast 'student_left' to teachers
        self.broadcast(
            ActiveClients.teachers,
            json.dumps({
                'command': 'student_left',
                'arguments': {
                    'student_id': self.student_id
                    }
                }))

