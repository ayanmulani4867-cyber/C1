from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app.extensions import db
from app.utils.decorators import role_required, admin_required
from app.utils.uploads import save_uploaded_file
from app.models.user import Role
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.leave import LeaveApplication
from app.forms.leave_forms import LeaveApplyForm, LeaveReviewForm

leave_bp = Blueprint('leave', __name__)


@leave_bp.route('/')
@login_required
def index():
    if current_user.role == Role.STUDENT:
        std = Student.query.filter_by(user_id=current_user.id).first()
        leaves = LeaveApplication.query.filter_by(student_id=std.id).order_by(LeaveApplication.created_at.desc()).all() if std else []
        return render_template('leaves/student_leaves.html', leaves=leaves)

    elif current_user.role == Role.FACULTY:
        fac = Faculty.query.filter_by(user_id=current_user.id).first()
        my_leaves = LeaveApplication.query.filter_by(faculty_id=fac.id).order_by(LeaveApplication.created_at.desc()).all() if fac else []
        
        # If HOD, also see department student leaves
        dept_student_leaves = []
        if fac and getattr(fac, 'is_hod', False):
            dept_student_leaves = LeaveApplication.query.join(Student).filter(
                Student.department_id == fac.department_id,
                LeaveApplication.status == 'Pending'
            ).all()

        return render_template('leaves/faculty_leaves.html', my_leaves=my_leaves, dept_student_leaves=dept_student_leaves, is_hod=getattr(fac, 'is_hod', False))

    # Admin view
    pending_leaves = LeaveApplication.query.filter_by(status='Pending').order_by(LeaveApplication.created_at.desc()).all()
    all_leaves = LeaveApplication.query.order_by(LeaveApplication.created_at.desc()).limit(30).all()
    return render_template('leaves/admin_leaves.html', pending_leaves=pending_leaves, all_leaves=all_leaves)


@leave_bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    form = LeaveApplyForm()
    if request.method == 'POST' and not form.validate():
        # Direct form fallback
        try:
            leave_type = request.form.get('leave_type', 'Casual Leave')
            start_str = request.form.get('start_date')
            end_str = request.form.get('end_date')
            reason = request.form.get('reason', '')
            if start_str and end_str and reason:
                from datetime import date
                start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
                student_id = None
                faculty_id = None
                if current_user.role == Role.STUDENT:
                    std = Student.query.filter_by(user_id=current_user.id).first()
                    if std: student_id = std.id
                elif current_user.role == Role.FACULTY:
                    fac = Faculty.query.filter_by(user_id=current_user.id).first()
                    if fac: faculty_id = fac.id

                days = max(1, (end_date - start_date).days + 1)
                leave_app = LeaveApplication(
                    user_id=current_user.id,
                    student_id=student_id,
                    faculty_id=faculty_id,
                    leave_type=leave_type,
                    start_date=start_date,
                    end_date=end_date,
                    total_days=days,
                    reason=reason.strip(),
                    status='Pending'
                )
                db.session.add(leave_app)
                db.session.commit()
                flash('Your leave application has been submitted for review.', 'success')
                return redirect(url_for('leave.index'))
        except Exception:
            pass

    if form.validate_on_submit():
        if form.end_date.data < form.start_date.data:
            flash('End date cannot be earlier than start date.', 'danger')
            return render_template('leaves/apply.html', form=form)

        doc_filename = None
        if form.document_file.data:
            doc_filename = save_uploaded_file(form.document_file.data, subfolder='documents')

        student_id = None
        faculty_id = None

        if current_user.role == Role.STUDENT:
            std = Student.query.filter_by(user_id=current_user.id).first()
            if std:
                student_id = std.id
        elif current_user.role == Role.FACULTY:
            fac = Faculty.query.filter_by(user_id=current_user.id).first()
            if fac:
                faculty_id = fac.id

        days = max(1, (form.end_date.data - form.start_date.data).days + 1)
        leave_app = LeaveApplication(
            user_id=current_user.id,
            student_id=student_id,
            faculty_id=faculty_id,
            leave_type=form.leave_type.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            total_days=days,
            reason=form.reason.data.strip(),
            document_file=doc_filename,
            status='Pending'
        )
        db.session.add(leave_app)
        db.session.commit()
        flash('Your leave application has been submitted for administrative review.', 'success')
        return redirect(url_for('leave.index'))

    return render_template('leaves/apply.html', form=form)


@leave_bp.route('/<int:leave_id>/review', methods=['GET', 'POST'])
@leave_bp.route('/<int:leave_id>/approve', methods=['POST'])
@leave_bp.route('/<int:leave_id>/reject', methods=['POST'])
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def review(leave_id):
    leave_app = LeaveApplication.query.get_or_404(leave_id)
    form = LeaveReviewForm()

    if request.path.endswith('/approve') or (request.method == 'POST' and request.form.get('action') == 'approve'):
        leave_app.status = 'Approved'
        leave_app.review_comment = request.form.get('remarks') or request.form.get('review_comment') or 'Approved'
        leave_app.reviewed_by_id = current_user.id
        leave_app.reviewed_at = datetime.utcnow()
        db.session.commit()
        flash(f'Leave application #{leave_app.id} approved.', 'success')
        return redirect(url_for('leave.index'))

    if request.path.endswith('/reject') or (request.method == 'POST' and request.form.get('action') == 'reject'):
        leave_app.status = 'Rejected'
        leave_app.review_comment = request.form.get('remarks') or request.form.get('review_comment') or 'Rejected'
        leave_app.reviewed_by_id = current_user.id
        leave_app.reviewed_at = datetime.utcnow()
        db.session.commit()
        flash(f'Leave application #{leave_app.id} rejected.', 'info')
        return redirect(url_for('leave.index'))

    if form.validate_on_submit():
        leave_app.status = form.status.data
        leave_app.review_comment = form.review_comment.data.strip() if form.review_comment.data else None
        leave_app.reviewed_by_id = current_user.id
        leave_app.reviewed_at = datetime.utcnow()
        db.session.commit()

        flash(f'Leave application #{leave_app.id} has been marked as {leave_app.status}.', 'success')
        return redirect(url_for('leave.index'))

    return render_template('leaves/review.html', form=form, leave_app=leave_app)
