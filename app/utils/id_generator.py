"""
Campus Connect ERP - Enterprise Identifier Generation Utility
Generates unique, deterministic, professional institutional identifiers for Students and Faculty:
- Student ID: STU{YEAR}{0001}
- Admission Number: ADM{YEAR}{0001}
- Enrollment Number: ENR{YEAR}{0001}
- Roll Number: {DEPT_CODE}-{DIV_NAME}-{001} or {DEPT_CODE}-{001}
- Faculty Employee ID: EMP{YEAR}{0001}
"""
import re
from datetime import datetime, date
from sqlalchemy import func
from app.extensions import db


def _extract_year(academic_year=None, session_id=None, reference_date=None):
    """Resolves a 4-digit academic year from params or current calendar year."""
    if academic_year:
        try:
            year_str = str(academic_year).strip()
            # If formatted like '2025-26' or '2025-2026'
            match = re.search(r'(\d{4})', year_str)
            if match:
                return int(match.group(1))
            return int(year_str)
        except Exception:
            pass

    if session_id:
        try:
            from app.models.academic_session import AcademicSession
            session = AcademicSession.query.get(session_id)
            if session:
                if session.start_year:
                    return int(session.start_year)
                if session.name:
                    match = re.search(r'(\d{4})', session.name)
                    if match:
                        return int(match.group(1))
        except Exception:
            pass

    if reference_date:
        if isinstance(reference_date, (datetime, date)):
            return reference_date.year
        try:
            match = re.search(r'(\d{4})', str(reference_date))
            if match:
                return int(match.group(1))
        except Exception:
            pass

    # Default to current session or calendar year
    try:
        from app.models.academic_session import AcademicSession
        curr_session = AcademicSession.query.filter_by(is_current=True).first()
        if curr_session and curr_session.start_year:
            return int(curr_session.start_year)
    except Exception:
        pass

    return datetime.utcnow().year


def generate_student_id(academic_year=None, session_id=None, admission_date=None):
    """
    Generates a unique institutional Student ID in the format: STU{YEAR}{0001}
    Example: STU20260001, STU20260002
    """
    from app.models.student import Student
    
    year = _extract_year(academic_year, session_id, admission_date)
    prefix = f"STU{year}"
    
    # Find maximum existing sequence with this prefix
    existing_students = Student.query.filter(Student.student_id.like(f"{prefix}%")).all()
    max_num = 0
    for s in existing_students:
        if s.student_id and s.student_id.startswith(prefix):
            suffix = s.student_id[len(prefix):]
            if suffix.isdigit():
                max_num = max(max_num, int(suffix))

    next_seq = max_num + 1
    new_id = f"{prefix}{next_seq:04d}"

    # Ensure absolute uniqueness in database
    while Student.query.filter_by(student_id=new_id).first() is not None:
        next_seq += 1
        new_id = f"{prefix}{next_seq:04d}"

    return new_id


def generate_admission_number(academic_year=None, session_id=None, admission_date=None):
    """
    Generates a unique institutional Admission Number in the format: ADM{YEAR}{0001}
    Example: ADM20260001, ADM20260002
    """
    from app.models.student import Student
    
    year = _extract_year(academic_year, session_id, admission_date)
    prefix = f"ADM{year}"
    
    existing_students = Student.query.filter(Student.admission_no.like(f"{prefix}%")).all()
    max_num = 0
    for s in existing_students:
        if s.admission_no and s.admission_no.startswith(prefix):
            suffix = s.admission_no[len(prefix):]
            if suffix.isdigit():
                max_num = max(max_num, int(suffix))

    next_seq = max_num + 1
    new_adm = f"{prefix}{next_seq:04d}"

    while Student.query.filter_by(admission_no=new_adm).first() is not None:
        next_seq += 1
        new_adm = f"{prefix}{next_seq:04d}"

    return new_adm


def generate_enrollment_number(academic_year=None, session_id=None, admission_date=None, prefix_code="ENR"):
    """
    Generates a unique institutional Enrollment Number in the format: {PREFIX}{YEAR}{0001}
    Example: ENR20260001, ENR20260002
    """
    from app.models.student import Student
    
    year = _extract_year(academic_year, session_id, admission_date)
    code = (prefix_code or "ENR").strip().upper()
    prefix = f"{code}{year}"
    
    existing_students = Student.query.filter(Student.enrollment_no.like(f"{prefix}%")).all()
    max_num = 0
    for s in existing_students:
        if s.enrollment_no and s.enrollment_no.startswith(prefix):
            suffix = s.enrollment_no[len(prefix):]
            if suffix.isdigit():
                max_num = max(max_num, int(suffix))

    next_seq = max_num + 1
    new_enr = f"{prefix}{next_seq:04d}"

    while Student.query.filter_by(enrollment_no=new_enr).first() is not None:
        next_seq += 1
        new_enr = f"{prefix}{next_seq:04d}"

    return new_enr


def generate_roll_number(department_id, course_id=None, semester_id=None, division_id=None, session_id=None, batch=None):
    """
    Generates a sequential Roll Number within an academic cohort (Department / Division / Semester / Course).
    Format: {DEPT_CODE}-{DIV_NAME}-{001} (e.g. CSE-A-001) or {DEPT_CODE}-{001} (e.g. CSE-001)
    """
    from app.models.student import Student
    from app.models.department import Department
    from app.models.class_division import ClassDivision
    from app.models.course import Course

    dept_code = "GEN"
    if department_id:
        dept = Department.query.get(department_id)
        if dept and dept.code:
            dept_code = dept.code.strip().upper()
        elif dept and dept.name:
            # Extract acronym from name
            dept_code = "".join(w[0] for w in dept.name.split() if w.isalnum()).upper() or "DEPT"

    div_suffix = ""
    if division_id and division_id != 0:
        div = ClassDivision.query.get(division_id)
        if div and div.name:
            # Clean division name like 'Section A' -> 'A' or 'A'
            clean_div = div.name.strip().upper().replace("SECTION", "").replace("SEC", "").strip()
            if clean_div:
                div_suffix = f"-{clean_div}"

    prefix = f"{dept_code}{div_suffix}"
    full_prefix = f"{prefix}-"

    # Query students with matching roll number prefix or within same cohort
    query = Student.query
    if department_id:
        query = query.filter_by(department_id=department_id)
    if division_id and division_id != 0:
        query = query.filter_by(division_id=division_id)
    if course_id:
        query = query.filter_by(course_id=course_id)
    if session_id:
        query = query.filter_by(session_id=session_id)

    cohort_students = query.all()
    max_seq = 0
    for s in cohort_students:
        if s.roll_no:
            # Check if ends in digits
            match = re.search(r'(\d+)$', s.roll_no.strip())
            if match:
                max_seq = max(max_seq, int(match.group(1)))

    # Also check all students across database starting with prefix-
    all_with_prefix = Student.query.filter(Student.roll_no.like(f"{full_prefix}%")).all()
    for s in all_with_prefix:
        if s.roll_no and s.roll_no.startswith(full_prefix):
            suffix = s.roll_no[len(full_prefix):]
            if suffix.isdigit():
                max_seq = max(max_seq, int(suffix))

    next_num = max_seq + 1
    new_roll = f"{full_prefix}{next_num:03d}"

    # Verify uniqueness
    while Student.query.filter_by(roll_no=new_roll).first() is not None:
        next_num += 1
        new_roll = f"{full_prefix}{next_num:03d}"

    return new_roll


def generate_faculty_employee_id(year=None, date_of_joining=None):
    """
    Generates a unique institutional Faculty / Employee ID in format: EMP{YEAR}{0001}
    Example: EMP20260001, EMP20260002
    """
    from app.models.faculty import Faculty

    resolved_year = _extract_year(year, reference_date=date_of_joining)
    prefix = f"EMP{resolved_year}"

    existing_faculties = Faculty.query.filter(
        (Faculty.employee_id.like(f"{prefix}%")) | (Faculty.faculty_id.like(f"{prefix}%"))
    ).all()

    max_num = 0
    for f in existing_faculties:
        for val in (f.employee_id, f.faculty_id):
            if val and val.startswith(prefix):
                suffix = val[len(prefix):]
                if suffix.isdigit():
                    max_num = max(max_num, int(suffix))

    next_seq = max_num + 1
    new_emp_id = f"{prefix}{next_seq:04d}"

    while Faculty.query.filter(
        (Faculty.employee_id == new_emp_id) | (Faculty.faculty_id == new_emp_id)
    ).first() is not None:
        next_seq += 1
        new_emp_id = f"{prefix}{next_seq:04d}"

    return new_emp_id


def backfill_missing_identifiers():
    """
    Safely inspects existing student and faculty records and backfills any
    missing IDs without altering valid existing data.
    """
    from app.models.student import Student
    from app.models.faculty import Faculty

    updated_students = 0
    updated_faculty = 0

    students = Student.query.all()
    for s in students:
        changed = False
        if not s.student_id:
            s.student_id = generate_student_id(session_id=s.session_id, admission_date=s.admission_date)
            changed = True
        if not s.admission_no:
            s.admission_no = generate_admission_number(session_id=s.session_id, admission_date=s.admission_date)
            changed = True
        if not s.enrollment_no:
            s.enrollment_no = generate_enrollment_number(session_id=s.session_id, admission_date=s.admission_date)
            changed = True
        if not s.roll_no:
            s.roll_no = generate_roll_number(
                department_id=s.department_id,
                course_id=s.course_id,
                semester_id=s.semester_id,
                division_id=s.division_id,
                session_id=s.session_id
            )
            changed = True
        if changed:
            updated_students += 1

    faculties = Faculty.query.all()
    for f in faculties:
        changed = False
        if not f.employee_id and not f.faculty_id:
            emp_id = generate_faculty_employee_id(date_of_joining=f.date_of_joining)
            f.employee_id = emp_id
            f.faculty_id = emp_id
            changed = True
        elif not f.employee_id and f.faculty_id:
            f.employee_id = f.faculty_id
            changed = True
        elif not f.faculty_id and f.employee_id:
            f.faculty_id = f.employee_id
            changed = True
        if changed:
            updated_faculty += 1

    if updated_students > 0 or updated_faculty > 0:
        db.session.commit()

    return {
        "updated_students": updated_students,
        "updated_faculty": updated_faculty
    }
