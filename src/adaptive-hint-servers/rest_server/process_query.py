import json
import tornado
from tornado.template import Template
from tornado_database import Connection
from tornado.web import RequestHandler

from webwork_config import mysql_username, mysql_password

# Connect to webwork mysql database
conn = Connection('localhost',
                  'webwork',
                  user=mysql_username,
                  password=mysql_password)

class ProcessQuery(tornado.web.RequestHandler):
    def process_query(self,
                      query_template,
                      write_response=True,
                      dehydrate=None):
        args = self.request.arguments
        for key in self.request.arguments.keys():
            args[key] = args[key][0]
        query_rendered = Template(query_template).generate(**args)
        if write_response:
            rows = conn.query(query_rendered)
            if not dehydrate is None:
                response = dehydrate(rows)
            else:
                response = rows
            self.write(json.dumps(response))
        else:
            conn.execute(query_rendered)
