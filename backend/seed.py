from db.database import get_db
from models import *
from schema import student_schema
from services.student_services import addStudentHelper

db = next(get_db())

try:
    # =========================
    # SUPER ADMIN
    # =========================
    existing_sp_admin = db.query(UserCredential).filter_by(username="super_admin", dept="CSS").first()

    if not existing_sp_admin:
        db.add(UserCredential(
            username="super_admin",
            hashed_password="TEMP_#Super_Admin123",
            role="super admin",
            dept="CSS",
        ))

    # =========================
    # ADMIN
    # =========================
    existing_admin = db.query(UserCredential).filter_by(username="admin", dept="CSS").first()

    if not existing_admin:
        db.add(UserCredential(
            username="admin",
            hashed_password="TEMP_#Admin123",
            role="admin",
            dept="CSS",
        ))


    # =========================
    # PROGRAM
    # =========================
    program = db.query(Program).filter_by(program_id="BSCS").first()

    if not program:
        program = Program(
            program_id="BSCS",
            program_name="Bachelor of Science in Computer Science",
            program_specialization="Data Science"
        )
        db.add(program)

    # =========================
    # COURSES
    # =========================
    courses = [
        Course(
            course_id="CS101",
            course_name="Introduction to Programming",
            course_hours=3,
            course_preq=None,
            course_sem=1,
            hours_lab=2,
            hours_lec=1,
            units_lab=1.00,
            units_lec=2.00,
        ),

        Course(
            course_id="CS102",
            course_name="Object-Oriented Programming",
            course_hours=4,
            course_preq="CS101",
            course_sem=2,
            hours_lab=2,
            hours_lec=2,
            units_lab=1.00,
            units_lec=3.00,
        ),

        Course(
            course_id="CS201",
            course_name="Data Structures and Algorithms",
            course_hours=5,
            course_preq="CS102",
            course_sem=1,
            hours_lab=2,
            hours_lec=3,
            units_lab=1.00,
            units_lec=4.00,
        ),

        Course(
            course_id="DB101",
            course_name="Database Management Systems",
            course_hours=4,
            course_preq="CS102",
            course_sem=2,
            hours_lab=2,
            hours_lec=2,
            units_lab=1.00,
            units_lec=3.00,
        ),

        Course(
            course_id="NET101",
            course_name="Computer Networks",
            course_hours=3,
            course_preq="CS201",
            course_sem=2,
            hours_lab=1,
            hours_lec=2,
            units_lab=1.00,
            units_lec=2.00,
        ),
    ]

    for c in courses:
        exists = db.query(Course).filter_by(course_id=c.course_id).first()
        if not exists:
            db.add(c)


    db.commit()
    # =========================
    # CURRICULUM
    # =========================
    curriculum = db.query(Curriculum).filter_by(name="2024 - 2025", program_id="BSCS").first()

    if not curriculum:
        curriculum = Curriculum(
            name="2024 - 2025",
            program_id="BSCS",
        )
        db.add(curriculum)
        db.flush()  # get curriculum.id BEFORE using it

    # =========================
    # CURRICULUM COURSES
    # =========================
    curriculum_courses = [
        CurriculumCourse(
            curriculum_id=curriculum.id,
            course_id="CS101",
            course_year=1,
            course_sem=1,
            sequence=1
        ),

        CurriculumCourse(
            curriculum_id=curriculum.id,
            course_id="CS102",
            course_year=1,
            course_sem=2,
            sequence=2
        ),

        CurriculumCourse(
            curriculum_id=curriculum.id,
            course_id="CS201",
            course_year=2,
            course_sem=1,
            sequence=3
        ),

        CurriculumCourse(
            curriculum_id=curriculum.id,
            course_id="DB101",
            course_year=2,
            course_sem=2,
            sequence=4
        ),

        CurriculumCourse(
            curriculum_id=curriculum.id,
            course_id="NET101",
            course_year=3,
            course_sem=1,
            sequence=5
        ),
    ]

    for curriculum_course in curriculum_courses:
        exists = db.query(CurriculumCourse).filter_by(
            curriculum_id=curriculum_course.curriculum_id,
            course_id=curriculum_course.course_id
        ).first()

        if not exists:
            db.add(curriculum_course)

    # =========================
    # STUDENT
    # =========================
    student = db.query(Student).filter_by(student_id="2025-0001").first()

    if not student:
        new_student = student_schema.Student(
            student_id="2025-0001",
            program_id="BSCS",
            curriculum_id=curriculum.id,
            f_name="Juan",
            l_name="Dela Cruz",
            m_name="Santos",
            gwa=0,
            status="Regular",
            year=2,
            gender="Male",
            is_transferee=False,
            archived=False,
            email="juan.delacruz@example.com",
            dept="CSS",
            evaluated=1
        )
        
        addStudentHelper(new_student, db)

    # =========================
    # COMMIT ONCE
    # =========================
    db.commit()

finally:
    db.close()