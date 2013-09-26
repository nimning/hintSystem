import json, yaml
import tornado
from tornado.template import Template
from tornado_database import Connection
from tornado.web import RequestHandler

with open('../server_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Connect to webwork mysql database
conn = Connection('localhost',
                  'webwork',
                  user=config['mysql_username'],
                  password=config['mysql_password'])

rows = conn.query("select * from CompoundProblems_hint")
print rows
# conn.execute should be used instead of conn.query for 
    # INSERT/UPDATE statements
