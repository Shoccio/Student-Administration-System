from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from sqlalchemy.orm import Session
from functions.student_course_func import updateGrades, getStudentCourses, updateGradesBulk
from functions.student_func import getStudent
from db.database import get_db
from pydantic import BaseModel
from typing import Optional
import csv
import io

router = APIRouter()

class Grades(BaseModel):
    grade: Optional[float] = None
    remark: str
    force_incomplete: bool = False
    retakes: Optional[int] = None
    evaluator: Optional[str] = None

@router.get("/get")
def getStudentCourse(student_id: str, program_id: str, db: Session = Depends(get_db)):
    return getStudentCourses(student_id, program_id, db=db)

@router.patch("/update-grade/{student_id}-{course_id}")
def updateGrade(course_id: str, student_id: str, newGrades: Grades, db: Session = Depends(get_db)):
    result = updateGrades(
        course_id,
        student_id,
        newGrades.grade,
        newGrades.remark,
        newGrades.force_incomplete,
        newGrades.retakes,
        newGrades.evaluator,
        db
    )

    getStudent(student_id, db)

    return result

@router.post("/update-grades-bulk/{student_id}")
async def updateGradesBulkRoute(student_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    csv_data = csv.DictReader(io.StringIO(contents.decode("utf-8")))
    
    grades_list = []
    for index, row in enumerate(csv_data, start=2):
        course_id = (row.get("course_id") or "").strip()
        if not course_id:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Missing course_id at CSV row {index}"
            )

        raw_grade = row.get("grade")
        if raw_grade is None:
            raw_grade = row.get("grades")

        raw_grade = str(raw_grade or "").strip()

        if raw_grade == "" or raw_grade.lower() == "null":
            parsed_grade = None
        else:
            try:
                parsed_grade = float(raw_grade)
            except ValueError:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    f"Invalid grade '{raw_grade}' at CSV row {index}"
                )

        grades_list.append({
            "course_id": course_id,
            "grade": parsed_grade
        })

    result = updateGradesBulk(student_id, grades_list, db)

    getStudent(student_id, db)
    return result

