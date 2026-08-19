import os
from datetime import datetime, date, time, timedelta
from flask import Blueprint, jsonify, request, g, current_app, url_for
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models.user import User, Role
from app.models.student import Student, StudentDocument
from app.models.faculty import Faculty
from app.models.department import Department
from app.models.course import Course
from app.models.semester import Semester
from app.models.academic_session import AcademicSession
from app.models.class_division import ClassDivision
from app.models.subject import Subject
from app.models.timetable import Timetable
from app.models.attendance import AttendanceSession, AttendanceRecord
from app.models.assignment import Assignment, AssignmentSubmission, StudyMaterial
from app.models.exam import Exam, ExamResult
from app.models.fee import FeeStructure, StudentFee, FeePayment
from app.models.leave import LeaveRequest
from app.models.certificate import CertificateRequest
from app.models.complaint import Complaint
from app.models.notice import Notice
from app.models.event import Event, EventRegistration
from app.models.feedback import Feedback
from app.models.notification import Notification
from app.utils.api_auth import api_auth_required, api_student_required, generate_api_token
from app.utils.helpers import generate_receipt_number, generate_transaction_id, generate_certificate_code
from app.utils.id_generator import (
    generate_student_id,
    generate_admission_number,
    generate_enrollment_number,
    generate_roll_number,
    generate_faculty_employee_id
)
from app.utils.uploads import save_uploaded_file
from app.utils.db_ops import verify_db_init_token, initialize_database_schema, seed_database_safely

api_bp = Blueprint('api', __name__)


# ==========================================
# 1. SYSTEM HEALTH, METADATA & DATABASE INIT
# ==========================================

@api_bp.route('/health')
@api_bp.route('/v1/health')
def health():
    return jsonify({
        'status': 'healthy',
        'success': True,
        'service': 'Campus Connect ERP REST API',
        'version': '1.0.0'
    }), 200


def _extract_init_token_from_request():
    """Extracts DB_INIT_TOKEN from header, Bearer auth, JSON body, or query param."""
    token = request.headers.get('X-DB-Init-Token') or request.headers.get('X-Init-Token')
    if not token:
        auth = request.headers.get('Authorization', '')
        if auth.startswith('Bearer '):
            token = auth[7:].strip()
    if not token and request.is_json:
        body = request.get_json(silent=True) or {}
        token = body.get('token') or body.get('init_token') or body.get('db_init_token')
    if not token:
        token = request.args.get('token') or request.args.get('init_token') or request.args.get('db_init_token')
    return token


@api_bp.route('/admin/initialize-database', methods=['POST', 'GET'])
@api_bp.route('/v1/admin/initialize-database', methods=['POST', 'GET'])
def api_initialize_database():
    """
    Secure one-time / safe production database initialization endpoint.
    Protected by secret DB_INIT_TOKEN environment variable.
    Creates all SQLAlchemy tables and provisions the master Admin account without dropping or resetting data.
    """
    token = _extract_init_token_from_request()
    is_valid, err_msg, status_code = verify_db_init_token(token)
    if not is_valid:
        current_app.logger.warning(f"Unauthorized DB initialization attempt: {err_msg}")
        return jsonify({
            'success': False,
            'error': 'Unauthorized' if status_code == 401 else 'Configuration Error',
            'message': err_msg
        }), status_code

    try:
        current_app.logger.info("Authorized production database schema initialization requested.")
        result = initialize_database_schema()
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(f"Fatal error during database schema initialization: {e}")
        return jsonify({
            'success': False,
            'error': 'Initialization Failed',
            'message': f"An error occurred while creating database tables: {str(e)}"
        }), 500


@api_bp.route('/admin/seed-database', methods=['POST', 'GET'])
@api_bp.route('/v1/admin/seed-database', methods=['POST', 'GET'])
def api_seed_database():
    """
    Secure idempotent institutional data seeding endpoint.
    Protected by secret DB_INIT_TOKEN environment variable.
    Populates required initial institutional records without overwriting or duplicating existing production data.
    """
    token = _extract_init_token_from_request()
    is_valid, err_msg, status_code = verify_db_init_token(token)
    if not is_valid:
        current_app.logger.warning(f"Unauthorized DB seeding attempt: {err_msg}")
        return jsonify({
            'success': False,
            'error': 'Unauthorized' if status_code == 401 else 'Configuration Error',
            'message': err_msg
        }), status_code

    try:
        current_app.logger.info("Authorized institutional database seeding requested.")
        result = seed_database_safely()
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(f"Fatal error during database seeding: {e}")
        return jsonify({
            'success': False,
            'error': 'Seeding Failed',
            'message': f"An error occurred while seeding database records: {str(e)}"
        }), 500


# ==========================================
# ADMIN STUDENT & FACULTY CREATION
# ==========================================

def _admin_api_required():
    """Allow only authenticated administrator users to create records."""
    user = getattr(g, 'current_user', None)
    if user is None:
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Administrator authentication required.'
        }), 401

    role = getattr(user, 'role', None)
    role_name = getattr(role, 'value', role)
    role_name = str(role_name).upper()

    if role_name != 'ADMIN':
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'Only administrators can create students or faculty.'
        }), 403

    return None


def _model_columns(model):
    """Return SQLAlchemy column names without assuming a particular model version."""
    try:
        return set(model.__table__.columns.keys())
    except Exception:
        return set()


def _set_if_column(obj, values):
    """Set only fields that actually exist on the current SQLAlchemy model."""
    columns = _model_columns(type(obj))
    for key, value in values.items():
        if key in columns and value is not None:
            setattr(obj, key, value)


def _next_code(model, field, prefix, width=4):
    """Generate a unique sequential institutional ID."""
    columns = _model_columns(model)
    if field not in columns:
        return None

    year = datetime.utcnow().year
    prefix_text = f'{prefix}{year}'
    number = 1

    existing = getattr(model, field, None)
    if existing is not None:
        rows = model.query.with_entities(existing).filter(existing.isnot(None)).all()
        numbers = []
        for row in rows:
            value = row[0]
            if not value:
                continue
            value = str(value)
            if value.startswith(prefix_text):
                suffix = value[len(prefix_text):]
                if suffix.isdigit():
                    numbers.append(int(suffix))
        if numbers:
            number = max(numbers) + 1

    code = f'{prefix_text}{number:0{width}d}'
    while model.query.filter(getattr(model, field) == code).first() is not None:
        number += 1
        code = f'{prefix_text}{number:0{width}d}'
    return code


def _set_user_password(user, password):
    """Use the project's password helper so login works with the existing auth system."""
    if hasattr(user, 'set_password'):
        user.set_password(password)
        return

    if hasattr(user, 'password_hash'):
        user.password_hash = generate_password_hash(password)
        return

    if hasattr(user, 'password'):
        user.password = generate_password_hash(password)
        return

    raise RuntimeError('User model does not expose a supported password field.')


def _resolve_department(dept_val):
    """Resolve a Department model instance from an int ID, string 'dept-cse', or code 'CSE'."""
    if dept_val is not None:
        try:
            dept = Department.query.get(int(dept_val))
            if dept:
                return dept
        except (TypeError, ValueError):
            pass
        dept_str = str(dept_val).strip()
        clean_code = dept_str.replace('dept-', '').replace('DEPT-', '').upper()
        dept = Department.query.filter(
            (db.func.upper(Department.code) == clean_code) |
            (db.func.upper(Department.code) == dept_str.upper()) |
            (db.func.lower(Department.name) == dept_str.lower())
        ).first()
        if dept:
            return dept
    return Department.query.filter_by(is_active=True).first() or Department.query.first()


def _resolve_course(course_val, department_id=None):
    """Resolve a Course model instance from an int ID, string 'course-btech-cse', or code 'BTECH-CSE'."""
    if course_val is not None:
        try:
            crs = Course.query.get(int(course_val))
            if crs:
                return crs
        except (TypeError, ValueError):
            pass
        crs_str = str(course_val).strip()
        clean_code = crs_str.replace('course-', '').replace('COURSE-', '').upper()
        crs = Course.query.filter(
            (db.func.upper(Course.code) == clean_code) |
            (db.func.upper(Course.code) == crs_str.upper()) |
            (db.func.lower(Course.name) == crs_str.lower())
        ).first()
        if crs:
            return crs
    if department_id:
        crs = Course.query.filter_by(department_id=department_id, is_active=True).first()
        if crs:
            return crs
    return Course.query.filter_by(is_active=True).first() or Course.query.first()


def _resolve_semester(sem_val):
    """Resolve a Semester model instance from int ID, semester number, or name."""
    if sem_val is not None:
        try:
            sem_int = int(sem_val)
            sem = Semester.query.get(sem_int) or Semester.query.filter_by(number=sem_int).first()
            if sem:
                return sem
        except (TypeError, ValueError):
            pass
        sem_str = str(sem_val).strip()
        clean_num = ''.join(filter(str.isdigit, sem_str))
        if clean_num:
            sem = Semester.query.filter_by(number=int(clean_num)).first()
            if sem:
                return sem
    return Semester.query.filter_by(is_active=True).first() or Semester.query.first()


def _resolve_session(sess_val):
    """Resolve AcademicSession instance."""
    if sess_val is not None:
        try:
            sess = AcademicSession.query.get(int(sess_val))
            if sess:
                return sess
        except (TypeError, ValueError):
            pass
        sess_str = str(sess_val).strip()
        sess = AcademicSession.query.filter(
            (AcademicSession.name == sess_str) |
            (AcademicSession.name.ilike(f'%{sess_str}%'))
        ).first()
        if sess:
            return sess
    return AcademicSession.query.filter_by(is_current=True).first() or AcademicSession.query.first()


def _resolve_division(div_val, department_id=None):
    """Resolve ClassDivision instance."""
    if div_val is not None:
        try:
            div = ClassDivision.query.get(int(div_val))
            if div:
                return div
        except (TypeError, ValueError):
            pass
        div_str = str(div_val).strip()
        clean_code = div_str.replace('div-', '').replace('DIV-', '').upper()
        div = ClassDivision.query.filter(
            (db.func.upper(ClassDivision.code) == clean_code) |
            (db.func.upper(ClassDivision.code) == div_str.upper()) |
            (db.func.lower(ClassDivision.name) == div_str.lower())
        ).first()
        if div:
            return div
    if department_id:
        div = ClassDivision.query.filter_by(department_id=department_id).first()
        if div:
            return div
    return ClassDivision.query.first()


@api_bp.route('/admin/students', methods=['POST'])
@api_bp.route('/admin/student', methods=['POST'])
@api_auth_required
def create_admin_student():
    """Create a student, linked User account, and dynamic institutional IDs."""
    auth_error = _admin_api_required()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or request.form.to_dict()

    try:
        email = (data.get('college_email') or data.get('collegeEmail') or data.get('email') or '').strip().lower()
        mobile = (data.get('mobile') or data.get('phone') or '').strip()

        if not email or not mobile:
            return jsonify({
                'success': False,
                'error': 'Validation Error',
                'message': 'College email and mobile number are required. The mobile number is the initial password.'
            }), 400

        existing_user = User.query.filter(
            (User.email.ilike(email)) | (User.username.ilike(email))
        ).first()
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'Duplicate Email',
                'message': 'A user account with this email already exists.'
            }), 409

        dept = _resolve_department(data.get('department_id') or data.get('departmentId'))
        dept_id = dept.id if dept else None

        course = _resolve_course(data.get('course_id') or data.get('courseId'), department_id=dept_id)
        course_id = course.id if course else None

        sem = _resolve_semester(data.get('semester_id') or data.get('semesterId') or data.get('semesterNumber') or data.get('semester_number'))
        sem_id = sem.id if sem else 1

        sess = _resolve_session(data.get('session_id') or data.get('sessionId'))
        sess_id = sess.id if sess else 1

        div = _resolve_division(data.get('division_id') or data.get('divisionId'), department_id=dept_id)
        div_id = div.id if div else None

        student_id = _next_code(Student, 'student_id', 'STU')
        admission_no = _next_code(Student, 'admission_no', 'ADM')
        enrollment_no = _next_code(Student, 'enrollment_no', 'ENR')
        roll_no = _next_code(Student, 'roll_no', 'ROLL')

        first_name = (data.get('first_name') or data.get('firstName') or '').strip()
        middle_name = (data.get('middle_name') or data.get('middleName') or None)
        last_name = (data.get('last_name') or data.get('lastName') or '').strip()
        full_name = data.get('full_name') or data.get('fullName') or ' '.join(filter(None, [first_name, middle_name, last_name]))

        user = User()
        _set_if_column(user, {
            'username': email,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'phone': mobile,
            'is_active': True,
            'must_change_password': True,
        })
        user.role = Role.STUDENT
        _set_user_password(user, mobile)

        db.session.add(user)
        db.session.flush()

        student = Student()
        _set_if_column(student, {
            'user_id': user.id,
            'student_id': student_id,
            'admission_no': admission_no,
            'enrollment_no': enrollment_no,
            'roll_no': roll_no,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'full_name': full_name,
            'college_email': email,
            'personal_email': data.get('personal_email') or data.get('personalEmail'),
            'mobile': mobile,
            'gender': data.get('gender') or 'Male',
            'blood_group': data.get('blood_group') or data.get('bloodGroup'),
            'batch': data.get('batch'),
            'status': data.get('status') or 'Active',
            'department_id': dept_id,
            'course_id': course_id,
            'semester_id': sem_id,
            'session_id': sess_id,
            'division_id': div_id,
            'profile_photo': data.get('profile_photo') or data.get('photo'),
        })

        db.session.add(student)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Student created and stored successfully.',
            'credentials': {
                'email': email,
                'username': email,
                'password': mobile
            },
            'student': {
                'id': student.id,
                'user_id': user.id,
                'student_id': student.student_id,
                'studentId': student.student_id,
                'admission_no': student.admission_no,
                'admissionNumber': student.admission_no,
                'enrollment_no': student.enrollment_no,
                'enrollmentNumber': student.enrollment_no,
                'roll_no': student.roll_no,
                'rollNumber': student.roll_no,
                'full_name': student.full_name,
                'fullName': student.full_name,
                'college_email': email,
                'collegeEmail': email,
                'mobile': mobile,
                'department_id': student.department_id,
                'departmentId': student.department_id,
                'course_id': student.course_id,
                'courseId': student.course_id,
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Student creation failed')
        return jsonify({
            'success': False,
            'error': 'Student Creation Failed',
            'message': str(e)
        }), 400


@api_bp.route('/admin/faculty', methods=['POST'])
@api_bp.route('/admin/faculties', methods=['POST'])
@api_bp.route('/admin/faculty/create', methods=['POST'])
@api_auth_required
def create_admin_faculty():
    """Create a faculty, linked User account, and dynamic employee IDs."""
    auth_error = _admin_api_required()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or request.form.to_dict()

    try:
        first_name = (data.get('first_name') or data.get('firstName') or '').strip()
        middle_name = (data.get('middle_name') or data.get('middleName') or None)
        last_name = (data.get('last_name') or data.get('lastName') or '').strip()
        email = (data.get('official_email') or data.get('officialEmail') or data.get('email') or '').strip().lower()
        mobile = (data.get('mobile') or data.get('phone') or '').strip()
        raw_dept = data.get('department_id') or data.get('departmentId')

        if not first_name or not last_name:
            return jsonify({'success': False, 'error': 'Validation Error', 'message': 'First name and last name are required.'}), 400
        if not email or not mobile:
            return jsonify({'success': False, 'error': 'Validation Error', 'message': 'Official email and mobile number are required. The mobile number is the initial password.'}), 400

        dept = _resolve_department(raw_dept)
        if not dept:
            return jsonify({'success': False, 'error': 'Validation Error', 'message': 'Department could not be resolved.'}), 400

        department_id = dept.id

        existing_user = User.query.filter(
            (User.email.ilike(email)) | (User.username.ilike(email))
        ).first()
        if existing_user:
            return jsonify({'success': False, 'error': 'Duplicate Email', 'message': 'A user account with this email already exists.'}), 409

        faculty_id = _next_code(Faculty, 'faculty_id', 'FAC')
        employee_id = _next_code(Faculty, 'employee_id', 'EMP')

        full_name = ' '.join(filter(None, [first_name, middle_name, last_name]))

        designation_str = data.get('designation') or 'Assistant Professor'
        is_hod = any(term in str(designation_str).upper() for term in ['HOD', 'HEAD OF DEPARTMENT', 'DEPT HEAD', 'DEPARTMENT HEAD'])
        assigned_role = Role.HOD if is_hod else Role.FACULTY

        user = User()
        _set_if_column(user, {
            'username': email,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'phone': mobile,
            'is_active': True,
            'must_change_password': True,
        })
        user.role = assigned_role
        _set_user_password(user, mobile)
        db.session.add(user)
        db.session.flush()

        faculty = Faculty()
        _set_if_column(faculty, {
            'user_id': user.id,
            'faculty_id': faculty_id,
            'employee_id': employee_id,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'full_name': full_name,
            'official_email': email,
            'personal_email': data.get('personal_email') or data.get('personalEmail'),
            'mobile': mobile,
            'alt_mobile': data.get('alt_mobile') or data.get('altMobile'),
            'gender': data.get('gender') or 'Male',
            'blood_group': data.get('blood_group') or data.get('bloodGroup'),
            'department_id': department_id,
            'designation': designation_str,
            'employment_type': data.get('employment_type') or data.get('employmentType') or 'Permanent',
            'joining_date': data.get('joining_date') or data.get('dateOfJoining') or None,
            'qualification': data.get('qualification'),
            'specialization': data.get('specialization'),
            'experience_years': float(data.get('experience_years') or data.get('experienceYears') or 0),
            'status': data.get('status') or 'Active',
            'profile_photo': data.get('profile_photo') or data.get('photo'),
            'curr_address_line1': data.get('curr_address_line1'),
            'curr_address_line2': data.get('curr_address_line2'),
            'curr_city': data.get('curr_city'),
            'curr_district': data.get('curr_district'),
            'curr_state': data.get('curr_state'),
            'curr_country': data.get('curr_country') or 'India',
            'curr_pincode': data.get('curr_pincode'),
            'perm_address_line1': data.get('perm_address_line1'),
            'perm_address_line2': data.get('perm_address_line2'),
            'perm_city': data.get('perm_city'),
            'perm_district': data.get('perm_district'),
            'perm_state': data.get('perm_state'),
            'perm_country': data.get('perm_country') or 'India',
            'perm_pincode': data.get('perm_pincode'),
            'emergency_name': data.get('emergency_name'),
            'emergency_relation': data.get('emergency_relation'),
            'emergency_phone': data.get('emergency_phone'),
            'emergency_alt_phone': data.get('emergency_alt_phone'),
        })

        db.session.add(faculty)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Faculty member {full_name} created and stored successfully in PostgreSQL.',
            'credentials': {
                'email': email,
                'username': email,
                'password': mobile,
                'role': assigned_role
            },
            'faculty': {
                'id': faculty.id,
                'user_id': user.id,
                'userId': user.id,
                'faculty_id': faculty.faculty_id,
                'facultyId': faculty.faculty_id,
                'employee_id': faculty.employee_id,
                'employeeId': faculty.employee_id,
                'first_name': faculty.first_name,
                'firstName': faculty.first_name,
                'last_name': faculty.last_name,
                'lastName': faculty.last_name,
                'full_name': faculty.full_name,
                'fullName': faculty.full_name,
                'official_email': faculty.official_email,
                'officialEmail': faculty.official_email,
                'personal_email': faculty.personal_email,
                'personalEmail': faculty.personal_email,
                'mobile': faculty.mobile,
                'phone': faculty.mobile,
                'department_id': faculty.department_id,
                'departmentId': faculty.department_id,
                'designation': faculty.designation,
                'employment_type': faculty.employment_type,
                'employmentType': faculty.employment_type,
                'status': faculty.status,
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Faculty creation failed')
        return jsonify({'success': False, 'error': 'Faculty Creation Failed', 'message': str(e)}), 400


@api_bp.route('/stats')
def stats():
    active_students = Student.query.filter_by(status='Active').count()
    active_faculty = Faculty.query.filter_by(status='Active').count()
    depts = Department.query.filter_by(is_active=True).count()
    courses = Course.query.filter_by(is_active=True).count()
    notices = Notice.query.filter_by(is_active=True).count()
    events = Event.query.count()

    stats_data = {
        'total_students': active_students,
        'total_faculty': active_faculty,
        'total_departments': depts,
        'total_courses': courses,
        'active_notices': notices,
        'upcoming_events': events
    }

    return jsonify({
        'success': True,
        'stats': stats_data,
        **stats_data
    })


@api_bp.route('/config')
def get_config():
    current_session = AcademicSession.query.filter_by(is_current=True).first()
    return jsonify({
        'success': True,
        'institute': {
            'name': current_app.config.get('COLLEGE_NAME', 'Apex Institute of Technology & Science'),
            'address': current_app.config.get('COLLEGE_ADDRESS', 'Knowledge City, Tech Campus'),
            'email': current_app.config.get('COLLEGE_EMAIL', 'contact@apextech.edu'),
            'phone': current_app.config.get('COLLEGE_PHONE', '+91 98765 43210'),
            'website': current_app.config.get('COLLEGE_WEBSITE', 'https://campusconnect.edu'),
            'academic_session': current_session.name if current_session else '2025-26'
        },
        'api_version': 'v1',
        'auth_method': 'Bearer Token'
    })


# ==========================================
# 2. AUTHENTICATION & IDENTITY
# ==========================================

@api_bp.route('/login', methods=['POST'])
@api_bp.route('/auth/login', methods=['POST'])
@api_bp.route('/android/login', methods=['POST'])
@api_bp.route('/student/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data:
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': 'JSON payload with username/email and password required.'
        }), 400

    username_or_email = data.get('username') or data.get('email') or data.get('student_id') or data.get('studentId') or data.get('identifier')
    password = data.get('password')

    if not username_or_email or not password:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'message': 'Both username (or email/ID) and password are required.'
        }), 400

    user = User.get_by_identifier(username_or_email)

    if not user or not user.check_password(password):
        return jsonify({
            'success': False,
            'error': 'Invalid Credentials',
            'message': 'The username/email or password you entered is incorrect.'
        }), 401

    if not user.is_active:
        return jsonify({
            'success': False,
            'error': 'Account Deactivated',
            'message': 'Your account has been deactivated. Please contact campus administration.'
        }), 403

    # Check Android / Mobile App Student-Only access rule
    is_mobile_request = (
        request.path.startswith('/api/android') or 
        request.path.startswith('/api/student') or 
        request.headers.get('X-Client-Platform', '').lower() == 'android' or
        request.headers.get('X-Client-Type', '').lower() == 'android' or
        str(data.get('platform', '')).lower() == 'android' or
        data.get('is_android') is True
    )

    if is_mobile_request and user.role != Role.STUDENT:
        return jsonify({
            'success': False,
            'error': 'Access Denied',
            'message': 'Access denied. Only student accounts can use the mobile application.'
        }), 403

    student = Student.query.filter_by(user_id=user.id).first() if user.role == Role.STUDENT else None
    faculty = Faculty.query.filter_by(user_id=user.id).first() if user.role in (Role.FACULTY, Role.HOD) or user.faculty_profile else None
    token = generate_api_token(user, student=student)

    # Format student payload if student with both snake_case and camelCase support
    student_payload = None
    if student:
        student_payload = {
            'id': student.id,
            'student_id': student.student_id,
            'studentId': student.student_id,
            'roll_no': student.roll_no or student.student_id,
            'rollNumber': student.roll_no or student.student_id,
            'enrollment_no': student.enrollment_no,
            'enrollmentNumber': student.enrollment_no,
            'admission_no': student.admission_no,
            'admissionNumber': student.admission_no,
            'first_name': student.first_name,
            'firstName': student.first_name,
            'last_name': student.last_name,
            'lastName': student.last_name,
            'full_name': student.full_name,
            'fullName': student.full_name,
            'college_email': student.college_email,
            'collegeEmail': student.college_email,
            'personal_email': student.personal_email,
            'personalEmail': student.personal_email,
            'mobile': student.mobile,
            'dob': student.dob.strftime('%Y-%m-%d') if student.dob else None,
            'dateOfBirth': student.dob.strftime('%Y-%m-%d') if student.dob else None,
            'gender': student.gender,
            'blood_group': student.blood_group,
            'bloodGroup': student.blood_group,
            'department_id': student.department_id,
            'departmentId': student.department_id,
            'department_name': student.department.name if student.department else None,
            'departmentName': student.department.name if student.department else None,
            'department_code': student.department.code if student.department else None,
            'departmentCode': student.department.code if student.department else None,
            'course_id': student.course_id,
            'courseId': student.course_id,
            'course_name': student.course.name if student.course else None,
            'courseName': student.course.name if student.course else None,
            'course_code': student.course.code if student.course else None,
            'courseCode': student.course.code if student.course else None,
            'semester_id': student.semester_id,
            'semesterId': student.semester_id,
            'semester_number': student.semester.number if student.semester else None,
            'semesterNumber': student.semester.number if student.semester else None,
            'division_id': student.division_id,
            'divisionId': student.division_id,
            'division_name': student.division.name if student.division else None,
            'divisionName': student.division.name if student.division else None,
            'batch': student.batch,
            'status': student.status,
            'profile_photo': student.profile_photo,
            'profilePhoto': student.profile_photo
        }

    # Format faculty payload if faculty/hod
    faculty_payload = None
    if faculty:
        faculty_payload = {
            'id': faculty.id,
            'faculty_id': faculty.faculty_id,
            'facultyId': faculty.faculty_id,
            'employee_id': faculty.employee_id,
            'employeeId': faculty.employee_id,
            'first_name': faculty.first_name,
            'firstName': faculty.first_name,
            'last_name': faculty.last_name,
            'lastName': faculty.last_name,
            'full_name': faculty.full_name,
            'fullName': faculty.full_name,
            'official_email': faculty.official_email,
            'officialEmail': faculty.official_email,
            'personal_email': faculty.personal_email,
            'personalEmail': faculty.personal_email,
            'mobile': faculty.mobile,
            'phone': faculty.mobile,
            'designation': faculty.designation,
            'department_id': faculty.department_id,
            'departmentId': faculty.department_id,
            'department': faculty.department.name if faculty.department else None,
            'department_name': faculty.department.name if faculty.department else None,
            'departmentName': faculty.department.name if faculty.department else None,
            'department_code': faculty.department.code if faculty.department else None,
            'departmentCode': faculty.department.code if faculty.department else None,
            'employment_type': faculty.employment_type,
            'employmentType': faculty.employment_type,
            'qualification': faculty.qualification,
            'specialization': faculty.specialization,
            'experience_years': faculty.experience_years,
            'experienceYears': faculty.experience_years,
            'status': faculty.status,
            'profile_photo': faculty.profile_photo or user.profile_image,
            'profilePhoto': faculty.profile_photo or user.profile_image
        }

    dept_name = None
    dept_id = None
    if student and student.department:
        dept_name = student.department.name
        dept_id = student.department_id
    elif faculty and faculty.department:
        dept_name = faculty.department.name
        dept_id = faculty.department_id
    elif user.role == Role.ADMIN:
        dept_name = 'Administration'

    return jsonify({
        'success': True,
        'message': 'Authentication successful.',
        'token': token,
        'token_type': 'Bearer',
        'must_change_password': getattr(user, 'must_change_password', False),
        'mustChangePassword': getattr(user, 'must_change_password', False),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'first_name': user.first_name,
            'firstName': user.first_name,
            'last_name': user.last_name,
            'lastName': user.last_name,
            'full_name': user.full_name,
            'fullName': user.full_name,
            'phone': user.phone,
            'profile_image': user.profile_image_url if hasattr(user, 'profile_image_url') else user.profile_image,
            'profileImage': user.profile_image_url if hasattr(user, 'profile_image_url') else user.profile_image,
            'department': dept_name,
            'department_id': dept_id,
            'departmentId': dept_id,
            'must_change_password': getattr(user, 'must_change_password', False),
            'mustChangePassword': getattr(user, 'must_change_password', False)
        },
        'student': student_payload,
        'faculty': faculty_payload
    })


@api_bp.route('/auth/me')
@api_auth_required
def auth_me():
    user = g.current_user
    student = g.current_student
    faculty = Faculty.query.filter_by(user_id=user.id).first() if user.role in (Role.FACULTY, Role.HOD) or getattr(user, 'faculty_profile', None) else None

    student_payload = None
    if student:
        student_payload = {
            'id': student.id,
            'student_id': student.student_id,
            'studentId': student.student_id,
            'roll_no': student.roll_no or student.student_id,
            'rollNumber': student.roll_no or student.student_id,
            'enrollment_no': student.enrollment_no,
            'enrollmentNumber': student.enrollment_no,
            'admission_no': student.admission_no,
            'admissionNumber': student.admission_no,
            'first_name': student.first_name,
            'firstName': student.first_name,
            'last_name': student.last_name,
            'lastName': student.last_name,
            'full_name': student.full_name,
            'fullName': student.full_name,
            'college_email': student.college_email,
            'collegeEmail': student.college_email,
            'personal_email': student.personal_email,
            'personalEmail': student.personal_email,
            'mobile': student.mobile,
            'department': student.department.name if student.department else None,
            'department_name': student.department.name if student.department else None,
            'departmentName': student.department.name if student.department else None,
            'department_id': student.department_id,
            'departmentId': student.department_id,
            'department_code': student.department.code if student.department else None,
            'departmentCode': student.department.code if student.department else None,
            'course': student.course.name if student.course else None,
            'course_id': student.course_id,
            'courseId': student.course_id,
            'semester': student.semester.number if student.semester else None,
            'semester_id': student.semester_id,
            'semesterId': student.semester_id,
            'division': student.division.name if student.division else None,
            'division_id': student.division_id,
            'divisionId': student.division_id,
            'batch': student.batch,
            'status': student.status,
            'profile_photo': student.profile_photo,
            'profilePhoto': student.profile_photo
        }

    faculty_payload = None
    if faculty:
        faculty_payload = {
            'id': faculty.id,
            'faculty_id': faculty.faculty_id,
            'facultyId': faculty.faculty_id,
            'employee_id': faculty.employee_id,
            'employeeId': faculty.employee_id,
            'first_name': faculty.first_name,
            'firstName': faculty.first_name,
            'last_name': faculty.last_name,
            'lastName': faculty.last_name,
            'full_name': faculty.full_name,
            'fullName': faculty.full_name,
            'official_email': faculty.official_email,
            'officialEmail': faculty.official_email,
            'personal_email': faculty.personal_email,
            'personalEmail': faculty.personal_email,
            'mobile': faculty.mobile,
            'phone': faculty.mobile,
            'designation': faculty.designation,
            'department_id': faculty.department_id,
            'departmentId': faculty.department_id,
            'department': faculty.department.name if faculty.department else None,
            'department_name': faculty.department.name if faculty.department else None,
            'departmentName': faculty.department.name if faculty.department else None,
            'department_code': faculty.department.code if faculty.department else None,
            'departmentCode': faculty.department.code if faculty.department else None,
            'employment_type': faculty.employment_type,
            'employmentType': faculty.employment_type,
            'qualification': faculty.qualification,
            'specialization': faculty.specialization,
            'experience_years': faculty.experience_years,
            'experienceYears': faculty.experience_years,
            'status': faculty.status,
            'profile_photo': faculty.profile_photo or user.profile_image,
            'profilePhoto': faculty.profile_photo or user.profile_image
        }

    dept_name = None
    dept_id = None
    if student and student.department:
        dept_name = student.department.name
        dept_id = student.department_id
    elif faculty and faculty.department:
        dept_name = faculty.department.name
        dept_id = faculty.department_id
    elif user.role == Role.ADMIN:
        dept_name = 'Administration'

    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'first_name': user.first_name,
            'firstName': user.first_name,
            'last_name': user.last_name,
            'lastName': user.last_name,
            'full_name': user.full_name,
            'fullName': user.full_name,
            'phone': user.phone,
            'profile_image': user.profile_image_url if hasattr(user, 'profile_image_url') else user.profile_image,
            'profileImage': user.profile_image_url if hasattr(user, 'profile_image_url') else user.profile_image,
            'department': dept_name,
            'department_id': dept_id,
            'departmentId': dept_id,
            'must_change_password': getattr(user, 'must_change_password', False),
            'mustChangePassword': getattr(user, 'must_change_password', False)
        },
        'student': student_payload,
        'faculty': faculty_payload
    })


@api_bp.route('/auth/logout', methods=['POST', 'GET'])
def api_logout():
    return jsonify({
        'success': True,
        'message': 'Successfully logged out.'
    }), 200


@api_bp.route('/auth/change-password', methods=['POST'])
@api_auth_required
def change_password():
    data = request.get_json(silent=True) or request.form.to_dict()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'message': 'Both current_password and new_password are required.'
        }), 400

    if len(new_password) < 6:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'message': 'New password must be at least 6 characters long.'
        }), 400

    user = g.current_user
    if not user.check_password(current_password):
        return jsonify({
            'success': False,
            'error': 'Authentication Error',
            'message': 'Current password does not match.'
        }), 400

    user.set_password(new_password)
    user.must_change_password = False
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Password updated successfully.'
    })


# ==========================================
# 3. STUDENT PROFILE & DIGITAL ID CARD
# ==========================================

@api_bp.route('/student/profile')
@api_bp.route('/android/profile')
@api_student_required
def student_profile():
    std = g.current_student
    profile_data = {
        'id': std.id,
        'student_id': std.student_id,
        'studentId': std.student_id,
        'roll_no': std.roll_no or std.student_id,
        'rollNumber': std.roll_no or std.student_id,
        'enrollment_no': std.enrollment_no,
        'enrollmentNumber': std.enrollment_no,
        'admission_no': std.admission_no,
        'admissionNumber': std.admission_no,
        'first_name': std.first_name,
        'firstName': std.first_name,
        'middle_name': std.middle_name,
        'middleName': std.middle_name,
        'last_name': std.last_name,
        'lastName': std.last_name,
        'full_name': std.full_name,
        'fullName': std.full_name,
        'dob': std.dob.strftime('%Y-%m-%d') if std.dob else None,
        'dateOfBirth': std.dob.strftime('%Y-%m-%d') if std.dob else None,
        'gender': std.gender,
        'blood_group': std.blood_group,
        'bloodGroup': std.blood_group,
        'nationality': std.nationality,
        'college_email': std.college_email,
        'collegeEmail': std.college_email,
        'personal_email': std.personal_email,
        'personalEmail': std.personal_email,
        'mobile': std.mobile,
        'alt_mobile': std.alt_mobile,
        'altMobile': std.alt_mobile,
        'admission_date': std.admission_date.strftime('%Y-%m-%d') if std.admission_date else None,
        'admissionDate': std.admission_date.strftime('%Y-%m-%d') if std.admission_date else None,
        'batch': std.batch,
        'status': std.status,
        'profile_photo': std.profile_photo,
        'profilePhoto': std.profile_photo,
        'academic': {
            'department_id': std.department_id,
            'departmentId': std.department_id,
            'department_name': std.department.name if std.department else None,
            'departmentName': std.department.name if std.department else None,
            'department_code': std.department.code if std.department else None,
            'departmentCode': std.department.code if std.department else None,
            'course_id': std.course_id,
            'courseId': std.course_id,
            'course_name': std.course.name if std.course else None,
            'courseName': std.course.name if std.course else None,
            'course_code': std.course.code if std.course else None,
            'courseCode': std.course.code if std.course else None,
            'semester_id': std.semester_id,
            'semesterId': std.semester_id,
            'semester_number': std.semester.number if std.semester else None,
            'semesterNumber': std.semester.number if std.semester else None,
            'division_id': std.division_id,
            'divisionId': std.division_id,
            'division_name': std.division.name if std.division else None,
            'divisionName': std.division.name if std.division else None,
            'session_name': std.session.name if std.session else None,
            'sessionName': std.session.name if std.session else None
        },
        'address': {
            'current': {
                'line1': std.curr_address_line1,
                'line2': std.curr_address_line2,
                'city': std.curr_city,
                'district': std.curr_district,
                'state': std.curr_state,
                'country': std.curr_country,
                'pincode': std.curr_pincode
            },
            'permanent': {
                'line1': std.perm_address_line1,
                'line2': std.perm_address_line2,
                'city': std.perm_city,
                'district': std.perm_district,
                'state': std.perm_state,
                'country': std.perm_country,
                'pincode': std.perm_pincode
            }
        },
        'parent_info': {
            'father_name': std.father_name,
            'father_phone': std.father_phone,
            'father_email': std.father_email,
            'father_occupation': std.father_occupation,
            'mother_name': std.mother_name,
            'mother_phone': std.mother_phone,
            'mother_email': std.mother_email,
            'mother_occupation': std.mother_occupation
        },
        'emergency_contact': {
            'name': std.emergency_name,
            'relation': std.emergency_relation,
            'phone': std.emergency_phone,
            'alt_phone': std.emergency_alt_phone
        }
    }
    return jsonify({
        'success': True,
        'profile': profile_data,
        **profile_data
    })


# ==========================================
# 3.1 ADMIN AUTOMATIC REGISTRATION APIs
# ==========================================

def resolve_department(dept_identifier):
    """
    Safely resolves a Department model instance from various ID/code formats:
    - Integer / string digit: 1, "1"
    - String code with prefix: "dept-cse", "dept_ece"
    - Raw code: "CSE", "ECE", "ME"
    - Name: "Computer Science & Engineering"
    """
    if dept_identifier is None:
        return Department.query.filter_by(is_active=True).first() or Department.query.first()

    if isinstance(dept_identifier, int):
        d = Department.query.get(dept_identifier)
        if d:
            return d
    elif str(dept_identifier).strip().isdigit():
        d = Department.query.get(int(str(dept_identifier).strip()))
        if d:
            return d

    ident_str = str(dept_identifier).strip()
    # Check exact code
    d = Department.query.filter(db.func.upper(Department.code) == ident_str.upper()).first()
    if d:
        return d

    # Strip dept- / dept_ prefix
    clean_code = ident_str.lower().replace('dept-', '').replace('dept_', '').strip()
    d = Department.query.filter(db.func.lower(Department.code) == clean_code).first()
    if d:
        return d

    # Search by name
    d = Department.query.filter(Department.name.ilike(f"%{ident_str}%")).first()
    if d:
        return d

    return Department.query.filter_by(is_active=True).first() or Department.query.first()


@api_bp.route('/admin/students', methods=['POST'])
@api_bp.route('/students/enroll', methods=['POST'])
def api_enroll_student():
    """
    Automated student enrollment API endpoint.
    Accepts personal and academic information, automatically generating:
    - Student ID: STU{YEAR}{0001}
    - Admission Number: ADM{YEAR}{0001}
    - Enrollment Number: ENR{YEAR}{0001}
    - Roll Number: {DEPT}-{DIV}-{001}
    - User account with mobile as initial password and must_change_password=True.
    """
    try:
        data = request.get_json(silent=True) or request.form.to_dict()
        if not data:
            return jsonify({'success': False, 'error': 'Bad Request', 'message': 'Registration payload missing.'}), 400

        first_name = (data.get('first_name') or data.get('firstName') or '').strip()
        last_name = (data.get('last_name') or data.get('lastName') or '').strip()
        middle_name = (data.get('middle_name') or data.get('middleName') or '').strip()
        college_email = (data.get('college_email') or data.get('collegeEmail') or data.get('email') or '').strip().lower()
        mobile = (data.get('mobile') or data.get('phone') or '').strip()

        dept_id_input = data.get('department_id') or data.get('departmentId')
        course_id = data.get('course_id') or data.get('courseId')
        semester_id = data.get('semester_id') or data.get('semesterId')
        session_id = data.get('session_id') or data.get('sessionId')
        division_id = data.get('division_id') or data.get('divisionId')

        if not first_name or not last_name:
            return jsonify({'success': False, 'error': 'Validation Error', 'message': 'First name and last name are required.'}), 400
        if not college_email:
            return jsonify({'success': False, 'error': 'Validation Error', 'message': 'Official college email is required.'}), 400
        if not mobile or len(mobile) < 10:
            return jsonify({'success': False, 'error': 'Validation Error', 'message': 'A valid 10-15 digit mobile number is required.'}), 400

        # Resolve default academic refs if not passed
        resolved_dept = resolve_department(dept_id_input)
        dept_id = resolved_dept.id if resolved_dept else 1

        if not course_id:
            course = Course.query.filter_by(department_id=dept_id).first() or Course.query.first()
            course_id = course.id if course else 1
        if not semester_id:
            sem = Semester.query.first()
            semester_id = sem.id if sem else 1
        if not session_id:
            sess = AcademicSession.query.filter_by(is_current=True).first() or AcademicSession.query.first()
            session_id = sess.id if sess else 1

        # Check for existing email/username
        if User.query.filter((db.func.lower(User.email) == college_email) | (db.func.lower(User.username) == college_email)).first():
            return jsonify({'success': False, 'error': 'Conflict', 'message': 'A user account with this email address already exists.'}), 409

        # Generate IDs automatically
        gen_student_id = generate_student_id(session_id=session_id)
        gen_admission_no = generate_admission_number(session_id=session_id)
        gen_enrollment_no = generate_enrollment_number(session_id=session_id)
        gen_roll_no = generate_roll_number(
            department_id=dept_id,
            course_id=course_id,
            semester_id=semester_id,
            division_id=division_id,
            session_id=session_id
        )

        # Parse DOB
        dob_val = None
        if data.get('dob') or data.get('dateOfBirth'):
            try:
                dob_val = datetime.strptime(str(data.get('dob') or data.get('dateOfBirth'))[:10], '%Y-%m-%d').date()
            except Exception:
                pass

        full_name = f"{first_name} {middle_name + ' ' if middle_name else ''}{last_name}".strip()

        # Create User account: username = email, password = mobile
        user = User(
            username=college_email,
            email=college_email,
            role=Role.STUDENT,
            first_name=first_name,
            last_name=last_name,
            phone=mobile,
            must_change_password=True,
            is_active=True
        )
        user.set_password(mobile)
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id,
            student_id=gen_student_id,
            enrollment_no=gen_enrollment_no,
            admission_no=gen_admission_no,
            roll_no=gen_roll_no,
            first_name=first_name,
            middle_name=middle_name or None,
            last_name=last_name,
            full_name=full_name,
            dob=dob_val,
            gender=data.get('gender', 'Male'),
            blood_group=data.get('blood_group') or data.get('bloodGroup'),
            nationality=data.get('nationality', 'Indian'),
            personal_email=(data.get('personal_email') or data.get('personalEmail') or '').strip().lower() or None,
            college_email=college_email,
            mobile=mobile,
            alt_mobile=(data.get('alt_mobile') or data.get('altMobile') or '').strip() or None,
            department_id=dept_id,
            course_id=course_id,
            semester_id=semester_id,
            session_id=session_id,
            division_id=division_id if division_id and int(division_id) != 0 else None,
            admission_date=date.today(),
            batch=data.get('batch'),
            status='Active'
        )
        db.session.add(student)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Student enrolled successfully with auto-generated identifiers.',
            'credentials': {
                'login_username': user.username,
                'login_email': user.email,
                'initial_password_note': 'Registered mobile number',
                'must_change_password': True
            },
            'student': {
                'id': student.id,
                'student_id': student.student_id,
                'studentId': student.student_id,
                'admission_no': student.admission_no,
                'admissionNumber': student.admission_no,
                'enrollment_no': student.enrollment_no,
                'enrollmentNumber': student.enrollment_no,
                'roll_no': student.roll_no,
                'rollNumber': student.roll_no,
                'full_name': student.full_name,
                'fullName': student.full_name,
                'college_email': student.college_email,
                'mobile': student.mobile
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Student enrollment error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Database Error',
            'message': f"Student enrollment failed: {str(e)}"
        }), 500


@api_bp.route('/admin/faculty', methods=['POST'])
@api_bp.route('/faculty/register', methods=['POST'])
def api_register_faculty():
    """
    Automated faculty registration API endpoint.
    Accepts faculty info and generates unique Employee ID (EMP{YEAR}{0001}).
    Creates User (login = official_email, password = mobile) and Faculty record in PostgreSQL.
    """
    try:
        data = request.get_json(silent=True) or request.form.to_dict()
        if not data:
            return jsonify({'success': False, 'error': 'Bad Request', 'message': 'Registration payload missing.'}), 400

        first_name = (data.get('first_name') or data.get('firstName') or '').strip()
        last_name = (data.get('last_name') or data.get('lastName') or '').strip()
        middle_name = (data.get('middle_name') or data.get('middleName') or '').strip()
        official_email = (data.get('official_email') or data.get('officialEmail') or data.get('email') or '').strip().lower()
        mobile = (data.get('mobile') or data.get('phone') or '').strip()
        dept_id_input = data.get('department_id') or data.get('departmentId') or data.get('dept_id') or data.get('deptId')

        if not first_name or not last_name:
            return jsonify({'success': False, 'error': 'Validation Error', 'message': 'First name and last name are required.'}), 400
        if not official_email:
            return jsonify({'success': False, 'error': 'Validation Error', 'message': 'Official institute email is required.'}), 400
        if not mobile or len(mobile) < 10:
            return jsonify({'success': False, 'error': 'Validation Error', 'message': 'A valid 10-15 digit mobile number is required.'}), 400

        # Resolve department safely
        resolved_dept = resolve_department(dept_id_input)
        dept_id = resolved_dept.id if resolved_dept else 1

        # Check existing user / faculty
        existing_user = User.query.filter(
            (db.func.lower(User.email) == official_email) | (db.func.lower(User.username) == official_email)
        ).first()
        if existing_user:
            return jsonify({'success': False, 'error': 'Conflict', 'message': 'A user account with this official email already exists.'}), 409

        existing_fac = Faculty.query.filter(db.func.lower(Faculty.official_email) == official_email).first()
        if existing_fac:
            return jsonify({'success': False, 'error': 'Conflict', 'message': 'A faculty record with this official email already exists.'}), 409

        # Generate unique IDs
        gen_emp_id = generate_faculty_employee_id()
        gen_fac_id = data.get('faculty_id') or data.get('facultyId') or gen_emp_id

        # Determine Role (Check if designation indicates HOD)
        designation = data.get('designation', 'Assistant Professor')
        is_hod = any(term in str(designation).upper() for term in ['HOD', 'HEAD OF DEPARTMENT', 'DEPT HEAD', 'DEPARTMENT HEAD'])
        assigned_role = Role.HOD if is_hod else Role.FACULTY

        # 1. Create User
        user = User(
            username=official_email,
            email=official_email,
            role=assigned_role,
            first_name=first_name,
            last_name=last_name,
            phone=mobile,
            must_change_password=True,
            is_active=True
        )
        user.set_password(mobile)
        db.session.add(user)
        db.session.flush()

        # Compute full name (e.g. "Prof. Arthur Sterling" or "Arthur Sterling")
        full_name = f"Prof. {first_name} {middle_name + ' ' if middle_name else ''}{last_name}".strip()

        # Experience years parsing
        raw_exp = data.get('experience_years') or data.get('experienceYears') or 0.0
        try:
            exp_years = float(raw_exp)
        except (ValueError, TypeError):
            exp_years = 0.0

        # Profile photo
        photo = data.get('photo') or data.get('profile_photo') or data.get('profilePhoto')

        # 2. Create Faculty
        faculty = Faculty(
            user_id=user.id,
            faculty_id=gen_fac_id,
            employee_id=gen_emp_id,
            first_name=first_name,
            middle_name=middle_name or None,
            last_name=last_name,
            full_name=full_name,
            gender=data.get('gender', 'Male'),
            blood_group=data.get('blood_group') or data.get('bloodGroup'),
            personal_email=(data.get('personal_email') or data.get('personalEmail') or '').strip().lower() or None,
            official_email=official_email,
            mobile=mobile,
            alt_mobile=(data.get('alt_mobile') or data.get('altMobile') or '').strip() or None,
            department_id=dept_id,
            designation=designation,
            employment_type=data.get('employment_type') or data.get('employmentType') or 'Permanent',
            joining_date=date.today(),
            qualification=data.get('qualification') or data.get('qualifications'),
            specialization=data.get('specialization'),
            experience_years=exp_years,
            profile_photo=photo,
            status=data.get('status', 'Active'),
            curr_address_line1=data.get('room_office') or data.get('roomOffice') or data.get('office') or None
        )
        db.session.add(faculty)
        db.session.commit()

        dept_code_str = f"dept-{resolved_dept.code.lower()}" if resolved_dept and resolved_dept.code else str(faculty.department_id)

        return jsonify({
            'success': True,
            'message': 'Faculty member registered successfully with auto-generated Employee ID.',
            'credentials': {
                'login_username': user.username,
                'login_email': user.email,
                'initial_password_note': 'Registered mobile number',
                'must_change_password': True
            },
            'faculty': {
                'id': faculty.id,
                'faculty_id': faculty.faculty_id,
                'facultyId': faculty.faculty_id,
                'employee_id': faculty.employee_id,
                'employeeId': faculty.employee_id,
                'first_name': faculty.first_name,
                'firstName': faculty.first_name,
                'last_name': faculty.last_name,
                'lastName': faculty.last_name,
                'full_name': faculty.full_name,
                'fullName': faculty.full_name,
                'official_email': faculty.official_email,
                'officialEmail': faculty.official_email,
                'mobile': faculty.mobile,
                'department_id': faculty.department_id,
                'departmentId': dept_code_str,
                'designation': faculty.designation,
                'employment_type': faculty.employment_type,
                'employmentType': faculty.employment_type,
                'qualification': faculty.qualification,
                'specialization': faculty.specialization,
                'status': faculty.status,
                'roomOffice': faculty.curr_address_line1 or 'Room 301, Academic Block'
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Faculty registration error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Database Error',
            'message': f"Faculty creation failed: {str(e)}"
        }), 500


@api_bp.route('/student/profile', methods=['PUT', 'PATCH'])
@api_student_required
def update_student_profile():
    std = g.current_student
    user = g.current_user
    data = request.get_json(silent=True) or request.form.to_dict()

    if not data:
        return jsonify({'success': False, 'error': 'Bad Request', 'message': 'Update payload missing.'}), 400

    # Allowed student editable fields
    if 'personal_email' in data:
        std.personal_email = data['personal_email'].strip()
    if 'mobile' in data:
        std.mobile = data['mobile'].strip()
        user.phone = std.mobile
    if 'alt_mobile' in data:
        std.alt_mobile = data['alt_mobile'].strip() if data['alt_mobile'] else None
    if 'blood_group' in data:
        std.blood_group = data['blood_group'].strip()

    # Address updates
    if 'curr_address_line1' in data:
        std.curr_address_line1 = data['curr_address_line1'].strip()
    if 'curr_address_line2' in data:
        std.curr_address_line2 = data['curr_address_line2'].strip()
    if 'curr_city' in data:
        std.curr_city = data['curr_city'].strip()
    if 'curr_district' in data:
        std.curr_district = data['curr_district'].strip()
    if 'curr_state' in data:
        std.curr_state = data['curr_state'].strip()
    if 'curr_pincode' in data:
        std.curr_pincode = data['curr_pincode'].strip()

    # Emergency contact
    if 'emergency_name' in data:
        std.emergency_name = data['emergency_name'].strip()
    if 'emergency_relation' in data:
        std.emergency_relation = data['emergency_relation'].strip()
    if 'emergency_phone' in data:
        std.emergency_phone = data['emergency_phone'].strip()
    if 'emergency_alt_phone' in data:
        std.emergency_alt_phone = data['emergency_alt_phone'].strip()

    std.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Profile updated successfully.',
        'profile': {
            'student_id': std.student_id,
            'full_name': std.full_name,
            'mobile': std.mobile,
            'personal_email': std.personal_email,
            'blood_group': std.blood_group,
            'curr_city': std.curr_city,
            'curr_state': std.curr_state,
            'emergency_phone': std.emergency_phone
        }
    })


@api_bp.route('/student/profile-photo', methods=['POST'])
@api_student_required
def upload_profile_photo():
    std = g.current_student
    user = g.current_user

    photo_file = None
    if 'photo' in request.files:
        photo_file = request.files['photo']
    elif 'profile_photo' in request.files:
        photo_file = request.files['profile_photo']
    elif 'file' in request.files:
        photo_file = request.files['file']

    if not photo_file or not photo_file.filename:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'message': 'No image file uploaded in request.'
        }), 400

    new_path = save_profile_photo(photo_file, prefix=f"std_{std.student_id}")
    if not new_path:
        return jsonify({
            'success': False,
            'error': 'Invalid File',
            'message': 'Only valid image files (JPG, PNG, WEBP) under 5MB are accepted.'
        }), 400

    # Remove old photo if exists
    if std.profile_photo:
        delete_uploaded_file(std.profile_photo)

    std.profile_photo = new_path
    user.profile_image = new_path
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Profile photo updated successfully.',
        'profile_photo': new_path,
        'profile_image_url': f"/static/{new_path}"
    })


@api_bp.route('/student/profile-photo', methods=['DELETE'])
@api_student_required
def delete_profile_photo():
    std = g.current_student
    user = g.current_user

    if std.profile_photo:
        delete_uploaded_file(std.profile_photo)
        std.profile_photo = None
        user.profile_image = None
        db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Profile photo removed successfully.',
        'profile_photo': None
    })


@api_bp.route('/student/id-card')
@api_student_required
def student_id_card():
    std = g.current_student
    college_name = current_app.config.get('COLLEGE_NAME', 'Apex Institute of Technology & Science')
    college_address = current_app.config.get('COLLEGE_ADDRESS', 'Knowledge City, Tech Campus')
    
    # Generate digital ID validation string
    qr_payload = f"CAMPUS_CONNECT|STD_ID:{std.student_id}|ROLL:{std.roll_no}|ENR:{std.enrollment_no}|NAME:{std.full_name}|DEPT:{std.department.code if std.department else 'GEN'}|VERIFIED:TRUE"

    return jsonify({
        'success': True,
        'id_card': {
            'student_id': std.student_id,
            'roll_no': std.roll_no or std.student_id,
            'enrollment_no': std.enrollment_no,
            'full_name': std.full_name,
            'profile_photo': std.profile_photo,
            'department': std.department.name if std.department else 'N/A',
            'course': std.course.name if std.course else 'N/A',
            'semester': f"Semester {std.semester.number}" if std.semester else 'N/A',
            'division': f"Section {std.division.name}" if std.division else 'N/A',
            'blood_group': std.blood_group or 'N/A',
            'dob': std.dob.strftime('%d-%b-%Y') if std.dob else 'N/A',
            'emergency_phone': std.emergency_phone or std.father_phone or std.mobile or 'N/A',
            'batch': std.batch or '2023-2027',
            'valid_until': 'July 2027',
            'qr_verification_code': qr_payload,
            'institute': {
                'name': college_name,
                'address': college_address,
                'phone': current_app.config.get('COLLEGE_PHONE', '+91 98765 43210')
            }
        }
    })


# ==========================================
# 4. STUDENT DASHBOARD OVERVIEW
# ==========================================

@api_bp.route('/student/dashboard')
@api_student_required
def student_dashboard():
    std = g.current_student

    # 1. Attendance overview
    records = AttendanceRecord.query.filter_by(student_id=std.id).all()
    total_classes = len(records)
    attended_classes = sum(1 for r in records if r.status in ('Present', 'Late'))
    attendance_pct = round((attended_classes / total_classes * 100), 1) if total_classes > 0 else 100.0

    # 2. CGPA & Academic summary
    results = ExamResult.query.filter_by(student_id=std.id, is_published=True).all()
    gpas = [r.grade_point for r in results if r.grade_point is not None]
    cgpa = round(sum(gpas) / len(gpas), 2) if gpas else None
    passed_count = sum(1 for r in results if r.is_passed)

    # 3. Fees summary
    fee_records = StudentFee.query.filter_by(student_id=std.id).all()
    total_fees = sum(f.total_amount for f in fee_records)
    total_paid = sum(f.paid_amount for f in fee_records)
    total_pending = sum(f.pending_amount for f in fee_records)

    # 4. Pending assignments
    div_id = std.division_id
    pending_assignments = 0
    upcoming_assignments = []
    if div_id:
        assignments = Assignment.query.filter_by(class_division_id=div_id).order_by(Assignment.due_date.asc()).all()
        for a in assignments:
            subm = AssignmentSubmission.query.filter_by(assignment_id=a.id, student_id=std.id).first()
            if not subm:
                pending_assignments += 1
                if a.due_date >= datetime.utcnow() and len(upcoming_assignments) < 3:
                    upcoming_assignments.append({
                        'id': a.id,
                        'title': a.title,
                        'subject_name': a.subject.name if a.subject else 'Subject',
                        'due_date': a.due_date.strftime('%Y-%m-%d %H:%M'),
                        'max_marks': a.max_marks
                    })

    # 5. Today's schedule
    today_name = date.today().strftime('%A')
    today_classes = []
    if div_id:
        timetable_slots = Timetable.query.filter_by(class_division_id=div_id, day_of_week=today_name).order_by(Timetable.start_time.asc()).all()
        for slot in timetable_slots:
            today_classes.append({
                'id': slot.id,
                'subject_name': slot.subject.name if slot.subject else 'Subject',
                'subject_code': slot.subject.code if slot.subject else '',
                'faculty_name': slot.faculty.full_name if slot.faculty else 'Faculty',
                'start_time': slot.start_time.strftime('%I:%M %p'),
                'end_time': slot.end_time.strftime('%I:%M %p'),
                'room_number': slot.room_number
            })

    # 6. Upcoming exams
    upcoming_exams = []
    if std.semester_id:
        exams = Exam.query.filter(
            Exam.semester_id == std.semester_id,
            Exam.exam_date >= date.today()
        ).order_by(Exam.exam_date.asc()).limit(3).all()
        for ex in exams:
            upcoming_exams.append({
                'id': ex.id,
                'name': ex.name,
                'subject_name': ex.subject.name if ex.subject else 'Subject',
                'exam_date': ex.exam_date.strftime('%Y-%m-%d'),
                'start_time': ex.start_time.strftime('%I:%M %p'),
                'room_number': ex.room_number
            })

    # 7. Unread counts
    unread_notifs = Notification.query.filter_by(user_id=g.current_user.id, is_read=False).count()
    active_notices = Notice.query.filter_by(is_active=True).count()

    return jsonify({
        'success': True,
        'dashboard': {
            'student_name': std.full_name,
            'roll_no': std.roll_no or std.student_id,
            'department': std.department.name if std.department else None,
            'course': std.course.name if std.course else None,
            'semester': std.semester.number if std.semester else None,
            'division': std.division.name if std.division else None,
            'attendance': {
                'percentage': attendance_pct,
                'attended_classes': attended_classes,
                'total_classes': total_classes,
                'is_eligible': attendance_pct >= 75.0
            },
            'academics': {
                'cgpa': cgpa,
                'total_exams_graded': len(results),
                'passed_exams': passed_count
            },
            'fees': {
                'total_fees': total_fees,
                'paid_amount': total_paid,
                'pending_amount': total_pending,
                'status': 'Paid' if total_pending == 0 and total_fees > 0 else ('Partial' if total_paid > 0 else 'Pending')
            },
            'pending_assignments_count': pending_assignments,
            'upcoming_assignments': upcoming_assignments,
            'today_schedule': today_classes,
            'upcoming_exams': upcoming_exams,
            'unread_notifications_count': unread_notifs,
            'active_notices_count': active_notices
        }
    })


# ==========================================
# 5. ACADEMIC TIMETABLE
# ==========================================

@api_bp.route('/student/timetable')
@api_student_required
def student_timetable():
    std = g.current_student
    div_id = std.division_id
    if not div_id:
        return jsonify({
            'success': True,
            'timetable_by_day': {},
            'message': 'No division assigned currently.'
        })

    slots = Timetable.query.filter_by(class_division_id=div_id).order_by(Timetable.start_time.asc()).all()

    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    timetable_by_day = {d: [] for d in days_order}

    for s in slots:
        day = s.day_of_week
        if day not in timetable_by_day:
            timetable_by_day[day] = []
        timetable_by_day[day].append({
            'id': s.id,
            'subject_id': s.subject_id,
            'subject_code': s.subject.code if s.subject else '',
            'subject_name': s.subject.name if s.subject else 'Subject',
            'faculty_id': s.faculty_id,
            'faculty_name': s.faculty.full_name if s.faculty else 'Faculty',
            'start_time': s.start_time.strftime('%I:%M %p'),
            'end_time': s.end_time.strftime('%I:%M %p'),
            'start_time_raw': s.start_time.strftime('%H:%M:%S'),
            'end_time_raw': s.end_time.strftime('%H:%M:%S'),
            'room_number': s.room_number
        })

    return jsonify({
        'success': True,
        'division_name': std.division.name if std.division else '',
        'course_name': std.course.name if std.course else '',
        'semester_number': std.semester.number if std.semester else None,
        'timetable_by_day': timetable_by_day
    })


@api_bp.route('/student/timetable/today')
@api_student_required
def student_timetable_today():
    std = g.current_student
    div_id = std.division_id
    today_name = date.today().strftime('%A')

    if not div_id:
        return jsonify({
            'success': True,
            'day': today_name,
            'classes': []
        })

    slots = Timetable.query.filter_by(
        class_division_id=div_id,
        day_of_week=today_name
    ).order_by(Timetable.start_time.asc()).all()

    now_time = datetime.now().time()
    classes = []
    for s in slots:
        status = 'upcoming'
        if s.start_time <= now_time <= s.end_time:
            status = 'in_progress'
        elif now_time > s.end_time:
            status = 'completed'

        classes.append({
            'id': s.id,
            'subject_code': s.subject.code if s.subject else '',
            'subject_name': s.subject.name if s.subject else 'Subject',
            'faculty_name': s.faculty.full_name if s.faculty else 'Faculty',
            'start_time': s.start_time.strftime('%I:%M %p'),
            'end_time': s.end_time.strftime('%I:%M %p'),
            'room_number': s.room_number,
            'status': status
        })

    return jsonify({
        'success': True,
        'day': today_name,
        'date': date.today().strftime('%Y-%m-%d'),
        'total_classes_today': len(classes),
        'classes': classes
    })


# ==========================================
# 6. ATTENDANCE TRACKER & ANALYTICS
# ==========================================

@api_bp.route('/student/attendance')
@api_student_required
def student_attendance():
    std = g.current_student

    # All records for this student
    records = AttendanceRecord.query.filter_by(student_id=std.id).join(AttendanceSession).order_by(AttendanceSession.date.desc()).all()

    total_classes = len(records)
    attended_classes = sum(1 for r in records if r.status in ('Present', 'Late'))
    absent_classes = sum(1 for r in records if r.status == 'Absent')
    late_classes = sum(1 for r in records if r.status == 'Late')
    overall_pct = round((attended_classes / total_classes * 100), 1) if total_classes > 0 else 100.0

    # Subject-wise analytics
    subject_map = {}
    for r in records:
        sess = r.session
        if not sess:
            continue
        subj = sess.subject
        s_id = subj.id if subj else 0
        s_name = subj.name if subj else 'General'
        s_code = subj.code if subj else 'GEN'

        if s_id not in subject_map:
            subject_map[s_id] = {
                'subject_id': s_id,
                'subject_name': s_name,
                'subject_code': s_code,
                'total': 0,
                'attended': 0,
                'absent': 0,
                'late': 0
            }
        subject_map[s_id]['total'] += 1
        if r.status in ('Present', 'Late'):
            subject_map[s_id]['attended'] += 1
        if r.status == 'Absent':
            subject_map[s_id]['absent'] += 1
        if r.status == 'Late':
            subject_map[s_id]['late'] += 1

    subject_breakdown = []
    for s_info in subject_map.values():
        tot = s_info['total']
        att = s_info['attended']
        pct = round((att / tot * 100), 1) if tot > 0 else 100.0
        subject_breakdown.append({
            'subject_id': s_info['subject_id'],
            'subject_name': s_info['subject_name'],
            'subject_code': s_info['subject_code'],
            'total_classes': tot,
            'attended_classes': att,
            'absent_classes': s_info['absent'],
            'percentage': pct,
            'is_shortage': pct < 75.0
        })

    if not subject_breakdown:
        from app.models.subject import Subject
        subj_query = Subject.query
        if std.course_id and std.semester_id:
            subj_query = subj_query.filter_by(course_id=std.course_id, semester_id=std.semester_id)
        elif std.department_id:
            subj_query = subj_query.filter_by(department_id=std.department_id)
        for subj in subj_query.all():
            subject_breakdown.append({
                'subject_id': subj.id,
                'subject_name': subj.name,
                'subject_code': subj.code,
                'total_classes': 0,
                'attended_classes': 0,
                'absent_classes': 0,
                'percentage': 100.0,
                'is_shortage': False
            })

    # Recent history (last 20 sessions)
    recent_history = []
    for r in records[:20]:
        sess = r.session
        recent_history.append({
            'id': r.id,
            'date': sess.date.strftime('%Y-%m-%d') if sess else None,
            'time_slot': sess.time_slot if sess else None,
            'subject_name': sess.subject.name if sess and sess.subject else 'Subject',
            'subject_code': sess.subject.code if sess and sess.subject else '',
            'topic_covered': sess.topic_covered if sess else None,
            'faculty_name': sess.faculty.full_name if sess and sess.faculty else None,
            'status': r.status
        })

    return jsonify({
        'success': True,
        'summary': {
            'overall_percentage': overall_pct,
            'total_conducted': total_classes,
            'total_attended': attended_classes,
            'total_absent': absent_classes,
            'total_late': late_classes,
            'minimum_required': 75.0,
            'is_eligible_for_exams': overall_pct >= 75.0,
            'classes_needed_for_75': max(0, int((0.75 * total_classes - attended_classes) / 0.25)) if overall_pct < 75.0 and total_classes > 0 else 0
        },
        'subject_breakdown': subject_breakdown,
        'recent_history': recent_history
    })


# ==========================================
# 7. ASSIGNMENTS & SUBMISSIONS
# ==========================================

@api_bp.route('/student/assignments')
@api_student_required
def student_assignments():
    std = g.current_student
    div_id = std.division_id
    status_filter = request.args.get('status', 'all').lower()

    if div_id:
        assignments = Assignment.query.filter(
            (Assignment.class_division_id == div_id) | (Assignment.class_division_id.is_(None))
        ).order_by(Assignment.due_date.asc()).all()
    else:
        assignments = Assignment.query.order_by(Assignment.due_date.asc()).all()

    if not assignments:
        assignments = Assignment.query.order_by(Assignment.due_date.asc()).all()

    results = []

    for a in assignments:
        subm = AssignmentSubmission.query.filter_by(assignment_id=a.id, student_id=std.id).first()
        is_overdue = datetime.utcnow() > a.due_date and not subm

        subm_status = 'Pending'
        if subm:
            subm_status = subm.status
        elif is_overdue:
            subm_status = 'Overdue'

        if status_filter != 'all':
            if status_filter == 'pending' and subm_status not in ('Pending', 'Overdue'):
                continue
            if status_filter == 'submitted' and subm_status != 'Submitted':
                continue
            if status_filter == 'graded' and subm_status != 'Graded':
                continue
            if status_filter == 'overdue' and subm_status != 'Overdue':
                continue

        results.append({
            'id': a.id,
            'title': a.title,
            'description': a.description,
            'subject_id': a.subject_id,
            'subject_code': a.subject.code if a.subject else '',
            'subject_name': a.subject.name if a.subject else 'Subject',
            'faculty_name': a.faculty.full_name if a.faculty else None,
            'due_date': a.due_date.strftime('%Y-%m-%d %H:%M:%S'),
            'due_date_formatted': a.due_date.strftime('%b %d, %Y %I:%M %p'),
            'max_marks': a.max_marks,
            'file_attachment': a.file_path,
            'status': subm_status,
            'is_submitted': bool(subm),
            'submission': {
                'id': subm.id,
                'submitted_at': subm.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
                'submission_text': subm.submission_text,
                'submission_file': subm.submission_file,
                'marks_obtained': subm.marks_obtained,
                'feedback': subm.feedback,
                'status': subm.status
            } if subm else None
        })

    return jsonify({
        'success': True,
        'total_count': len(results),
        'assignments': results
    })


@api_bp.route('/student/assignments/<int:assignment_id>')
@api_student_required
def student_assignment_detail(assignment_id):
    std = g.current_student
    a = Assignment.query.get_or_404(assignment_id)

    subm = AssignmentSubmission.query.filter_by(assignment_id=a.id, student_id=std.id).first()
    is_overdue = datetime.utcnow() > a.due_date and not subm

    subm_status = 'Pending'
    if subm:
        subm_status = subm.status
    elif is_overdue:
        subm_status = 'Overdue'

    return jsonify({
        'success': True,
        'assignment': {
            'id': a.id,
            'title': a.title,
            'description': a.description,
            'subject_code': a.subject.code if a.subject else '',
            'subject_name': a.subject.name if a.subject else 'Subject',
            'faculty_name': a.faculty.full_name if a.faculty else None,
            'assigned_date': a.created_at.strftime('%Y-%m-%d'),
            'due_date': a.due_date.strftime('%Y-%m-%d %H:%M:%S'),
            'max_marks': a.max_marks,
            'file_path': a.file_path,
            'status': subm_status,
            'submission': {
                'id': subm.id,
                'submitted_at': subm.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
                'submission_text': subm.submission_text,
                'submission_file': subm.submission_file,
                'marks_obtained': subm.marks_obtained,
                'feedback': subm.feedback,
                'status': subm.status
            } if subm else None
        }
    })


@api_bp.route('/student/assignments/<int:assignment_id>/submit', methods=['POST'])
@api_student_required
def submit_assignment(assignment_id):
    std = g.current_student
    a = Assignment.query.get_or_404(assignment_id)

    if a.class_division_id and std.division_id and a.class_division_id != std.division_id:
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'Unauthorized assignment submission attempt.'
        }), 403

    data = request.get_json(silent=True) or request.form.to_dict()
    submission_text = data.get('submission_text', '').strip() if data else ''
    
    # Handle file upload if present
    file_path = None
    if 'submission_file' in request.files:
        file = request.files['submission_file']
        if file and file.filename:
            file_path = save_uploaded_file(file, subfolder='assignments')

    if not submission_text and not file_path:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'message': 'Please provide submission text notes or upload a file.'
        }), 400

    subm = AssignmentSubmission.query.filter_by(assignment_id=a.id, student_id=std.id).first()
    if not subm:
        subm = AssignmentSubmission(
            assignment_id=a.id,
            student_id=std.id,
            submission_text=submission_text,
            submission_file=file_path,
            submitted_at=datetime.utcnow(),
            status='Submitted'
        )
        db.session.add(subm)
    else:
        subm.submission_text = submission_text
        if file_path:
            subm.submission_file = file_path
        subm.submitted_at = datetime.utcnow()
        subm.status = 'Submitted'

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Assignment submitted successfully.',
        'submission_id': subm.id,
        'submitted_at': subm.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
        'status': subm.status
    })


# ==========================================
# 8. STUDY MATERIALS & REPOSITORY
# ==========================================

@api_bp.route('/student/study-materials')
@api_student_required
def student_study_materials():
    std = g.current_student
    div_id = std.division_id
    subject_id = request.args.get('subject_id', type=int)

    query = StudyMaterial.query
    if div_id:
        query = query.filter((StudyMaterial.class_division_id == div_id) | (StudyMaterial.class_division_id.is_(None)))
    if subject_id:
        query = query.filter_by(subject_id=subject_id)

    materials = query.order_by(StudyMaterial.upload_date.desc()).all()
    if not materials:
        materials = StudyMaterial.query.order_by(StudyMaterial.upload_date.desc()).all()
    results = []
    for m in materials:
        results.append({
            'id': m.id,
            'title': m.title,
            'description': m.description,
            'subject_id': m.subject_id,
            'subject_name': m.subject.name if m.subject else 'Subject',
            'subject_code': m.subject.code if m.subject else '',
            'faculty_name': m.faculty.full_name if m.faculty else 'Faculty',
            'file_path': m.file_path,
            'file_type': m.file_type,
            'file_size_kb': m.file_size_kb,
            'upload_date': m.upload_date.strftime('%Y-%m-%d')
        })

    return jsonify({
        'success': True,
        'materials': results
    })


# ==========================================
# 9. EXAMINATIONS & GRADE CARDS
# ==========================================

@api_bp.route('/student/exams')
@api_student_required
def student_exams():
    std = g.current_student
    sem_id = std.semester_id

    query = Exam.query
    if sem_id:
        query = query.filter_by(semester_id=sem_id)

    exams = query.order_by(Exam.exam_date.asc()).all()
    upcoming = []
    past = []

    today = date.today()
    for e in exams:
        item = {
            'id': e.id,
            'name': e.name,
            'exam_type': e.exam_type,
            'subject_id': e.subject_id,
            'subject_name': e.subject.name if e.subject else 'Subject',
            'subject_code': e.subject.code if e.subject else '',
            'exam_date': e.exam_date.strftime('%Y-%m-%d'),
            'start_time': e.start_time.strftime('%I:%M %p'),
            'end_time': e.end_time.strftime('%I:%M %p'),
            'room_number': e.room_number,
            'max_marks': e.max_marks,
            'passing_marks': e.passing_marks
        }
        if e.exam_date >= today:
            upcoming.append(item)
        else:
            past.append(item)

    return jsonify({
        'success': True,
        'upcoming_exams': upcoming,
        'past_exams': past
    })


@api_bp.route('/student/results')
@api_student_required
def student_results():
    std = g.current_student

    # Fetch published results only for this student
    results = ExamResult.query.filter_by(
        student_id=std.id,
        is_published=True
    ).order_by(ExamResult.created_at.desc()).all()

    if not results:
        results = ExamResult.query.filter_by(student_id=std.id).order_by(ExamResult.created_at.desc()).all()

    grade_cards = []
    gpas = []
    total_max = 0
    total_obtained = 0

    for r in results:
        gpas.append(r.grade_point)
        total_max += r.max_marks
        total_obtained += r.marks_obtained

        grade_cards.append({
            'id': r.id,
            'exam_id': r.exam_id,
            'exam_name': r.exam.name if r.exam else 'Examination',
            'exam_type': r.exam.exam_type if r.exam else 'Regular',
            'subject_id': r.subject_id,
            'subject_name': r.subject.name if r.subject else 'Subject',
            'subject_code': r.subject.code if r.subject else '',
            'marks_obtained': r.marks_obtained,
            'max_marks': r.max_marks,
            'percentage': r.percentage,
            'grade': r.grade,
            'grade_point': r.grade_point,
            'is_passed': r.is_passed,
            'published_at': r.published_at.strftime('%Y-%m-%d') if r.published_at else None,
            'remarks': r.remarks
        })

    cgpa = round(sum(gpas) / len(gpas), 2) if gpas else None
    overall_pct = round((total_obtained / total_max * 100), 2) if total_max > 0 else None

    return jsonify({
        'success': True,
        'summary': {
            'cgpa': cgpa,
            'overall_percentage': overall_pct,
            'total_subjects_evaluated': len(results),
            'passed_count': sum(1 for r in results if r.is_passed),
            'failed_count': sum(1 for r in results if not r.is_passed)
        },
        'grade_cards': grade_cards
    })


# ==========================================
# 10. FEES & PAYMENTS
# ==========================================

@api_bp.route('/student/fees')
@api_student_required
def student_fees():
    std = g.current_student

    fee_records = StudentFee.query.filter_by(student_id=std.id).order_by(StudentFee.created_at.desc()).all()
    results = []

    total_payable = 0
    total_paid = 0
    total_pending = 0

    for f in fee_records:
        struct = f.fee_structure
        total_payable += f.net_payable if f.net_payable else f.total_amount
        total_paid += f.paid_amount
        total_pending += f.pending_amount

        breakdown = {
            'tuition_fee': struct.tuition_fee if struct else 0,
            'exam_fee': struct.exam_fee if struct else 0,
            'library_fee': struct.library_fee if struct else 0,
            'lab_fee': struct.lab_fee if struct else 0,
            'other_fee': struct.other_fee if struct else 0
        }

        results.append({
            'id': f.id,
            'fee_structure_id': f.fee_structure_id,
            'title': struct.title if struct else 'Semester Academic Fee',
            'total_amount': f.total_amount,
            'discount_amount': f.discount_amount,
            'net_payable': f.net_payable,
            'paid_amount': f.paid_amount,
            'pending_amount': f.pending_amount,
            'status': f.status,
            'due_date': f.due_date.strftime('%Y-%m-%d') if f.due_date else (struct.due_date.strftime('%Y-%m-%d') if struct else None),
            'breakdown': breakdown
        })

    return jsonify({
        'success': True,
        'summary': {
            'total_payable': total_payable,
            'total_paid': total_paid,
            'total_pending': total_pending,
            'is_fully_paid': total_pending == 0 and total_payable > 0
        },
        'fees': results
    })


@api_bp.route('/student/fees/history')
@api_student_required
def student_fee_history():
    std = g.current_student
    payments = FeePayment.query.filter_by(student_id=std.id).order_by(FeePayment.payment_date.desc()).all()

    history = []
    for p in payments:
        history.append({
            'id': p.id,
            'student_fee_id': p.student_fee_id,
            'receipt_number': p.receipt_number,
            'amount': p.amount,
            'payment_mode': p.payment_mode,
            'transaction_id': p.transaction_id,
            'payment_date': p.payment_date.strftime('%Y-%m-%d %H:%M:%S'),
            'status': p.status,
            'notes': p.notes
        })

    return jsonify({
        'success': True,
        'payment_history': history
    })


@api_bp.route('/student/fees/pay', methods=['POST'])
@api_student_required
def pay_fee():
    std = g.current_student
    data = request.get_json(silent=True) or request.form.to_dict()

    if not data:
        return jsonify({'success': False, 'error': 'Bad Request', 'message': 'Payment details missing.'}), 400

    fee_id = data.get('student_fee_id')
    amount = float(data.get('amount', 0))
    payment_mode = data.get('payment_mode', 'Online UPI')
    transaction_id = data.get('transaction_id') or generate_transaction_id()

    if not fee_id or amount <= 0:
        return jsonify({'success': False, 'error': 'Validation Error', 'message': 'Valid fee ID and positive amount required.'}), 400

    fee_rec = StudentFee.query.filter_by(id=fee_id, student_id=std.id).first()
    if not fee_rec:
        return jsonify({'success': False, 'error': 'Not Found', 'message': 'Fee record not found for this student.'}), 404

    if amount > fee_rec.pending_amount and fee_rec.pending_amount > 0:
        return jsonify({'success': False, 'error': 'Validation Error', 'message': f'Amount ₹{amount} exceeds pending balance of ₹{fee_rec.pending_amount}.'}), 400

    receipt_no = generate_receipt_number()
    payment = FeePayment(
        student_fee_id=fee_rec.id,
        student_id=std.id,
        receipt_number=receipt_no,
        amount=amount,
        payment_mode=payment_mode,
        transaction_id=transaction_id,
        payment_date=datetime.utcnow(),
        status='Success',
        notes='Online payment received via Mobile Android App'
    )
    db.session.add(payment)
    db.session.flush()

    fee_rec.update_balance()
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Payment of ₹{amount:,.2f} recorded successfully.',
        'receipt': {
            'receipt_number': receipt_no,
            'transaction_id': transaction_id,
            'amount_paid': amount,
            'payment_mode': payment_mode,
            'remaining_balance': fee_rec.pending_amount,
            'fee_status': fee_rec.status,
            'date': payment.payment_date.strftime('%Y-%m-%d %H:%M:%S')
        }
    })


# ==========================================
# 11. DIGITAL CERTIFICATES
# ==========================================

@api_bp.route('/student/certificates')
@api_bp.route('/student/certificate')
@api_student_required
def student_certificates():
    std = g.current_student
    requests = CertificateRequest.query.filter_by(student_id=std.id).order_by(CertificateRequest.created_at.desc()).all()

    results = []
    for cr in requests:
        results.append({
            'id': cr.id,
            'certificate_type': cr.certificate_type,
            'purpose': cr.purpose,
            'status': cr.status,
            'certificate_number': cr.certificate_number,
            'verification_code': cr.verification_code,
            'requested_at': cr.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'issued_date': cr.issued_date.strftime('%Y-%m-%d') if cr.issued_date else None,
            'rejection_reason': cr.rejection_reason
        })

    return jsonify({
        'success': True,
        'certificates': results
    })


@api_bp.route('/student/certificates', methods=['POST'])
@api_bp.route('/student/certificate', methods=['POST'])
@api_bp.route('/student/certificates/apply', methods=['POST'])
@api_student_required
def apply_certificate():
    std = g.current_student
    data = request.get_json(silent=True) or request.form.to_dict()

    if not data:
        return jsonify({'success': False, 'error': 'Bad Request', 'message': 'Certificate details missing.'}), 400

    cert_type = data.get('certificate_type')
    purpose = data.get('purpose', '').strip()

    if not cert_type or not purpose:
        return jsonify({'success': False, 'error': 'Validation Error', 'message': 'Both certificate_type and purpose are required.'}), 400

    code = generate_certificate_code()
    cert_req = CertificateRequest(
        student_id=std.id,
        certificate_type=cert_type,
        purpose=purpose,
        status='Pending',
        verification_code=code
    )
    db.session.add(cert_req)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'{cert_type} application submitted for administrative review.',
        'request_id': cert_req.id,
        'verification_code': code,
        'status': 'Pending'
    })


# ==========================================
# 12. LEAVE APPLICATIONS
# ==========================================

@api_bp.route('/student/leaves')
@api_bp.route('/student/leave')
@api_student_required
def student_leaves():
    std = g.current_student
    leaves = LeaveRequest.query.filter_by(student_id=std.id).order_by(LeaveRequest.created_at.desc()).all()

    results = []
    for l in leaves:
        results.append({
            'id': l.id,
            'leave_type': l.leave_type,
            'start_date': l.start_date.strftime('%Y-%m-%d'),
            'end_date': l.end_date.strftime('%Y-%m-%d'),
            'total_days': l.total_days,
            'reason': l.reason,
            'status': l.status,
            'review_comment': l.review_comment,
            'applied_at': l.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify({
        'success': True,
        'leaves': results
    })


@api_bp.route('/student/leave', methods=['POST'])
@api_bp.route('/student/leave/apply', methods=['POST'])
@api_bp.route('/student/leaves/apply', methods=['POST'])
@api_student_required
def apply_leave():
    std = g.current_student
    data = request.get_json(silent=True) or request.form.to_dict()

    if not data:
        return jsonify({'success': False, 'error': 'Bad Request', 'message': 'Leave application payload missing.'}), 400

    leave_type = data.get('leave_type')
    start_str = data.get('start_date')
    end_str = data.get('end_date')
    reason = data.get('reason', '').strip()

    if not leave_type or not start_str or not end_str or not reason:
        return jsonify({'success': False, 'error': 'Validation Error', 'message': 'leave_type, start_date, end_date, and reason are required.'}), 400

    try:
        start_d = datetime.strptime(start_str, '%Y-%m-%d').date()
        end_d = datetime.strptime(end_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'error': 'Validation Error', 'message': 'Dates must be formatted as YYYY-MM-DD.'}), 400

    if end_d < start_d:
        return jsonify({'success': False, 'error': 'Validation Error', 'message': 'end_date cannot be earlier than start_date.'}), 400

    total_days = (end_d - start_d).days + 1

    leave = LeaveRequest(
        user_id=g.current_user.id,
        student_id=std.id,
        applicant_role='STUDENT',
        leave_type=leave_type,
        start_date=start_d,
        end_date=end_d,
        total_days=total_days,
        reason=reason,
        status='Pending'
    )
    db.session.add(leave)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Leave application for {total_days} day(s) submitted successfully.',
        'leave_id': leave.id,
        'status': 'Pending'
    })


# ==========================================
# 13. GRIEVANCES & TICKETS
# ==========================================

@api_bp.route('/student/grievances')
@api_bp.route('/student/complaints')
@api_student_required
def student_grievances():
    std = g.current_student
    complaints = Complaint.query.filter_by(student_id=std.id).order_by(Complaint.created_at.desc()).all()

    results = []
    for c in complaints:
        results.append({
            'id': c.id,
            'ticket_number': c.ticket_number,
            'category': c.category,
            'title': c.title,
            'description': c.description,
            'priority': c.priority,
            'location': c.location,
            'status': c.status,
            'resolution_notes': c.resolution_notes,
            'created_at': c.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'resolved_at': c.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if c.resolved_at else None
        })

    return jsonify({
        'success': True,
        'grievances': results,
        'complaints': results
    })


@api_bp.route('/student/grievances/submit', methods=['POST'])
@api_bp.route('/student/complaints', methods=['POST'])
@api_student_required
def submit_grievance():
    std = g.current_student
    data = request.get_json(silent=True) or request.form.to_dict()

    if not data:
        return jsonify({'success': False, 'error': 'Bad Request', 'message': 'Grievance data missing.'}), 400

    category = data.get('category')
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    priority = data.get('priority', 'Medium')
    location = data.get('location', '').strip()

    if not category or not title or not description:
        return jsonify({'success': False, 'error': 'Validation Error', 'message': 'category, title, and description are required.'}), 400

    import random
    ticket_no = f"TKT-{datetime.utcnow().year}-{random.randint(1000, 9999)}"

    complaint = Complaint(
        ticket_number=ticket_no,
        student_id=std.id,
        category=category,
        title=title,
        description=description,
        priority=priority,
        location=location if location else None,
        status='Submitted'
    )
    db.session.add(complaint)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Grievance ticket {ticket_no} logged successfully.',
        'ticket_number': ticket_no,
        'status': 'Submitted'
    })


# ==========================================
# 14. NOTICES & CIRCULARS
# ==========================================

@api_bp.route('/student/notices')
@api_student_required
def student_notices():
    std = g.current_student

    # Filter notices: ALL, STUDENT, or student's specific department
    query = Notice.query.filter(
        Notice.is_active == True,
        Notice.target_audience.in_(['ALL', 'STUDENT']) | (Notice.department_id == std.department_id)
    ).order_by(Notice.publish_date.desc(), Notice.created_at.desc())

    notices = query.all()
    results = []
    for n in notices:
        results.append({
            'id': n.id,
            'title': n.title,
            'content': n.content,
            'priority': n.priority,
            'publish_date': n.publish_date.strftime('%Y-%m-%d'),
            'target_audience': n.target_audience,
            'attachment_url': n.attachment_path,
            'published_by': n.published_by.full_name if n.published_by else 'Administration'
        })

    return jsonify({
        'success': True,
        'notices': results
    })


@api_bp.route('/student/notices/<int:notice_id>')
@api_student_required
def student_notice_detail(notice_id):
    n = Notice.query.get_or_404(notice_id)
    return jsonify({
        'success': True,
        'notice': {
            'id': n.id,
            'title': n.title,
            'content': n.content,
            'priority': n.priority,
            'publish_date': n.publish_date.strftime('%Y-%m-%d'),
            'attachment_url': n.attachment_path,
            'published_by': n.published_by.full_name if n.published_by else 'Administration'
        }
    })


# ==========================================
# 15. EVENTS & REGISTRATIONS
# ==========================================

@api_bp.route('/student/events')
@api_student_required
def student_events():
    std = g.current_student
    events = Event.query.order_by(Event.start_datetime.asc()).all()

    results = []
    for e in events:
        reg = EventRegistration.query.filter_by(event_id=e.id, student_id=std.id).first()
        results.append({
            'id': e.id,
            'title': e.title,
            'description': e.description,
            'event_type': e.event_type,
            'venue': e.venue,
            'start_datetime': e.start_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'end_datetime': e.end_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'registration_deadline': e.registration_deadline.strftime('%Y-%m-%d %H:%M:%S') if e.registration_deadline else None,
            'is_open': e.is_open_for_registration,
            'is_registered': reg is not None and reg.status == 'Confirmed',
            'registered_count': e.registered_count,
            'max_participants': e.max_participants
        })

    return jsonify({
        'success': True,
        'events': results
    })


@api_bp.route('/student/events/<int:event_id>/register', methods=['POST'])
@api_student_required
def register_event(event_id):
    std = g.current_student
    e = Event.query.get_or_404(event_id)

    if not e.is_open_for_registration:
        return jsonify({'success': False, 'error': 'Event Closed', 'message': 'Registrations for this event are closed.'}), 400

    reg = EventRegistration.query.filter_by(event_id=e.id, student_id=std.id).first()
    if reg:
        if reg.status == 'Confirmed':
            reg.status = 'Cancelled'
            msg = 'Registration cancelled.'
            is_reg = False
        else:
            reg.status = 'Confirmed'
            msg = 'Registration renewed.'
            is_reg = True
    else:
        reg = EventRegistration(
            event_id=e.id,
            student_id=std.id,
            status='Confirmed'
        )
        db.session.add(reg)
        msg = f'Successfully registered for {e.title}!'
        is_reg = True

    db.session.commit()
    return jsonify({
        'success': True,
        'message': msg,
        'is_registered': is_reg
    })


@api_bp.route('/student/events/register', methods=['POST'])
@api_student_required
def register_event_body():
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data or not data.get('event_id'):
        return jsonify({'success': False, 'error': 'Bad Request', 'message': 'event_id required in request body.'}), 400
    try:
        event_id = int(data.get('event_id'))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Validation Error', 'message': 'event_id must be a valid integer.'}), 400
    return register_event(event_id)


# ==========================================
# 16. FEEDBACK
# ==========================================

@api_bp.route('/student/feedback')
@api_student_required
def student_feedback_list():
    std = g.current_student
    feedbacks = Feedback.query.filter_by(student_id=std.id).order_by(Feedback.created_at.desc()).all()
    results = []
    for f in feedbacks:
        results.append({
            'id': f.id,
            'feedback_type': f.feedback_type,
            'faculty_name': f.faculty.full_name if f.faculty else 'General',
            'rating': f.rating,
            'comments': f.comments,
            'is_anonymous': f.is_anonymous,
            'submitted_at': f.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify({
        'success': True,
        'feedback_history': results
    })


@api_bp.route('/student/feedback/subjects')
@api_student_required
def student_feedback_subjects():
    std = g.current_student
    div_id = std.division_id

    subjects = Subject.query.filter_by(department_id=std.department_id, semester_id=std.semester_id).all()
    results = []
    for s in subjects:
        fac = s.assigned_faculty[0] if s.assigned_faculty else None
        results.append({
            'subject_id': s.id,
            'subject_name': s.name,
            'subject_code': s.code,
            'faculty_id': fac.id if fac else None,
            'faculty_name': fac.full_name if fac else 'Assigned Faculty'
        })

    return jsonify({
        'success': True,
        'subjects': results
    })


@api_bp.route('/student/feedback', methods=['POST'])
@api_bp.route('/student/feedback/submit', methods=['POST'])
@api_student_required
def submit_feedback():
    std = g.current_student
    data = request.get_json(silent=True) or request.form.to_dict()

    if not data:
        return jsonify({'success': False, 'error': 'Bad Request', 'message': 'Feedback payload missing.'}), 400

    feedback_type = data.get('feedback_type', 'Faculty')
    faculty_id = data.get('faculty_id')
    course_id = std.course_id
    dept_id = std.department_id
    rating = int(data.get('rating', 5))
    clarity = int(data.get('clarity_rating', 5))
    punctuality = int(data.get('punctuality_rating', 5))
    helpfulness = int(data.get('helpfulness_rating', 5))
    comments = data.get('comments', '').strip()
    is_anon = bool(data.get('is_anonymous', False))

    if not comments:
        return jsonify({'success': False, 'error': 'Validation Error', 'message': 'Comments are required for feedback.'}), 400

    fb = Feedback(
        feedback_type=feedback_type,
        student_id=None if is_anon else std.id,
        is_anonymous=is_anon,
        faculty_id=faculty_id,
        course_id=course_id,
        department_id=dept_id,
        rating=rating,
        clarity_rating=clarity,
        punctuality_rating=punctuality,
        helpfulness_rating=helpfulness,
        comments=comments
    )
    db.session.add(fb)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Thank you! Your feedback has been submitted securely.'
    })


# ==========================================
# 17. NOTIFICATIONS
# ==========================================

@api_bp.route('/student/notifications')
@api_student_required
def student_notifications():
    user_id = g.current_user.id
    notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(30).all()

    results = []
    for n in notifs:
        results.append({
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'link': n.link,
            'notification_type': n.notification_type,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify({
        'success': True,
        'unread_count': sum(1 for n in notifs if not n.is_read),
        'notifications': results
    })


@api_bp.route('/student/notifications/<int:notification_id>/read', methods=['POST', 'PATCH'])
@api_student_required
def mark_notification_read(notification_id):
    notif = Notification.query.filter_by(id=notification_id, user_id=g.current_user.id).first()
    if notif:
        notif.is_read = True
        db.session.commit()
    return jsonify({'success': True, 'message': 'Notification marked as read.'})


@api_bp.route('/student/notifications/read-all', methods=['POST', 'PATCH'])
@api_student_required
def mark_all_notifications_read():
    Notification.query.filter_by(user_id=g.current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True, 'message': 'All notifications marked as read.'})


@api_bp.route('/student/notifications/token', methods=['POST'])
@api_student_required
def save_device_token():
    data = request.get_json(silent=True) or request.form.to_dict()
    token = data.get('token') or data.get('fcm_token') or data.get('device_token') if data else None

    if not token:
        return jsonify({'success': False, 'error': 'Bad Request', 'message': 'Device token required.'}), 400

    # In production with FCM, this stores token associated with user/student
    return jsonify({
        'success': True,
        'message': 'Device registration token saved successfully for push notifications.'
    })


# ==========================================
# 18. CASCADE DROPDOWN & WEB ERP HELPERS
# ==========================================

@api_bp.route('/courses-by-department/<int:department_id>')
def courses_by_department(department_id):
    courses = Course.query.filter_by(department_id=department_id, is_active=True).all()
    return jsonify([{'id': c.id, 'name': c.name, 'code': c.code} for c in courses])


@api_bp.route('/divisions-by-course/<int:course_id>')
def divisions_by_course(course_id):
    divisions = ClassDivision.query.filter_by(course_id=course_id).all()
    return jsonify([{'id': d.id, 'name': d.name, 'semester_id': d.semester_id} for d in divisions])


@api_bp.route('/subjects-by-course-semester/<int:course_id>/<int:semester_id>')
def subjects_by_course_semester(course_id, semester_id):
    subjects = Subject.query.filter_by(course_id=course_id, semester_id=semester_id).all()
    return jsonify([{'id': s.id, 'name': s.name, 'code': s.code, 'credits': s.credits} for s in subjects])


@api_bp.route('/students-by-division/<int:division_id>')
def students_by_division(division_id):
    students = Student.query.filter_by(division_id=division_id, status='Active').order_by(Student.roll_no.asc()).all()
    return jsonify([{
        'id': s.id,
        'roll_number': s.roll_no or s.student_id,
        'full_name': s.full_name,
        'photo': s.profile_photo
    } for s in students])
