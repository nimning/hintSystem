import sockjs.tornado
import json
import logging

def pack_message(msg_type, args):
    """Create a JSON message from message type and arguments""" 
    return json.dumps({ 'type': msg_type,
                        'arguments': args })

class ActiveClients(object):
    """Keeps track of opened clients for both students and teachers"""
    students = set()
    teachers = set()

class _BaseConnection(sockjs.tornado.SockJSConnection):
    def __init__(self, *args, **kwargs):
        super(_BaseConnection, self).__init__(*args, **kwargs)
        self.handlers = {}

    def add_handler(self, msg_type):
        """Decorator function for adding a message handler."""
        def handler(func):
            def wrapper(*args, **kwargs):
                func(*args, **kwargs)
            self.handlers[msg_type] = wrapper
            return wrapper
        return handler

    def on_message(self, message):
        """Callback for when a message is received"""
        try:
            message = json.loads(message)
            f = self.handlers[message['type']]
            f(self, message['arguments'])
        except KeyError:
            logging.warning("unhandled message type")
        except Exception:
            import traceback
            traceback.print_exc()
