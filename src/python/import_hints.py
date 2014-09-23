#!/usr/bin/env python

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Import hints from one course to another")
    parser.add_argument('source', help="Source Course", default="UCSD_CSE103")
    parser.add_argument('target', help="Target Course", default="CSE103_Fall14")
    args = parser.parse_args()
    engine = create_engine('mysql+mysqldb://{0}:{1}@localhost/{2}'.format(mysql_username, mysql_password, db), pool_recycle=3600)
    metadata = MetaData()

    old_hints = Table("{0}_hint".format(args.source), metadata,
                      Column('id', Integer, nullable=False, primary_key=True),
                      Column('pg_text', String(65536), nullable=False),
                      Column('author', String(255), nullable=False),
                      Column('set_id', String(255), nullable=False),
                      Column('problem_id', Integer, nullable=False),
                      Column('part_id', Integer),
                      Column('created', TIMESTAMP),
                      Column('deleted', Boolean)
    )

    new_hints = Table("{0}_hint".format(args.target), metadata,
                      Column('id', Integer, nullable=False, primary_key=True),
                      Column('pg_text', String(65536), nullable=False),
                      Column('author', String(255), nullable=False),
                      Column('set_id', String(255), nullable=False),
                      Column('problem_id', Integer, nullable=False),
                      Column('part_id', Integer),
                      Column('created', TIMESTAMP),
                      Column('deleted', Boolean)
    )

    old_assigned_hint = Table("{0}_assigned_hint".format(args.source), metadata,
                              Column('id', Integer, nullable=False, primary_key=True),
                              Column('set_id', String(255), nullable=False),
                              Column('problem_id', Integer, nullable=False),
                              Column('pg_id', String(255), nullable=False),
                              Column('user_id', String(255), nullable=False),
                              Column('hint_id', Integer, nullable=False),
                              Column('assigned', TIMESTAMP),
                              Column('hint_html', Text, nullable=False)
    )

    new_assigned_hint = Table("{0}_assigned_hint".format(args.target), metadata,
                              Column('id', Integer, nullable=False, primary_key=True),
                              Column('set_id', String(255), nullable=False),
                              Column('problem_id', Integer, nullable=False),
                              Column('pg_id', String(255), nullable=False),
                              Column('user_id', String(255), nullable=False),
                              Column('hint_id', Integer, nullable=False),
                              Column('assigned', TIMESTAMP),
                              Column('hint_html', Text, nullable=False)
    )


    s = select([old_hints]).order_by(asc('id'))
    conn = engine.connect()
    hint_rows = conn.execute(s)
    hint_mapping = {}
    for row in hint_rows:
        ins = new_hints.insert().values(pg_text = row.pg_text, author=row.author, set_id=row.set_id, problem_id=row.problem_id, part_id=row.part_id, created=row.created, deleted=row.deleted)
        res = conn.execute(ins)
        hint_mapping[row.id]=res.inserted_primary_key[0]

    print "Finished importing hints"
    s2 = select([old_assigned_hint]).order_by(asc('id'))
    assigned_hints = conn.execute(s2)
    for row in assigned_hints:
        ins = new_assigned_hint.insert().values(
            set_id = row.set_id,
            problem_id = row.problem_id, pg_id = row.pg_id, user_id = row.user_id,
            hint_id = hint_mapping[row.hint_id], assigned = row.assigned,
            hint_html = row.hint_html)
        conn.execute(ins )
    print "Finished importing hint assignments"
