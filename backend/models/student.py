"""
SQLAlchemy ORM model for Student table.
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime
from datetime import datetime
from db.base import Base


class Student(Base):
    __tablename__ = "students"

    student_id = Column(String, primary_key=True)
    program_id = Column(String, ForeignKey("programs.program_id", ondelete="CASCADE"), nullable=False)
    curriculum_id = Column(Integer, ForeignKey("curriculum.id", ondelete="SET NULL"), nullable=True)
    f_name = Column(String, nullable=False)
    l_name = Column(String, nullable=False)
    m_name = Column(String, nullable=True)
    gwa = Column(Float, nullable=True)
    status = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    gender = Column(String, nullable=True)
    is_transferee = Column(Boolean, default=False)
    archived = Column(Boolean, default=False)
    email = Column(String, nullable=True)
    dept = Column(String, nullable=True)
    evaluated = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Student(student_id='{self.student_id}', f_name='{self.f_name}', l_name='{self.l_name}')>"
