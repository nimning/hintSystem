"""
SockJS server for the adaptive hint project.

The server binds to a specific IP address and listens on a specific
port. It responses to the requests from SockJS clients.
"""
import tornado.ioloop
import tornado.web
import sockjs.tornado

from student_handler import StudentSockJSHandler
from teacher_handler import TeacherSockJSHandler

# Server Configurations 
BIND_IP = '0.0.0.0'
DEFAULT_PORT = 4350

if __name__ == "__main__":
    import logging    
    logging.getLogger().setLevel(logging.DEBUG)

    # read command-line arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port",
                        type=int,
                        default=DEFAULT_PORT,
                        help="port to listen")
    args = parser.parse_args()

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
    logging.info(" [*] Listening on %s:%d"%(BIND_IP,args.port))
    
    # Start IOLoop
    tornado.ioloop.IOLoop.instance().start()
