from schema.course_schema import CourseSchema 
from functions.program_course_func import updateOrder
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Course, ProgramCourse

#--------------------------SQLAlchemy ORM Functions--------------------------
def getAllCourses(db: Session):
    """Get all courses from the courses table"""
    try:
        courses = db.query(Course).all()
        # Sort by course_id
        return sorted(courses, key=lambda x: x.course_id if hasattr(x, 'course_id') else "")
    except SQLAlchemyError as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def addCourse(course: CourseSchema, db: Session):
    course_dict = course.model_dump()
    
    try:
        # Check if course already exists
        existing = db.query(Course).filter(Course.course_id == course_dict['course_id']).first()
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, "Course already exists")
        
        new_course = Course(**course_dict)
        db.add(new_course)
        db.commit()
        db.refresh(new_course)
        return new_course
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def editCourse(course: CourseSchema, course_id: str, db: Session):
    # Check if old course exists
    old_course = db.query(Course).filter(Course.course_id == course_id).first()
    
    if not old_course:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course does not exist")
    
    course_dict = course.model_dump()
    new_id = course_dict["course_id"]
    
    try:
        # If the course_id changed, delete old and insert new
        if course_id != new_id:
            # Check if new_id already exists
            existing = db.query(Course).filter(Course.course_id == new_id).first()
            if existing:
                raise HTTPException(status.HTTP_409_CONFLICT, f"Course {new_id} already exists")
            
            db.delete(old_course)
            db.flush()
            
            new_course = Course(**course_dict)
            db.add(new_course)
        else:
            # If course_id is same, just update
            for key, value in course_dict.items():
                setattr(old_course, key, value)
        
        db.commit()
        db.refresh(old_course) if course_id == new_id else db.refresh(new_course)
        return old_course if course_id == new_id else new_course
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def deleteCourse(course_id: str, db: Session):
    # Check if course exists
    course = db.query(Course).filter(Course.course_id == course_id).first()
    
    if not course:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course does not exist")
    
    try:
        db.delete(course)
        db.commit()
        return {"message": "Course deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")


def updateCourses(program_id: str, courses: list[CourseSchema], db: Session):
    """
    Sync course changes across courses and program_course tables.
    Ported from course_checklist updateCourses / checkCourses / checkCollection,
    adapted for SQL — uses upsert instead of Firestore batch operations.
    """
    errors = []

    for course in courses:
        course_dict = course.model_dump()
        course_id = course_dict["course_id"]
        sequence = course_dict.pop("sequence", 0) if "sequence" in course_dict else 0

        try:
            # Upsert into courses table (insert or update)
            existing = db.query(Course).filter(Course.course_id == course_id).first()
            if existing:
                for key, value in course_dict.items():
                    setattr(existing, key, value)
            else:
                new_course = Course(**course_dict)
                db.add(new_course)

            db.flush()

            # Upsert into program_course table
            pc_existing = db.query(ProgramCourse).filter(
                ProgramCourse.program_id == program_id,
                ProgramCourse.course_id == course_id
            ).first()

            if pc_existing:
                pc_existing.sequence = sequence
            else:
                new_pc = ProgramCourse(
                    program_id=program_id,
                    course_id=course_id,
                    sequence=sequence
                )
                db.add(new_pc)

        except Exception as e:
            errors.append({"course_id": course_id, "error": str(e)})

    if errors:
        db.rollback()
        raise HTTPException(
            status.HTTP_207_MULTI_STATUS,
            detail={"message": "Some courses failed to sync", "errors": errors}
        )
    
    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

    return {"message": f"{len(courses)} course(s) synced for program {program_id}"}

