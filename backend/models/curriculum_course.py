"""
SQLAlchemy ORM model for CurriculumCourse junction table.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from db.base import Base


class CurriculumCourse(Base):
    __tablename__ = "curriculum_course"

    id = Column(Integer, primary_key=True)
    curriculum_id = Column(Integer, ForeignKey("curriculum.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(String, ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False)
    course_year = Column(Integer, nullable=False)
    course_sem = Column(Integer, nullable=False)
    sequence = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<CurriculumCourse(id={self.id}, curriculum_id={self.curriculum_id}, course_id='{self.course_id}')>"
