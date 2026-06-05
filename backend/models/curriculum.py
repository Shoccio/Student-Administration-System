"""
SQLAlchemy ORM model for Curriculum table.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from db.base import Base


class Curriculum(Base):
    __tablename__ = "curriculum"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    program_id = Column(String, ForeignKey("programs.program_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Curriculum(id={self.id}, name='{self.name}', program_id='{self.program_id}')>"
