"""
Campus Connect ERP - Production Database Operations & Seeding Utility
Provides safe schema initialization and idempotent institutional data seeding.
"""
import os
import hmac
import logging
from datetime import datetime, date, time, timedelta
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.utils.helpers import generate_receipt_number, generate_transaction_id, generate_certificate_code

logger = logging.getLogger(__name__)


def verify_db_init_token(provided_token: str):
    """
    Verifies the DB_INIT_TOKEN against the secret environment variable on Render.
    Returns (is_valid: bool, error_message: str or None, http_status: int).
    """
    secret_token = os.environ.get('DB_INIT_TOKEN')
    
    if not secret_token:
        logger.error("DB_INIT_TOKEN environment variable is not configured on the server.")
        return False, "Server configuration error: DB_INIT_TOKEN environment variable is not set on Render.", 500
    
    if not provided_token:
        logger.warning("Database operation attempt without initialization token.")
        return False, "Missing authorization token. Please provide DB_INIT_TOKEN via 'X-DB-Init-Token' header, Bearer Authorization, or JSON payload.", 401
    
    # Timing-attack safe comparison
    if not hmac.compare_digest(str(provided_token).strip(), str(secret_token).strip()):
        logger.warning("Invalid DB_INIT_TOKEN provided.")
        return False, "Unauthorized: Invalid initialization token.", 401
    
    return True, None, 200


def initialize_database_schema():
    """
    Creates all SQLAlchemy database tables if they do not exist and provisions
    the default master Admin account ('admin') and baseline academic entities.
    Does NOT drop tables, reset data, or overwrite existing production tables.
    """
    # Import all models to ensure complete SQLAlchemy metadata registration
    import app.models  # noqa: F401
    from app.models.user import User, Role
    from app.models.academic_session import AcademicSession
    from app.models.semester import Semester

    logger.info("Executing initialize_database_schema...")
    
    # 1. Create all missing tables
    db.create_all()
    
    created_entities = []
    
    # 2. Ensure baseline Academic Sessions exist
    session_2025_26 = AcademicSession.query.filter_by(name='2025-26').first()
    if not session_2025_26:
        session_2025_26 = AcademicSession(name='2025-26', start_year=2025, end_year=2026, is_current=True)
        db.session.add(session_2025_26)
        created_entities.append("AcademicSession: 2025-26")
    
    # 3. Ensure baseline Semesters 1 through 8 exist
    for sem_num in range(1, 9):
        sem = Semester.query.filter_by(number=sem_num).first()
        if not sem:
            sem = Semester(number=sem_num, name=f'Semester {sem_num}', is_active=True)
            db.session.add(sem)
            created_entities.append(f"Semester: {sem_num}")

    db.session.flush()

    # 4. Ensure master Admin user exists
    admin_user = User.query.filter_by(username='admin').first()
    admin_created = False
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@campusconnect.edu',
            first_name='Administrator',
            last_name='',
            phone='+91 98765 00001',
            role=Role.ADMIN,
            must_change_password=False,
            is_active=True
        )
        admin_user.set_password('admin')
        db.session.add(admin_user)
        admin_created = True
        created_entities.append("User: admin (Master Administrator)")
    else:
        # Guarantee name and active status are set without altering custom password
        if not admin_user.first_name:
            admin_user.first_name = 'Administrator'
        if not admin_user.is_active:
            admin_user.is_active = True
        if admin_user.role != Role.ADMIN:
            admin_user.role = Role.ADMIN

    db.session.commit()

    # 5. Backfill any missing sequential identifiers for existing students & faculty
    try:
        from app.utils.id_generator import backfill_missing_identifiers
        backfill_result = backfill_missing_identifiers()
        if backfill_result.get('students_updated') or backfill_result.get('faculty_updated'):
            created_entities.append(f"Auto-IDs Backfilled: {backfill_result.get('students_updated')} students, {backfill_result.get('faculty_updated')} faculty")
    except Exception as e:
        logger.warning(f"Identifier backfill notice: {e}")

    logger.info(f"Database schema initialized successfully. Created: {len(created_entities)} baseline items.")

    return {
        "success": True,
        "status": "initialized",
        "message": "Database tables and master admin account successfully initialized.",
        "admin_user": {
            "username": "admin",
            "name": admin_user.full_name,
            "role": admin_user.role,
            "status": "Created" if admin_created else "Already Exists",
            "must_change_password": admin_user.must_change_password
        },
        "created_entities": created_entities,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


def seed_database_safely():
    """
    Populates comprehensive realistic institutional data if not already present.
    Guarantees safety:
    - Never drops existing tables
    - Never truncates or deletes existing production records
    - Checks for entity existence before adding
    """
    import app.models  # noqa: F401
    from app.models.user import User, Role
    from app.models.department import Department
    from app.models.course import Course
    from app.models.semester import Semester
    from app.models.academic_session import AcademicSession
    from app.models.class_division import ClassDivision
    from app.models.subject import Subject
    from app.models.faculty import Faculty
    from app.models.student import Student
    from app.models.timetable import Timetable
    from app.models.attendance import AttendanceSession, AttendanceRecord
    from app.models.assignment import Assignment, AssignmentSubmission, StudyMaterial
    from app.models.exam import Exam, ExamResult
    from app.models.fee import FeeStructure, StudentFee, FeePayment
    from app.models.leave import LeaveRequest
    from app.models.notice import Notice
    from app.models.feedback import Feedback
    from app.models.complaint import Complaint
    from app.models.event import Event, EventRegistration
    from app.models.certificate import CertificateRequest
    from app.models.notification import Notification

    logger.info("Executing seed_database_safely...")

    # Ensure tables exist first
    db.create_all()

    # 1. Academic Sessions
    session_2025_26 = AcademicSession.query.filter_by(name='2025-26').first()
    if not session_2025_26:
        session_2025_26 = AcademicSession(name='2025-26', start_year=2025, end_year=2026, is_current=True)
        db.session.add(session_2025_26)

    session_2024_25 = AcademicSession.query.filter_by(name='2024-25').first()
    if not session_2024_25:
        session_2024_25 = AcademicSession(name='2024-25', start_year=2024, end_year=2025, is_current=False)
        db.session.add(session_2024_25)

    # 2. Semesters
    semesters = {}
    for i in range(1, 9):
        sem = Semester.query.filter_by(number=i).first()
        if not sem:
            sem = Semester(number=i, name=f'Semester {i}', is_active=True)
            db.session.add(sem)
        semesters[i] = sem
    db.session.flush()

    # 3. Departments
    depts_data = [
        ('Computer Science & Engineering', 'CSE', 'Department of Computer Science & Engineering with state-of-the-art AI & Cloud labs.'),
        ('Electronics & Communication Engineering', 'ECE', 'Department of ECE focusing on Embedded Systems, VLSI, and IoT.'),
        ('Information Technology', 'IT', 'Department of IT focusing on Software Architecture, Cybersecurity, and Data Analytics.'),
        ('Mechanical Engineering', 'MECH', 'Department of Mechanical Engineering with advanced Robotics and CAD/CAM labs.'),
        ('Management Studies', 'MBA', 'School of Management offering finance, marketing, and systems specialization.')
    ]
    departments = {}
    for name, code, desc in depts_data:
        dept = Department.query.filter_by(code=code).first()
        if not dept:
            dept = Department(name=name, code=code, description=desc)
            db.session.add(dept)
        departments[code] = dept
    db.session.flush()

    dept_cse = departments['CSE']
    dept_ece = departments['ECE']
    dept_it = departments['IT']
    dept_mba = departments['MBA']

    # 4. Courses
    courses_data = [
        ('B.Tech Computer Science & Engineering', 'BT-CSE', dept_cse.id, 4, 8),
        ('B.Tech Electronics & Communication', 'BT-ECE', dept_ece.id, 4, 8),
        ('B.Tech Information Technology', 'BT-IT', dept_it.id, 4, 8),
        ('Master of Business Administration', 'MBA', dept_mba.id, 2, 4)
    ]
    courses = {}
    for name, code, dept_id, dur, tot_sem in courses_data:
        crs = Course.query.filter_by(code=code).first()
        if not crs:
            crs = Course(name=name, code=code, department_id=dept_id, duration_years=dur, total_semesters=tot_sem)
            db.session.add(crs)
        courses[code] = crs
    db.session.flush()

    course_btech_cse = courses['BT-CSE']

    # 5. Class Divisions
    div_cse_4a = ClassDivision.query.filter_by(department_id=dept_cse.id, course_id=course_btech_cse.id, semester_id=semesters[4].id, name='A').first()
    if not div_cse_4a:
        div_cse_4a = ClassDivision(name='A', department_id=dept_cse.id, course_id=course_btech_cse.id, semester_id=semesters[4].id, session_id=session_2025_26.id, room_number='LT-301')
        db.session.add(div_cse_4a)

    div_cse_4b = ClassDivision.query.filter_by(department_id=dept_cse.id, course_id=course_btech_cse.id, semester_id=semesters[4].id, name='B').first()
    if not div_cse_4b:
        div_cse_4b = ClassDivision(name='B', department_id=dept_cse.id, course_id=course_btech_cse.id, semester_id=semesters[4].id, session_id=session_2025_26.id, room_number='LT-302')
        db.session.add(div_cse_4b)

    db.session.flush()

    # 6. Users & Accounts
    # Admin
    user_admin = User.query.filter_by(username='admin').first()
    if not user_admin:
        user_admin = User(
            username='admin',
            email='admin@campusconnect.edu',
            password_hash=generate_password_hash('admin'),
            role=Role.ADMIN,
            first_name='Administrator',
            last_name='',
            phone='+91 98765 00001',
            must_change_password=False,
            is_active=True
        )
        db.session.add(user_admin)

    # HOD User & Faculty Record
    user_hod = User.query.filter_by(username='hod_cse').first()
    if not user_hod:
        user_hod = User(
            username='hod_cse',
            email='hod.cse@campusconnect.edu',
            password_hash=generate_password_hash('hod123'),
            role=Role.HOD,
            first_name='Dr. Rajesh',
            last_name='Sharma',
            phone='+91 98765 00002',
            is_active=True
        )
        db.session.add(user_hod)
        db.session.flush()

    faculty_hod = Faculty.query.filter_by(user_id=user_hod.id).first()
    if not faculty_hod:
        faculty_hod = Faculty(
            user_id=user_hod.id,
            faculty_id='FAC-CSE-001',
            employee_id='EMP1001',
            first_name='Dr. Rajesh',
            last_name='Sharma',
            full_name='Dr. Rajesh Sharma',
            designation='Professor & Head of Department',
            department_id=dept_cse.id,
            official_email='hod.cse@campusconnect.edu',
            mobile='+91 98765 00002',
            qualification='Ph.D. in Computer Science (IIT Bombay)',
            specialization='Distributed Systems & Cloud Computing',
            joining_date=date(2016, 7, 1),
            status='Active',
            blood_group='O+'
        )
        db.session.add(faculty_hod)
        db.session.flush()
        dept_cse.hod_faculty_id = faculty_hod.id

    # Faculty Member
    user_faculty = User.query.filter_by(username='faculty').first()
    if not user_faculty:
        user_faculty = User(
            username='faculty',
            email='faculty@campusconnect.edu',
            password_hash=generate_password_hash('faculty123'),
            role=Role.FACULTY,
            first_name='Prof. Priya',
            last_name='Nair',
            phone='+91 98765 00003',
            is_active=True
        )
        db.session.add(user_faculty)
        db.session.flush()

    faculty_priya = Faculty.query.filter_by(user_id=user_faculty.id).first()
    if not faculty_priya:
        faculty_priya = Faculty(
            user_id=user_faculty.id,
            faculty_id='FAC-CSE-002',
            employee_id='EMP1002',
            first_name='Prof. Priya',
            last_name='Nair',
            full_name='Prof. Priya Nair',
            designation='Associate Professor',
            department_id=dept_cse.id,
            official_email='faculty@campusconnect.edu',
            mobile='+91 98765 00003',
            qualification='M.Tech CSE, Ph.D. (Pursuing)',
            specialization='Database Systems & Web Technologies',
            joining_date=date(2019, 8, 15),
            status='Active',
            blood_group='B+'
        )
        db.session.add(faculty_priya)
        db.session.flush()

    # Additional Faculty: Dr. Meera (ECE HOD)
    user_meera = User.query.filter_by(username='meera.nambiar').first()
    if not user_meera:
        user_meera = User(
            username='meera.nambiar',
            email='meera.nambiar@apex.edu',
            password_hash=generate_password_hash('faculty123'),
            role=Role.HOD,
            first_name='Dr. Meera',
            last_name='Nambiar',
            phone='+91 98450 34567',
            is_active=True
        )
        db.session.add(user_meera)
        db.session.flush()

    fac_meera = Faculty.query.filter_by(user_id=user_meera.id).first()
    if not fac_meera:
        fac_meera = Faculty(
            user_id=user_meera.id,
            faculty_id='FAC-ECE-001',
            employee_id='EMP1003',
            first_name='Dr. Meera',
            last_name='Nambiar',
            full_name='Dr. Meera Nambiar',
            designation='Professor & HOD',
            department_id=dept_ece.id,
            official_email='meera.nambiar@apex.edu',
            mobile='+91 98450 34567',
            qualification='Ph.D. Microelectronics',
            specialization='VLSI Design & Embedded Systems',
            joining_date=date(2017, 6, 1),
            status='Active',
            blood_group='A+'
        )
        db.session.add(fac_meera)
        db.session.flush()
        dept_ece.hod_faculty_id = fac_meera.id

    # Additional Faculty: Prof. Ananya Iyer (CSE)
    user_ananya = User.query.filter_by(username='ananya.iyer').first()
    if not user_ananya:
        user_ananya = User(
            username='ananya.iyer',
            email='ananya.iyer@apex.edu',
            password_hash=generate_password_hash('faculty123'),
            role=Role.FACULTY,
            first_name='Prof. Ananya',
            last_name='Iyer',
            phone='+91 98450 93456',
            is_active=True
        )
        db.session.add(user_ananya)
        db.session.flush()

    fac_ananya = Faculty.query.filter_by(user_id=user_ananya.id).first()
    if not fac_ananya:
        fac_ananya = Faculty(
            user_id=user_ananya.id,
            faculty_id='FAC-CSE-003',
            employee_id='EMP1004',
            first_name='Prof. Ananya',
            last_name='Iyer',
            full_name='Prof. Ananya Iyer',
            designation='Assistant Professor',
            department_id=dept_cse.id,
            official_email='ananya.iyer@apex.edu',
            mobile='+91 98450 93456',
            qualification='M.Tech IISc Bangalore',
            specialization='AI, Computer Vision & Transformers',
            joining_date=date(2021, 7, 15),
            status='Active',
            blood_group='O+'
        )
        db.session.add(fac_ananya)
        db.session.flush()

    # Primary Student (Aarav Patel)
    user_student = User.query.filter_by(username='student').first()
    if not user_student:
        user_student = User(
            username='student',
            email='student@campusconnect.edu',
            password_hash=generate_password_hash('student123'),
            role=Role.STUDENT,
            first_name='Aarav',
            last_name='Patel',
            phone='+91 98765 11111',
            is_active=True
        )
        db.session.add(user_student)
        db.session.flush()

    student_aarav = Student.query.filter_by(user_id=user_student.id).first()
    if not student_aarav:
        student_aarav = Student(
            user_id=user_student.id,
            student_id='STD-2023-0101',
            enrollment_no='EN2023CSE0101',
            admission_no='ADM-2023-0101',
            roll_no='23CS401',
            first_name='Aarav',
            last_name='Patel',
            full_name='Aarav Patel',
            dob=date(2004, 5, 14),
            gender='Male',
            blood_group='O+',
            college_email='student@campusconnect.edu',
            mobile='+91 98765 11111',
            department_id=dept_cse.id,
            course_id=course_btech_cse.id,
            semester_id=semesters[4].id,
            session_id=session_2025_26.id,
            division_id=div_cse_4a.id,
            admission_date=date(2023, 8, 1),
            batch='2023-2027',
            status='Active',
            father_name='Vikram Patel',
            father_phone='+91 98765 22222',
            father_occupation='Software Architect',
            mother_name='Sunita Patel',
            curr_address_line1='Flat 402, Green Meadows, Tech Park Road',
            curr_city='Knowledge City',
            curr_state='State Capital',
            curr_pincode='560100',
            emergency_name='Vikram Patel',
            emergency_phone='+91 98765 22222',
            emergency_relation='Father'
        )
        db.session.add(student_aarav)

    # Student 2: Priya Patel
    user_priya_stu = User.query.filter_by(username='priya.patel').first()
    if not user_priya_stu:
        user_priya_stu = User(
            username='priya.patel',
            email='priya.patel@student.apex.edu',
            password_hash=generate_password_hash('student123'),
            role=Role.STUDENT,
            first_name='Priya',
            last_name='Patel',
            phone='+91 98450 54321',
            is_active=True
        )
        db.session.add(user_priya_stu)
        db.session.flush()

    student_priya = Student.query.filter_by(user_id=user_priya_stu.id).first()
    if not student_priya:
        student_priya = Student(
            user_id=user_priya_stu.id,
            student_id='STD-2023-0102',
            enrollment_no='EN2023CSE0102',
            admission_no='ADM-2023-0102',
            roll_no='23CS402',
            first_name='Priya',
            last_name='Patel',
            full_name='Priya Patel',
            dob=date(2004, 9, 22),
            gender='Female',
            blood_group='O+',
            college_email='priya.patel@student.apex.edu',
            mobile='+91 98450 54321',
            department_id=dept_cse.id,
            course_id=course_btech_cse.id,
            semester_id=semesters[4].id,
            session_id=session_2025_26.id,
            division_id=div_cse_4a.id,
            admission_date=date(2023, 8, 1),
            batch='2023-2027',
            status='Active',
            father_name='Kishore Patel',
            father_phone='+91 98450 98765',
            curr_address_line1='Hostel Block-A, Room 108',
            curr_city='Apex University Campus',
            curr_state='California',
            curr_pincode='94016',
        )
        db.session.add(student_priya)

    # Student 3: Aditya Roy (6th Sem)
    user_aditya = User.query.filter_by(username='aditya.roy').first()
    if not user_aditya:
        user_aditya = User(
            username='aditya.roy',
            email='aditya.roy@student.apex.edu',
            password_hash=generate_password_hash('student123'),
            role=Role.STUDENT,
            first_name='Aditya',
            last_name='Roy',
            phone='+91 98450 78123',
            is_active=True
        )
        db.session.add(user_aditya)
        db.session.flush()

    student_aditya = Student.query.filter_by(user_id=user_aditya.id).first()
    if not student_aditya:
        student_aditya = Student(
            user_id=user_aditya.id,
            student_id='STD-2022-0055',
            enrollment_no='EN2022CSE0055',
            admission_no='ADM-2022-7102',
            roll_no='22CS055',
            first_name='Aditya',
            last_name='Roy',
            full_name='Aditya Roy',
            dob=date(2003, 5, 18),
            gender='Male',
            blood_group='A+',
            college_email='aditya.roy@student.apex.edu',
            mobile='+91 98450 78123',
            department_id=dept_cse.id,
            course_id=course_btech_cse.id,
            semester_id=semesters[6].id,
            session_id=session_2025_26.id,
            division_id=div_cse_4a.id,
            admission_date=date(2022, 8, 1),
            batch='2022-2026',
            status='Active',
            father_name='Debabrata Roy',
            father_phone='+91 98450 89234',
            curr_address_line1='Hostel Block-C, Room 402',
            curr_city='Apex University Campus',
            curr_state='California',
            curr_pincode='94016',
        )
        db.session.add(student_aditya)

    # 7. Subjects
    subjects_data = [
        ('Database Management Systems', 'CS401', 4, 'Theory'),
        ('Operating Systems', 'CS402', 4, 'Theory'),
        ('Design & Analysis of Algorithms', 'CS403', 4, 'Theory'),
        ('Full Stack Web Technologies', 'CS404', 3, 'Practical'),
        ('Software Engineering & Agile Methodologies', 'CS405', 3, 'Theory')
    ]
    subjects = {}
    for name, code, cred, stype in subjects_data:
        sub = Subject.query.filter_by(code=code).first()
        if not sub:
            sub = Subject(
                name=name,
                code=code,
                credits=cred,
                subject_type=stype,
                department_id=dept_cse.id,
                course_id=course_btech_cse.id,
                semester_id=semesters[4].id
            )
            db.session.add(sub)
        subjects[code] = sub
    db.session.flush()

    sub_dbms = subjects['CS401']
    sub_os = subjects['CS402']

    # 8. Timetable
    if Timetable.query.filter_by(class_division_id=div_cse_4a.id).count() == 0:
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        for d in days:
            tt1 = Timetable(
                class_division_id=div_cse_4a.id,
                subject_id=sub_dbms.id,
                faculty_id=faculty_priya.id,
                semester_id=semesters[4].id,
                session_id=session_2025_26.id,
                day_of_week=d,
                start_time=time(9, 0),
                end_time=time(10, 0),
                room_number='LT-301'
            )
            tt2 = Timetable(
                class_division_id=div_cse_4a.id,
                subject_id=sub_os.id,
                faculty_id=faculty_hod.id,
                semester_id=semesters[4].id,
                session_id=session_2025_26.id,
                day_of_week=d,
                start_time=time(10, 0),
                end_time=time(11, 0),
                room_number='LT-301'
            )
            db.session.add_all([tt1, tt2])

    # 9. Fee Structure & Student Fee Record
    fee_struct = FeeStructure.query.filter_by(course_id=course_btech_cse.id, semester_id=semesters[4].id).first()
    today = date.today()
    if not fee_struct:
        fee_struct = FeeStructure(
            title='Academic Year 2025-26 - B.Tech Semester 4 Fee',
            course_id=course_btech_cse.id,
            semester_id=semesters[4].id,
            session_id=session_2025_26.id,
            tuition_fee=45000.0,
            library_fee=2000.0,
            lab_fee=5000.0,
            exam_fee=3500.0,
            other_fee=9500.0,
            total_amount=65000.0,
            due_date=today + timedelta(days=30),
            is_active=True
        )
        db.session.add(fee_struct)
        db.session.flush()

    if student_aarav and fee_struct:
        std_fee = StudentFee.query.filter_by(student_id=student_aarav.id, fee_structure_id=fee_struct.id).first()
        if not std_fee:
            std_fee = StudentFee(
                student_id=student_aarav.id,
                fee_structure_id=fee_struct.id,
                total_amount=65000.0,
                discount_amount=5000.0,
                net_payable=60000.0,
                paid_amount=40000.0,
                pending_amount=20000.0,
                status='Partial',
                due_date=today + timedelta(days=30)
            )
            db.session.add(std_fee)
            db.session.flush()

            payment = FeePayment(
                student_fee_id=std_fee.id,
                student_id=student_aarav.id,
                receipt_number=generate_receipt_number(),
                amount=40000.0,
                payment_mode='Online',
                transaction_id=generate_transaction_id(),
                payment_date=datetime.utcnow() - timedelta(days=15),
                status='Success',
                notes='Semester 4 partial tuition & lab fee payment'
            )
            db.session.add(payment)

    # 10. Notices
    if Notice.query.count() == 0:
        n1 = Notice(
            title='Campus Placement Drive 2026: Apex Tech & Global Solutions',
            content='We are pleased to announce the upcoming on-campus recruitment drive for final and pre-final year engineering students starting March 10th. Register via the portal.',
            target_audience='ALL',
            department_id=dept_cse.id,
            published_by_id=user_admin.id,
            priority='High',
            is_active=True
        )
        n2 = Notice(
            title='Schedule for Mid-Term Lab Practical Assessments & Project Demos',
            content='All 4th and 6th semester students must submit their laboratory record notebooks and code repositories by Friday.',
            target_audience='STUDENT',
            department_id=dept_cse.id,
            published_by_id=user_hod.id,
            priority='Normal',
            is_active=True
        )
        n3 = Notice(
            title='Annual National Hackathon "InnovateX 2026" Registrations Open',
            content='Form teams of 3-4 members and participate in the 36-hour hackathon with cash prizes up to INR 1,50,000.',
            target_audience='ALL',
            published_by_id=user_admin.id,
            priority='Urgent',
            is_active=True
        )
        db.session.add_all([n1, n2, n3])

    # 11. Assignments
    if Assignment.query.count() == 0 and sub_dbms:
        f_priya = Faculty.query.filter_by(official_email='priya.nair@apex.edu').first() or Faculty.query.first()
        f_hod = Faculty.query.filter_by(official_email='arthur.sterling@apex.edu').first() or f_priya
        asg1 = Assignment(
            title='Lab Exercise 3: SQL Triggers and Stored Procedures',
            description='Implement relational database triggers and complex stored procedures for banking transaction consistency.',
            subject_id=sub_dbms.id,
            faculty_id=f_priya.id if f_priya else 1,
            class_division_id=div_cse_4a.id,
            due_date=datetime.utcnow() + timedelta(days=7),
            max_marks=20
        )
        asg2 = Assignment(
            title='Assignment 2: CPU Scheduling Algorithms Simulation',
            description='Implement FCFS, Round Robin, and Shortest Job First scheduling simulation in C/Python.',
            subject_id=sub_os.id if sub_os else sub_dbms.id,
            faculty_id=f_hod.id if f_hod else 1,
            class_division_id=div_cse_4a.id,
            due_date=datetime.utcnow() + timedelta(days=10),
            max_marks=25
        )
        db.session.add_all([asg1, asg2])

    # 12. Study Materials
    if StudyMaterial.query.count() == 0 and sub_dbms:
        f_priya = Faculty.query.filter_by(official_email='priya.nair@apex.edu').first() or Faculty.query.first()
        f_hod = Faculty.query.filter_by(official_email='arthur.sterling@apex.edu').first() or f_priya
        mat1 = StudyMaterial(
            title='Unit 2: Relational Algebra and Normalization Notes',
            description='Complete unit lecture notes covering 1NF, 2NF, 3NF, BCNF with step-by-step solved examples.',
            subject_id=sub_dbms.id,
            faculty_id=f_priya.id if f_priya else 1,
            file_type='PDF',
            file_path='materials/dbms_unit2_notes.pdf',
            file_size_kb=3450.0
        )
        mat2 = StudyMaterial(
            title='Unit 3: Operating Systems Memory Management Slides',
            description='Virtual memory, paging, segmentation, and page replacement algorithm presentation slides.',
            subject_id=sub_os.id if sub_os else sub_dbms.id,
            faculty_id=f_hod.id if f_hod else 1,
            file_type='PPT',
            file_path='materials/os_memory_management.pptx',
            file_size_kb=5200.0
        )
        db.session.add_all([mat1, mat2])

    # 13. Exams and Exam Results
    if Exam.query.count() == 0 and sub_dbms:
        ex1 = Exam(
            name='Mid-Semester Examination - DBMS',
            subject_id=sub_dbms.id,
            semester_id=semesters[4].id,
            session_id=session_2025_26.id,
            exam_type='Midterm',
            exam_date=date.today() - timedelta(days=20),
            start_time=time(10, 0),
            end_time=time(12, 0),
            max_marks=50,
            passing_marks=20
        )
        ex2 = Exam(
            name='End-Semester Theory Examination - OS',
            subject_id=sub_os.id if sub_os else sub_dbms.id,
            semester_id=semesters[4].id,
            session_id=session_2025_26.id,
            exam_type='End Semester',
            exam_date=date.today() + timedelta(days=25),
            start_time=time(10, 0),
            end_time=time(13, 0),
            max_marks=100,
            passing_marks=40
        )
        db.session.add_all([ex1, ex2])
        db.session.flush()

        if student_aarav:
            res1 = ExamResult(
                exam_id=ex1.id,
                student_id=student_aarav.id,
                subject_id=sub_dbms.id,
                marks_obtained=44.0,
                max_marks=50.0,
                percentage=88.0,
                grade='A',
                grade_point=9.0,
                is_passed=True,
                is_published=True,
                status='Published_By_Admin',
                published_at=datetime.utcnow()
            )
            db.session.add(res1)

    # 14. Events
    if Event.query.count() == 0 and user_admin:
        ev1 = Event(
            title='InnovateX National Student Hackathon 2026',
            description='36-hour hackathon for building AI, Cloud, and Web3 applications with industry mentors and cash prizes.',
            event_type='Hackathon',
            start_datetime=datetime.utcnow() + timedelta(days=14),
            end_datetime=datetime.utcnow() + timedelta(days=16),
            venue='Main Campus Auditorium & Innovation Labs',
            registration_deadline=datetime.utcnow() + timedelta(days=10),
            created_by_id=user_admin.id,
            is_open_for_registration=True
        )
        db.session.add(ev1)

    db.session.commit()
    logger.info("seed_database_safely completed successfully.")

    return {
        "success": True,
        "status": "seeded",
        "message": "Institutional seed data verified and populated without modifying existing production data.",
        "counts": {
            "departments": Department.query.count(),
            "courses": Course.query.count(),
            "semesters": Semester.query.count(),
            "users": User.query.count(),
            "faculty": Faculty.query.count(),
            "students": Student.query.count(),
            "subjects": Subject.query.count(),
            "notices": Notice.query.count()
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
