import tornado.ioloop
import tornado.web
import tornado.gen
import logging
import pg_wrapper
import os
import tempfile
import base64

def task_render(pg_file, seed, callback=None):
    callback(pg_wrapper.render_pg(pg_file, int(seed)))
 
class Render(tornado.web.RequestHandler):
    """Interface with Webwork/PG for rendering a PG
    """

    def initialize(self):
        # Allows X-site requests
        self.set_header("Access-Control-Allow-Origin", "*")
        
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        """POST /render

        Arguments:
          pg_file
            Either a path to a PG file or the content of a PG file
            encoded with Base64.
          seed
            Random seed
            
        """
        pg_file = self.get_argument("pg_file")
        seed = self.get_argument("seed")

        # check validity of input
        if (len(pg_file) == 0 or len(seed) == 0 or not seed.isdigit()):
            raise tornato.web.HTTPError(400)

        response = { 'render_html' : '',
                     'error_msg' : '' }
        
        # Case1: pg_file is a path
        if os.path.isabs(pg_file):
            # check if the file actually exists
            if not os.path.isfile(pg_file):
                response['error_msg'] = 'PG file not found'
                self.write(response)
                return

            # call the PG wrapper
            rendered_html = yield tornado.gen.Task(task_render,
                                                   pg_file,
                                                   int(seed))
            
            if rendered_html is None:
                response['error_msg'] = 'PG service error'
                self.write(response)
                return

            # all good
            response = { 'rendered_html': rendered_html }
            self.write(response)
        else:
            # Case 2: pg_file is base64 encoded.
            try:
                # create a temp file and decode the pg to the file
                temp = tempfile.NamedTemporaryFile(delete=False)
                temp.write(base64.b64decode(pg_file))
                temp.close()
            except Exception:
                response['error_msg'] = 'Unable to create a temporary file'
                self.write(response)
                return
                
            rendered_html = yield tornado.gen.Task(task_render,
                                                   temp.name,
                                                   int(seed))
            # remove the temp file
            os.remove(temp.name)

            if rendered_html is None:
                response['error_msg'] = 'PG service error'
                self.write(response)
                return
        
            response = { 'rendered_html': rendered_html }
            self.write(response)