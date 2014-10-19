import tornado.ioloop
import tornado.web
import tornado.gen
import pg_wrapper
import os
import tempfile
import base64
from json_request_handler import JSONRequestHandler
import logging
logger = logging.getLogger(__name__)

def task_checkanswer(pg_file, answers, seed, psvn, callback=None):
    callback(pg_wrapper.check_answer_xmlrpc(pg_file, answers, seed, psvn))
 
class CheckAnswer(JSONRequestHandler, tornado.web.RequestHandler):
    """Interface with Webwork/PG for checking answers with a PG
    """

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
        psvn = self.get_argument("psvn", 1234)

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
            self.set_status(400)
            self._write_finish(response)
            return
        # Case1: pg_file is a path
        if os.path.isabs(pg_file):
            # check if the file actually exists
            if not os.path.isfile(pg_file):
                response = { 'error_msg': 'PG file not found' }
                self.set_status(500)
                self._write_finish(response)
                return

            # call the PG wrapper
            results = yield tornado.gen.Task(task_checkanswer, pg_file, answers, \
                                             seed, psvn)

            if results is None:
                response = { 'error_msg': 'PG service error' }
                self.set_status(500)
                self._write_finish(response)
                return

            # all done
            self._write_finish(results)
            
        # Case 2: pg_file is base64 encoded.
        else:
            
            try:
                # create a temp file and decode the pg to the file
                temp = tempfile.NamedTemporaryFile(delete=False)
                temp.write(base64.b64decode(pg_file))
                temp.close()
            except Exception:
                response = { 'error_msg': 'Unable to create a temporary file' }
                self.set_status(500)
                self._write_finish(response)
                return

            # call the PG wrapper
            results = yield tornado.gen.Task(task_checkanswer, temp.name, answers, \
                                             seed, psvn)

            # remove the temp file
            os.remove(temp.name)

            if results is None:
                response = { 'error_msg': 'PG service error' }
                self.set_status(500)
                self._write_finish(response)
                return

            # all done
            self._write_finish(results)

    def _write_finish(self, response):
        self.write(response)
        self.finish()
