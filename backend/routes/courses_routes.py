from functions import courses_func
from functions.program_course_func import getCourseByProgram
from schema.course_schema import CourseSchema
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.deps import get_db

router = APIRouter()

#--------------------------SQLAlchemy ORM Routes--------------------------
@router.get("/getAll")
def getAllCourses(db: Session = Depends(get_db)):
    return courses_func.getAllCourses(db)

@router.post("/add")
def addCourseRoute(course: CourseSchema, db: Session = Depends(get_db)):
    courses_func.addCourse(course, db)
    return {"message": "Course add successful"}

@router.put("/edit/{course_id}")
def editCourseRoute(course: CourseSchema, course_id: str, db: Session = Depends(get_db)):
    courses_func.editCourse(course, course_id, db)
    return {"message": "Course edited succesful"}

@router.delete("/delete/{course_id}")
def deleteCourseRoute(course_id: str, db: Session = Depends(get_db)):
    courses_func.deleteCourse(course_id, db)
    return {"message": "Course deleted succesful"}

@router.put("/update/{program_id}")
def updateCourses(program_id: str, course: list[CourseSchema], db: Session = Depends(get_db)):
    return courses_func.updateCourses(program_id, course, db)

@router.get("/get/{program_id}")
def getCourse(program_id: str, db: Session = Depends(get_db)):
    return getCourseByProgram(program_id, db)