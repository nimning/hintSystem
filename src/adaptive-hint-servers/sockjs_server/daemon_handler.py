from tornado import gen
import logging

from _base_handler import _BaseSockJSHandler
from hint_rest_api import HintRestAPI
from student_session import StudentSession
from teacher_session import TeacherSession

logger = logging.getLogger(__name__)

class DaemonSockJSHandler(_BaseSockJSHandler):
    """Daemon SockJS connection handler

    This class handles messages received from the answer daemon.

    A new handler for a message can be defined as follows:

    def __init__(self, *args, **kwargs):
        ...
        @self.add_handler('new_message')
        def handle_new_message(self, args):
            pass
        ...

    Properties
    ----------

    """
    def __init__(self, *args, **kwargs):
        super(DaemonSockJSHandler, self).__init__(*args, **kwargs)
        @self.add_handler('student_answer')
        def handle_student_answer(self, args):
            """Handler for 'student_answer'

            'student_answer' is sent from the daemon when a new answer has been
            submitted by a student.

            It needs to
            - run the assigned filter functions for this part
            - if any filters match, assign a hint to the student
            - if the student is online, update their view with the inserted hints

            args
            ----
            user_id
            set_id
            problem_id
            part_id
            answer_string
            (maybe needs course too)

            """
            # Send the same data back, just as acknowledgement for now
            self.send_message('echo', {'data': args})
            try:
                logger.info(args)
            except:
                pass
