from functions import curriculum_course_func
from schema.curriculum_course_schema import CurriculumCourse, DeleteCurriculumCourse
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from db.deps import get_db
from pydantic import BaseModel

class ReorderCoursesRequest(BaseModel):
    program_id: str
    curriculum: str
    course_ids: list

router = APIRouter()

@router.get("/get_courses")
def getCurrCourses(program: str, curriculum: str, db: Session = Depends(get_db)):
    return curriculum_course_func.getCurrCourse(program, curriculum, db)

@router.post("/add-course")
def addCourse(course: CurriculumCourse, db: Session = Depends(get_db)):
    return curriculum_course_func.addCourse(course, db)

@router.post("/delete-course")
def deleteCourse(course: DeleteCurriculumCourse, db: Session = Depends(get_db)):
    return curriculum_course_func.deleteCourse(course.course_id, course.program_id, course.curriculum, db)

@router.post("/reorder-courses")
def reorderCourses(request: ReorderCoursesRequest, db: Session = Depends(get_db)):
    return curriculum_course_func.reorderCourses(request.program_id, request.curriculum, request.course_ids, db)
