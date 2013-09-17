import json
import logging
import sockjs.tornado

class _BaseSockJSHandler(sockjs.tornado.SockJSConnection):
    def __init__(self, *args, **kwargs):
        super(_BaseSockJSHandler, self).__init__(*args, **kwargs)
        self.handlers = {}

    def add_handler(self, msg_type):
        """Decorator function for adding a message handler."""
        def handler(func):
            def wrapper(*args, **kwargs):
                func(*args, **kwargs)
            self.handlers[msg_type] = wrapper
            return wrapper
        return handler

    def send_message(self, msg_type, args):
        """Send a message to client

        Arguments
        ---------
          msg_type : string
            Message type e.g. 'student_join', 'answer_status'

          args : dict or list
            Arguments to the message
            
        """
        packed_message = json.dumps({ 'type': msg_type, 'arguments': args })
        self.send(packed_message)
        
    def on_message(self, message):
        """Callback for when a message is received"""
        try:
            message = json.loads(message)
            f = self.handlers[message['type']]
            f(self, message['arguments'])
        except KeyError:
            logging.warning("unhandled message type")
        except:
            logging.exception("Exception in on_message")

