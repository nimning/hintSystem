import logging
logger = logging.getLogger(__name__)


def filtered_answers(answers, correct_string, correct_tree,
                     user_vars, filter_function_string, pipe, queue):
    '''
    This function represents a process which runs the filter function
    on a set of answers. It is intended to be run in a subprocess
    using the multiprocessing module.

    Returns a list of students who matched the filter, along with their answer,
    like
    [{user_id: 'iawwal', answer_string: '1+1'},..]
    '''
    import os
    import sys
    import StringIO
    import tempfile
    USER_ID = 1009

    tempdir = tempfile.mkdtemp()
    os.chown(tempdir, USER_ID, -1)
    os.chroot(tempdir)
    os.setuid(USER_ID)

    class QueueStringIO(StringIO.StringIO):
        def __init__(self, queue, *args, **kwargs):
            StringIO.StringIO.__init__(self, *args, **kwargs)
            self.queue = queue

        def flush(self):
            self.queue.put(self.getvalue())
            self.truncate(0)

    selected_answers = []
    out = QueueStringIO(queue)
    sys.stderr = sys.stdout = out

    try:
        exec filter_function_string in globals(), locals()
        for a in answers:
            user_id = a['user_id']
            if len(user_vars) > 0:
                student_vars = dict(user_vars[user_vars['user_id']==user_id][['name', 'value']].values.tolist())
            else:
                student_vars = {}
            logger.debug('vars: %s', student_vars)
            # This function must be defined by the exec'd code
            ret = answer_filter(a['string'], a['parsed'], a['evaled'], correct_string, correct_tree, a['correct_eval'], student_vars)
            if ret:
                selected_answers.append({'user_id': user_id, 'answer_string': a['string']})
    except Exception, e:
        logger.error("Error in filter function: %s", e)
        print e
    pipe.send(selected_answers)
    out.flush()
    return
