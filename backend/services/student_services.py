from schema.student_schema import Student
from functions.student_func import addStudent
from functions.student_course_func import addEntry
from models import Curriculum, UserCredential
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status


def addStudentHelper(student: Student, db: Session):
    """Add a new student with auto-created user credentials and courses"""
    try:
        # Resolve curriculum_id from curriculum name if needed
        if student.curriculum and not student.curriculum_id:
            curriculum = db.query(Curriculum).filter(
                Curriculum.program_id == student.program_id,
                Curriculum.name == student.curriculum
            ).first()

            if curriculum:
                student.curriculum_id = curriculum.id

        # Add student record
        added_student = addStudent(student, db)

        # Auto-create user credentials (ported from course_checklist addUser).
        # Check if credentials already exist to avoid duplicate key errors
        existing_creds = db.query(UserCredential).filter(
            UserCredential.username == student.student_id
        ).first()
        
        if not existing_creds:
            # Username = student_id. Password stored as TEMP_<student_id> so it gets
            # bcrypt-hashed automatically on the student's first login.
            new_cred = UserCredential(
                username=student.student_id,
                hashed_password="TEMP_#Uphsl123",
                role="student",
                student_id=student.student_id,
                full_name=f"{student.f_name} {student.l_name}",
                email=student.email
            )
            db.add(new_cred)
            db.commit()

        # Add their courses
        addEntry(student.student_id, student.program_id, student.curriculum, student.curriculum_id, db)
        
        return added_student
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")


def bulkAddStudents(rows: list[dict], db: Session) -> dict:
    """
    Insert multiple students from parsed CSV rows.
    Returns { inserted: int, failed: int, errors: [{row, reason}] }
    """
    inserted = 0
    failed = 0
    errors = []

    for i, row in enumerate(rows, start=2):  # start=2: row 1 is the header
        try:
            required_fields = [
                "student_id", "email", "dept", "program_id", "curriculum",
                "f_name", "l_name", "year", "status", "gender"
            ]

            for field in required_fields:
                if not row.get(field, "").strip():
                    raise ValueError(f"Missing required value for '{field}'")

            student = Student(
                student_id   = row["student_id"].strip(),
                f_name       = row["f_name"].strip(),
                m_name       = row.get("m_name", "").strip() or None,
                l_name       = row["l_name"].strip(),
                program_id   = row["program_id"].strip(),
                curriculum   = row["curriculum"].strip(),
                year         = int(row["year"]),
                status       = row["status"].strip(),
                is_transferee= row.get("is_transferee", "false").strip().lower() == "true",
                dept         = row["dept"].strip(),
                email        = row["email"].strip(),
                gwa          = float(row["gwa"]) if row.get("gwa", "").strip() else None,
                evaluated    = int(row["evaluated"]) if row.get("evaluated", "").strip() else None,
                archived     = row.get("archived", "false").strip().lower() == "true",
                gender       = row["gender"].strip(),
            )
            addStudentHelper(student, db)
            inserted += 1
        except Exception as e:
            failed += 1
            errors.append({"row": i, "student_id": row.get("student_id", ""), "reason": str(e)})

    return {"inserted": inserted, "failed": failed, "errors": errors}

