from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

user = 'webworkWrite'
password = 'webwork'
db = 'webwork'
engine = create_engine('mysql+mysqldb://{0}:{1}@localhost/{2}'.format(user, password, db), pool_recycle=3600)
Session = sessionmaker(bind=engine)

class WebWorkBase(object):
    """
    A base class for SQLAlchemy ORM models which map to WebWork tables.

    This makes the tablename depend on the course.
    """

    course = 'UCSD_CSE103'

    @declared_attr
    def __tablename__(cls):
        return "{0}_{1}".format(cls.course, cls.__bases__[0].__name__.lower())

Base = declarative_base(cls=WebWorkBase)

class TableBase(object):
    """
    A base class for table classes for SQL Alchemy.

    This allows adapting a model to a course by calling Model.course_class.
    It's needed to allow defining the course property before the declarative_base is created.

    TODO: the declarative_base could possibly be cached.
    """
    @classmethod
    def course_class(cls, course):
        my_course_base = type("{0}Base".format(course.capitalize()), (WebWorkBase,), {'course': course})
        MyBase = declarative_base(cls=my_course_base)
        MyClass = type("{0}{1}".format(course, cls.__name__), (cls, MyBase,), {})
        return MyClass


