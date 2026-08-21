import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_wtf.csrf import CSRFError
from config import config
from app.extensions import db, login_manager, migrate, csrf
from app.models.user import User


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    config_class = config.get(config_name, config['default'])
    app.config.from_object(config_class)
    if hasattr(config_class, 'init_app'):
        config_class.init_app(app)
    
    # Enable ProxyFix so Flask recognizes HTTPS and forwarded headers behind proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'photos'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'assignments'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'materials'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'certificates'), exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please sign in to access Campus Connect.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.request_loader
    def load_user_from_request(req):
        from app.utils.api_auth import verify_api_token
        auth_header = req.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()
            user, _, _ = verify_api_token(token)
            if user and user.is_active:
                return user
        return None

    @login_manager.unauthorized_handler
    def handle_unauthorized():
        if 'text/html' in request.headers.get('Accept', '') and not request.path.startswith('/api/'):
            return render_template('auth/bootstrap.html'), 200
        if request.path.startswith('/api/'):
            from flask import jsonify
            return jsonify({'success': False, 'error': 'Unauthorized', 'message': 'Authentication required.'}), 401
        return redirect(url_for('auth.login', next=request.url))

    # Configure CSRF protection using public Flask-WTF APIs
    app.config.setdefault('WTF_CSRF_CHECK_DEFAULT', False)

    @app.before_request
    def csrf_protect_requests():
        if not app.config.get('WTF_CSRF_ENABLED', True):
            return
        # Exempt Bearer-authenticated requests from cookie-based CSRF checks
        auth = request.headers.get('Authorization', '')
        if auth.startswith('Bearer '):
            return
        try:
            csrf.protect(apply_exemptions=True)
        except TypeError:
            csrf.protect()

    @app.before_request
    def load_bearer_user():
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            from flask import g
            from app.utils.api_auth import verify_api_token
            token = auth_header.split(' ', 1)[1].strip()
            user, student, _ = verify_api_token(token)
            if user and user.is_active:
                g._login_user = user
                g.current_user = user
                g.current_student = student
    
    # Custom Jinja filters and helpers
    @app.template_filter('currency')
    def currency_filter(value):
        try:
            return f"₹{float(value):,.2f}"
        except (ValueError, TypeError):
            return f"₹{value}"

    @app.template_filter('datetime_format')
    def datetime_format_filter(value, format='%b %d, %Y %I:%M %p'):
        if value is None:
            return '-'
        return value.strftime(format)

    @app.template_filter('date_format')
    def date_format_filter(value, format='%b %d, %Y'):
        if value is None:
            return '-'
        return value.strftime(format)

    @app.template_filter('time_format')
    def time_format_filter(value, format='%I:%M %p'):
        if value is None:
            return '-'
        return value.strftime(format)

    # Inject global context (institute details, app name, notifications)
    @app.context_processor
    def inject_global_context():
        from app.models.notice import Notice
        from app.models.notification import Notification
        from app.models.academic_session import AcademicSession
        from flask_login import current_user
        
        unread_notices_count = 0
        unread_notifications_count = 0
        recent_notifications = []
        current_session = None

        try:
            current_session = AcademicSession.query.filter_by(is_current=True).first()
            if current_user.is_authenticated:
                unread_notices_count = Notice.query.filter_by(is_active=True).count()
                unread_notifications_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
                recent_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()
        except Exception:
            pass
            
        return {
            'APP_NAME': app.config.get('APP_NAME', 'Campus Connect'),
            'COLLEGE_NAME': app.config.get('COLLEGE_NAME', 'Apex Institute of Technology & Science'),
            'COLLEGE_ADDRESS': app.config.get('COLLEGE_ADDRESS', 'Knowledge City, Expressway Campus'),
            'COLLEGE_EMAIL': app.config.get('COLLEGE_EMAIL', 'contact@apextech.edu'),
            'COLLEGE_PHONE': app.config.get('COLLEGE_PHONE', '+91 98765 43210'),
            'unread_notices_count': unread_notices_count,
            'unread_notifications_count': unread_notifications_count,
            'recent_notifications': recent_notifications,
            'current_academic_session': current_session.name if current_session else '2025-26'
        }

    # Register Blueprints
    from app.routes.main_routes import main_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.student_routes import student_bp
    from app.routes.faculty_routes import faculty_bp
    from app.routes.academic_routes import academic_bp
    from app.routes.attendance_routes import attendance_bp
    from app.routes.timetable_routes import timetable_bp
    from app.routes.assignment_routes import assignment_bp
    from app.routes.exam_routes import exam_bp
    from app.routes.fee_routes import fee_bp
    from app.routes.leave_routes import leave_bp
    from app.routes.notice_routes import notice_bp
    from app.routes.feedback_routes import feedback_bp
    from app.routes.certificate_routes import certificate_bp
    from app.routes.complaint_routes import complaint_bp
    from app.routes.event_routes import event_bp
    from app.routes.report_routes import report_bp
    from app.routes.api_routes import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(faculty_bp, url_prefix='/faculty')
    app.register_blueprint(academic_bp, url_prefix='/academic')
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(timetable_bp, url_prefix='/timetable')
    app.register_blueprint(assignment_bp, url_prefix='/assignments')
    app.register_blueprint(exam_bp, url_prefix='/exams')
    app.register_blueprint(fee_bp, url_prefix='/fees')
    app.register_blueprint(leave_bp, url_prefix='/leaves')
    app.register_blueprint(notice_bp, url_prefix='/notices')
    app.register_blueprint(feedback_bp, url_prefix='/feedback')
    app.register_blueprint(certificate_bp, url_prefix='/certificates')
    app.register_blueprint(complaint_bp, url_prefix='/complaints')
    app.register_blueprint(event_bp, url_prefix='/events')
    app.register_blueprint(report_bp, url_prefix='/reports')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(api_bp, url_prefix='/api/v1', name='api_v1')

    # Root health endpoint
    @app.route('/health')
    def root_health():
        from flask import jsonify
        return jsonify({"status": "ok"}), 200

    # Exempt API routes from CSRF token requirements
    csrf.exempt(api_bp)
    csrf.exempt(root_health)

    # Force password change for accounts requiring it on initial sign in
    @app.before_request
    def check_must_change_password():
        if request.path.startswith('/api/'):
            return None
        from flask_login import current_user
        if current_user.is_authenticated and getattr(current_user, 'must_change_password', False):
            allowed_endpoints = ('auth.change_password', 'auth.logout', 'static')
            if request.endpoint and request.endpoint not in allowed_endpoints and not request.path.startswith('/static'):
                flash('You are required to change your temporary password on initial login.', 'warning')
                return redirect(url_for('auth.change_password'))

    # Error handlers
    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        if request.path.startswith('/api/'):
            from flask import jsonify
            return jsonify({'success': False, 'error': 'CSRF Error', 'message': str(error)}), 400
        flash('Security validation issue: please refresh and try submitting again.', 'warning')
        referer = request.referrer
        if referer and referer.startswith(request.host_url):
            return redirect(referer)
        return redirect(url_for('auth.login'))

    @app.errorhandler(403)
    def forbidden_error(error):
        if request.path.startswith('/api/'):
            from flask import jsonify
            return jsonify({'success': False, 'error': 'Forbidden', 'message': 'Access denied to this resource.'}), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            from flask import jsonify
            return jsonify({'success': False, 'error': 'Not Found', 'message': 'Requested API endpoint was not found.'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            from flask import jsonify
            return jsonify({'success': False, 'error': 'Internal Server Error', 'message': 'An unexpected server error occurred.'}), 500
        return render_template('errors/500.html'), 500

    @app.after_request
    def set_security_headers(response):
        # Allow embedding in AI Studio preview iframe
        response.headers.pop('X-Frame-Options', None)
        return response

    # Automatically ensure database tables & default admin exist on application startup
    with app.app_context():
        try:
            from app.utils.db_ops import initialize_database_schema
            initialize_database_schema()
        except Exception as e:
            app.logger.warning(f"Startup database schema check notice: {e}")

    return app
