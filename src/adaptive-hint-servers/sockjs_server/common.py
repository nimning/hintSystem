import sockjs.tornado
import json
import logging

class ActiveClients(object):
    """Keeps track of opened clients for both students and teachers"""
    students = set()
    teachers = set()


class _BaseConnection(sockjs.tornado.SockJSConnection):
    def __init__(self, *args, **kwargs):
        super(_BaseConnection, self).__init__(*args, **kwargs)
        self.handlers = {}

    def add_handler(self, command):
        """Decorator function for adding a command handler."""
        def handler(func):
            def wrapper(*args, **kwargs):
                func(*args, **kwargs)
            self.handlers[command] = wrapper
            return wrapper
        return handler

    def on_message(self, message):
        """Callback for when a message is received"""
        try:
            message = json.loads(message)
            logging.info("[%s] student command: %s"%(
                self.session.conn_info.ip,
                message['command']))
            f = self.handlers[message['command']]
            f(self, message['arguments'])
        except KeyError:
            logging.warning("unhandled command")
        except Exception:
            import traceback
            traceback.print_exc()
