"""
SQLAlchemy ORM model for ProgramCourse junction table.
"""
from sqlalchemy import Column, String, Integer, ForeignKey
from db.base import Base


class ProgramCourse(Base):
    __tablename__ = "program_course"

    program_id = Column(String, ForeignKey("programs.program_id", ondelete="CASCADE"), primary_key=True)
    course_id = Column(String, ForeignKey("courses.course_id", ondelete="CASCADE"), primary_key=True)
    sequence = Column(Integer, default=0)

    def __repr__(self):
        return f"<ProgramCourse(program_id='{self.program_id}', course_id='{self.course_id}')>"
