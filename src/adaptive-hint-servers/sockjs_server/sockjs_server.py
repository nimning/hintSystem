"""
SockJS server for the adaptive hint project.

The server binds to a specific IP address and listens on a specific
port. It responses to the requests from SockJS clients.
"""
import tornado.ioloop
import tornado.web
import sockjs.tornado
import logging
import argparse

from hint_rest_api import HintRestAPI
from student_handler import StudentSockJSHandler
from teacher_handler import TeacherSockJSHandler

# Server Configurations 
BIND_IP = '0.0.0.0'
DEFAULT_PORT = 4350
REST_SERVER = 'http://127.0.0.1'
DEFAULT_REST_PORT = 4351
LOG_PATH = '/var/log/hint'

if __name__ == "__main__":
    # read command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--port",
                        type=int,
                        default=DEFAULT_PORT,
                        help="port to listen")
    parser.add_argument("--rest_port",
                        type=int,
                        default=DEFAULT_REST_PORT,
                        help="port of the ReST server")

    args = parser.parse_args()

    # set up the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - '
                                  '%(levelname)s - %(message)s')

    log_filename =  LOG_PATH + "/sockjs-%d.log"%args.port
    handler = logging.handlers.RotatingFileHandler(log_filename,
                                                   maxBytes=2000000,
                                                   backupCount=5)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Set the location of the ReSTful services
    HintRestAPI.setBaseUrl("%s:%d"%(REST_SERVER, args.rest_port))
    
    # Create routers
    StudentRouter = sockjs.tornado.SockJSRouter(StudentSockJSHandler,
                                                '/student')
    TeacherRouter = sockjs.tornado.SockJSRouter(TeacherSockJSHandler,
                                                '/teacher')

    # Create Tornado application
    app = tornado.web.Application(StudentRouter.urls +
                                  TeacherRouter.urls)

    # Make Tornado app listen on the specific port
    app.listen(args.port, address=BIND_IP)
    logging.info(" [*] Listening on %s:%d"%(BIND_IP, args.port))
    
    # Start IOLoop
    tornado.ioloop.IOLoop.instance().start()
