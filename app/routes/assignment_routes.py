from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.extensions import db
from app.utils.decorators import role_required
from app.utils.uploads import save_uploaded_file
from app.models.user import Role
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.subject import Subject
from app.models.academic import ClassDivision
from app.models.assignment import Assignment, AssignmentSubmission, StudyMaterial
from app.forms.assignment_forms import AssignmentForm, AssignmentSubmissionForm, GradeSubmissionForm, StudyMaterialForm
from app.utils.helpers import create_notification

assignment_bp = Blueprint('assignment', __name__)


@assignment_bp.route('/')
@login_required
def index():
    division_id = request.args.get('division_id', type=int)
    subject_id = request.args.get('subject_id', type=int)

    if current_user.role == Role.STUDENT:
        std = Student.query.filter_by(user_id=current_user.id).first()
        if std:
            division_id = std.class_division_id

    query = Assignment.query
    if division_id:
        query = query.filter_by(class_division_id=division_id)
    if subject_id:
        query = query.filter_by(subject_id=subject_id)

    assignments = query.order_by(Assignment.due_date.desc()).all()
    materials = StudyMaterial.query.order_by(StudyMaterial.upload_date.desc()).limit(8).all()
    divisions = ClassDivision.query.all()
    subjects = Subject.query.all()

    # Track student submission status
    student_submissions = {}
    if current_user.role == Role.STUDENT:
        std = Student.query.filter_by(user_id=current_user.id).first()
        if std:
            subs = AssignmentSubmission.query.filter_by(student_id=std.id).all()
            student_submissions = {s.assignment_id: s for s in subs}

    return render_template('assignments/index.html',
        assignments=assignments,
        materials=materials,
        divisions=divisions,
        subjects=subjects,
        student_submissions=student_submissions,
        selected_div=division_id,
        selected_subj=subject_id
    )


@assignment_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def create():
    form = AssignmentForm()
    form.class_division_id.choices = [(d.id, f"{d.name} ({d.course.code} - Sem {d.semester.number})") for d in ClassDivision.query.all()]
    form.subject_id.choices = [(s.id, f"{s.name} ({s.code})") for s in Subject.query.all()]

    if request.method == 'POST' and (form.validate_on_submit() or request.form.get('title')):
        title = (form.title.data or request.form.get('title', '')).strip()
        class_div_id = form.class_division_id.data or request.form.get('class_division_id', type=int)
        subject_id = form.subject_id.data or request.form.get('subject_id', type=int)
        due_date = form.due_date.data

        if not due_date:
            due_date_str = request.form.get('due_date', '').strip()
            if due_date_str:
                for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
                    try:
                        due_date = datetime.strptime(due_date_str, fmt)
                        break
                    except ValueError:
                        continue
            if not due_date:
                due_date = datetime.utcnow() + timedelta(days=7)

        attachment_filename = None
        upload_obj = form.attachment_file.data or request.files.get('attachment_file') or request.files.get('file')
        if upload_obj and hasattr(upload_obj, 'filename') and upload_obj.filename:
            attachment_filename = save_uploaded_file(upload_obj, subfolder='assignments')

        faculty = Faculty.query.filter_by(user_id=current_user.id).first()
        faculty_id = faculty.id if faculty else (Faculty.query.first().id if Faculty.query.first() else None)

        assignment = Assignment(
            title=title,
            description=(form.description.data or request.form.get('description', '')).strip() or None,
            class_division_id=class_div_id,
            subject_id=subject_id,
            faculty_id=faculty_id,
            due_date=due_date,
            max_marks=float(form.max_marks.data or request.form.get('max_marks', 20.0)),
            attachment_path=attachment_filename
        )
        db.session.add(assignment)
        db.session.commit()

        # Notify enrolled students
        try:
            if assignment.class_division_id:
                students = Student.query.filter_by(class_division_id=assignment.class_division_id).all()
                for s in students:
                    if s.user_id:
                        create_notification(
                            user_id=s.user_id,
                            title=f"New Assignment: {assignment.title}",
                            message=f"Due on {assignment.due_date.strftime('%b %d, %Y')}. Max marks: {assignment.max_marks}",
                            link=f"/assignments/{assignment.id}",
                            notification_type='Assignment'
                        )
        except Exception:
            pass

        flash(f'Assignment "{assignment.title}" published successfully.', 'success')
        return redirect(url_for('assignment.detail', assignment_id=assignment.id))

    return render_template('assignments/create.html', form=form)


@assignment_bp.route('/<int:assignment_id>', methods=['GET', 'POST'])
@assignment_bp.route('/<int:assignment_id>/submit', methods=['GET', 'POST'])
@login_required
def detail(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    submission_form = AssignmentSubmissionForm()
    my_submission = None

    if current_user.role == Role.STUDENT:
        std = Student.query.filter_by(user_id=current_user.id).first()
        if std:
            my_submission = AssignmentSubmission.query.filter_by(assignment_id=assignment.id, student_id=std.id).first()

            if request.method == 'POST':
                sub_text = (submission_form.submission_text.data or request.form.get('submission_text') or '').strip()
                sub_file = None
                upload_obj = submission_form.submission_file.data or request.files.get('submission_file') or request.files.get('file')
                if upload_obj and hasattr(upload_obj, 'filename') and upload_obj.filename:
                    sub_file = save_uploaded_file(upload_obj, subfolder='assignments')

                if sub_text or sub_file or my_submission:
                    if not my_submission:
                        my_submission = AssignmentSubmission(
                            assignment_id=assignment.id,
                            student_id=std.id,
                            submission_text=sub_text,
                            submission_file=sub_file,
                            submitted_at=datetime.utcnow(),
                            status='Submitted'
                        )
                        db.session.add(my_submission)
                    else:
                        if sub_text:
                            my_submission.submission_text = sub_text
                        if sub_file:
                            my_submission.submission_file = sub_file
                        my_submission.submitted_at = datetime.utcnow()
                        my_submission.status = 'Submitted'

                    db.session.commit()

                    try:
                        if assignment.faculty and assignment.faculty.user_id:
                            create_notification(
                                user_id=assignment.faculty.user_id,
                                title=f"Submission: {std.full_name}",
                                message=f"{std.full_name} submitted assignment '{assignment.title}'",
                                link=f"/assignments/{assignment.id}",
                                notification_type='Assignment'
                            )
                    except Exception:
                        pass

                    flash('Your assignment submission has been saved.', 'success')
                    return redirect(url_for('assignment.detail', assignment_id=assignment.id))

    submissions = AssignmentSubmission.query.filter_by(assignment_id=assignment.id).all() if current_user.role in [Role.ADMIN, Role.FACULTY] else []

    return render_template('assignments/detail.html',
        assignment=assignment,
        submission_form=submission_form,
        my_submission=my_submission,
        submissions=submissions
    )


@assignment_bp.route('/submission/<int:submission_id>/grade', methods=['POST'])
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def grade_submission(submission_id):
    submission = AssignmentSubmission.query.get_or_404(submission_id)
    marks = request.form.get('marks_obtained', type=float)
    feedback = request.form.get('feedback', '')

    submission.marks_obtained = marks
    submission.feedback = feedback
    submission.status = 'Graded'
    submission.evaluated_at = datetime.utcnow()
    db.session.commit()

    flash(f'Submission graded: {marks} / {submission.assignment.max_marks}', 'success')
    return redirect(url_for('assignment.detail', assignment_id=submission.assignment_id))


# --- STUDY MATERIALS ---
@assignment_bp.route('/materials')
@login_required
def materials():
    return redirect(url_for('assignment.index'))


@assignment_bp.route('/materials/upload', methods=['GET', 'POST'])
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def material_upload():
    form = StudyMaterialForm()
    form.class_division_id.choices = [(d.id, f"{d.name} ({d.course.code})") for d in ClassDivision.query.all()]
    form.subject_id.choices = [(s.id, f"{s.name} ({s.code})") for s in Subject.query.all()]

    if form.validate_on_submit():
        filename = save_uploaded_file(form.material_file.data, subfolder='materials')
        if filename:
            faculty = Faculty.query.filter_by(user_id=current_user.id).first()
            faculty_id = faculty.id if faculty else (Faculty.query.first().id if Faculty.query.first() else None)

            mat = StudyMaterial(
                title=form.title.data.strip(),
                description=form.description.data.strip() if form.description.data else None,
                class_division_id=form.class_division_id.data,
                subject_id=form.subject_id.data,
                faculty_id=faculty_id,
                file_path=filename
            )
            db.session.add(mat)
            db.session.commit()
            flash(f'Study material "{mat.title}" uploaded successfully.', 'success')
            return redirect(url_for('assignment.index'))

    return render_template('assignments/material_upload.html', form=form)


@assignment_bp.route('/<int:assignment_id>/delete', methods=['POST'])
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def delete(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    title = assignment.title
    db.session.delete(assignment)
    db.session.commit()
    flash(f'Assignment "{title}" deleted.', 'info')
    return redirect(url_for('assignment.index'))


@assignment_bp.route('/materials/<int:material_id>/delete', methods=['POST'])
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def material_delete(material_id):
    mat = StudyMaterial.query.get_or_404(material_id)
    title = mat.title
    db.session.delete(mat)
    db.session.commit()
    flash(f'Study material "{title}" deleted.', 'info')
    return redirect(url_for('assignment.index'))
