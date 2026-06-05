"""
SQLAlchemy ORM model for Course table.
"""
from sqlalchemy import Column, String, Integer, Numeric, TIMESTAMP
from sqlalchemy.sql import func
from db.base import Base

class Course(Base):
    __tablename__ = "courses"

    course_id = Column(String(20), primary_key=True)
    course_name = Column(String, nullable=False)

    course_hours = Column(Integer)
    course_preq = Column(String(20))

    course_sem = Column(Integer)

    hours_lab = Column(Integer)
    hours_lec = Column(Integer)

    units_lab = Column(Numeric(4,2))
    units_lec = Column(Numeric(4,2))

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
