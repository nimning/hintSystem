from sqlalchemy import Column, Integer, String
from base import WebWorkBase, Base, engine, Session, TableBase

class User(TableBase):
    user_id = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email_address = Column(String)
    student_id = Column(String)
    status = Column(String)
    section = Column(String)
    recitation = Column(String)
    comment = Column(String)

"""
Example code using this class:
session = Session()
CSE103User = User.course_class('UCSD_CSE103')
for instance in session.query(CSE103User).order_by(CSE103User.user_id):
    print instance.first_name, instance.last_name, instance.student_id
"""
