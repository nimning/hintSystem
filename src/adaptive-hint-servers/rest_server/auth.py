import tornado
import json
import tornado.ioloop
import tornado.web
import logging
import jwt

from process_query import conn
from webwork_config import jwt_key
from crypt import crypt

from json_request_handler import JSONRequestHandler

logger = logging.getLogger(__name__)

class Login(JSONRequestHandler, tornado.web.RequestHandler):
    """ /login """
    def post(self):
        ''' For authenticating users against a Webwork course.

            Sample arguments:
            course="CompoundProblems",
            user_id="iawwal",
            password="mypassword",

            Returning: [
                {
                    "user_id": "iawwal",
                    "permission": 5
                },
                ...
            ]
        '''
        data = tornado.escape.json_decode(self.request.body)
        course = data.get("course")
        user_id = data.get("username")
        password = data.get("password")
        query = '''SELECT * from {0}_password as passwd
        JOIN {0}_permission as perm ON perm.user_id = passwd.user_id
        WHERE passwd.user_id=%s'''.format(course)
        result = conn.query(query, user_id)[0]
        salt = result['password']
        permission_level = result['permission']
        if crypt(password, salt) == salt and permission_level > 0:
            # Password is correct and has higher than student privileges
            userdata = {"user_id": user_id,
                        "permission": permission_level,
                    }
            jwt_string = jwt.encode(userdata, jwt_key)
            response = {"message": "Successfully logged in",
                        "token": jwt_string
                    }
        else:
            response = {"message": "Incorrect username or password"}
            self.set_status(401)
        self.write(json.dumps(response))
        self.flush()
        return

