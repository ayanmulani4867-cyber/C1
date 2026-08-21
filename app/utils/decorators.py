from functools import wraps
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user


def role_required(*allowed_roles):
    """Decorator to enforce role-based access control"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                from flask import render_template
                if 'text/html' in request.headers.get('Accept', '') and not request.path.startswith('/api/'):
                    return render_template('auth/bootstrap.html'), 200
                return redirect(url_for('auth.login', next=request.url))
            
            # If the user must change password, force them to change password first
            if current_user.must_change_password and request.endpoint not in ('auth.change_password', 'auth.logout', 'static'):
                flash('You must change your temporary password before accessing the system.', 'warning')
                return redirect(url_for('auth.change_password'))
            
            if current_user.role not in allowed_roles:
                abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return role_required('ADMIN')(f)


def hod_required(f):
    return role_required('ADMIN', 'HOD')(f)


def faculty_required(f):
    return role_required('ADMIN', 'HOD', 'FACULTY')(f)


def student_required(f):
    return role_required('STUDENT')(f)
