import json
import tornado
from HTMLParser import HTMLParser
from tornado.template import Template
from torndb import Connection
from tornado.web import RequestHandler
from get_header_footer import get_header, get_footer
from json_request_handler import JSONRequestHandler
import os

from webwork_config import mysql_username, mysql_password, webwork_dir
import logging
logger = logging.getLogger(__name__)
# Connect to webwork mysql database
conn = Connection('localhost',
                  'webwork',
                  user=mysql_username,
                  password=mysql_password)

class ProcessQuery(JSONRequestHandler, tornado.web.RequestHandler):
    def where_clause(self, **kwargs):
        ''' Utilitiy function for generating WHERE clauses of SQL queries '''
        if len(kwargs) == 0:
            return '';
        clauses = ['{column} = "{value}"'.format(column=k, value=v) for k, v in kwargs.iteritems()]
        return 'WHERE ' + ' AND '.join(clauses)

    def filtered_arguments(self, *args_allowed):
        ''' Utility method for filtering arguments passed to a request. '''
        args = self.request.arguments
        return { k: args[k][-1] for k in args_allowed if k in args}

    def set_default_headers(self):
        # Allows X-site requests
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "X-Requested-With, content-type, Authorization")
    def options(self):
        return
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

        p = HTMLParser()
        for row in response:
            row['pg_text'] = p.unescape(row['pg_text'])
            row['pg_header'] = header
            row['pg_footer'] = footer
            row['pg_file_path'] = pg_file_path
        return response

    def get_source(self):
        course = self.get_argument('course')
        set_id = self.get_argument('set_id')
        problem_id = self.get_argument('problem_id')

        source_file = conn.query('''select source_file from {course}_problem
            where problem_id={problem_id} and set_id="{set_id}";
        '''.format(course=course, set_id=set_id, problem_id=problem_id))[0]['source_file']
        pg_path = os.path.join(webwork_dir, 'courses', course, 'templates', source_file)
        with open(pg_path, 'r') as fin:
            pg_file = fin.read()
            return pg_file
