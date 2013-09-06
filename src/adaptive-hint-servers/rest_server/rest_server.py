import tornado.ioloop
import tornado.web
import logging

from render import Render 
from checkanswer import CheckAnswer

# Server configuration
BIND_IP = '0.0.0.0'
DEFAULT_PORT = 4351

class PG(tornado.web.RequestHandler):
    """PG Resource (REST API)"""
    def post(self):
        """POST /pg"""
        pg_path = self.get_argument('pg_path', '')
        response = { 'pg_id': 1, 
                     'pg_source': '' }
        self.write(response)
 
class Hint(tornado.web.RequestHandler):
    """Hint Resource (REST API)"""
    def get(self, pg_id):
        """GET /hints/:pg_id"""
        response = { 'hint_id': 2,
                     'pg': '',
                     'html': '' }
        self.write(response)

    def post(self, pg_id):
        """POST /hints/:pg_id"""
        pg_source = self.get_argument('pg_source', '')
        response = { 'result': 'done' }
        self.write(response)
        
    def delete(self, pg_id):
        """DELETE /hints/:pg_id"""
        response = {'result': 'done' }
        self.write(response)

 
    
application = tornado.web.Application([
        (r"/pg/([0-9]+)", PG),
        (r"/hints/([0-9]+)", Hint),
        (r"/render", Render),
        (r"/checkanswer", CheckAnswer),
        ])
 
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port",
                        type=int,
                        default=DEFAULT_PORT,
                        help="port to listen")
    args = parser.parse_args()

    logging.getLogger().setLevel(logging.DEBUG)

    application.listen(args.port, address=BIND_IP)
    logging.info(" [*] Listening on %s:%d"%(BIND_IP,args.port))
    
    tornado.ioloop.IOLoop.instance().start()
