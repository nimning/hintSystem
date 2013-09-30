import json
import tornado
from tornado.template import Template
from tornado_database import Connection
from tornado.web import RequestHandler
from get_header_footer import get_header, get_footer


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
                      dehydrate=None,
                      post_process=None,
                      hydrate=None,
                      verbose=False):
        self.args = self.request.arguments
        for key in self.request.arguments.keys():
            self.args[key] = self.args[key][0]
        if not hydrate is None:
            self.args = hydrate(self.args)
        query_rendered = Template(query_template).generate(**self.args)
        if verbose:
            print 'Running sql query:'
            print query_rendered
        if write_response:
            rows = conn.query(query_rendered)
            if not dehydrate is None:
                response = dehydrate(rows)
            else:
                response = rows
            self.write(json.dumps(response))
        else:
            response = conn.execute(query_rendered)
            if not post_process is None:
                response = post_process(response)
            if not response is None:
               self.write(json.dumps(response))

    def add_header_footer(self, response):
        query_template = '''
            select source_file from {{course}}_problem
            where
                set_id="{{set_id}}" and
                problem_id={{problem_id}}
        '''
        relative_filename_query = Template(query_template).generate(**self.args)
        relative_filename = conn.query(relative_filename_query) \
            [0]['source_file']
        pg_file_path = '/opt/webwork/courses/%s/templates/%s' % \
            (self.args['course'], relative_filename)
        with open(pg_file_path, 'r') as f:
            pg_file_str = f.read()
            header = get_header(pg_file_str)
            footer = get_footer(pg_file_str)

        for row in response:
            row['pg_header'] = header
            row['pg_footer'] = footer
            row['pg_file_path'] = pg_file_path
        return response

