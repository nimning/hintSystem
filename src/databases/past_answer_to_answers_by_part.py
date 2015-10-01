#!/usr/bin/env python

from rest_server.tornado_database import Connection
from rest_server.webwork_config import mysql_username, mysql_password
import argparse

from sqlalchemy import *
from sqlalchemy.sql import *
from sqlalchemy.dialects.mysql import \
        BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
        DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
        LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
        NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
        TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR

import pandas as pd
import numpy as np
import re
from IPython import embed
import logging
import time
from websocket import create_connection
import json

from sqlalchemy.orm import sessionmaker
db = 'webwork'

class PastAnswerConverter(object):
    def __init__(self, course, engine):
        self.course = course
        self.engine = engine
        self.metadata = MetaData()
        self.init_database()
        self.start_id = self.get_last_converted_row_id()
        self.last_pa_by_user_q = "SELECT answer_string from {0}_past_answer WHERE answer_id < {1} \
    AND user_id = '{2}' AND problem_id = '{3}' AND set_id='{4}' \
    ORDER BY answer_id DESC LIMIT 1"
        self.ws = create_connection("ws://localhost:4350/daemon/websocket")
    def init_database(self):
        self.answers_by_part = Table("{0}_answers_by_part".format(self.course), self.metadata,
                                     Column('id', Integer, primary_key=True),
                                     Column('user_id', String(100), nullable=False, index=True),
                                     Column('answer_id', Integer, nullable=False),
                                     Column('answer_string', String(1024)),
                                     Column('score', String(1), nullable=False),
                                     Column('problem_id', Integer, nullable=False, index=True),
                                     Column('set_id', String(100), nullable=False, index=True),
                                     Column('part_id', Integer, nullable=False),
                                     Column('timestamp', DateTime, nullable=False)
        )

        self.answers_by_part.create(self.engine, checkfirst=True)
        self.conn = self.engine.connect()


    def get_last_converted_row_id(self):
        '''Gets last row that was converted from a compound answer to answers by part'''
        s = select([self.answers_by_part]).order_by(desc('answer_id')).limit(1)
        res = self.conn.execute(s).fetchone()
        if res:
            return res.answer_id+1
        else:
            return 0

    def last_answer_before(self, user_id, set_id, problem_id):
        query = self.last_pa_by_user_q.format(self.course, self.start_id, user_id, problem_id, set_id)
        result = self.conn.execute(query).fetchone()
        if result and result[0]:
            return result[0].split('\t')
        else:
            return []

    def loop(self):
        pa = pd.read_sql_query('SELECT user_id, answer_id, answer_string, scores, problem_id, set_id, timestamp from {0}_past_answer WHERE answer_id >= {1} LIMIT 1000;'.format(self.course, self.start_id), engine, parse_dates={'timestamp': {'unit': 's'}})
        if len(pa) == 0:
            return
        print 'Converting', len(pa), 'past answers'
        ans_by_part={'user_id':[], 'answer_id':[], 'answer_string':[], 'score':[],
                     'problem_id':[], 'set_id': [], 'part_id':[],'timestamp':[]}

        for (set_id, problem_id), pas in pa.groupby(['set_id', 'problem_id']):
            logging.debug('%s - #%d', set_id, problem_id)
            for user, user_pa in pas.sort('timestamp').groupby('user_id'):
                prev_answers = self.last_answer_before(user, set_id, problem_id)
                for i in range(len(user_pa)):
                    row=user_pa.iloc[i]
                    if not row['answer_string']:
                        continue
                    answers=re.split('\t', row['answer_string'].strip())

                    for part in range(len(answers)):
                        if (len(prev_answers)<=part or len(prev_answers[part])==0 \
                            or answers[part] != prev_answers[part]) and len(answers[part]) > 0:
                            if  len(row.scores) <= part: # This is a weird error case, probably bug in webwork
                                logging.error(row)
                            else:
                                ans_by_part['user_id'].append(row['user_id'])
                                ans_by_part['answer_id'].append(row['answer_id'])
                                ans_by_part['answer_string'].append(answers[part])
                                ans_by_part['score'].append(row['scores'][part])
                                ans_by_part['problem_id'].append(row['problem_id'])
                                ans_by_part['set_id'].append(row['set_id'])
                                ans_by_part['part_id'].append(part+1)
                                ans_by_part['timestamp'].append(row['timestamp'])
                                if not self.ws.connected:
                                    # TODO Need better error handling/reconnection logic
                                    self.ws = create_connection("ws://localhost:4350/daemon/websocket")
                                self.ws.send(json.dumps({'type':'student_answer', 'arguments': {
                                    'user_id': row['user_id'],
                                    'course': self.course,
                                    'set_id': row['set_id'],
                                    'problem_id': row['problem_id'],
                                    'part_id': part+1,
                                    'answer_string': answers[part],
                                    'score': row['scores'][part]
                                }}))
                                print 'Sent', row
                    prev_answers=answers
        # It is actually a bit overkill to use a DataFrame when this loop runs
        # so often, but it's a quick and easy way to write SQL to a table
        Answer_DF=pd.DataFrame(ans_by_part)
        logging.info(Answer_DF.sort(columns=['part_id','user_id','timestamp']))
        if len(Answer_DF) > 0:
            Answer_DF.to_sql('{0}_answers_by_part'.format(self.course), self.engine, if_exists='append', index=False)
        self.start_id = pa.answer_id.max() + 1 # Make sure to start from the next row next loop

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-c', '--course', help="Course", default="CSE103_Fall2015")
    args = parser.parse_args()
    engine = create_engine('mysql+mysqldb://{0}:{1}@localhost/{2}'.format(mysql_username, mysql_password, db), pool_recycle=3600)

    converter = PastAnswerConverter(args.course, engine)
    while True:
        converter.loop()
        time.sleep(1)

