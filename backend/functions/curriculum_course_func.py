from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from schema.curriculum_course_schema import CurriculumCourse
from models import Curriculum, CurriculumCourse as CurriculumCourseModel, Course

def getCurrCourse(program: str, curriculum: str, db: Session):
    """Get all courses for a specific curriculum"""
    try:
        # First get the curriculum ID by name and program
        curr = db.query(Curriculum).filter(
            Curriculum.program_id == program,
            Curriculum.name == curriculum
        ).first()
        
        if not curr:
            return []
        
        curriculum_id = curr.id
        
        # Get all curriculum_course entries with course details, sorted properly
        cc_courses = db.query(CurriculumCourseModel, Course).join(
            Course, CurriculumCourseModel.course_id == Course.course_id
        ).filter(
            CurriculumCourseModel.curriculum_id == curriculum_id
        ).order_by(
            CurriculumCourseModel.course_year,
            CurriculumCourseModel.course_sem,
            CurriculumCourseModel.sequence
        ).all()
        
        # Flatten the response
        courses = []
        for cc, course in cc_courses:
            courses.append({
                "course_id": course.course_id,
                "course_name": course.course_name,
                "course_hours": course.course_hours,
                "course_preq": course.course_preq,
                "hours_lec": course.hours_lec,
                "hours_lab": course.hours_lab,
                "units_lec": course.units_lec,
                "units_lab": course.units_lab,
                "course_year": cc.course_year,
                "course_sem": cc.course_sem,
                "sequence": cc.sequence,
                "curriculum": curriculum
            })
        
        return courses
    except SQLAlchemyError as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def addCourse(course: CurriculumCourse, db: Session):
    """Add a course to a curriculum"""
    try:
        # Get curriculum ID from name
        curr = db.query(Curriculum).filter(
            Curriculum.name == course.curriculum,
            Curriculum.program_id == course.program_id
        ).first()
        
        if not curr:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Curriculum '{course.curriculum}' not found")
        
        curriculum_id = curr.id
        
        # Check if course already exists in this curriculum
        existing = db.query(CurriculumCourseModel).filter(
            CurriculumCourseModel.curriculum_id == curriculum_id,
            CurriculumCourseModel.course_id == course.course_id
        ).first()
        
        if existing:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Course '{course.course_id}' already exists in curriculum '{course.curriculum}'"
            )
        
        # Insert the curriculum_course entry
        new_cc = CurriculumCourseModel(
            curriculum_id=curriculum_id,
            course_id=course.course_id,
            course_year=course.course_year,
            course_sem=course.course_sem,
            sequence=course.sequence
        )
        db.add(new_cc)
        db.commit()
        
        return {"message": "Course added to curriculum successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Failed to add course: {str(e)}")

def deleteCourse(course_id: str, program_id: str, curriculum: str, db: Session):
    """Delete a course from a curriculum"""
    try:
        # Get curriculum ID from name
        curr = db.query(Curriculum).filter(
            Curriculum.program_id == program_id,
            Curriculum.name == curriculum
        ).first()
        
        if not curr:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Curriculum '{curriculum}' not found")
        
        curriculum_id = curr.id
        
        # Delete the curriculum_course entry
        cc = db.query(CurriculumCourseModel).filter(
            CurriculumCourseModel.curriculum_id == curriculum_id,
            CurriculumCourseModel.course_id == course_id
        ).first()
        
        if not cc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found in curriculum")
        
        db.delete(cc)
        db.commit()
        
        return {"message": "Course deleted from curriculum successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def reorderCourses(program_id: str, curriculum: str, courses_data: list, db: Session):
    """Update the sequence of courses in a curriculum"""
    try:
        # Get curriculum ID from name
        curr = db.query(Curriculum).filter(
            Curriculum.program_id == program_id,
            Curriculum.name == curriculum
        ).first()
        
        if not curr:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Curriculum '{curriculum}' not found")
        
        curriculum_id = curr.id
        
        # Update sequence for each course
        for idx, course_id in enumerate(courses_data):
            cc = db.query(CurriculumCourseModel).filter(
                CurriculumCourseModel.curriculum_id == curriculum_id,
                CurriculumCourseModel.course_id == course_id
            ).first()
            
            if cc:
                cc.sequence = idx + 1
        
        db.commit()
        return {"message": "Courses reordered successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")
