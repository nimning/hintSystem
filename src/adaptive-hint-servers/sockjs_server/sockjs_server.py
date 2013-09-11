"""
SockJS server for the adaptive hint project.

The server binds to a specific IP address and listens on a specific
port. It responses to the requests from SockJS clients.
"""
import tornado.ioloop
import tornado.web
import sockjs.tornado

from student_conn import StudentConnection 
from teacher_conn import TeacherConnection

# Server Configurations 
BIND_IP = '0.0.0.0'
LISTEN_PORT = 4350

if __name__ == "__main__":
    import logging
    
    logging.getLogger().setLevel(logging.DEBUG)

    # Create routers
    StudentRouter = sockjs.tornado.SockJSRouter(StudentConnection, '/student')
    TeacherRouter = sockjs.tornado.SockJSRouter(TeacherConnection, '/teacher')

    # Create Tornado application
    app = tornado.web.Application(StudentRouter.urls +
                                  TeacherRouter.urls)

    # Make Tornado app listen on the specific port
    app.listen(LISTEN_PORT, address=BIND_IP)
    logging.info(" [*] Listening on %s:%d"%(BIND_IP,LISTEN_PORT))
    
    # Start IOLoop
    tornado.ioloop.IOLoop.instance().start()
