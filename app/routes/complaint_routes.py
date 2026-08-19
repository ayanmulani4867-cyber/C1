import uuid
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.utils.decorators import role_required
from app.utils.uploads import save_uploaded_file
from app.models.user import Role
from app.models.student import Student
from app.models.complaint import Complaint
from app.forms.complaint_forms import ComplaintSubmitForm, ComplaintReviewForm

complaint_bp = Blueprint('complaint', __name__)


@complaint_bp.route('/')
@login_required
def index():
    status_filter = request.args.get('status', '').strip()
    category_filter = request.args.get('category', '').strip()

    if current_user.role == Role.STUDENT:
        std = Student.query.filter_by(user_id=current_user.id).first()
        if not std:
            flash('Student profile not linked to user account.', 'warning')
            return redirect(url_for('auth.profile'))
        
        query = Complaint.query.filter_by(student_id=std.id)
        if status_filter:
            query = query.filter_by(status=status_filter)
        complaints = query.order_by(Complaint.created_at.desc()).all()
        return render_template('complaints/student_list.html', complaints=complaints, status_filter=status_filter)

    # Admin / HOD / Faculty view
    query = Complaint.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)

    complaints = query.order_by(Complaint.created_at.desc()).all()
    pending_count = Complaint.query.filter(Complaint.status.in_(['Submitted', 'Assigned', 'In Progress'])).count()
    resolved_count = Complaint.query.filter_by(status='Resolved').count()

    return render_template('complaints/admin_list.html',
        complaints=complaints,
        status_filter=status_filter,
        category_filter=category_filter,
        pending_count=pending_count,
        resolved_count=resolved_count
    )


@complaint_bp.route('/submit', methods=['GET', 'POST'])
@login_required
@role_required(Role.STUDENT)
def submit():
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash('Only registered students can file grievance tickets.', 'danger')
        return redirect(url_for('main.index'))

    form = ComplaintSubmitForm()
    if request.method == 'POST' and not form.validate():
        category = request.form.get('category', 'General')
        title = request.form.get('subject') or request.form.get('title')
        description = request.form.get('description')
        if title and description:
            ticket_number = f"GRV-{datetime.utcnow().strftime('%y%m')}-{str(uuid.uuid4().hex[:6]).upper()}"
            complaint = Complaint(
                ticket_number=ticket_number,
                student_id=student.id,
                category=category,
                title=title.strip(),
                description=description.strip(),
                location=request.form.get('location'),
                priority=request.form.get('priority', 'Medium'),
                status='Submitted'
            )
            db.session.add(complaint)
            db.session.commit()
            flash(f'Grievance ticket #{ticket_number} submitted successfully.', 'success')
            return redirect(url_for('complaint.detail', complaint_id=complaint.id))

    if form.validate_on_submit():
        attachment_filename = None
        if form.attachment.data:
            attachment_filename = save_uploaded_file(form.attachment.data, subfolder='documents')

        ticket_number = f"GRV-{datetime.utcnow().strftime('%y%m')}-{str(uuid.uuid4().hex[:6]).upper()}"

        complaint = Complaint(
            ticket_number=ticket_number,
            student_id=student.id,
            category=form.category.data,
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            location=form.location.data.strip() if form.location.data else None,
            priority=form.priority.data,
            attachment_path=attachment_filename,
            status='Submitted'
        )
        db.session.add(complaint)
        db.session.commit()

        flash(f'Grievance ticket #{ticket_number} submitted successfully. Campus authorities will review it shortly.', 'success')
        return redirect(url_for('complaint.detail', complaint_id=complaint.id))

    return render_template('complaints/submit.html', form=form)


@complaint_bp.route('/<int:complaint_id>')
@login_required
def detail(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)

    # Permission check for students
    if current_user.role == Role.STUDENT:
        std = Student.query.filter_by(user_id=current_user.id).first()
        if not std or std.id != complaint.student_id:
            flash('Unauthorized access to this grievance record.', 'danger')
            return redirect(url_for('complaint.index'))

    form = ComplaintReviewForm(obj=complaint)
    return render_template('complaints/detail.html', complaint=complaint, form=form)


@complaint_bp.route('/<int:complaint_id>/review', methods=['POST'])
@complaint_bp.route('/<int:complaint_id>/resolve', methods=['POST'])
@login_required
@role_required(Role.ADMIN, Role.HOD, Role.FACULTY)
def review(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    form = ComplaintReviewForm()

    if request.path.endswith('/resolve') or (request.method == 'POST' and not form.validate()):
        status = request.form.get('status', 'Resolved')
        complaint.status = status
        complaint.resolution_notes = request.form.get('resolution_notes') or request.form.get('remarks') or 'Resolved by admin.'
        complaint.assigned_to_id = current_user.id
        if status in ('Resolved', 'Closed'):
            complaint.resolved_at = datetime.utcnow()
        db.session.commit()
        flash(f'Ticket #{complaint.ticket_number} marked as {status}.', 'success')
        return redirect(url_for('complaint.detail', complaint_id=complaint.id))

    if form.validate_on_submit():
        complaint.status = form.status.data
        complaint.priority = form.priority.data
        complaint.resolution_notes = form.resolution_notes.data.strip()
        complaint.assigned_to_id = current_user.id
        
        if form.status.data in ('Resolved', 'Closed'):
            complaint.resolved_at = datetime.utcnow()

        db.session.commit()
        flash(f'Ticket #{complaint.ticket_number} updated to {complaint.status}.', 'success')
        return redirect(url_for('complaint.detail', complaint_id=complaint.id))

    flash('Please fill in valid resolution details.', 'danger')
    return redirect(url_for('complaint.detail', complaint_id=complaint.id))
