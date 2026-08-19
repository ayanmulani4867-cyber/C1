import io
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from datetime import datetime
from app.extensions import db
from app.utils.decorators import role_required, student_required, admin_required
from app.utils.helpers import generate_certificate_code
from app.utils.pdf import generate_certificate_pdf
from app.models.user import Role
from app.models.student import Student
from app.models.certificate import CertificateRequest
from app.forms.certificate_forms import CertificateRequestForm, CertificateReviewForm

certificate_bp = Blueprint('certificate', __name__)


@certificate_bp.route('/')
@login_required
def index():
    if current_user.role == Role.STUDENT:
        std = Student.query.filter_by(user_id=current_user.id).first()
        requests = CertificateRequest.query.filter_by(student_id=std.id).order_by(CertificateRequest.created_at.desc()).all() if std else []
        return render_template('certificates/student_certificates.html', requests=requests)

    # Admin view
    pending_requests = CertificateRequest.query.filter_by(status='Pending').order_by(CertificateRequest.created_at.desc()).all()
    all_requests = CertificateRequest.query.order_by(CertificateRequest.created_at.desc()).limit(30).all()
    return render_template('certificates/admin_certificates.html', pending_requests=pending_requests, all_requests=all_requests)


@certificate_bp.route('/request', methods=['GET', 'POST'])
@certificate_bp.route('/request-certificate', methods=['GET', 'POST'], endpoint='request_certificate')
@login_required
@student_required
def request_cert():
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash('Student record not linked.', 'warning')
        return redirect(url_for('student.dashboard'))

    form = CertificateRequestForm()
    if request.method == 'POST' and not form.validate():
        # Fallback to direct form parsing
        c_type = request.form.get('certificate_type')
        purpose = request.form.get('purpose')
        if c_type and purpose:
            cert_req = CertificateRequest(
                student_id=student.id,
                certificate_type=c_type,
                purpose=purpose.strip(),
                status='Pending'
            )
            db.session.add(cert_req)
            db.session.commit()
            flash('Certificate request submitted.', 'success')
            return redirect(url_for('certificate.index'))

    if form.validate_on_submit():
        cert_req = CertificateRequest(
            student_id=student.id,
            certificate_type=form.certificate_type.data,
            purpose=form.purpose.data.strip(),
            status='Pending'
        )
        db.session.add(cert_req)
        db.session.commit()
        flash('Certificate request submitted. The registrar office will review and issue your certificate.', 'success')
        return redirect(url_for('certificate.index'))

    return render_template('certificates/request_form.html', form=form)


@certificate_bp.route('/<int:request_id>/review', methods=['GET', 'POST'])
@certificate_bp.route('/<int:request_id>/status', methods=['POST'])
@login_required
@admin_required
def review(request_id):
    cert_req = CertificateRequest.query.get_or_404(request_id)
    form = CertificateReviewForm()

    if request.path.endswith('/status') or (request.method == 'POST' and not form.validate()):
        status = request.form.get('status', 'Approved')
        cert_req.status = status
        cert_req.reviewed_by_id = current_user.id
        cert_req.reviewed_at = datetime.utcnow()
        if status == 'Approved':
            cert_req.issued_date = datetime.utcnow()
            cert_req.certificate_number = generate_certificate_code(cert_req.certificate_type)
        else:
            cert_req.rejection_reason = request.form.get('remarks') or request.form.get('rejection_reason')
        db.session.commit()
        flash(f'Certificate request #{cert_req.id} processed: {cert_req.status}.', 'success')
        return redirect(url_for('certificate.index'))

    if form.validate_on_submit():
        cert_req.status = form.status.data
        cert_req.reviewed_by_id = current_user.id
        cert_req.reviewed_at = datetime.utcnow()

        if form.status.data == 'Approved':
            cert_req.issued_date = datetime.utcnow()
            cert_req.certificate_number = generate_certificate_code(cert_req.certificate_type)
        else:
            cert_req.rejection_reason = form.rejection_reason.data.strip() if form.rejection_reason.data else None

        db.session.commit()
        flash(f'Certificate request #{cert_req.id} processed: {cert_req.status}.', 'success')
        return redirect(url_for('certificate.index'))

    return render_template('certificates/review.html', form=form, cert_req=cert_req)


@certificate_bp.route('/<int:request_id>/download')
@certificate_bp.route('/<int:cert_id>/download-pdf', endpoint='download_pdf')
@login_required
def download(request_id=None, cert_id=None):
    req_id = request_id or cert_id
    cert_req = CertificateRequest.query.get_or_404(req_id)
    if cert_req.status != 'Approved':
        flash('Certificate has not been approved or issued yet.', 'warning')
        return redirect(url_for('certificate.index'))

    college_info = {
        'name': current_app.config.get('COLLEGE_NAME', 'Apex Institute of Technology & Science'),
        'address': current_app.config.get('COLLEGE_ADDRESS', 'Knowledge City, Tech Campus'),
        'phone': current_app.config.get('COLLEGE_PHONE', '+91 98765 43210'),
        'email': current_app.config.get('COLLEGE_EMAIL', 'contact@apextech.edu')
    }

    pdf_buffer = generate_certificate_pdf(cert_req, college_info=college_info)
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"Certificate_{cert_req.certificate_type.replace(' ', '_')}_{cert_req.certificate_number or cert_req.id}.pdf"
    )
