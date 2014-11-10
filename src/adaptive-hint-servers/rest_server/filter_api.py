import tornado
import simplejson as json
import tornado.ioloop
import tornado.web
import logging

from tornado.template import Template
from convert_timestamp import utc_to_system_timestamp
from process_query import ProcessQuery, conn
from operator import itemgetter
import pandas as pd
from datetime import datetime
from dateutil.tz import tzlocal
import os

tz = tzlocal()

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial

logger = logging.getLogger(__name__)
BASE = '/opt/AdaptiveHintsFilters'

class FilterFunctions(ProcessQuery):
    """ /filter_functions """

    def set_default_headers(self):
        # Allows X-site requests
        super(ProcessQuery, self).set_default_headers()
        self.add_header("Access-Control-Allow-Methods", "PUT,DELETE")

    def filter_path(self, id):
        ''' Helper method for generating file path to put filter functions. '''
        args = self.filtered_arguments('course', 'set_id', 'problem_id', 'name').values() + [id]
        logger.debug(args)
        path = os.path.join(BASE, *args)
        logger.debug(path)
        
    def get(self):
        ''' For loading filter functions

            Sample arguments:
            id="1",

            Returning: [
                {
                    "id": 3, ...
                },
                ...
            ]
        '''

        allowed_args = self.filtered_arguments('id', 'set_id', 'problem_id', 'name', 'author', 'course')
        where = self.where_clause(**allowed_args)
        query = '''select * from filter_functions {WHERE};'''.format(WHERE=where)
        logger.debug(query)
        rows = conn.query(query)
        self.write(json.dumps(rows, default=serialize_datetime))

    def post(self):
        ''' For creating filter functions. '''
        course = self.get_argument('course')
        set_id = self.get_argument('set_id', 'GenericFilterFunctions')
        problem_id = self.get_argument('problem_id', 1)
        author = self.get_argument('author')
        name = self.get_argument('name')
        code = self.get_argument('code')
        # Create dummy hint first
        create_hint ='''insert into {course}_hint
            (pg_text, author, set_id, problem_id, part_id) values
            ("", "{author}", "DummyHints", 1, 1)
        '''.format(course=course, author=author)
        hint_id = conn.execute(create_hint)
        logger.debug(hint_id)
        now = datetime.now().isoformat()
        create_filter_function = ''' INSERT INTO filter_functions
        (name, course, author, set_id, problem_id, dummy_hint_id, code, created, updated)
        values ("{name}", "{course}", "{author}", "{set_id}", {problem_id}, {hint_id}, "{code}", "{created}", "{updated}");
        '''.format(name=name, course=course, author=author, set_id=set_id,
                   problem_id=problem_id, hint_id=hint_id, code=code,
                   created=now, updated=now)
        ret = conn.execute(create_filter_function) # Returns row ID
        self.write(json.dumps(ret))

    def put(self):
        id = self.get_argument('id')
        logger.debug(id)
        code = self.get_argument('code')
        now = datetime.now().isoformat()
        query = ''' UPDATE filter_functions SET
        code = "{code}", updated = "{time}"
        WHERE id={id};'''.format(code=code, time=now, id=id)
        get_query = ''' SELECT * FROM filter_functions where '''
        logger.debug(query)
        ret = conn.execute(query)
        self.write(json.dumps(ret))
        logger.debug(self.filter_path(id))
        
    def delete(self):
        pass

class ApplyFilterFunctions(ProcessQuery):
    def set_default_headers(self):
        # Allows X-site requests
        super(ProcessQuery, self).set_default_headers()
        self.add_header("Access-Control-Allow-Methods", "PUT,DELETE")

    def post(self):
        '''
        Tests a student's answer against the filters defined for the problem part.

        For any filters which match, returns the hint_id of the matched hint and
        any PGML which should be inserted into the hint.

        '''
        ret = {}
        self.write(json.dumps(ret))
        pass
