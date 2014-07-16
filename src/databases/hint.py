from sqlalchemy import Column, Integer, String, DateTime, Boolean
from base import WebWorkBase, Base, engine, Session, TableBase

class Hint(TableBase):
    id = Column(Integer, primary_key=True)
    pg_text = Column(String)
    author = Column(String(255))
    set_id = Column(String(255))
    problem_id = Column(Integer)
    created = Column(DateTime)
    deleted = Column(Boolean)

