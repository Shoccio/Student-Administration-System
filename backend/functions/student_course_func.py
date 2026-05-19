# functions/student_course_func.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import math
from models import StudentCourse, Course, Curriculum, CurriculumCourse, ProgramCourse, Student as StudentModel

def addEntry(student_id: str, program_id: str, curriculum: str | None = None, curriculum_id: int | None = None, db: Session = None):
    try:
        pc_result = None

        if curriculum_id is None and curriculum:
            curr = db.query(Curriculum).filter(
                Curriculum.program_id == program_id,
                Curriculum.name == curriculum
            ).first()

            if not curr:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    f"Curriculum '{curriculum}' not found for program '{program_id}'"
                )

            curriculum_id = curr.id

        if curriculum_id is not None:
            cc_result = db.query(CurriculumCourse).filter(
                CurriculumCourse.curriculum_id == curriculum_id
            ).order_by(
                CurriculumCourse.course_year,
                CurriculumCourse.course_sem,
                CurriculumCourse.sequence
            ).all()
            pc_result = [{"course_id": cc.course_id} for cc in cc_result]
        else:
            # Fallback: get all courses for the program
            pc_result_data = db.query(ProgramCourse).filter(
                ProgramCourse.program_id == program_id
            ).all()
            pc_result = [{"course_id": pc.course_id} for pc in pc_result_data]
        
        if not pc_result:
            if curriculum:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    f"No courses found for curriculum '{curriculum}'"
                )
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No courses found for this program")
        
        # Create student_course entries (only IDs, no denormalized data)
        student_courses = [
            StudentCourse(
                student_id=student_id,
                course_id=course["course_id"],
                grade=None,
                remark="",
                evaluator=""
            )
            for course in pc_result
        ]
        
        # Insert in bulk
        db.add_all(student_courses)
        db.commit()
        return {"message": "Courses added successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def addCourseStudent(course_ids: list[str], db: Session):
    try:
        # Get all students
        students = db.query(StudentModel).all()
        students_ids = [student.student_id for student in students]
        
        # Create student_course entries
        entries = []
        for student_id in students_ids:
            for course_id in course_ids:
                entries.append(StudentCourse(
                    student_id=student_id,
                    course_id=course_id,
                    grade=None,
                    remark="",
                    evaluator=""
                ))
        
        # Insert in bulk
        if entries:
            db.add_all(entries)
            db.commit()
        return {"message": "Courses added to all students successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def deleteCourses(course_id: str, db: Session):
    try:
        # Delete all student_courses for this course_id
        deleted = db.query(StudentCourse).filter(StudentCourse.course_id == course_id).delete()
        db.commit()
        
        if deleted == 0:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found")
        
        return {"message": "Course deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def deleteStudent(student_id: str, db: Session):
    try:
        # Delete all courses for this student
        deleted = db.query(StudentCourse).filter(StudentCourse.student_id == student_id).delete()
        db.commit()
        
        if deleted == 0:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")
        
        return {"message": "Student courses deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")
    
def getStudentCourses(student_id: str, program_id: str, curriculum_id: int | None = None, db: Session = None):
    try:
        # 1. Get student_courses for this student
        student_courses_data = db.query(StudentCourse).filter(
            StudentCourse.student_id == student_id
        ).all()
        
        if not student_courses_data:
            return []
        
        # Get list of course_ids
        course_ids = [sc.course_id for sc in student_courses_data]
        
        if not course_ids:
            return []
        
        # 2. Get course details
        courses_data = db.query(Course).filter(Course.course_id.in_(course_ids)).all()
        course_map = {c.course_id: c for c in courses_data}
        
        # 3. Resolve curriculum mapping
        curriculum_meta_map = {}
        selected_curriculum_id = curriculum_id

        if selected_curriculum_id is None:
            curriculums = db.query(Curriculum).filter(
                Curriculum.program_id == program_id
            ).all()

            if curriculums:
                curriculum_ids = [curr.id for curr in curriculums]
                curriculum_courses = db.query(CurriculumCourse).filter(
                    CurriculumCourse.curriculum_id.in_(curriculum_ids),
                    CurriculumCourse.course_id.in_(course_ids)
                ).all()

                overlap_count = {}
                for item in curriculum_courses:
                    cid = item.curriculum_id
                    overlap_count[cid] = overlap_count.get(cid, 0) + 1

                if overlap_count:
                    selected_curriculum_id = max(overlap_count, key=overlap_count.get)

        if selected_curriculum_id is not None:
            selected_curriculum_courses = db.query(CurriculumCourse).filter(
                CurriculumCourse.curriculum_id == selected_curriculum_id,
                CurriculumCourse.course_id.in_(course_ids)
            ).all()

            curriculum_meta_map = {
                item.course_id: {
                    "course_year": item.course_year,
                    "course_sem": item.course_sem,
                    "sequence": item.sequence
                }
                for item in selected_curriculum_courses
            }

        # 4. Get program_course data for this program (fallback metadata)
        program_courses_data = db.query(ProgramCourse).filter(
            ProgramCourse.program_id == program_id,
            ProgramCourse.course_id.in_(course_ids)
        ).all()
        
        # Create lookup maps
        sequence_map = {pc.course_id: pc.sequence for pc in program_courses_data}
        grade_map = {
            sc.course_id: {
                "grade": sc.grade,
                "remark": sc.remark,
                "retakes": sc.retakes if hasattr(sc, 'retakes') else None,
                "evaluator": sc.evaluator
            }
            for sc in student_courses_data
        }
        
        # Build final course list
        courses = []
        for index, course_id in enumerate(course_ids):
            curriculum_meta = curriculum_meta_map.get(course_id, {})

            sequence = curriculum_meta.get("sequence")
            if sequence is None:
                sequence = sequence_map.get(course_id)

            if sequence is None:
                # Fallback for curriculum-seeded courses that are not present in program_course
                sequence = 10000 + index
            
            course_data = course_map.get(course_id)
            grade_data = grade_map.get(course_id, {})
            remark_value = grade_data.get("remark") or "N/A"
            evaluated_value = bool(grade_data.get("grade") is not None or (remark_value not in ["", "N/A"]))
            
            year = curriculum_meta.get("course_year")
            semester = curriculum_meta.get("course_sem") or (course_data.course_sem if course_data else None)

            # Fallback when curriculum metadata is unavailable.
            if year is None:
                if sequence >= 10000:
                    year = 1
                else:
                    year = min((sequence // 10) + 1, 4)
            
            units_lec = course_data.units_lec if course_data else 0 or 0
            units_lab = course_data.units_lab if course_data else 0 or 0
            
            courses.append({
                "course_id": course_id,
                "course_name": course_data.course_name if course_data else None,
                "course_units": str(units_lec + units_lab),
                "units_lec": str(units_lec),
                "units_lab": str(units_lab),
                "semester": semester,
                "year": year,
                "grade": grade_data.get("grade"),
                "remark": remark_value,
                "evaluated": evaluated_value,
                "sequence": sequence,
                "retakes": grade_data.get("retakes"),
                "evaluator": grade_data.get("evaluator")
            })
        
        # Sort by curriculum year/semester first, then sequence for stable in-sem ordering.
        courses.sort(key=lambda x: (x.get("year") or 999, x.get("semester") or 999, x["sequence"], x["course_id"] or ""))
            
        return courses
    except SQLAlchemyError as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def getGWA(courses):
    total_weighted = 0
    total_units = 0

    for course in courses:
        grade = course.get("grade")
        units = course.get("course_units")
        remark = course.get("remark", "")

        if grade is not None and remark == "Passed":
            fixed = gradeConversion(grade)
            total_weighted += fixed * units
            total_units += units

    if total_units == 0:
        return 0.0

    return round(total_weighted / total_units, 2)

def updateGrades(course_id: str, student_id: str, grade: float, remark: str, force_incomplete: bool = False, retakes: int | None = None, evaluator: str | None = None, db: Session = None):
    try:
        if grade == -1.0:
            grade = None
        if force_incomplete or str(remark or "").strip().lower() == "incomplete":
            grade = None
            remark = "Incomplete"
        else:
            remark = getRemark(grade)
        
        # Find the student_course record
        course_record = db.query(StudentCourse).filter(
            StudentCourse.course_id == course_id,
            StudentCourse.student_id == student_id
        ).first()
        
        if not course_record:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Student/Course not found")
        
        # Update the record
        course_record.grade = grade
        course_record.remark = remark
        
        if retakes is not None:
            course_record.retakes = retakes
        
        if evaluator is not None:
            course_record.evaluator = evaluator

        db.commit()
        return {"message": "Grade updated successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def updateGradesBulk(student_id: str, grades_list: list, db: Session):
    try:
        for grade_entry in grades_list:
            course_id = grade_entry["course_id"]
            grade = grade_entry["grade"]

            if grade == -1.0:
                grade = None

            remark = getRemark(grade)

            course_record = db.query(StudentCourse).filter(
                StudentCourse.course_id == course_id,
                StudentCourse.student_id == student_id
            ).first()

            if course_record:
                course_record.grade = grade
                course_record.remark = remark
            else:
                print(f"Course {course_id} not found for student {student_id}")

        db.commit()
        return {"message": "Grades updated successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

def getRemark(grade: float | None) -> str:
    if grade is None:
        return "N/A"
    elif grade >= 75:
        return "Passed"
    else:
        return "Failed"

def gradeConversion(grade: float):
    fixed = math.floor(grade)

    if grade >= 99 and grade <= 100:
        return 1.0
    elif grade >= 96 and grade <= 98:
        return 1.25
    elif grade >= 93 and grade <= 95:
        return 1.50
    elif grade >= 90 and grade <= 92:
        return 1.75
    elif grade >= 87 and grade <= 89:
        return 2.0
    elif grade >= 84 and grade <= 86:
        return 2.25
    elif grade >= 81 and grade <= 83:
        return 2.5
    elif grade >= 78 and grade <= 80:
        return 2.75
    elif grade >= 75 and grade <= 77:
        return 3.0
    
    return 5.0

    