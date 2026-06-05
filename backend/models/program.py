"""
SQLAlchemy ORM model for Program table.
"""
from sqlalchemy import Column, String
from db.base import Base


class Program(Base):
    __tablename__ = "programs"

    program_id = Column(String, primary_key=True)
    program_name = Column(String, nullable=False)
    program_specialization = Column(String, nullable=True)

    def __repr__(self):
        return f"<Program(program_id='{self.program_id}', program_name='{self.program_name}')>"
