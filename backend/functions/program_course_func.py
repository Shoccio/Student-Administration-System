from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from models import Curriculum, CurriculumCourse, Course, ProgramCourse

def getCourseByProgram(program_id: str, db: Session):
    """Get all courses in the active curriculum for a program, ordered by year/semester"""
    try:
        # Get the active curriculum for this program (or latest if no active flag)
        curriculum = db.query(Curriculum)\
            .filter(Curriculum.program_id == program_id)\
            .order_by(Curriculum.created_at.desc())\
            .first()
        
        if not curriculum:
            return []
        
        curriculum_id = curriculum.id
        
        # Get all courses in this curriculum, ordered by course_year and course_sem
        curriculum_courses = db.query(CurriculumCourse, Course)\
            .join(Course, CurriculumCourse.course_id == Course.course_id)\
            .filter(CurriculumCourse.curriculum_id == curriculum_id)\
            .order_by(CurriculumCourse.course_year, CurriculumCourse.course_sem, CurriculumCourse.sequence)\
            .all()
        
        courses = []
        for cc, course in curriculum_courses:
            courses.append({
                "course_id": course.course_id,
                "course_name": course.course_name,
                "course_hours": course.course_hours,
                "course_preq": course.course_preq,
                "course_sem": course.course_sem,
                "hours_lab": course.hours_lab,
                "hours_lec": course.hours_lec,
                "units_lab": course.units_lab,
                "units_lec": course.units_lec,
                "sequence": cc.sequence,
                "course_year": cc.course_year,
                "curriculum_course_sem": cc.course_sem
            })
        
        return courses
    except SQLAlchemyError as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def updateOrder(program_id: str, course_ids: list[str], db: Session):
    """Update sequence for each course in the order provided"""
    try:
        for index, course_id in enumerate(course_ids):
            program_course = db.query(ProgramCourse)\
                .filter(
                    ProgramCourse.program_id == program_id,
                    ProgramCourse.course_id == course_id
                )\
                .first()
            
            if program_course:
                program_course.sequence = index
        
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

