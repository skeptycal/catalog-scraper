from sqlalchemy import (create_engine, Column, ForeignKey, Integer, String,
                        Boolean)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker

db_name = "/catalog.db"
engine = create_engine("sqlite://" + db_name)
session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Model = declarative_base(name='Model')
Model.query = session.query_property()

def init_db():
    """
    Sets up db and returns a db object to interact with.
    """
    Model.metadata.create_all(bind=engine)


class Course(Model):
    """
    Represents a course.
    """
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True)
    num = Column(Integer)
    tag = Column(String(6))
    title = Column(String(100))
    # Some courses are variable credits.
    credits = Column(String(4))
    specialty = Column(String(4), default='')
    url = Column(String(200))


class CourseOffering(Model):
    """
    Represents an offering of a specific course.
    """
    __tablename__ = 'course_offerings'

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    term = Column(String(10))
    crn = Column(Integer)
    section = Column(Integer)
    pass_nopass = Column(Boolean)
    instructor = Column(String)
    day_time = Column(String(250))
    location = Column(String(100))
    campus = Column(String(250))
    c_type = Column(String(100))
    status = Column(String(50))
    cap = Column(Integer)
    current = Column(Integer)
    available = Column(String(10))
    wl_cap = Column(Integer)
    wl_current = Column(Integer)
    wl_available = Column(Integer)
    section_title = Column(String(150))
    fees = Column(String(100))
    restrictions = Column(String(500))
    comments = Column(String(500))

    course = relationship('Course', backref='course_offering')
