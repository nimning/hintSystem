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

import logging

from sqlalchemy.orm import sessionmaker
db = 'webwork'


def create_table(engine):
    engine = engine
    metadata = MetaData()
    filter_functions = Table("filter_functions", metadata,
                             Column('id', Integer, primary_key=True, autoincrement=True),
                             Column('name', String(100), nullable=False, index=True),
                             Column('course', String(100), nullable=False, index=True),
                             Column('author', String(100), nullable=False),
                             Column('set_id', String(100), nullable=False, index=True),
                             Column('problem_id', Integer, nullable=False, index=True),
                             # To allow generating hints through code, we need a
                             # hint record to reference when assigning hints
                             Column('dummy_hint_id', Integer, nullable=False),
                             Column('code', Text, nullable=False),
                             Column('created', DateTime, nullable=False),
                             Column('updated', DateTime, nullable=False)
    )

    filter_functions.create(engine, checkfirst=True)

if __name__ == '__main__':
    engine = create_engine('mysql+mysqldb://{0}:{1}@localhost/{2}'.format(mysql_username, mysql_password, db), pool_recycle=3600)
    create_table(engine)
