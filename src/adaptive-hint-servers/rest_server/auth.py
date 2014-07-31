import tornado
import json
import tornado.ioloop
import tornado.web
import logging
import jwt

from tornado.template import Template
from convert_timestamp import utc_to_system_timestamp
from process_query import ProcessQuery, conn
from hint_filters.AllFilters import hint_filters
from operator import itemgetter
import pandas as pd
from webwork_config import mysql_username, mysql_password, jwt_key
from tornado_database import Connection
from crypt import crypt
import jwt

logger = logging.getLogger(__name__)

conn = Connection('localhost',
                  'webwork',
                  user=mysql_username,
                  password=mysql_password)

class Login(tornado.web.RequestHandler):
    """ /login """
    
    def set_default_headers(self):
        # Allows X-site requests
        self.set_header("Access-Control-Allow-Origin", "*")

    def _add_header_footer(self, rows):
        ''' Add header footer and convert timestamps '''
        rows = self.add_header_footer(rows)
        for row in rows:
            row['timestamp'] = utc_to_system_timestamp(
                row['timestamp'])
        return rows
    
    def post(self):
        ''' For authenticating users against a Webwork course.  

            Sample arguments:
            course="CompoundProblems",
            user_id="iawwal", 
            password="mypassword",

            Returning: [
                {
                    "hint_id": 3,"
                },
                ...
            ]
        '''
        course = self.get_argument("course")
        user_id = self.get_argument("user_id")
        password = self.get_argument("password")
        query = 'SELECT * from {0}_password WHERE user_id=%s'.format(course)
        result = conn.query(query, user_id)[0]
        salt = result['password']
        if crypt(password, salt) == salt: # Password is correct
            # TODO: Send along access levels too
            userdata = {"user_id": user_id,
                    }
            jwt_string = jwt.encode(userdata, jwt_key)
            response = {"message": "Successfully logged in",
                        "JWT": jwt_string
                    }
        else:
            response = {"message": "Incorrect username or password"}
            self.set_status(401)
        self.write(json.dumps(response))
        self.flush()
        return

