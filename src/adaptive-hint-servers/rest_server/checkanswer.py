import tornado.ioloop
import tornado.web
import tornado.gen
import logging
import pg_wrapper
import os
import tempfile
import base64

def task_checkanswer(pg_file, answers, seed, callback=None):
    callback(pg_wrapper.checkanswer(pg_file, answers, int(seed)))
 
class CheckAnswer(tornado.web.RequestHandler):
    """Interface with Webwork/PG for checking answers with a PG
    """
    def initialize(self):
        # Allows X-site requests
        self.set_header("Access-Control-Allow-Origin", "*")

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        """POST /checkanswer
        
        Arguments:
          pg_file
            Either a path to a PG file or the content of a PG file
            encoded with Base64.
          seed
            Random seed

        Output:
          A dictionary containing answer results.

        """
        pg_file = self.get_argument("pg_file")
        seed = self.get_argument("seed")

        # check validity of the input
        if len(pg_file) == 0 or len(seed) == 0 or not seed.isdigit():
            raise tornato.web.HTTPError(400)

        # parse AnSwEr*s
        answers = {}
        for key in self.request.arguments:
            if key.startswith('AnSwEr'):
                answers[key] = self.request.arguments[key][0]
            
        if len(answers) == 0:
            response = { 'error_msg': 'Need at least 1 answer' }
            self.write(response)
            return

        # Case1: pg_file is a path
        if os.path.isabs(pg_file):
            # check if the file actually exists
            if not os.path.isfile(pg_file):
                response = { 'error_msg': 'PG file not found' }
                self.write(response)
                return

            # call the PG wrapper
            results = yield tornado.gen.Task(task_checkanswer,
                                             pg_file,
                                             answers,
                                             int(seed))

            if results is None:
                response = { 'error_msg': 'PG service error' }
                self.write(response)
                return

            # all done
            self.write(results)
        else:
            # Case 2: pg_file is base64 encoded.
            try:
                # create a temp file and decode the pg to the file
                temp = tempfile.NamedTemporaryFile(delete=False)
                temp.write(base64.b64decode(pg_file))
                temp.close()
            except Exception:
                response = { 'error_msg': 'Unable to create a temporary file' }
                self.write(response)
                return

            # call the PG wrapper
            results = yield tornado.gen.Task(task_checkanswer,
                                             temp.name,
                                             answers,
                                             int(seed))

            # remove the temp file
            os.remove(temp.name)

            if results is None:
                response = { 'error_msg': 'PG service error' }
                self.write(response)
                return

            # all done
            self.write(results)
