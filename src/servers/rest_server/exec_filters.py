import logging
logger = logging.getLogger(__name__)

""" 
This is the function that executes the filter. This is fine for running the filter in the development window. However when running the filter in production the pattern is different: we have a single attempt and we are running it against a bunch of filters. I think a better approach in this case is to have a parallel process (or processes) that are sent the attept information and send back the hint string (or nothing).

Also, it would make thing run faster if the code is compiled before it is executed.
""" 

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
    logger.debug('finished  filtered_answers')

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
        logger.debug('About to exec filter function definition')
        exec filter_function_string in globals(), locals()
        logger.debug('About to start processing %d attempts'%len(answers))
        for a in answers:
            user_id = a['user_id']
            logger.debug('processing '+user_id)

            if len(user_vars) > 0:
                student_vars = dict(user_vars[user_vars['user_id']==user_id][['name', 'value']].values.tolist())
            else:
                 student_vars = {}
            #logger.debug('vars: %s', student_vars)
            # This function must be defined by the exec'd code
            ret = answer_filter(a['string'], a['parsed'], a['evaled'], correct_string, correct_tree, a['correct_eval'], student_vars)
            if ret:
                selected_answers.append({'user_id': user_id, 'answer_string': a['string']})
    except Exception, e:
        logger.error("Error in filter function: %s", e)
        print e
        #continue

    pipe.send(selected_answers)
    out.flush()
    logger.debug('finished  filtered_answers')
    return
