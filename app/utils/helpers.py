import random
import string
from datetime import datetime
from flask import flash, request
from flask_login import current_user
from app.extensions import db
from app.models.notification import Notification
from app.models.audit_log import AuditLog


def generate_random_password(length=10):
    """Generates a secure random initial password"""
    chars = string.ascii_letters + string.digits + "@#$%"
    return ''.join(random.choice(chars) for _ in range(length))


def generate_receipt_number():
    """Generates a unique receipt number like REC-YYYYMMDD-XXXX"""
    now_str = datetime.utcnow().strftime('%Y%m%d')
    rand_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"REC-{now_str}-{rand_part}"


def generate_transaction_id():
    """Generates a unique transaction reference ID"""
    now_str = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    rand_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"TXN-{now_str}-{rand_part}"


def generate_certificate_code(cert_type=None, *args, **kwargs):
    """Generates a unique verification code for certificates"""
    now_str = datetime.utcnow().strftime('%Y%m')
    rand_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    prefix = "CERT"
    if cert_type:
        prefix = ''.join(e[0] for e in cert_type.split() if e.isalnum()).upper() or "CERT"
    return f"{prefix}-{now_str}-{rand_part}"


def create_notification(user_id, title, message, link=None, notification_type='General'):
    """Dispatches a persistent notification to a user"""
    try:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            link=link,
            notification_type=notification_type
        )
        db.session.add(notif)
        db.session.commit()
    except Exception as e:
        db.session.rollback()


def log_audit(action, module, record_id=None, details=None):
    """Helper to record an audit log event with client IP"""
    ip = request.remote_addr if request else None
    user = current_user if current_user.is_authenticated else None
    AuditLog.log(action=action, module=module, user=user, record_id=record_id, details=details, ip_address=ip)


def flash_form_errors(form):
    """Flash all validation errors from a WTForms instance"""
    for field, errors in form.errors.items():
        label = getattr(form, field).label.text if hasattr(form, field) and hasattr(getattr(form, field), 'label') else field
        for error in errors:
            flash(f"Error in {label}: {error}", 'danger')


def calculate_student_attendance_summary(student_id, semester_id=None):
    """
    Calculates real total attendance percentage for a student.
    Returns: (total_sessions, attended_sessions, percentage)
    """
    from app.models.attendance import AttendanceRecord, AttendanceSession
    
    query = AttendanceRecord.query.filter_by(student_id=student_id)
    if semester_id:
        query = query.join(AttendanceSession).filter(AttendanceSession.class_division.has(semester_id=semester_id))
        
    records = query.all()
    total = len(records)
    if total == 0:
        return 0, 0, 0.0
        
    attended = sum(1 for r in records if r.status == 'Present')
    pct = round((attended / total) * 100, 2)
    return total, attended, pct


def calculate_student_cgpa(student_id):
    """
    Calculates real CGPA based on published exam results and subject credits.
    """
    from app.models.result import ExamResult
    from app.models.subject import Subject
    
    results = ExamResult.query.filter_by(student_id=student_id, status='Published_By_Admin').all()
    if not results:
        return 0.0
        
    total_credit_points = 0.0
    total_credits = 0
    
    for r in results:
        subject = r.subject
        credits = subject.credits if subject else 3
        total_credit_points += (r.grade_point * credits)
        total_credits += credits
        
    if total_credits == 0:
        return 0.0
        
    return round(total_credit_points / total_credits, 2)
