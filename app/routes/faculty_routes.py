from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from datetime import date, datetime
from app.extensions import db
from app.utils.decorators import admin_required, faculty_required
from app.utils.uploads import save_uploaded_file, save_profile_photo
from app.utils.pdf import generate_faculty_id_card_pdf
from app.models.user import User, Role
from app.models.faculty import Faculty, FacultyDocument, FacultyAddress, FacultyEmergencyContact
from app.models.department import Department
from app.models.subject import Subject
from app.models.timetable import Timetable
from app.models.attendance import AttendanceSession, AttendanceRecord
from app.models.assignment import Assignment, AssignmentSubmission, StudyMaterial
from app.models.exam import Exam, ExamResult
from app.models.leave import LeaveRequest
from app.models.feedback import Feedback
from app.models.notice import Notice
from app.models.student import Student
from app.models.class_division import ClassDivision
from app.forms.faculty_forms import FacultyCreateForm, FacultyEditForm, FacultyDocumentForm
from app.utils.id_generator import generate_faculty_employee_id

faculty_bp = Blueprint('faculty', __name__)


@faculty_bp.route('/dashboard')
@login_required
@faculty_required
def dashboard():
    faculty = Faculty.query.filter_by(user_id=current_user.id).first()
    if not faculty:
        flash('Faculty record not linked to your user account.', 'warning')
        return redirect(url_for('auth.profile'))

    today_name = date.today().strftime('%A')
    today_schedule = Timetable.query.filter_by(faculty_id=faculty.id, day_of_week=today_name).order_by(Timetable.start_time.asc()).all()
    assigned_subjects = faculty.subjects
    
    # Assignments created
    my_assignments = Assignment.query.filter_by(faculty_id=faculty.id).order_by(Assignment.due_date.desc()).limit(5).all()

    # Leaves
    my_leaves = LeaveRequest.query.filter_by(faculty_id=faculty.id).order_by(LeaveRequest.created_at.desc()).limit(5).all()

    # Feedback ratings
    feedbacks = Feedback.query.filter_by(faculty_id=faculty.id).all()
    avg_rating = round(sum(f.rating for f in feedbacks) / len(feedbacks), 1) if feedbacks else 5.0
    total_feedbacks = len(feedbacks)

    # Active study materials
    my_materials = StudyMaterial.query.filter_by(faculty_id=faculty.id).count() if hasattr(StudyMaterial, 'faculty_id') else 0

    notices = Notice.query.filter_by(is_published=True).order_by(Notice.created_at.desc()).limit(5).all()

    return render_template('faculty/dashboard.html',
        faculty=faculty,
        today_schedule=today_schedule,
        assigned_subjects=assigned_subjects,
        my_assignments=my_assignments,
        my_leaves=my_leaves,
        avg_rating=avg_rating,
        total_feedbacks=total_feedbacks,
        my_materials=my_materials,
        notices=notices
    )


@faculty_bp.route('/profile')
@login_required
def my_profile():
    if current_user.role in (Role.FACULTY, Role.HOD):
        faculty = Faculty.query.filter_by(user_id=current_user.id).first()
        if faculty:
            return redirect(url_for('faculty.profile_view', faculty_id=faculty.id))
    return redirect(url_for('auth.profile'))


@faculty_bp.route('')
@faculty_bp.route('/')
@faculty_bp.route('/list')
@login_required
def index():
    dept_id = request.args.get('dept_id', type=int)
    designation = request.args.get('designation', '')
    status = request.args.get('status', '')
    search = request.args.get('q', '').strip()

    query = Faculty.query
    if dept_id:
        query = query.filter_by(department_id=dept_id)
    if designation:
        query = query.filter_by(designation=designation)
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(
            (Faculty.first_name.ilike(f'%{search}%')) |
            (Faculty.last_name.ilike(f'%{search}%')) |
            (Faculty.faculty_id.ilike(f'%{search}%')) |
            (Faculty.employee_id.ilike(f'%{search}%')) |
            (Faculty.official_email.ilike(f'%{search}%'))
        )

    faculty_list = query.order_by(Faculty.first_name.asc()).all()
    departments = Department.query.filter_by(is_active=True).all()

    # Real Database Metrics
    total_faculty_count = Faculty.query.count()
    active_faculty_count = Faculty.query.filter_by(status='Active').count()
    inactive_faculty_count = Faculty.query.filter_by(status='Inactive').count()
    total_departments_count = Department.query.filter_by(is_active=True).count()
    
    # Distinct Designations from Database
    raw_designations = db.session.query(Faculty.designation).distinct().all()
    designations_list = sorted(list(set([d[0] for d in raw_designations if d and d[0]])))

    return render_template('faculty/list.html',
        faculty_list=faculty_list,
        departments=departments,
        designations_list=designations_list,
        total_faculty_count=total_faculty_count,
        active_faculty_count=active_faculty_count,
        inactive_faculty_count=inactive_faculty_count,
        total_departments_count=total_departments_count,
        selected_dept=dept_id,
        selected_desig=designation,
        selected_status=status,
        search=search
    )


@faculty_bp.route('/my-classes')
@login_required
@faculty_required
def my_classes():
    faculty = Faculty.query.filter_by(user_id=current_user.id).first()
    if not faculty:
        flash('Faculty profile not found.', 'warning')
        return redirect(url_for('faculty.dashboard'))

    # Classes taught from Timetable
    timetable_entries = Timetable.query.filter_by(faculty_id=faculty.id).all()
    division_ids = list(set([t.division_id for t in timetable_entries if t.division_id]))
    divisions = ClassDivision.query.filter(ClassDivision.id.in_(division_ids)).all() if division_ids else []

    return render_template('faculty/my_classes.html', faculty=faculty, divisions=divisions, timetable_entries=timetable_entries)


@faculty_bp.route('/my-subjects')
@login_required
@faculty_required
def my_subjects():
    faculty = Faculty.query.filter_by(user_id=current_user.id).first()
    if not faculty:
        flash('Faculty profile not found.', 'warning')
        return redirect(url_for('faculty.dashboard'))

    subjects = faculty.subjects
    return render_template('faculty/my_subjects.html', faculty=faculty, subjects=subjects)


@faculty_bp.route('/student-performance')
@login_required
@faculty_required
def student_performance():
    faculty = Faculty.query.filter_by(user_id=current_user.id).first()
    if not faculty:
        flash('Faculty profile not found.', 'warning')
        return redirect(url_for('faculty.dashboard'))

    dept_students = Student.query.filter_by(department_id=faculty.department_id, status='Active').all() if faculty.department_id else []
    return render_template('faculty/student_performance.html', faculty=faculty, students=dept_students)


@faculty_bp.route('/documents')
@login_required
def documents():
    doc_form = FacultyDocumentForm()
    if current_user.role == Role.ADMIN:
        docs = FacultyDocument.query.order_by(FacultyDocument.upload_date.desc()).all()
        faculty = None
    else:
        faculty = Faculty.query.filter_by(user_id=current_user.id).first()
        docs = FacultyDocument.query.filter_by(faculty_id=faculty.id).order_by(FacultyDocument.upload_date.desc()).all() if faculty else []

    return render_template('faculty/documents.html', documents=docs, faculty=faculty, doc_form=doc_form)


@faculty_bp.route('/<int:faculty_id>/documents')
@login_required
def faculty_documents(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    # Check permissions
    if current_user.role in (Role.FACULTY, Role.HOD):
        curr_fac = Faculty.query.filter_by(user_id=current_user.id).first()
        if not curr_fac or curr_fac.id != faculty.id:
            flash('Access restricted.', 'danger')
            return redirect(url_for('faculty.dashboard'))
    elif current_user.role != Role.ADMIN:
        flash('Access restricted.', 'danger')
        return redirect(url_for('main.index'))

    docs = FacultyDocument.query.filter_by(faculty_id=faculty.id).order_by(FacultyDocument.upload_date.desc()).all()
    doc_form = FacultyDocumentForm()
    return render_template('faculty/documents.html', documents=docs, faculty=faculty, doc_form=doc_form)


@faculty_bp.route('/id-card')
@login_required
def id_card_view():
    faculty = Faculty.query.filter_by(user_id=current_user.id).first()
    if not faculty:
        flash('Faculty profile not found.', 'warning')
        return redirect(url_for('main.index'))
    return redirect(url_for('faculty.download_id_card', faculty_id=faculty.id))


@faculty_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = FacultyCreateForm()
    form.department_id.choices = [(d.id, f"{d.name} ({d.code})") for d in Department.query.filter_by(is_active=True).all()]

    if form.validate_on_submit():
        try:
            # Auto-generate unique Employee/Faculty ID
            joining_d = getattr(getattr(form, 'joining_date', None), 'data', None) or date.today()
            generated_emp_id = form.employee_id.data.strip() if form.employee_id.data and form.employee_id.data.strip() else (
                form.faculty_id.data.strip() if form.faculty_id.data and form.faculty_id.data.strip() else generate_faculty_employee_id(date_of_joining=joining_d)
            )
            generated_fac_id = form.faculty_id.data.strip() if form.faculty_id.data and form.faculty_id.data.strip() else generated_emp_id

            # 1. Create User
            official_email_clean = form.official_email.data.strip().lower()
            username = form.username.data.strip().lower() if form.username.data and form.username.data.strip() else official_email_clean
            
            mobile_clean = form.mobile.data.strip()
            raw_password = mobile_clean if mobile_clean else (form.temporary_password.data if form.temporary_password.data else 'Campus@123')

            # Check designation for HOD
            designation_str = form.designation.data or 'Assistant Professor'
            is_hod = any(term in str(designation_str).upper() for term in ['HOD', 'HEAD OF DEPARTMENT', 'DEPT HEAD', 'DEPARTMENT HEAD'])
            assigned_role = Role.HOD if is_hod else Role.FACULTY

            user = User(
                username=username,
                email=official_email_clean,
                role=assigned_role,
                first_name=form.first_name.data.strip(),
                last_name=form.last_name.data.strip(),
                phone=mobile_clean or None,
                must_change_password=True,
                is_active=True
            )
            user.set_password(raw_password)
            db.session.add(user)
            db.session.flush()

            photo_filename = None
            if form.profile_photo.data:
                photo_filename = save_profile_photo(form.profile_photo.data, prefix='fac')
                if photo_filename:
                    user.profile_image = photo_filename

            # 2. Create Faculty
            mid_name = form.middle_name.data.strip() if form.middle_name.data else ''
            computed_full_name = f"{form.first_name.data.strip()} {mid_name + ' ' if mid_name else ''}{form.last_name.data.strip()}".strip()

            faculty = Faculty(
                user_id=user.id,
                faculty_id=generated_fac_id,
                employee_id=generated_emp_id,
                first_name=form.first_name.data.strip(),
                middle_name=mid_name or None,
                last_name=form.last_name.data.strip(),
                full_name=computed_full_name,
                dob=form.dob.data,
                gender=form.gender.data,
                blood_group=form.blood_group.data if form.blood_group.data else None,
                personal_email=form.personal_email.data.strip().lower() if form.personal_email.data else None,
                official_email=official_email_clean,
                mobile=mobile_clean,
                alt_mobile=form.alt_mobile.data.strip() if form.alt_mobile.data else None,
                department_id=form.department_id.data,
                designation=designation_str,
                employment_type=form.employment_type.data,
                joining_date=joining_d,
                qualification=form.qualification.data.strip() if form.qualification.data else None,
                specialization=form.specialization.data.strip() if form.specialization.data else None,
                experience_years=form.experience_years.data or 0.0,
                profile_photo=photo_filename,
                status=form.status.data,
                curr_address_line1=form.curr_address_line1.data if form.curr_address_line1.data else None,
                curr_city=form.curr_city.data if form.curr_city.data else None,
                curr_state=form.curr_state.data if form.curr_state.data else None,
                curr_pincode=form.curr_pincode.data if form.curr_pincode.data else None,
                emergency_name=form.emergency_name.data if form.emergency_name.data else None,
                emergency_relation=form.emergency_relation.data if form.emergency_relation.data else None,
                emergency_phone=form.emergency_phone.data if form.emergency_phone.data else None
            )
            db.session.add(faculty)
            db.session.commit()

            flash(
                f"Faculty member {faculty.full_name} registered successfully! "
                f"Auto-generated Employee ID: {faculty.employee_id}. "
                f"Login email: {faculty.official_email}. Initial password is the registered mobile number ({faculty.mobile}). "
                f"The faculty member will be prompted to change password upon first login.",
                "success"
            )
            return redirect(url_for('faculty.profile_view', faculty_id=faculty.id))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating faculty in web route: {str(e)}", exc_info=True)
            flash(f"Faculty creation failed: {str(e)}", "danger")

    return render_template('faculty/create.html', form=form)


@faculty_bp.route('/<int:faculty_id>', endpoint='profile_view')
@faculty_bp.route('/<int:faculty_id>', endpoint='view')
@login_required
def profile_view(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    doc_form = FacultyDocumentForm()
    
    schedule = Timetable.query.filter_by(faculty_id=faculty.id).order_by(Timetable.day_of_week.asc(), Timetable.start_time.asc()).all()
    feedbacks = Feedback.query.filter_by(faculty_id=faculty.id).order_by(Feedback.created_at.desc()).limit(10).all()
    leaves = LeaveRequest.query.filter_by(faculty_id=faculty.id).order_by(LeaveRequest.created_at.desc()).limit(5).all()
    documents = FacultyDocument.query.filter_by(faculty_id=faculty.id).order_by(FacultyDocument.upload_date.desc()).all()

    return render_template('faculty/profile.html',
        faculty=faculty,
        schedule=schedule,
        feedbacks=feedbacks,
        leaves=leaves,
        documents=documents,
        doc_form=doc_form
    )


@faculty_bp.route('/edit/<int:faculty_id>', methods=['GET', 'POST'])
@faculty_bp.route('/<int:faculty_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    form = FacultyEditForm(obj=faculty)
    form.department_id.choices = [(d.id, f"{d.name} ({d.code})") for d in Department.query.filter_by(is_active=True).all()]

    if request.method == 'GET':
        form.department_id.data = faculty.department_id
        if faculty.dob:
            form.dob.data = faculty.dob

    if form.validate_on_submit():
        faculty.first_name = form.first_name.data.strip()
        faculty.middle_name = form.middle_name.data.strip() if form.middle_name.data else None
        faculty.last_name = form.last_name.data.strip()
        faculty.full_name = f"{form.first_name.data.strip()} {form.middle_name.data.strip() + ' ' if form.middle_name.data else ''}{form.last_name.data.strip()}".strip()
        faculty.dob = form.dob.data
        faculty.gender = form.gender.data
        faculty.blood_group = form.blood_group.data
        faculty.personal_email = form.personal_email.data.strip().lower() if form.personal_email.data else None
        faculty.mobile = form.mobile.data.strip()
        faculty.alt_mobile = form.alt_mobile.data.strip() if form.alt_mobile.data else None
        faculty.department_id = form.department_id.data
        faculty.designation = form.designation.data
        faculty.employment_type = form.employment_type.data
        faculty.qualification = form.qualification.data.strip() if form.qualification.data else None
        faculty.specialization = form.specialization.data.strip() if form.specialization.data else None
        faculty.experience_years = form.experience_years.data or 0.0
        faculty.status = form.status.data

        if form.profile_photo.data:
            filename = save_profile_photo(form.profile_photo.data, prefix='fac')
            if filename:
                faculty.profile_photo = filename
                if faculty.user:
                    faculty.user.profile_image = filename

        # Direct fields on faculty model
        faculty.curr_address_line1 = form.curr_address_line1.data or ''
        faculty.curr_address_line2 = form.curr_address_line2.data or ''
        faculty.curr_city = form.curr_city.data or ''
        faculty.curr_district = form.curr_district.data or ''
        faculty.curr_state = form.curr_state.data or ''
        faculty.curr_pincode = form.curr_pincode.data or ''

        faculty.perm_address_line1 = form.perm_address_line1.data or ''
        faculty.perm_address_line2 = form.perm_address_line2.data or ''
        faculty.perm_city = form.perm_city.data or ''
        faculty.perm_district = form.perm_district.data or ''
        faculty.perm_state = form.perm_state.data or ''
        faculty.perm_pincode = form.perm_pincode.data or ''

        faculty.emergency_name = form.emergency_name.data or ''
        faculty.emergency_relation = form.emergency_relation.data or ''
        faculty.emergency_phone = form.emergency_phone.data or ''
        faculty.emergency_alt_phone = form.emergency_alt_phone.data or ''

        # Also sync linked user
        if faculty.user:
            faculty.user.first_name = faculty.first_name
            faculty.user.last_name = faculty.last_name
            faculty.user.phone = faculty.mobile
            faculty.user.is_active = (faculty.status == 'Active')

        db.session.commit()
        flash(f'Faculty profile for {faculty.full_name} updated successfully.', 'success')
        return redirect(url_for('faculty.profile_view', faculty_id=faculty.id))

    return render_template('faculty/edit.html', form=form, faculty=faculty)


@faculty_bp.route('/<int:faculty_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_status(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    faculty.status = 'Inactive' if faculty.status == 'Active' else 'Active'
    if faculty.user:
        faculty.user.is_active = (faculty.status == 'Active')
    db.session.commit()
    flash(f'Faculty member {faculty.full_name} status updated to {faculty.status}.', 'success')
    return redirect(request.referrer or url_for('faculty.index'))


@faculty_bp.route('/<int:faculty_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    name = faculty.full_name
    user = faculty.user
    db.session.delete(faculty)
    if user:
        db.session.delete(user)
    db.session.commit()
    flash(f'Faculty record for {name} has been deleted.', 'info')
    return redirect(url_for('faculty.index'))


@faculty_bp.route('/<int:faculty_id>/id-card/download')
@login_required
def download_id_card(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    college_info = {
        'name': current_app.config.get('COLLEGE_NAME', 'Sharad Institute of Technology'),
        'short_name': current_app.config.get('COLLEGE_SHORT_NAME', 'SITCOE'),
        'address': current_app.config.get('COLLEGE_ADDRESS', 'Yadrav (Ichalkaranji), Maharashtra - 416145'),
        'phone': current_app.config.get('COLLEGE_PHONE', '+91 2322 253000'),
        'email': current_app.config.get('COLLEGE_EMAIL', 'contact@sitcoe.org.in')
    }
    pdf_buffer = generate_faculty_id_card_pdf(faculty, college_info=college_info)
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"Faculty_ID_{faculty.faculty_id.replace('/', '_')}.pdf"
    )


@faculty_bp.route('/<int:faculty_id>/upload-document', methods=['POST'])
@faculty_bp.route('/<int:faculty_id>/documents/upload', methods=['POST'])
@login_required
def upload_document(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    # Check permissions
    if current_user.role in (Role.FACULTY, Role.HOD):
        curr_fac = Faculty.query.filter_by(user_id=current_user.id).first()
        if not curr_fac or curr_fac.id != faculty.id:
            flash('Unauthorized action.', 'danger')
            return redirect(url_for('faculty.dashboard'))
    elif current_user.role != Role.ADMIN:
        flash('Access restricted.', 'danger')
        return redirect(url_for('main.index'))

    form = FacultyDocumentForm()
    if form.validate_on_submit():
        filename = save_uploaded_file(form.document_file.data, subfolder='documents', prefix='fac_doc')
        if filename:
            doc = FacultyDocument(
                faculty_id=faculty.id,
                doc_type=form.doc_type.data,
                title=form.title.data.strip(),
                file_path=filename,
                upload_date=datetime.utcnow(),
                verification_status='Verified' if current_user.role == Role.ADMIN else 'Pending'
            )
            db.session.add(doc)
            db.session.commit()
            flash(f'Document "{doc.title}" uploaded successfully.', 'success')
        else:
            flash('Failed to save document. Please ensure the file is in PDF, DOC, or Image format.', 'danger')
    else:
        for field, errors in form.errors.items():
            for err in errors:
                flash(f'Upload error ({field}): {err}', 'danger')

    redirect_target = request.referrer or url_for('faculty.faculty_documents', faculty_id=faculty.id)
    return redirect(redirect_target)


@faculty_bp.route('/documents/<int:doc_id>/download')
@login_required
def download_document(doc_id):
    doc = FacultyDocument.query.get_or_404(doc_id)
    # Security: check authorization
    if current_user.role in (Role.FACULTY, Role.HOD):
        curr_fac = Faculty.query.filter_by(user_id=current_user.id).first()
        if not curr_fac or curr_fac.id != doc.faculty_id:
            flash('Unauthorized access to document.', 'danger')
            return redirect(url_for('faculty.dashboard'))
    elif current_user.role != Role.ADMIN:
        flash('Access restricted.', 'danger')
        return redirect(url_for('main.index'))

    import os
    clean_path = str(doc.file_path).replace('\\', '/').lstrip('/')
    if clean_path.startswith('static/'):
        clean_path = clean_path[7:]
    full_path = os.path.join(current_app.root_path, 'static', clean_path)

    if not os.path.isfile(full_path):
        flash('Document file not found on the server.', 'danger')
        return redirect(request.referrer or url_for('faculty.documents'))

    ext = doc.file_path.rsplit('.', 1)[-1].lower() if '.' in doc.file_path else 'pdf'
    from werkzeug.utils import secure_filename
    safe_title = secure_filename(doc.title) or f"Document_{doc.id}"
    return send_file(
        full_path,
        as_attachment=True,
        download_name=f"{safe_title}.{ext}"
    )


@faculty_bp.route('/documents/<int:doc_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_document(doc_id):
    doc = FacultyDocument.query.get_or_404(doc_id)
    fac_id = doc.faculty_id
    doc_title = doc.title
    
    from app.utils.uploads import delete_uploaded_file
    delete_uploaded_file(doc.file_path)
    
    db.session.delete(doc)
    db.session.commit()
    flash(f'Document "{doc_title}" deleted successfully.', 'info')
    return redirect(request.referrer or url_for('faculty.faculty_documents', faculty_id=fac_id))

