import json
import tornado.web

class JSONRequestHandler(object):
    def prepare(self):
        '''Incorporate request JSON into arguments dictionary.'''
        if self.request.body:
            try:
                print "Parsing JSON args"
                json_data = json.loads(self.request.body)
                for k, v in json_data.items():
                    # Tornado expects values in the argument dict to be lists.
                    # in tornado.web.RequestHandler._get_argument the last argument is returned.
                    json_data[k] = [v]
                print self.request.arguments
                # self.request.arguments.pop(self.request.body)
                self.request.arguments.update(json_data)
                print self.request.arguments
            except ValueError, e:
                message = 'Unable to parse JSON.'
                self.send_error(400, message=message) # Bad Request
