import csv
import io
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from schema.student_schema import Student
from functions import student_func, auth_func
from db.database import get_db
from services.student_services import addStudentHelper, bulkAddStudents


router = APIRouter()

@router.post("/add")
def addStudent(student: Student, db: Session = Depends(get_db)):
    return addStudentHelper(student, db)

@router.put("/edit")
def editStudent(student: Student, db: Session = Depends(get_db)):
    return student_func.editStudent(student, db)

@router.delete("/delete/{student_id}")
def deleteStudent(student_id: str, db: Session = Depends(get_db)):
    return student_func.deleteStudent(student_id, db)

@router.get("/search")
def search_students(q: str = Query(default="", min_length=0), apply_filters: bool = Query(default=False), request: Request = None, db: Session = Depends(get_db)):
    # Get admin's department from token
    admin_dept = None
    if request:
        admin_dept = auth_func.get_admin_dept_from_token(request)
    return student_func.search_students(q, apply_filters, admin_dept, db)

@router.get("/get/{student_id}")
def getStudentByID(student_id: str, db: Session = Depends(get_db)):
    return student_func.getStudent(student_id, db)

@router.get("/get_all")
def getAllStudents(db: Session = Depends(get_db)):
    return student_func.get_students(db)

@router.get("/filter/{key}/{value}")
def getFilteredStudents(key: str, value: str, db: Session = Depends(get_db)):
    result = student_func.filter_students(key, value, db)
    return JSONResponse(content=result)

@router.post("/edit_filter/{key}/{value}")
def editFilter(key: str, value: str, db: Session = Depends(get_db)):
    updated_filters = student_func.edit_filter(key, value, db)
    return JSONResponse(content={"filters": updated_filters})

@router.put("/reset_filter")
def resetFilter(db: Session = Depends(get_db)):
    updated_filters = student_func.reset_filter()
    return JSONResponse(content={"filters": updated_filters})

@router.post("/evaluate/{student_id}")
def evaluateStudent(student_id: str, db: Session = Depends(get_db)):
    return student_func.evaluateStudent(student_id, db)

@router.post("/take_off_evaluation/{student_id}")
def takeOffEvaluation(student_id: str, db: Session = Depends(get_db)):
    return student_func.takeOffEvaluation(student_id, db)


@router.post("/bulk-upload")
async def bulk_upload_students(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Accept a CSV file and insert each row as a student.
        Required columns (same as Add Student popup):
            student_id, email, dept, program_id, curriculum, f_name, l_name, year, status, gender
        Optional columns:
            m_name, is_transferee, gwa, evaluated, archived

    Returns a summary: { inserted, failed, errors: [{row, reason}] }
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only .csv files are accepted")

    content = await file.read()
    try:
        text = content.decode("utf-8-sig")  # strip BOM if present
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    required = {
        "student_id",
        "email",
        "dept",
        "program_id",
        "curriculum",
        "f_name",
        "l_name",
        "year",
        "status",
        "gender",
    }
    if not required.issubset(set(reader.fieldnames or [])):
        missing = required - set(reader.fieldnames or [])
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"CSV missing required columns: {', '.join(sorted(missing))}"
        )

    rows = list(reader)
    results = bulkAddStudents(rows, db)
    return JSONResponse(status_code=207, content=results)

@router.patch("/archive")
def archiveStudent(student_id: str = Query(...), db: Session = Depends(get_db)):
    return student_func.archiveStudent(student_id, db)

@router.patch("/unarchive")
def unarchiveStudent(student_id: str = Query(...), db: Session = Depends(get_db)):
    return student_func.unarchiveStudent(student_id, db)

