from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.utils.decorators import admin_required
from app.models.user import Role
from app.models.department import Department
from app.models.course import Course
from app.models.academic_session import AcademicSession
from app.models.semester import Semester
from app.models.class_division import ClassDivision
from app.models.subject import Subject
from app.models.faculty import Faculty
from app.models.student import Student
from app.forms.academic_forms import DepartmentForm, CourseForm, SemesterForm, AcademicSessionForm, ClassDivisionForm, SubjectForm

academic_bp = Blueprint('academic', __name__)


# --- DEPARTMENTS ---
@academic_bp.route('/departments')
@login_required
def departments():
    depts = Department.query.all()
    return render_template('academic/departments.html', departments=depts)


@academic_bp.route('/departments/<int:dept_id>')
@login_required
def department_detail(dept_id):
    dept = Department.query.get_or_404(dept_id)
    courses = Course.query.filter_by(department_id=dept.id, is_active=True).all()
    faculty_members = Faculty.query.filter_by(department_id=dept.id, status='Active').all()
    students = Student.query.filter_by(department_id=dept.id, status='Active').all()
    subjects = Subject.query.filter_by(department_id=dept.id).all()
    divisions = ClassDivision.query.filter_by(department_id=dept.id).all()
    
    return render_template('academic/department_detail.html',
        dept=dept,
        courses=courses,
        faculty_members=faculty_members,
        students=students,
        subjects=subjects,
        divisions=divisions
    )


@academic_bp.route('/departments/create', methods=['GET', 'POST'])
@login_required
@admin_required
def department_create():
    form = DepartmentForm()
    faculties = Faculty.query.filter_by(status='Active').all()
    form.hod_faculty_id.choices = [(0, '-- Select Head of Department --')] + [(f.id, f"{f.full_name} ({f.faculty_id})") for f in faculties]

    if form.validate_on_submit():
        dept = Department(
            name=form.name.data.strip(),
            code=form.code.data.strip().upper(),
            description=form.description.data.strip() if form.description.data else None,
            hod_faculty_id=form.hod_faculty_id.data if form.hod_faculty_id.data != 0 else None,
            is_active=form.is_active.data
        )
        db.session.add(dept)
        db.session.commit()
        flash(f'Department "{dept.name}" created successfully.', 'success')
        return redirect(url_for('academic.departments'))

    return render_template('academic/department_form.html', form=form, title='Create Department')


@academic_bp.route('/departments/<int:dept_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def department_edit(dept_id):
    dept = Department.query.get_or_404(dept_id)
    form = DepartmentForm(obj=dept)
    faculties = Faculty.query.filter_by(department_id=dept.id, status='Active').all()
    form.hod_faculty_id.choices = [(0, '-- Select HOD --')] + [(f.id, f"{f.full_name} ({f.faculty_id})") for f in faculties]

    if request.method == 'GET':
        form.hod_faculty_id.data = dept.hod_faculty_id or 0

    if form.validate_on_submit():
        dept.name = form.name.data.strip()
        dept.code = form.code.data.strip().upper()
        dept.description = form.description.data.strip() if form.description.data else None
        dept.hod_faculty_id = form.hod_faculty_id.data if form.hod_faculty_id.data != 0 else None
        dept.is_active = form.is_active.data
        db.session.commit()
        flash(f'Department "{dept.name}" updated successfully.', 'success')
        return redirect(url_for('academic.departments'))

    return render_template('academic/department_form.html', form=form, title='Edit Department', dept=dept)


@academic_bp.route('/hods')
@login_required
def hod_list():
    depts = Department.query.filter_by(is_active=True).all()
    return render_template('academic/hod_list.html', departments=depts)


# --- COURSES ---
@academic_bp.route('/courses')
@login_required
def courses():
    course_list = Course.query.all()
    return render_template('academic/courses.html', courses=course_list)


@academic_bp.route('/courses/create', methods=['GET', 'POST'])
@login_required
@admin_required
def course_create():
    form = CourseForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.filter_by(is_active=True).all()]

    if form.validate_on_submit():
        course = Course(
            name=form.name.data.strip(),
            code=form.code.data.strip().upper(),
            department_id=form.department_id.data,
            duration_years=form.duration_years.data,
            total_semesters=form.total_semesters.data,
            description=form.description.data.strip() if form.description.data else None,
            is_active=form.is_active.data
        )
        db.session.add(course)
        db.session.commit()
        flash(f'Course "{course.name}" created successfully.', 'success')
        return redirect(url_for('academic.courses'))

    return render_template('academic/course_form.html', form=form, title='Create Course')


@academic_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def course_edit(course_id):
    course = Course.query.get_or_404(course_id)
    form = CourseForm(obj=course)
    form.department_id.choices = [(d.id, d.name) for d in Department.query.filter_by(is_active=True).all()]

    if form.validate_on_submit():
        course.name = form.name.data.strip()
        course.code = form.code.data.strip().upper()
        course.department_id = form.department_id.data
        course.duration_years = form.duration_years.data
        course.total_semesters = form.total_semesters.data
        course.description = form.description.data.strip() if form.description.data else None
        course.is_active = form.is_active.data
        db.session.commit()
        flash(f'Course "{course.name}" updated successfully.', 'success')
        return redirect(url_for('academic.courses'))

    return render_template('academic/course_form.html', form=form, title='Edit Course', course=course)


# --- SESSIONS & SEMESTERS ---
@academic_bp.route('/sessions', methods=['GET', 'POST'])
@login_required
@admin_required
def sessions():
    form = AcademicSessionForm()
    if form.validate_on_submit():
        if form.is_current.data:
            AcademicSession.query.update({AcademicSession.is_current: False})
            
        ses = AcademicSession(
            name=form.name.data.strip(),
            start_year=form.start_year.data,
            end_year=form.end_year.data,
            is_current=form.is_current.data
        )
        db.session.add(ses)
        db.session.commit()
        flash(f'Academic Session "{ses.name}" saved.', 'success')
        return redirect(url_for('academic.sessions'))

    session_list = AcademicSession.query.order_by(AcademicSession.start_year.desc()).all()
    return render_template('academic/sessions.html', sessions=session_list, form=form)


@academic_bp.route('/sessions/<int:session_id>/set-current', methods=['POST'])
@login_required
@admin_required
def set_current_session(session_id):
    AcademicSession.query.update({AcademicSession.is_current: False})
    ses = AcademicSession.query.get_or_404(session_id)
    ses.is_current = True
    db.session.commit()
    flash(f'Session {ses.name} is now the active academic session.', 'success')
    return redirect(url_for('academic.sessions'))


@academic_bp.route('/semesters')
@login_required
def semesters():
    sem_list = Semester.query.order_by(Semester.number.asc()).all()
    return render_template('academic/semesters.html', semesters=sem_list)


# --- CLASS DIVISIONS / SECTIONS ---
@academic_bp.route('/divisions')
@login_required
def divisions():
    divs = ClassDivision.query.all()
    return render_template('academic/divisions.html', divisions=divs)


@academic_bp.route('/divisions/create', methods=['GET', 'POST'])
@login_required
@admin_required
def division_create():
    form = ClassDivisionForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.filter_by(is_active=True).all()]
    form.course_id.choices = [(c.id, c.name) for c in Course.query.filter_by(is_active=True).all()]
    form.semester_id.choices = [(s.id, s.name) for s in Semester.query.filter_by(is_active=True).order_by(Semester.number.asc()).all()]
    form.session_id.choices = [(ses.id, ses.name) for ses in AcademicSession.query.all()]

    if form.validate_on_submit():
        div = ClassDivision(
            name=form.name.data.strip().upper(),
            department_id=form.department_id.data,
            course_id=form.course_id.data,
            semester_id=form.semester_id.data,
            session_id=form.session_id.data,
            room_number=form.room_number.data.strip() if form.room_number.data else None
        )
        db.session.add(div)
        db.session.commit()
        flash(f'Class Division "{div.name}" created successfully.', 'success')
        return redirect(url_for('academic.divisions'))

    return render_template('academic/division_form.html', form=form, title='Create Class Division')


# --- SUBJECTS ---
@academic_bp.route('/subjects')
@login_required
def subjects():
    dept_id = request.args.get('dept_id', type=int)
    course_id = request.args.get('course_id', type=int)
    semester_id = request.args.get('semester_id', type=int)

    query = Subject.query
    if dept_id:
        query = query.filter_by(department_id=dept_id)
    if course_id:
        query = query.filter_by(course_id=course_id)
    if semester_id:
        query = query.filter_by(semester_id=semester_id)

    subject_list = query.all()
    departments = Department.query.filter_by(is_active=True).all()
    courses = Course.query.filter_by(is_active=True).all()
    semesters = Semester.query.filter_by(is_active=True).all()

    return render_template('academic/subjects.html',
        subjects=subject_list,
        departments=departments,
        courses=courses,
        semesters=semesters,
        selected_dept=dept_id,
        selected_course=course_id,
        selected_sem=semester_id
    )


@academic_bp.route('/subjects/create', methods=['GET', 'POST'])
@login_required
@admin_required
def subject_create():
    form = SubjectForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.filter_by(is_active=True).all()]
    form.course_id.choices = [(c.id, c.name) for c in Course.query.filter_by(is_active=True).all()]
    form.semester_id.choices = [(s.id, s.name) for s in Semester.query.filter_by(is_active=True).order_by(Semester.number.asc()).all()]
    form.assigned_faculty_ids.choices = [(f.id, f"{f.full_name} ({f.department.code if f.department else ''})") for f in Faculty.query.filter_by(status='Active').all()]

    if form.validate_on_submit():
        subj = Subject(
            name=form.name.data.strip(),
            code=form.code.data.strip().upper(),
            credits=form.credits.data,
            subject_type=form.subject_type.data,
            department_id=form.department_id.data,
            course_id=form.course_id.data,
            semester_id=form.semester_id.data
        )
        if form.assigned_faculty_ids.data:
            assigned = Faculty.query.filter(Faculty.id.in_(form.assigned_faculty_ids.data)).all()
            subj.faculties = assigned

        db.session.add(subj)
        db.session.commit()
        flash(f'Subject "{subj.name}" ({subj.code}) added successfully.', 'success')
        return redirect(url_for('academic.subjects'))

    return render_template('academic/subject_form.html', form=form, title='Create Subject')


@academic_bp.route('/subjects/<int:subj_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def subject_edit(subj_id):
    subj = Subject.query.get_or_404(subj_id)
    form = SubjectForm(obj=subj)
    form.department_id.choices = [(d.id, d.name) for d in Department.query.filter_by(is_active=True).all()]
    form.course_id.choices = [(c.id, c.name) for c in Course.query.filter_by(is_active=True).all()]
    form.semester_id.choices = [(s.id, s.name) for s in Semester.query.filter_by(is_active=True).order_by(Semester.number.asc()).all()]
    form.assigned_faculty_ids.choices = [(f.id, f"{f.full_name} ({f.department.code if f.department else ''})") for f in Faculty.query.filter_by(status='Active').all()]

    if request.method == 'GET':
        form.assigned_faculty_ids.data = [f.id for f in subj.faculties]

    if form.validate_on_submit():
        subj.name = form.name.data.strip()
        subj.code = form.code.data.strip().upper()
        subj.credits = form.credits.data
        subj.subject_type = form.subject_type.data
        subj.department_id = form.department_id.data
        subj.course_id = form.course_id.data
        subj.semester_id = form.semester_id.data

        if form.assigned_faculty_ids.data is not None:
            subj.faculties = Faculty.query.filter(Faculty.id.in_(form.assigned_faculty_ids.data)).all()

        db.session.commit()
        flash(f'Subject "{subj.name}" updated successfully.', 'success')
        return redirect(url_for('academic.subjects'))

    return render_template('academic/subject_form.html', form=form, title='Edit Subject', subj=subj)
