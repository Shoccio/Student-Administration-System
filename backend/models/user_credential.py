"""
SQLAlchemy ORM model for UserCredential table.
Handles authentication for all user types: admin, student, and faculty.
Replaces Supabase Auth with database-backed authentication.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from datetime import datetime
from db.base import Base


class UserCredential(Base):
    __tablename__ = "user_credentials"

    username = Column(String, primary_key=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'admin', 'student', 'super admin'
    full_name = Column(String, nullable=True)
    student_id = Column(String, ForeignKey("students.student_id", ondelete="SET NULL"), unique=True, nullable=True)
    email = Column(String, nullable=True)
    dept = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<UserCredential(username='{self.username}', role='{self.role}')>"
