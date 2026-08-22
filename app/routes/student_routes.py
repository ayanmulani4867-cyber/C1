import io
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from datetime import date, datetime
from app.extensions import db
from app.utils.decorators import admin_required, student_required
from app.utils.uploads import save_uploaded_file, save_profile_photo
from app.utils.pdf import generate_id_card_pdf
from app.models.user import User, Role
from app.models.student import Student, StudentDocument, Address, ParentInfo, EmergencyContact
from app.models.department import Department
from app.models.course import Course
from app.models.semester import Semester
from app.models.academic_session import AcademicSession
from app.models.class_division import ClassDivision
from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.assignment import Assignment, AssignmentSubmission, StudyMaterial
from app.models.exam import Exam, ExamResult
from app.models.fee import StudentFee, FeePayment, FeeStructure
from app.models.leave import LeaveRequest
from app.models.certificate import CertificateRequest
from app.models.notice import Notice
from app.models.timetable import Timetable
from app.forms.student_forms import StudentCreateForm, StudentEditForm, StudentDocumentForm
from app.utils.id_generator import (
    generate_student_id,
    generate_admission_number,
    generate_enrollment_number,
    generate_roll_number
)

student_bp = Blueprint('student', __name__)


@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash('Student record not linked to your user account. Please contact registrar.', 'warning')
        return redirect(url_for('auth.profile'))

    # Attendance calculation from real database records
    records = AttendanceRecord.query.filter_by(student_id=student.id).all()
    total_classes = len(records)
    attended_classes = sum(1 for r in records if r.status in ('Present', 'Late'))
    attendance_pct = round((attended_classes / total_classes * 100), 1) if total_classes > 0 else 100.0

    # Subject-wise attendance
    subject_attendance = {}
    for r in records:
        subj_name = r.session.subject.name if r.session and r.session.subject else 'General'
        if subj_name not in subject_attendance:
            subject_attendance[subj_name] = {'total': 0, 'present': 0}
        subject_attendance[subj_name]['total'] += 1
        if r.status in ('Present', 'Late'):
            subject_attendance[subj_name]['present'] += 1

    for k, v in subject_attendance.items():
        v['pct'] = round((v['present'] / v['total'] * 100), 1) if v['total'] > 0 else 0

    # Pending assignments
    division_id = student.class_division_id
    assignments = []
    if division_id:
        assignments = Assignment.query.filter_by(class_division_id=division_id).order_by(Assignment.due_date.asc()).limit(5).all()

    # Fee status
    fee_records = StudentFee.query.filter_by(student_id=student.id).all()
    total_due = sum(f.pending_amount for f in fee_records)
    total_paid = sum(f.paid_amount for f in fee_records)

    # Exam results / CGPA
    results = ExamResult.query.filter_by(student_id=student.id).all()
    gpas = [r.grade_point for r in results if r.grade_point is not None]
    cgpa = round(sum(gpas) / len(gpas), 2) if gpas else None

    # Upcoming exams
    upcoming_exams = Exam.query.filter(
        Exam.semester_id == student.semester_id,
        Exam.exam_date >= date.today()
    ).order_by(Exam.exam_date.asc()).limit(4).all()

    # Recent notices
    notices = Notice.query.filter_by(is_published=True).order_by(Notice.created_at.desc()).limit(5).all()

    # Today's schedule
    today_name = date.today().strftime('%A')
    today_schedule = []
    div_id = student.class_division_id or student.division_id
    if div_id:
        today_schedule = Timetable.query.filter_by(class_division_id=div_id, day_of_week=today_name).order_by(Timetable.start_time.asc()).all()

    return render_template('student/dashboard.html',
        student=student,
        attendance_pct=attendance_pct,
        total_classes=total_classes,
        attended_classes=attended_classes,
        subject_attendance=subject_attendance,
        assignments=assignments,
        total_due=total_due,
        total_paid=total_paid,
        cgpa=cgpa,
        upcoming_exams=upcoming_exams,
        today_schedule=today_schedule,
        notices=notices
    )


@student_bp.route('/list')
@login_required
def index():
    if current_user.role not in [Role.ADMIN, Role.FACULTY, Role.HOD]:
        flash('Access restricted.', 'danger')
        return redirect(url_for('main.index'))

    dept_id = request.args.get('dept_id', type=int)
    course_id = request.args.get('course_id', type=int)
    semester_id = request.args.get('semester_id', type=int)
    division_id = request.args.get('division_id', type=int)
    status = request.args.get('status', '')
    search = request.args.get('q', '').strip()

    query = Student.query
    if dept_id:
        query = query.filter_by(department_id=dept_id)
    if course_id:
        query = query.filter_by(course_id=course_id)
    if semester_id:
        query = query.filter_by(semester_id=semester_id)
    if division_id:
        query = query.filter_by(division_id=division_id)
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(
            (Student.first_name.ilike(f'%{search}%')) |
            (Student.last_name.ilike(f'%{search}%')) |
            (Student.full_name.ilike(f'%{search}%')) |
            (Student.roll_no.ilike(f'%{search}%')) |
            (Student.student_id.ilike(f'%{search}%')) |
            (Student.admission_no.ilike(f'%{search}%')) |
            (Student.college_email.ilike(f'%{search}%'))
        )

    students = query.order_by(Student.roll_no.asc(), Student.id.asc()).all()
    departments = Department.query.filter_by(is_active=True).all()
    courses = Course.query.filter_by(is_active=True).all()
    semesters = Semester.query.filter_by(is_active=True).all()
    divisions = ClassDivision.query.all()

    return render_template('student/list.html',
        students=students,
        departments=departments,
        courses=courses,
        semesters=semesters,
        divisions=divisions,
        selected_dept=dept_id,
        selected_course=course_id,
        selected_sem=semester_id,
        selected_div=division_id,
        selected_status=status,
        search=search
    )


@student_bp.route('/documents')
@login_required
def documents():
    if current_user.role == Role.ADMIN:
        docs = StudentDocument.query.order_by(StudentDocument.uploaded_at.desc()).all()
    else:
        student = Student.query.filter_by(user_id=current_user.id).first()
        docs = StudentDocument.query.filter_by(student_id=student.id).all() if student else []

    return render_template('student/documents.html', documents=docs)


@student_bp.route('/profile')
@login_required
def my_profile():
    if current_user.role == Role.STUDENT:
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student:
            return redirect(url_for('student.profile_view', student_id=student.id))
    return redirect(url_for('auth.profile'))


@student_bp.route('/id-card')
@login_required
def id_card_view():
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash('Student profile not found.', 'warning')
        return redirect(url_for('main.index'))
    return redirect(url_for('student.download_id_card', student_id=student.id))


@student_bp.route('/attendance')
@login_required
def attendance_view():
    return redirect(url_for('attendance.index'))


@student_bp.route('/results')
@login_required
def results_view():
    return redirect(url_for('exam.results'))


@student_bp.route('/timetable')
@login_required
def timetable_view():
    return redirect(url_for('timetable.index'))


@student_bp.route('/assignments')
@login_required
def assignments_view():
    return redirect(url_for('assignment.index'))


@student_bp.route('/study-materials')
@login_required
def materials_view():
    return redirect(url_for('assignment.materials'))


@student_bp.route('/exams')
@login_required
def exams_view():
    return redirect(url_for('exam.index'))


@student_bp.route('/fees')
@login_required
def fees_view():
    return redirect(url_for('fee.index'))


@student_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = StudentCreateForm()
    
    # Populate dropdown choices
    form.department_id.choices = [(d.id, f"{d.name} ({d.code})") for d in Department.query.filter_by(is_active=True).all()]
    form.course_id.choices = [(c.id, f"{c.name} ({c.code})") for c in Course.query.filter_by(is_active=True).all()]
    form.semester_id.choices = [(s.id, s.name) for s in Semester.query.filter_by(is_active=True).order_by(Semester.number.asc()).all()]
    form.session_id.choices = [(ses.id, ses.name) for ses in AcademicSession.query.all()]
    
    divisions = ClassDivision.query.all()
    form.division_id.choices = [(0, '-- None / Unassigned --')] + [(div.id, f"{div.name} ({div.course.code if div.course else 'Course'} - Sem {div.semester.number if div.semester else ''})") for div in divisions]

    if form.validate_on_submit():
        # Auto-generate unique identifiers
        generated_student_id = form.student_id.data.strip() if form.student_id.data and form.student_id.data.strip() else generate_student_id(session_id=form.session_id.data, admission_date=form.admission_date.data)
        generated_admission_no = form.admission_no.data.strip() if form.admission_no.data and form.admission_no.data.strip() else generate_admission_number(session_id=form.session_id.data, admission_date=form.admission_date.data)
        generated_enrollment_no = form.enrollment_no.data.strip() if form.enrollment_no.data and form.enrollment_no.data.strip() else generate_enrollment_number(session_id=form.session_id.data, admission_date=form.admission_date.data)
        
        div_id = form.division_id.data if form.division_id.data and form.division_id.data != 0 else None
        generated_roll_no = form.roll_no.data.strip() if form.roll_no.data and form.roll_no.data.strip() else generate_roll_number(
            department_id=form.department_id.data,
            course_id=form.course_id.data,
            semester_id=form.semester_id.data,
            division_id=div_id,
            session_id=form.session_id.data,
            batch=form.batch.data
        )

        # 1. Create or bind User account
        # Primary login identifier is the official college email
        college_email_clean = form.college_email.data.strip().lower()
        username = form.username.data.strip().lower() if form.username.data and form.username.data.strip() else college_email_clean
        
        # Initial password is the registered mobile number
        mobile_clean = form.mobile.data.strip()
        raw_password = mobile_clean if mobile_clean else (form.temporary_password.data if form.temporary_password.data else 'Campus@123')
        
        user = User(
            username=username,
            email=college_email_clean,
            role=Role.STUDENT,
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            phone=mobile_clean or None,
            must_change_password=True,
            is_active=True
        )
        user.set_password(raw_password)
        db.session.add(user)
        db.session.flush()

        # Handle photo
        photo_filename = None
        if form.profile_photo.data:
            photo_filename = save_profile_photo(form.profile_photo.data, prefix='std')
            if photo_filename:
                user.profile_image = photo_filename

        full_name = f"{form.first_name.data.strip()} {form.middle_name.data.strip() + ' ' if form.middle_name.data else ''}{form.last_name.data.strip()}".strip()

        perm_l1 = form.curr_address_line1.data if form.same_as_current.data else form.perm_address_line1.data
        perm_l2 = form.curr_address_line2.data if form.same_as_current.data else form.perm_address_line2.data
        perm_c = form.curr_city.data if form.same_as_current.data else form.perm_city.data
        perm_d = form.curr_district.data if form.same_as_current.data else form.perm_district.data
        perm_s = form.curr_state.data if form.same_as_current.data else form.perm_state.data
        perm_cntry = form.curr_country.data if form.same_as_current.data else form.perm_country.data
        perm_pin = form.curr_pincode.data if form.same_as_current.data else form.perm_pincode.data

        # 2. Create Student
        student = Student(
            user_id=user.id,
            student_id=generated_student_id,
            enrollment_no=generated_enrollment_no,
            admission_no=generated_admission_no,
            roll_no=generated_roll_no,
            first_name=form.first_name.data.strip(),
            middle_name=form.middle_name.data.strip() if form.middle_name.data else None,
            last_name=form.last_name.data.strip(),
            full_name=full_name,
            profile_photo=photo_filename,
            dob=form.dob.data,
            gender=form.gender.data,
            blood_group=form.blood_group.data if form.blood_group.data else None,
            nationality=form.nationality.data if form.nationality.data else 'Indian',
            personal_email=form.personal_email.data.strip().lower() if form.personal_email.data else None,
            college_email=college_email_clean,
            mobile=mobile_clean,
            alt_mobile=form.alt_mobile.data.strip() if form.alt_mobile.data else None,
            department_id=form.department_id.data,
            course_id=form.course_id.data,
            semester_id=form.semester_id.data,
            session_id=form.session_id.data,
            division_id=div_id,
            admission_date=form.admission_date.data or date.today(),
            batch=form.batch.data if form.batch.data else None,
            status=form.status.data,
            curr_address_line1=form.curr_address_line1.data or '',
            curr_address_line2=form.curr_address_line2.data or '',
            curr_city=form.curr_city.data or '',
            curr_district=form.curr_district.data or '',
            curr_state=form.curr_state.data or '',
            curr_country=form.curr_country.data or 'India',
            curr_pincode=form.curr_pincode.data or '',
            perm_address_line1=perm_l1 or '',
            perm_address_line2=perm_l2 or '',
            perm_city=perm_c or '',
            perm_district=perm_d or '',
            perm_state=perm_s or '',
            perm_country=perm_cntry or 'India',
            perm_pincode=perm_pin or '',
            father_name=form.father_name.data or '',
            father_phone=form.father_phone.data or '',
            father_email=form.father_email.data or '',
            father_occupation=form.father_occupation.data or '',
            mother_name=form.mother_name.data or '',
            mother_phone=form.mother_phone.data or '',
            mother_email=form.mother_email.data or '',
            mother_occupation=form.mother_occupation.data or '',
            emergency_name=form.emergency_name.data or '',
            emergency_relation=form.emergency_relation.data or '',
            emergency_phone=form.emergency_phone.data or '',
            emergency_alt_phone=form.emergency_alt_phone.data or '',
            prev_qualification=form.prev_qualification.data or '',
            prev_institution=form.prev_institution.data or '',
            prev_percentage=form.prev_percentage.data
        )
        db.session.add(student)
        db.session.commit()
        flash(
            f"Student {student.full_name} enrolled successfully! "
            f"Auto-generated IDs: [Student ID: {student.student_id} | Admission No: {student.admission_no} | "
            f"Enrollment No: {student.enrollment_no} | Roll No: {student.roll_no}]. "
            f"Login email: {student.college_email}. Initial password is the registered mobile number ({student.mobile}). "
            f"The student will be prompted to change password upon first login.",
            "success"
        )
        return redirect(url_for('student.profile_view', student_id=student.id))

    return render_template('student/create.html', form=form)


@student_bp.route('/<int:student_id>', endpoint='profile_view')
@student_bp.route('/<int:student_id>', endpoint='view')
@login_required
def profile_view(student_id):
    student = Student.query.get_or_404(student_id)
    doc_form = StudentDocumentForm()
    
    # Check permissions
    if current_user.role == Role.STUDENT:
        current_std = Student.query.filter_by(user_id=current_user.id).first()
        if not current_std or current_std.id != student.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('student.dashboard'))

    # Attendance
    records = AttendanceRecord.query.filter_by(student_id=student.id).all()
    total_classes = len(records)
    attended = sum(1 for r in records if r.status in ('Present', 'Late'))
    attendance_pct = round((attended / total_classes * 100), 1) if total_classes > 0 else 100.0

    # Results
    results = ExamResult.query.filter_by(student_id=student.id).all()

    # Fee Records
    fee_records = StudentFee.query.filter_by(student_id=student.id).all()

    # Documents
    documents = StudentDocument.query.filter_by(student_id=student.id).all()

    return render_template('student/profile.html',
        student=student,
        attendance_pct=attendance_pct,
        total_classes=total_classes,
        attended=attended,
        results=results,
        fee_records=fee_records,
        documents=documents,
        doc_form=doc_form
    )


@student_bp.route('/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(student_id):
    student = Student.query.get_or_404(student_id)
    form = StudentEditForm(obj=student)
    
    form.department_id.choices = [(d.id, f"{d.name} ({d.code})") for d in Department.query.filter_by(is_active=True).all()]
    form.course_id.choices = [(c.id, f"{c.name} ({c.code})") for c in Course.query.filter_by(is_active=True).all()]
    form.semester_id.choices = [(s.id, s.name) for s in Semester.query.filter_by(is_active=True).order_by(Semester.number.asc()).all()]
    form.session_id.choices = [(ses.id, ses.name) for ses in AcademicSession.query.all()]
    
    divisions = ClassDivision.query.all()
    form.division_id.choices = [(0, '-- None / Unassigned --')] + [(div.id, f"{div.name} ({div.course.code if div.course else 'Course'} - Sem {div.semester.number if div.semester else ''})") for div in divisions]

    if request.method == 'GET':
        form.department_id.data = student.department_id
        form.course_id.data = student.course_id
        form.semester_id.data = student.semester_id
        form.session_id.data = student.session_id
        form.division_id.data = student.division_id or 0
        if student.dob:
            form.dob.data = student.dob
        if student.admission_date:
            form.admission_date.data = student.admission_date

    if form.validate_on_submit():
        student.first_name = form.first_name.data.strip()
        student.middle_name = form.middle_name.data.strip() if form.middle_name.data else None
        student.last_name = form.last_name.data.strip()
        student.full_name = f"{form.first_name.data.strip()} {form.middle_name.data.strip() + ' ' if form.middle_name.data else ''}{form.last_name.data.strip()}".strip()
        student.roll_no = form.roll_no.data.strip() if form.roll_no.data else None
        student.batch = form.batch.data.strip() if form.batch.data else None
        student.admission_date = form.admission_date.data
        student.dob = form.dob.data
        student.gender = form.gender.data
        student.blood_group = form.blood_group.data
        student.nationality = form.nationality.data.strip() if form.nationality.data else 'Indian'
        student.personal_email = form.personal_email.data.strip().lower() if form.personal_email.data else None
        student.mobile = form.mobile.data.strip()
        student.alt_mobile = form.alt_mobile.data.strip() if form.alt_mobile.data else None
        student.department_id = form.department_id.data
        student.course_id = form.course_id.data
        student.semester_id = form.semester_id.data
        student.session_id = form.session_id.data
        student.division_id = form.division_id.data if form.division_id.data and form.division_id.data != 0 else None
        student.status = form.status.data

        if form.profile_photo.data:
            filename = save_profile_photo(form.profile_photo.data, prefix='std')
            if filename:
                student.profile_photo = filename
                if student.user:
                    student.user.profile_image = filename

        student.curr_address_line1 = form.curr_address_line1.data or ''
        student.curr_address_line2 = form.curr_address_line2.data or ''
        student.curr_city = form.curr_city.data or ''
        student.curr_district = form.curr_district.data or ''
        student.curr_state = form.curr_state.data or ''
        student.curr_pincode = form.curr_pincode.data or ''

        student.perm_address_line1 = form.perm_address_line1.data or ''
        student.perm_address_line2 = form.perm_address_line2.data or ''
        student.perm_city = form.perm_city.data or ''
        student.perm_district = form.perm_district.data or ''
        student.perm_state = form.perm_state.data or ''
        student.perm_pincode = form.perm_pincode.data or ''

        student.father_name = form.father_name.data or ''
        student.father_phone = form.father_phone.data or ''
        student.father_email = form.father_email.data or ''
        student.father_occupation = form.father_occupation.data or ''
        student.mother_name = form.mother_name.data or ''
        student.mother_phone = form.mother_phone.data or ''
        student.mother_email = form.mother_email.data or ''
        student.mother_occupation = form.mother_occupation.data or ''

        student.emergency_name = form.emergency_name.data or ''
        student.emergency_relation = form.emergency_relation.data or ''
        student.emergency_phone = form.emergency_phone.data or ''
        student.emergency_alt_phone = form.emergency_alt_phone.data or ''

        student.prev_qualification = form.prev_qualification.data or ''
        student.prev_institution = form.prev_institution.data or ''
        student.prev_percentage = form.prev_percentage.data
        student.admission_type = form.admission_type.data or 'Regular'
        student.scholarship_status = form.scholarship_status.data or 'None'
        student.hostel_status = form.hostel_status.data or 'Day Scholar'
        student.transport_status = form.transport_status.data or 'Self'

        # Also sync user status and mobile
        if student.user:
            student.user.first_name = student.first_name
            student.user.last_name = student.last_name
            student.user.phone = student.mobile
            student.user.is_active = (student.status == 'Active')

        db.session.commit()
        flash(f'Student profile for {student.full_name} updated successfully.', 'success')
        return redirect(url_for('student.profile_view', student_id=student.id))

    return render_template('student/edit.html', form=form, student=student)


@student_bp.route('/<int:student_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_status(student_id):
    student = Student.query.get_or_404(student_id)
    student.status = 'Inactive' if student.status == 'Active' else 'Active'
    if student.user:
        student.user.is_active = (student.status == 'Active')
    db.session.commit()
    flash(f'Student {student.full_name} status updated to {student.status}.', 'success')
    return redirect(request.referrer or url_for('student.index'))


@student_bp.route('/<int:student_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(student_id):
    student = Student.query.get_or_404(student_id)
    name = student.full_name
    # Remove user account if exists
    user = student.user
    db.session.delete(student)
    if user:
        db.session.delete(user)
    db.session.commit()
    flash(f'Student record for {name} has been deleted.', 'info')
    return redirect(url_for('student.index'))


@student_bp.route('/<int:student_id>/id-card')
@student_bp.route('/<int:student_id>/id-card/download')
@login_required
def download_id_card(student_id):
    student = Student.query.get_or_404(student_id)
    
    # Check permissions
    if current_user.role == Role.STUDENT:
        current_std = Student.query.filter_by(user_id=current_user.id).first()
        if not current_std or current_std.id != student.id:
            flash('Unauthorized action.', 'danger')
            return redirect(url_for('student.dashboard'))

    college_info = {
        'name': current_app.config.get('COLLEGE_NAME', 'Sharad Institute of Technology'),
        'short_name': current_app.config.get('COLLEGE_SHORT_NAME', 'SITCOE'),
        'address': current_app.config.get('COLLEGE_ADDRESS', 'Yadrav (Ichalkaranji), Maharashtra - 416145'),
        'phone': current_app.config.get('COLLEGE_PHONE', '+91 2322 253000'),
        'email': current_app.config.get('COLLEGE_EMAIL', 'contact@sitcoe.org.in')
    }

    pdf_buffer = generate_id_card_pdf(student, college_info=college_info)
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"ID_Card_{student.roll_number.replace('/', '_')}.pdf"
    )


@student_bp.route('/<int:student_id>/upload-document', methods=['POST'])
@login_required
def upload_document(student_id):
    student = Student.query.get_or_404(student_id)
    form = StudentDocumentForm()
    if form.validate_on_submit():
        filename = save_uploaded_file(form.document_file.data, subfolder='documents')
        if filename:
            doc = StudentDocument(
                student_id=student.id,
                doc_type=form.doc_type.data,
                title=form.title.data.strip(),
                file_path=filename
            )
            db.session.add(doc)
            db.session.commit()
            flash('Document uploaded successfully.', 'success')
        else:
            flash('Failed to save document. Check file format.', 'danger')
    return redirect(url_for('student.profile_view', student_id=student.id))
