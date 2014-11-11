import json
import tornado.web
import logging
import jwt
from webwork_config import jwt_key
logger = logging.getLogger(__name__)

class JSONRequestHandler(object):
    def set_default_headers(self):
        # Allows X-site requests
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "X-Requested-With, content-type, Authorization")
    def options(self):
        return
    def prepare(self):
        '''Incorporate request JSON into arguments dictionary.'''
        if self.request.body and self.request.headers['content-type'].startswith('application/json'):
            try:
                json_data = json.loads(self.request.body)
                for k, v in json_data.items():
                    # Tornado expects values in the argument dict to be lists.
                    # in tornado.web.RequestHandler._get_argument the last argument is returned.
                    json_data[k] = [str(v)]
                # self.request.arguments.pop(self.request.body)
                self.request.arguments.update(json_data)
            except ValueError, e:
                logger.warn("Failed to parse JSON")
                message = 'Unable to parse JSON.'
                # self.send_error(400, message=message) # Bad Request
        if 'Authorization' in self.request.headers:
            auth_header = self.request.headers['Authorization']
            # Authorization header takes the form 'Bearer JWT_TOKEN'
            try:
                token = auth_header.split()[1]
                data = jwt.decode(token, jwt_key)
                self.auth_data = data
            except jwt.DecodeError:
                logger.error("Invalid authorization header in request")
