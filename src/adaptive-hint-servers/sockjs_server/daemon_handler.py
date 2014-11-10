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
        @gen.engine
        def handle_student_answer(self, args):
            """Handler for 'student_answer'

            'student_answer' is sent from the daemon when a new answer has been
            submitted by a student.

            It must
            - run the assigned filter functions for this part
            - if any filters match, assign a hint to the student
            - if the student is online, update their view with the inserted hints

            args
            ----
            user_id
            course
            set_id
            problem_id
            part_id
            answer_string

            """
            # Send the same data back, just as acknowledgement for now
            # self.send_message('echo', {'data': args})
            logger.info('Got an answer')
            if args['score'] != '1':
                try:
                    assigned_hints = yield gen.Task(self._perform_run_filters, args['user_id'], args['course'],
                                                    args['set_id'], args['problem_id'], args['part_id'], args['user_id'])
                    if assigned_hints:
                        logger.info("Assigned hints to user %s: %s", args['user_id'], assigned_hints)
                        # TODO Update student session
                except Exception as e:
                    logger.warn('Exception %s', e)

    ################################################################
    # Asynchronous Tasks                                           #
    ################################################################
    def _perform_run_filters(self, user_id, course, set_id, problem_id, part_id, answer_string, callback=None):
        '''
        Runs all assigned filter functions on the given student's answer.

        If a filter returns True, render that hint and assign it to the student.
        If a filter returns PGML text, render that instead, and assign it to the hint.

        HintRestAPI.apply_hint_filters, HintRestAPI.render_html_assign_hint
        '''
        return HintRestAPI.apply_filter_functions(user_id, course, set_id, problem_id, part_id, answer_string)

