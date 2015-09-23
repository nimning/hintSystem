from sqlalchemy import Column, Integer, String, DateTime, Boolean
from base import WebWorkBase, Base, engine, Session, TableBase

class Hint(TableBase):
    id = Column(Integer, primary_key=True)
    pg_text = Column(String, nullable=False)
    author = Column(String(255), nullable=False)
    set_id = Column(String(255), nullable=False)
    problem_id = Column(Integer, nullable=False)
    created = Column(DateTime, nullable=False)
    deleted = Column(Boolean)
    approved = Column(Boolean, nullable=False)
