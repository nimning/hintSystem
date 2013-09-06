import tornado.ioloop
import tornado.web
import tornado.gen
import logging
import pg_wrapper
import os

def task_render(pg_file, seed, callback=None):
    callback(pg_wrapper.render_pg(pg_file, int(seed)))
 
class Render(tornado.web.RequestHandler):
    """Render PG"""
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        """POST /render"""
        pg_file = self.get_argument("pg_file", default='', strip=False)
        seed = self.get_argument("seed", default='1', strip=False)

        if not os.path.isfile(pg_file):
            self.set_status(500)
            self.write("PG file not found\n")
            return
        
        rendered_html = yield tornado.gen.Task(task_render, pg_file, int(seed))
        
        if rendered_html is None:
            self.set_status(500)
            self.write("Something went wrong\n")
            return
        
        response = { 'rendered_html': rendered_html }
        self.write(response)
