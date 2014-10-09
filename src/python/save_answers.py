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

import xmlrpclib
import base64
import os.path

db = 'webwork'
url='http://192.168.33.10/mod_xmlrpc'
server = xmlrpclib.ServerProxy(url)

part_re = re.compile('AnSwEr(\d{4})')
def get_all_answers(problem_file, seeds):
    with open(problem_file, 'r') as f:
        pg_text = f.read()
    all_answers = {seed: get_answers(pg_text, problem_file, seed) for seed in seeds}
    return all_answers

def get_answers(problem_text, filename, seed):
    args = {'envir':
            {'fileName': filename, 'problemSeed': int(seed), 'displayMode':'images'},
            'source': base64.b64encode(problem_text),
            'userID': 'admin', 'password': 'admin', 'courseID':'CSE103'}
    res=server.WebworkXMLRPC.renderProblem(args)
    out = {}

    for key, value in res['answers'].iteritems():
        m = part_re.match(key)
        part_id = int(m.group(1))
        out[part_id] = value['correct_ans']
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-c', '--course', help="Course", default="UCSD_CSE103")
    parser.add_argument('-s', '--set-id', help="Set ID", default="Week1")
    parser.add_argument('-b', '--base-dir', help="Webwork base directory", default="/opt/webwork/courses")
    args = parser.parse_args()
    engine = create_engine('mysql+mysqldb://{0}:{1}@localhost/{2}'.format(mysql_username, mysql_password, db), pool_recycle=3600)
    conn = engine.connect()
    metadata = MetaData()

    p = Table("{0}_problem".format(args.course), metadata,
                         Column('set_id', TINYBLOB, nullable=False),
                         Column('problem_id', Integer, nullable=False),
                         Column('source_file', Text),
                         Column('value', Integer),
                         Column('max_attempts', Integer),
                         Column('flags', Text)
    )

    p_u = Table("{0}_problem_user".format(args.course), metadata,
                         Column('user_id', TINYBLOB, nullable=False),
                         Column('set_id', TINYBLOB, nullable=False),
                         Column('problem_id', Integer, nullable=False),
                         Column('source_file', Text),
                         Column('value', Integer),
                         Column('max_attempts', Integer),
                         Column('problem_seed', Integer),
                         Column('status', Float),
                         Column('attempted', Integer),
                         Column('last_answer', Text),
                         Column('num_correct', Integer),
                         Column('num_incorrect', Integer),
                         Column('sub_status', Float),
                         Column('flags', Text)
    )


    answers_table = Table("{0}_correct_answers".format(args.course), metadata,
                            Column('set_id', String(100), nullable=False, index=True),
                            Column('problem_id', Integer, nullable=False, index=True),
                            Column('problem_seed', Integer, nullable=False, index=True),
                            Column('part_id', Integer, nullable=False, index=True),
                            Column('answer', String(1024))
    )


    answers_table.create(engine, checkfirst=True)

    problems = pd.read_sql_query('''SELECT p.set_id, p.problem_id, p.source_file
    FROM {course}_problem as p WHERE p.set_id = ("{set_id}")'''.
                                 format(course=args.course, set_id=args.set_id), engine)

    problem_users = pd.read_sql_query('''SELECT pu.set_id, pu.problem_id, pu.problem_seed
    FROM {course}_problem_user as pu WHERE pu.set_id = ("{set_id}")'''.
                                      format(course=args.course, set_id=args.set_id), engine)
    ans_by_part={
                 'set_id': [],
                 'problem_id':[],
                 'part_id':[],
                 'problem_seed':[],
                 'answer':[]
             }

    for idx, problem in problems.iterrows():
        print problem
        seeds = set(problem_users[problem_users['problem_id']==problem.problem_id].problem_seed)
        print seeds
        full_path = os.path.join(args.base_dir, args.course, 'templates', problem.source_file)
        all_answers = get_all_answers(full_path, seeds)
        for seed, answers in all_answers.iteritems():
            for part_id, answer in answers.iteritems():
                ans_by_part['set_id'].append(args.set_id)
                ans_by_part['problem_id'].append(problem.problem_id)
                ans_by_part['part_id'].append(part_id)
                ans_by_part['problem_seed'].append(seed)
                ans_by_part['answer'].append(answer)

    DF = pd.DataFrame(ans_by_part)
    print DF
    DF.to_sql('{course}_correct_answers'.format(course='args.course'), engine, if_exists='append', index=False)
