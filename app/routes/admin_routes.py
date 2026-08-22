from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import date, datetime
from app.extensions import db
from app.utils.decorators import admin_required
from app.models.user import User, Role
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.department import Department
from app.models.course import Course
from app.models.academic_session import AcademicSession
from app.models.class_division import ClassDivision
from app.models.subject import Subject
from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.fee import FeePayment, StudentFee, FeeStructure
from app.models.leave import LeaveRequest
from app.models.certificate import CertificateRequest
from app.models.complaint import Complaint
from app.models.notice import Notice
from app.models.feedback import Feedback
from app.models.event import Event
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.models.mobile_config import (
    MobileAppConfig,
    MobileHomeSection,
    MobileQuickAction,
    MobileBanner,
    MobileFeatureFlag
)
from app.routes.api_routes import ensure_default_mobile_config
from app.forms.auth_forms import UserCreateForm

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    today = date.today()
    
    # 1. Real Counts from Database
    total_students = Student.query.count()
    active_students = Student.query.filter_by(status='Active').count()
    total_faculty = Faculty.query.count()
    active_faculty = Faculty.query.filter_by(status='Active').count()
    total_depts = Department.query.filter_by(is_active=True).count()
    total_courses = Course.query.filter_by(is_active=True).count()
    total_subjects = Subject.query.count()
    total_divisions = ClassDivision.query.count()
    
    # 2. Attendance stats for today
    today_sessions = AttendanceSession.query.filter_by(date=today).all()
    today_records = AttendanceRecord.query.filter(AttendanceRecord.attendance_session_id.in_([s.id for s in today_sessions])).all() if today_sessions else []
    today_present = sum(1 for r in today_records if r.status in ('Present', 'Late'))
    today_total = len(today_records)
    attendance_rate = round((today_present / today_total * 100), 1) if today_total > 0 else 0
    
    # 3. Real Fee stats from database
    fee_records = StudentFee.query.all()
    total_fee_demanded = sum(r.total_amount or 0 for r in fee_records)
    total_fee_collected = sum(r.paid_amount or 0 for r in fee_records)
    total_fee_pending = sum(r.pending_amount or 0 for r in fee_records)
    recent_payments = FeePayment.query.order_by(FeePayment.payment_date.desc()).limit(6).all()

    # 4. Pending workflows / queues
    pending_leaves = LeaveRequest.query.filter_by(status='Pending').count()
    pending_complaints = Complaint.query.filter(Complaint.status.in_(['Submitted', 'Assigned', 'In Progress'])).count()
    pending_certificates = CertificateRequest.query.filter_by(status='Pending').count()
    
    # 5. Recent items
    recent_notices = Notice.query.order_by(Notice.created_at.desc()).limit(5).all()
    recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
    recent_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(5).all()
    upcoming_events = Event.query.order_by(Event.start_datetime.asc()).limit(4).all()

    # 6. Department student distribution data for Chart
    depts = Department.query.filter_by(is_active=True).all()
    dept_labels = [d.code or d.name for d in depts]
    dept_student_counts = [Student.query.filter_by(department_id=d.id, status='Active').count() for d in depts]
    dept_faculty_counts = [Faculty.query.filter_by(department_id=d.id, status='Active').count() for d in depts]

    # Current academic session
    current_session = AcademicSession.query.filter_by(is_current=True).first()

    return render_template('admin/dashboard.html',
        total_students=total_students,
        active_students=active_students,
        total_faculty=total_faculty,
        active_faculty=active_faculty,
        total_depts=total_depts,
        total_courses=total_courses,
        total_subjects=total_subjects,
        total_divisions=total_divisions,
        attendance_rate=attendance_rate,
        today_total=today_total,
        today_present=today_present,
        total_fee_demanded=total_fee_demanded,
        total_fee_collected=total_fee_collected,
        total_fee_pending=total_fee_pending,
        recent_payments=recent_payments,
        pending_leaves=pending_leaves,
        pending_complaints=pending_complaints,
        pending_certificates=pending_certificates,
        recent_notices=recent_notices,
        recent_students=recent_students,
        recent_complaints=recent_complaints,
        upcoming_events=upcoming_events,
        dept_labels=dept_labels,
        dept_student_counts=dept_student_counts,
        dept_faculty_counts=dept_faculty_counts,
        current_session=current_session
    )


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    role_filter = request.args.get('role', '')
    search = request.args.get('q', '').strip()
    
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (User.first_name.ilike(f'%{search}%')) |
            (User.last_name.ilike(f'%{search}%'))
        )
    
    users_list = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users_list, role_filter=role_filter, search=search)


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def user_create():
    form = UserCreateForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip().lower(),
            email=form.email.data.strip().lower(),
            role=form.role.data,
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            phone=form.phone.data.strip() if form.phone.data else None,
            must_change_password=True,
            is_active=form.is_active.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        AuditLog.log(
            action='Create',
            module='User',
            user=current_user,
            record_id=user.id,
            details=f"Created user @{user.username} with role {user.role}",
            ip_address=request.remote_addr
        )
        
        flash(f'User account @{user.username} created successfully.', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/user_create.html', form=form)


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    if user_id == current_user.id:
        flash('You cannot deactivate your own administrative account.', 'danger')
        return redirect(url_for('admin.users'))

    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status_str = 'activated' if user.is_active else 'deactivated'
    
    AuditLog.log(
        action='StatusChange',
        module='User',
        user=current_user,
        record_id=user.id,
        details=f"Account @{user.username} {status_str}",
        ip_address=request.remote_addr
    )
    
    flash(f'Account for @{user.username} has been {status_str}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_user_password(user_id):
    user = User.query.get_or_404(user_id)
    new_pwd = request.form.get('new_password', 'Campus@123')
    user.set_password(new_pwd)
    user.must_change_password = True
    db.session.commit()
    
    AuditLog.log(
        action='PasswordReset',
        module='User',
        user=current_user,
        record_id=user.id,
        details=f"Admin reset password for @{user.username}",
        ip_address=request.remote_addr
    )
    
    flash(f'Password for @{user.username} has been reset. Temporary credentials required on next login.', 'info')
    return redirect(url_for('admin.users'))


@admin_bp.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    module = request.args.get('module', '')
    action = request.args.get('action', '')
    search = request.args.get('q', '').strip()
    
    query = AuditLog.query
    if module:
        query = query.filter_by(module=module)
    if action:
        query = query.filter_by(action=action)
    if search:
        query = query.filter(
            (AuditLog.username.ilike(f'%{search}%')) |
            (AuditLog.details.ilike(f'%{search}%')) |
            (AuditLog.action.ilike(f'%{search}%')) |
            (AuditLog.module.ilike(f'%{search}%'))
        )
        
    logs = query.order_by(AuditLog.created_at.desc()).limit(150).all()
    modules = db.session.query(AuditLog.module).distinct().all()
    actions = db.session.query(AuditLog.action).distinct().all()
    
    return render_template('admin/audit_logs.html',
        logs=logs,
        modules=[m[0] for m in modules if m[0]],
        actions=[a[0] for a in actions if a[0]],
        selected_module=module,
        selected_action=action,
        search=search
    )


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    if request.method == 'POST':
        college_name = request.form.get('college_name', '').strip()
        college_address = request.form.get('college_address', '').strip()
        college_email = request.form.get('college_email', '').strip()
        college_phone = request.form.get('college_phone', '').strip()
        
        if college_name:
            current_app.config['COLLEGE_NAME'] = college_name
        if college_address:
            current_app.config['COLLEGE_ADDRESS'] = college_address
        if college_email:
            current_app.config['COLLEGE_EMAIL'] = college_email
        if college_phone:
            current_app.config['COLLEGE_PHONE'] = college_phone
            
        flash('Institutional settings updated successfully.', 'success')
        return redirect(url_for('admin.settings'))
        
    sessions = AcademicSession.query.all()
    current_session = AcademicSession.query.filter_by(is_current=True).first()
    
    return render_template('admin/settings.html',
        sessions=sessions,
        current_session=current_session
    )


# ==========================================
# MOBILE APP MANAGEMENT (REMOTE CONFIG ENGINE)
# ==========================================

@admin_bp.route('/mobile-management', methods=['GET', 'POST'])
@login_required
@admin_required
def mobile_management():
    ensure_default_mobile_config()

    if request.method == 'POST':
        action_type = request.form.get('action_type', 'save_config')

        if action_type == 'save_config':
            # 1. Update Core Settings
            cfg = MobileAppConfig.query.first()
            if not cfg:
                cfg = MobileAppConfig()
                db.session.add(cfg)

            cfg.config_version = request.form.get('config_version', '1.0').strip()
            cfg.maintenance_mode = 'maintenance_mode' in request.form
            cfg.maintenance_message = request.form.get('maintenance_message', '').strip()
            cfg.min_app_version = request.form.get('min_app_version', '1.0.0').strip()
            cfg.update_url = request.form.get('update_url', '').strip()
            cfg.updated_at = datetime.utcnow()

            # 2. Update Home Sections
            sections = MobileHomeSection.query.all()
            for sec in sections:
                sec.is_enabled = f"section_{sec.section_key}_enabled" in request.form
                order_val = request.form.get(f"section_{sec.section_key}_order", str(sec.display_order))
                try:
                    sec.display_order = int(order_val)
                except ValueError:
                    pass

            # 3. Update Quick Actions
            actions = MobileQuickAction.query.all()
            for act in actions:
                act.is_enabled = f"action_{act.action_key}_enabled" in request.form
                order_val = request.form.get(f"action_{act.action_key}_order", str(act.display_order))
                try:
                    act.display_order = int(order_val)
                except ValueError:
                    pass

            # 4. Update Feature Flags
            flags = MobileFeatureFlag.query.all()
            for flg in flags:
                flg.is_enabled = f"flag_{flg.flag_key}_enabled" in request.form

            db.session.commit()
            flash('Mobile App configuration published successfully to student devices.', 'success')
            return redirect(url_for('admin.mobile_management'))

    cfg = MobileAppConfig.query.first()
    sections = MobileHomeSection.query.order_by(MobileHomeSection.display_order.asc()).all()
    actions = MobileQuickAction.query.order_by(MobileQuickAction.display_order.asc()).all()
    banners = MobileBanner.query.order_by(MobileBanner.display_order.asc()).all()
    flags = MobileFeatureFlag.query.all()

    return render_template('admin/mobile_management.html',
        config=cfg,
        sections=sections,
        actions=actions,
        banners=banners,
        flags=flags
    )


@admin_bp.route('/mobile-management/banner/create', methods=['POST'])
@login_required
@admin_required
def create_mobile_banner():
    title = request.form.get('title', '').strip()
    subtitle = request.form.get('subtitle', '').strip()
    image_url = request.form.get('image_url', '').strip()
    action_url = request.form.get('action_url', '').strip()
    order_val = request.form.get('display_order', '1')

    if title:
        try:
            order = int(order_val)
        except ValueError:
            order = 1

        banner = MobileBanner(
            title=title,
            subtitle=subtitle if subtitle else None,
            image_url=image_url if image_url else None,
            action_url=action_url if action_url else None,
            is_active=True,
            display_order=order
        )
        db.session.add(banner)
        db.session.commit()
        flash(f'Promotional Banner "{title}" created.', 'success')
    else:
        flash('Banner title is required.', 'danger')

    return redirect(url_for('admin.mobile_management'))


@admin_bp.route('/mobile-management/banner/<int:banner_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_mobile_banner(banner_id):
    banner = MobileBanner.query.get_or_404(banner_id)
    title = banner.title
    db.session.delete(banner)
    db.session.commit()
    flash(f'Banner "{title}" deleted.', 'info')
    return redirect(url_for('admin.mobile_management'))

