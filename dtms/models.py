from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class DrexelClass(Base):
    __tablename__ = "drexel_course_catalogue_class"
    id = Column(Integer, primary_key=True, index=True)
    college = Column(String)
    subject = Column(String)
    number = Column(String, unique=True)
    name = Column(String)
    low_credits = Column(Float)
    high_credits = Column(Float)
    writing_intensive = Column(Boolean)
    prereqs = Column(String)
    desc = Column(String)


class DrexelTMSClass(Base):
    __tablename__ = "drexel_tms_classes"
    id = Column(Integer, primary_key=True, index=True)
    term = Column(String)
    subject = Column(String)
    course_number = Column(String)
    instruction_type = Column(String)
    instruction_method = Column(String)
    section = Column(String)
    crn = Column(String)
    days_time = Column(String)
    instructors = Column(String)
    drexel_class_id = Column(Integer, ForeignKey("drexel_course_catalogue_class.id"))

    drexel_class = relationship("DrexelClass", backref="drexel_tms_classes")
