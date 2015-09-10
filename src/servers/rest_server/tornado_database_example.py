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

rows = conn.query("select * from CompoundProblems_hint")
print rows
# conn.execute should be used instead of conn.query for 
    # INSERT/UPDATE statements
