from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from functions.student_course_func import getStudentCourses, getGWA, deleteCourses as DS
from schema.student_schema import Student
from schema.user_schema import User
from models import Student as StudentModel, StudentCourse, UserCredential

# Load students on module import
# Note: With SQLAlchemy, we no longer need to load all students into memory
# Database queries are efficient and don't require caching

active_filter = {
    "status": {"value": "", "active": False}, 
    "is_transferee": {"value": "", "active": False},
    "program_id": ["BSCS", "BSIT", "BSEMC", "BITCF"],
    "year": [1, 2, 3, 4]}

search_filter = {
    "year": [1, 2, 3, 4],
    "status": ["Regular", "Irregular"], 
    "is_transferee": [True, False],
    "program_id": ["BSCS", "BSIT", "BSEMC", "BITCF"],
    "archived": [False]}

def addStudent(student: Student, db: Session):
    student_info = student.model_dump(exclude={"curriculum"}, exclude_none=True)
    
    try:
        # Check if student_id already exists
        existing = db.query(StudentModel).filter(StudentModel.student_id == student.student_id).first()
        if existing:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Student with ID '{student.student_id}' already exists")
        
        # Check if email already exists (if provided)
        if student.email:
            existing_email = db.query(StudentModel).filter(StudentModel.email == student.email).first()
            if existing_email:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Student with email '{student.email}' already exists")
        
        new_student = StudentModel(**student_info)
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return new_student
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def editStudent(student: Student, db: Session):
    student_info = student.model_dump(exclude={"curriculum"}, exclude_none=True)
    student_id = student_info["student_id"]
    
    try:
        # Check if student exists
        existing_student = db.query(StudentModel).filter(StudentModel.student_id == student_id).first()
        if not existing_student:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Student with ID '{student_id}' not found")
        
        # Check if email already exists in another student record (if provided)
        if student.email:
            existing_email = db.query(StudentModel).filter(
                StudentModel.email == student.email,
                StudentModel.student_id != student_id
            ).first()
            if existing_email:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Student with email '{student.email}' already exists")
        
        # Update student
        for key, value in student_info.items():
            setattr(existing_student, key, value)
        
        db.commit()
        db.refresh(existing_student)
        return existing_student
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def deleteStudent(student_id: str, db: Session):
    try:
        # Check if student exists
        student = db.query(StudentModel).filter(StudentModel.student_id == student_id).first()
        
        if not student:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")
        
        # Delete related records
        db.query(UserCredential).filter(UserCredential.student_id == student_id).delete()
        db.query(StudentCourse).filter(StudentCourse.student_id == student_id).delete()
        
        # Delete student
        db.delete(student)
        db.commit()
        
        return {"message": "Student deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def getStudent(student_id: str = None, db: Session = None):
    if not student_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Admin must specify a student ID.")
    
    try:
        # Get student from database
        student_data = db.query(StudentModel).filter(StudentModel.student_id == student_id).first()
        
        if not student_data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")
        
        # Convert to dict for manipulation
        student_dict = {
            "student_id": student_data.student_id,
            "program_id": student_data.program_id,
            "curriculum_id": student_data.curriculum_id,
            "f_name": student_data.f_name,
            "l_name": student_data.l_name,
            "m_name": student_data.m_name,
            "gwa": student_data.gwa,
            "status": student_data.status,
            "year": student_data.year,
            "gender": student_data.gender,
            "is_transferee": student_data.is_transferee,
            "archived": student_data.archived,
            "email": student_data.email,
            "dept": student_data.dept,
            "evaluated": student_data.evaluated
        }

        # Check if student has any courses in student_courses
        check_courses = db.query(StudentCourse).filter(StudentCourse.student_id == student_id).first()
        
        # Only auto-populate courses for regular students (not irregular, not transferee)
        is_regular = student_dict.get("status", "").upper() == "REGULAR"
        is_transferee = student_dict.get("is_transferee", False)
        
        if not check_courses and is_regular and not is_transferee:
            from functions.student_course_func import addEntry
            addEntry(student_id, student_dict["program_id"], db=db)
        
        courses = getStudentCourses(student_id, student_dict["program_id"], student_dict.get("curriculum_id"), db=db)

        total_units = sum(float(course["course_units"]) for course in courses)
        units_taken = sum(float(course["course_units"]) for course in courses if course["remark"] == "Passed")
        gwa = getGWA(courses)

        student_dict["gwa"] = gwa
        student_dict["units_taken"] = units_taken
        student_dict["total_units_required"] = total_units
        student_dict["role"] = "student"
        middle_name = student_dict.get("m_name") or ""
        student_dict["full_name"] = f"{student_dict['l_name']}, {student_dict['f_name']} {middle_name}".strip()

        from models import Program
        program = db.query(Program).filter(Program.program_id == student_dict["program_id"]).first()
        program_specialization = ""
        if program:
            program_specialization = program.program_specialization or ""

        student_dict["prgm_spec"] = (
            f"{student_dict['program_id']} - {program_specialization}"
            if program_specialization
            else student_dict["program_id"]
        )
        
        # Update GWA in database
        student_data.gwa = gwa
        db.commit()

        student_dict["gwa"] = str(gwa)

        
        # Convert evaluated timestamp to string if it exists
        if "evaluated" in student_dict and student_dict["evaluated"] is not None:
            if hasattr(student_dict["evaluated"], "isoformat"):
                student_dict["evaluated"] = student_dict["evaluated"].isoformat()
            else:
                student_dict["evaluated"] = str(student_dict["evaluated"])

        return JSONResponse(content={"student": student_dict, "courses": courses})
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in getStudent for {student_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error fetching student: {str(e)}")

def search_students(query: str, apply_filters: bool = False, admin_dept: str = None, db: Session = None):
    """
    Search students by name or student_id in the students table.
    When apply_filters is True, applies the active search filters.
    When query is empty and apply_filters is True, returns all students that match the active filters.
    When admin_dept is provided, only returns students from that department.
    """
    try:
        query_lower = query.lower().strip() if query else ""
        results = []

        # Start building the query
        query_obj = db.query(StudentModel)
        
        # Filter by admin's department if provided
        if admin_dept:
            query_obj = query_obj.filter(StudentModel.dept == admin_dept)
        
        # Only apply search filters if apply_filters is True
        if apply_filters:
            if search_filter.get("status"):
                query_obj = query_obj.filter(StudentModel.status.in_(search_filter["status"]))
            
            if search_filter.get("is_transferee") is not None:
                query_obj = query_obj.filter(StudentModel.is_transferee.in_(search_filter["is_transferee"]))
            
            if search_filter.get("program_id"):
                query_obj = query_obj.filter(StudentModel.program_id.in_(search_filter["program_id"]))
            
            if search_filter.get("year"):
                query_obj = query_obj.filter(StudentModel.year.in_(search_filter["year"]))

            if search_filter.get("archived"):
                query_obj = query_obj.filter(StudentModel.archived.in_(search_filter["archived"]))
        
        db_results = query_obj.limit(1000).all()

        for s in db_results:
            full_name = " ".join(
                filter(None, [s.l_name, s.f_name, s.m_name or ""])
            ).lower()
            # If query is empty, include all students; otherwise filter by query
            if not query_lower or query_lower in full_name or query_lower in s.student_id.lower():
                results.append({
                    "student_id": s.student_id,
                    "name": f"{s.l_name}, {s.f_name} {s.m_name or ''}".strip(),
                    "evaluated": str(s.evaluated) if s.evaluated else "",
                    "dept": s.dept or ""
                })
                if len(results) >= 30:
                    break

        return results
    except SQLAlchemyError as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def get_students(db: Session):
    """Get all students sorted by status (Regular first) and GWA"""
    try:
        students = db.query(StudentModel).all()
        # Sort by status (Regular first) and GWA (descending)
        sorted_students = sorted(
            students,
            key=lambda x: (x.status != "Regular", -(x.gwa or 0))
        )
        return [{
            "student_id": s.student_id,
            "f_name": s.f_name,
            "l_name": s.l_name,
            "m_name": s.m_name,
            "program_id": s.program_id,
            "year": s.year,
            "status": s.status,
            "gwa": s.gwa,
            "is_transferee": s.is_transferee,
            "archived": s.archived,
            "email": s.email,
            "dept": s.dept
        } for s in sorted_students]
    except SQLAlchemyError as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def edit_filter(key: str, value: str):
    if key == "is_transferee" or key == "archived":
        value = str_to_bool(value)
    elif key == "year":
        value = int(value)

    if value in search_filter[key]:
        search_filter[key].remove(value)
    else:
        search_filter[key].append(value)
    
    return search_filter


def str_to_bool(value: str):
    if value == "true":
        return True
    elif value == "false":
        return False
    
    return value

def apply_filter():
    pool = students_list

    for key, value in search_filter.items():
        print(key)

        pool = [students for students in pool
                if students[key] in search_filter[key]]
        
    return pool

def reset_searchFilter():
    global search_filter 
    search_filter = {
    "year": [1, 2, 3, 4],
    "status": ["Regular", "Irregular"], 
    "is_transferee": [True, False],
    "program_id": ["BSCS", "BSIT", "BSEMC", "BITCF"]}
    return search_filter

def archiveStudent(student_id: str, db: Session):
    try:
        # Check if student exists
        student = db.query(StudentModel).filter(StudentModel.student_id == student_id).first()
        
        if not student:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")
        
        student.archived = True
        db.commit()
        
        return JSONResponse(content={"message": "Student archived successfully"})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def unarchiveStudent(student_id: str, db: Session):
    try:
        # Check if student exists
        student = db.query(StudentModel).filter(StudentModel.student_id == student_id).first()
        
        if not student:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")
        
        student.archived = False
        db.commit()
        
        return JSONResponse(content={"message": "Student unarchived successfully"})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")
    

#------------------------------------------------FOR DASHBOARD--------------------------------------------------------

def filter_students(key: str, value: str):
    if key == "program_id":
        if value in active_filter[key]:
            active_filter[key].remove(value)
        else:
            active_filter[key].append(value)

        return {"filtered": execute_filter(), "filters": active_filter}

    if key == "year":
        num = int(value)

        if num in active_filter[key]:
            active_filter[key].remove(num)
        else:
            active_filter[key].append(num)

        return {"filtered": execute_filter(), "filters": active_filter}
            
    if key == "is_transferee":
        value = str_to_bool(value)

    if active_filter[key]["value"] == value:
        active_filter[key]["value"] = ""
        active_filter[key]["active"] = False
    else:
        active_filter[key]["value"] = value
        active_filter[key]["active"] = True

    return {"filtered": execute_filter(), "filters": active_filter}

def execute_filter():
    pool = students_list

    for key, value in active_filter.items():
        if key == "program_id" or key == "year":
            pool = [students for students in pool
                    if students[key] in active_filter[key]]
            continue

        if value["active"] != True:
            continue

        pool = [students for students in pool
                if students[key] == value["value"]]
        
    return pool

def reset_filter():
    global active_filter 
    active_filter = {
    "status": {"value": "", "active": False}, 
    "is_transferee": {"value": "", "active": False},
    "program_id": ["BSCS", "BSIT", "BSEMC", "BITCF"],
    "year": [1, 2, 3, 4]}
    return active_filter

#------------------------------------------------FOR EVALUATION--------------------------------------------------------

def evaluateStudent(student_id: str, db: Session):
    from datetime import datetime, timezone
    
    try:
        # Check if student exists
        student = db.query(StudentModel).filter(StudentModel.student_id == student_id).first()
        
        if not student:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")
        
        current_timestamp = str(datetime.now(timezone.utc).date())
        student.evaluated = current_timestamp
        db.commit()
        
        return JSONResponse(content={"message": "Student evaluated successfully", "timestamp": str(current_timestamp)})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def takeOffEvaluation(student_id: str, db: Session):
    try:
        # Check if student exists
        student = db.query(StudentModel).filter(StudentModel.student_id == student_id).first()
        
        if not student:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")
        
        student.evaluated = None
        db.commit()
        
        return JSONResponse(content={"message": "Evaluation removed successfully"})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")