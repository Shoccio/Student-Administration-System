"""
SQLAlchemy ORM model for StudentCourse junction table.
Tracks course grades, remarks, and evaluator information for each student-course pair.
"""
from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime
from datetime import datetime
from db.base import Base


class StudentCourse(Base):
    __tablename__ = "student_courses"

    student_id = Column(String, ForeignKey("students.student_id", ondelete="CASCADE"), primary_key=True)
    course_id = Column(String, ForeignKey("courses.course_id", ondelete="CASCADE"), primary_key=True)
    grade = Column(Float, nullable=True)
    remark = Column(String, default="")
    evaluator = Column(String, nullable=True)
    retakes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<StudentCourse(student_id='{self.student_id}', course_id='{self.course_id}', grade={self.grade})>"
