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
url='http://webwork.cse.ucsd.edu/mod_xmlrpc'
# Login details for fake course for XMLRPC requests
user = 'scheaman'
password = 'scheaman'
course = 'CompoundProblems'

server = xmlrpclib.ServerProxy(url)

part_re = re.compile('AnSwEr(\d{4})')
variables_re = re.compile('(\$\w+)\s*=')
box_re = re.compile('\[_+\]')
ignored_variables = set(['$showPartialCorrectAnswers'])
def get_all_answers(problem_file, problem_users):
    print "Users: ", len(problem_users)
    with open(problem_file, 'r') as f:
        pg_text = f.read()
    box_count = len(box_re.findall(pg_text))
    print "Boxes", box_count
    variables = variables_re.findall(pg_text)
    var_names = []
    var_boxes = []
    for var in variables:
        if var not in ignored_variables:
            var_names.append(var)
            var_boxes.append('[____]{{{0}}}'.format(var))
    file_parts = pg_text.split('END_PGML')

    file_parts.insert(1, 'END_PGML')
    file_parts[1:1] = var_boxes # Add answer boxes for variable values
    new_text = '\n'.join(file_parts)
    print problem_users
    all_answers = {user.user_id: get_answers(new_text, problem_file, user.problem_seed, user.psvn, box_count, var_names) for (idx, user) in problem_users.iterrows()}
    return all_answers

def get_answers(problem_text, filename, seed, psvn, part_count, var_names):
    args = {'envir':
            {'fileName': filename, 'problemSeed': int(seed), 'displayMode':'images', 'psvn': psvn},
            'source': base64.b64encode(problem_text),
            'userID': user, 'password': password, 'courseID': course}
    res=server.WebworkXMLRPC.renderProblem(args)
    part_answers = {}
    variables = {}
    for key, value in res['answers'].iteritems():
        m = part_re.match(key)
        part_id = int(m.group(1))
        if part_id <= part_count:
            part_answers[part_id] = value['correct_ans']
        else:
            variables[var_names[part_id-part_count-1]] = value['correct_ans']
    return part_answers, variables


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-c', '--course', help="Course", default="UCSD_CSE103")
    parser.add_argument('-s', '--set-id', help="Set ID", default="Week1")
    parser.add_argument('-b', '--base-dir', help="Webwork base directory", default="/opt/webwork/courses")
    args = parser.parse_args()
    engine = create_engine('mysql+mysqldb://{0}:{1}@localhost/{2}'.format(mysql_username, mysql_password, db), pool_recycle=3600)
    conn = engine.connect()
    metadata = MetaData()

    answers_table = Table("{0}_correct_answers".format(args.course), metadata,
                            Column('set_id', String(1024), nullable=False, index=True),
                            Column('problem_id', Integer, nullable=False, index=True),
                            Column('user_id', String(1024), nullable=False, index=True),
                            Column('part_id', Integer, nullable=False, index=True),
                            Column('answer', String(1024))
    )

    variables_table = Table("{0}_user_variables".format(args.course), metadata,
                            Column('set_id', String(1024), nullable=False, index=True),
                            Column('problem_id', Integer, nullable=False, index=True),
                            Column('user_id', String(1024), nullable=False, index=True),
                            Column('name', String(1024), nullable=False, index=True),
                            Column('value', Integer, nullable=False)
    )

    answers_table.create(engine, checkfirst=True)
    variables_table.create(engine, checkfirst=True)

    problems = pd.read_sql_query('''SELECT p.set_id, p.problem_id, p.source_file
    FROM {course}_problem as p WHERE p.set_id = ("{set_id}")'''.
                                 format(course=args.course, set_id=args.set_id), engine)

    problem_users = pd.read_sql_query('''SELECT pu.set_id, pu.problem_id, pu.user_id, pu.problem_seed, su.psvn
    FROM {course}_problem_user as pu
    JOIN {course}_set_user as su ON su.user_id = pu.user_id AND su.set_id=("{set_id}")
    WHERE pu.set_id = ("{set_id}")'''.
                                      format(course=args.course, set_id=args.set_id), engine)
    # print problem_users
    ans_by_part={
                 'set_id': [],
                 'problem_id':[],
                 'part_id':[],
                 'user_id':[],
                 'answer':[]
             }
    variable_arrs = {
                 'set_id': [],
                 'problem_id':[],
                 'user_id':[],
                 'name':[],
                 'value':[]
    }
    for idx, problem in problems.iterrows():
        print "Problem!"
        print problem
        
        problem_users = problem_users[(problem_users['problem_id']==problem.problem_id) & (problem_users['set_id']==problem.set_id)]
        full_path = os.path.join(args.base_dir, args.course, 'templates', problem.source_file)
        all_answers = get_all_answers(full_path, problem_users)
        for user_id, (answers, variables) in all_answers.iteritems():
            print user_id
            print variables
            for part_id, answer in answers.iteritems():
                ans_by_part['set_id'].append(args.set_id)
                ans_by_part['problem_id'].append(problem.problem_id)
                ans_by_part['part_id'].append(part_id)
                ans_by_part['user_id'].append(user_id)
                ans_by_part['answer'].append(answer)
            for var_name, var_val in variables.iteritems():
                variable_arrs['set_id'].append(args.set_id)
                variable_arrs['problem_id'].append(problem.problem_id)
                variable_arrs['user_id'].append(user_id)
                variable_arrs['name'].append(var_name)
                variable_arrs['value'].append(var_val)

    ans_DF = pd.DataFrame(ans_by_part)
    var_DF = pd.DataFrame(variable_arrs)
    print ans_DF
    print var_DF
    ans_DF.to_sql('{course}_correct_answers'.format(course='args.course'), engine, if_exists='append', index=False)
    var_DF.to_sql('{course}_user_variables'.format(course='args.course'), engine, if_exists='append', index=False)
