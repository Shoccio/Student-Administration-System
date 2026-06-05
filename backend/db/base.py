"""
Database declarative base for all SQLAlchemy models.
This is the base class all ORM models inherit from.
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
