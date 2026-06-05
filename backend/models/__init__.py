"""
SQLAlchemy ORM models package.
Exports all database models for easy importing.
"""
from models.course import Course
from models.program import Program
from models.program_course import ProgramCourse
from models.curriculum import Curriculum
from models.curriculum_course import CurriculumCourse
from models.student import Student
from models.student_course import StudentCourse
from models.user_credential import UserCredential

__all__ = [
    "Course",
    "Program",
    "ProgramCourse",
    "Curriculum",
    "CurriculumCourse",
    "Student",
    "StudentCourse",
    "UserCredential",
]
