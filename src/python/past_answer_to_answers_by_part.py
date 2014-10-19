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

from sqlalchemy.orm import sessionmaker
db = 'webwork'

# Session = sessionmaker(bind=engine)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-c', '--course', help="Course", default="UCSD_CSE103")
    args = parser.parse_args()
    engine = create_engine('mysql+mysqldb://{0}:{1}@localhost/{2}'.format(mysql_username, mysql_password, db), pool_recycle=3600)
    metadata = MetaData()

    past_answers = Table("{0}_past_answer".format(args.course), metadata,
                         Column('answer_id', Integer, nullable=False),
                         Column('course_id', String(100), nullable=False),
                         Column('user_id', String(100), nullable=False),
                         Column('set_id', String(100), nullable=False),
                         Column('problem_id', String(100), nullable=False),
                         Column('source_file', Text),
                         Column('timestamp', Integer),
                         Column('scores', TINYTEXT),
                         Column('answer_string', String(1024)),
                         Column('comment_string', String(1024))
    )


    answers_by_part = Table("{0}_answers_by_part".format(args.course), metadata,
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

    answers_by_part.create(engine, checkfirst=True)
    s = select([answers_by_part]).order_by(desc('answer_id')).limit(1)
    conn = engine.connect()
    res1 = conn.execute(s).fetchone()
    print res1

    if res1:
        start_id = res1.answer_id+1
        print "Starting from", start_id
    else:
        start_id= 0
    limit = 1000000
    pa = pd.read_sql_query('SELECT user_id, answer_id, answer_string, scores, problem_id, set_id, timestamp from {0}_past_answer WHERE answer_id >= {1} LIMIT {2}'.format(args.course, start_id, limit), engine, parse_dates={'timestamp': {'unit': 's'}})

    last_pa_by_user_q ="SELECT answer_string from {0}_past_answer WHERE answer_id < {1} \
    AND user_id = '{2}' AND problem_id = '{3}' AND set_id='{4}' \
    ORDER BY answer_id DESC LIMIT 1"

    def last_answer_before(user_id, set_id, problem_id):
        query = last_pa_by_user_q.format(args.course, start_id, user_id, problem_id, set_id)
        result = conn.execute(query).fetchone()
        if result and result[0]:
            return result[0].split('\t')
        else:
            return []
    ans_by_part={'user_id':[],
                 'answer_id':[],
                 'answer_string':[],
                 'score':[],
                 'problem_id':[],
                 'set_id': [],
                 'part_id':[],
                 'timestamp':[]
             }
    print len(pa)
    blank_lines = 0
    part_answer_c = 0
    duplicate_answer_c = 0
    total_answer_count = 0
    for (set_id, problem_id), pas in pa.groupby(['set_id', 'problem_id']):
        print set_id, problem_id

        for user, user_pa in pas.sort('timestamp').groupby('user_id'):
            # user_pa = pas[pas['user_id']==user].sort(columns='timestamp') # get all rows for this user and sort by time
            prev_answers = last_answer_before(user, set_id, problem_id)
            for i in range(len(user_pa)):
                row=user_pa.iloc[i]
                if not row['answer_string']:
                    blank_lines += 1
                    continue
                answers=re.split('\t', row['answer_string'].strip())
                total_answer_count += len(answers)
                for part in range(len(answers)):
                    if (len(prev_answers)<=part or len(prev_answers[part])==0 \
                       or answers[part] != prev_answers[part]) and len(answers[part]) > 0:
                        if  len(row.scores) <= part: # This is a weird error case
                            print row
                        else:
                            part_answer_c += 1
                            ans_by_part['user_id'].append(row['user_id'])
                            ans_by_part['answer_id'].append(row['answer_id'])
                            ans_by_part['answer_string'].append(answers[part])
                            ans_by_part['score'].append(row['scores'][part])
                            ans_by_part['problem_id'].append(row['problem_id'])
                            ans_by_part['set_id'].append(row['set_id'])
                            ans_by_part['part_id'].append(part+1)
                            ans_by_part['timestamp'].append(row['timestamp'])
                    else:
                        if len(prev_answers) > part and answers[part] == prev_answers[part]:
                            duplicate_answer_c += 1
                prev_answers=answers

    print blank_lines
    Answer_DF=pd.DataFrame(ans_by_part)
    print Answer_DF.sort(columns=['part_id','user_id','timestamp'])
    Answer_DF.to_sql('{0}_answers_by_part'.format(args.course), engine, if_exists='append', index=False)

