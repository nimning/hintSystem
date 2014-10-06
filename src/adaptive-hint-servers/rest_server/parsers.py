"""Webwork Answer Parsing API"""
import os.path
from process_query import ProcessQuery, conn
from webwork_config import webwork_dir
from tornado.template import Template
from convert_timestamp import utc_to_system_timestamp
from json_request_handler import JSONRequestHandler
import tornado.web
import json
from datetime import datetime
from webwork_parser import parse_webwork
from Eval_parsed import eval_parsed, Collect_numbers
import logging
logger = logging.getLogger(__name__)

# GET /parse_string?
class ParseString(JSONRequestHandler, tornado.web.RequestHandler):
    def post(self):
        '''
            Parses an expression and returns the parsed data structure.

            Sample arguments:
            expression="1+1"

            Response:
                [['+', [0,2]], 1, 1]
            '''
        expression = self.get_argument('expression')
        etree = parse_webwork(expression)
        if etree:
            self.write(json.dumps(etree))
        else:
            logger.error("Failed to parse expression '%s'", expression)
            self.set_status(400)
            self.write(json.dumps({'error': 'Error parsing expression %s' % expression}))
