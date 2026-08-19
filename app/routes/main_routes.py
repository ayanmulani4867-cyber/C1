import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import current_user, login_required
from app.models.user import User, Role
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.department import Department
from app.models.course import Course
from app.models.notice import Notice
from app.models.notification import Notification
from app.extensions import db

logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)


@main_bp.route('/health')
def health():
    """
    Public health check endpoint for monitoring and Render ingress.
    Returns clean JSON status without exposing sensitive credentials.
    """
    return jsonify({"status": "ok"}), 200


@main_bp.route('/students/create', methods=['GET', 'POST'])
def students_create_alias():
    from app.routes.student_routes import create as student_create
    return student_create()


@main_bp.route('/faculty/create', methods=['GET', 'POST'])
def faculty_create_alias():
    from app.routes.faculty_routes import create as faculty_create
    return faculty_create()


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == Role.ADMIN:
            return redirect(url_for('admin.dashboard'))
        elif current_user.role in (Role.FACULTY, Role.HOD):
            return redirect(url_for('faculty.dashboard'))
        elif current_user.role == Role.STUDENT:
            return redirect(url_for('student.dashboard'))

    # Public landing page stats & circulars with safe fallbacks
    stats = {
        'students_count': 0,
        'faculty_count': 0,
        'departments_count': 0,
        'courses_count': 0
    }
    recent_notices = []
    departments = []
    
    try:
        stats = {
            'students_count': Student.query.filter_by(status='Active').count(),
            'faculty_count': Faculty.query.filter_by(status='Active').count(),
            'departments_count': Department.query.filter_by(is_active=True).count(),
            'courses_count': Course.query.filter_by(is_active=True).count()
        }
        recent_notices = Notice.query.filter_by(is_published=True).order_by(Notice.created_at.desc()).limit(5).all()
        departments = Department.query.filter_by(is_active=True).limit(6).all()
    except Exception as e:
        logger.warning(f"Initial DB query fallback in main.index: {e}")
        db.session.rollback()

    return render_template('main/index.html', stats=stats, notices=recent_notices, departments=departments)


@main_bp.route('/about')
def about():
    departments = []
    try:
        departments = Department.query.filter_by(is_active=True).all()
    except Exception as e:
        logger.warning(f"Initial DB query fallback in main.about: {e}")
        db.session.rollback()
    return render_template('main/about.html', departments=departments)


@main_bp.route('/contact')
def contact():
    departments = []
    try:
        departments = Department.query.filter_by(is_active=True).all()
    except Exception as e:
        logger.warning(f"Initial DB query fallback in main.contact: {e}")
        db.session.rollback()
    return render_template('main/contact.html', departments=departments)


@main_bp.route('/notifications')
@login_required
def notifications():
    user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('main/notifications.html', notifications=user_notifications)


@main_bp.route('/notifications/<int:notification_id>/read', methods=['POST', 'GET'])
@login_required
def mark_notification_read(notification_id):
    notif = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    notif.is_read = True
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({'success': True})
        
    if notif.link:
        return redirect(notif.link)
    return redirect(url_for('main.notifications'))


@main_bp.route('/notifications/read-all', methods=['POST', 'GET'])
@login_required
def mark_all_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({'success': True})
        
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('main.notifications'))
