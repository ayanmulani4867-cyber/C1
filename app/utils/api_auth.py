import functools
from datetime import datetime
# pyrefly: ignore [missing-import]
from flask import request, jsonify, g, current_app
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app.models.user import User, Role
from app.models.student import Student


def get_token_serializer():
    secret_key = current_app.config.get('SECRET_KEY', 'campus-connect-default-secret-key-2026')
    return URLSafeTimedSerializer(secret_key, salt='campus-connect-student-api-v1')


def generate_api_token(user: User, student: Student = None, expires_in_days: int = 30) -> str:
    """
    Generates a secure, cryptographically signed token for API client authentication.
    """
    serializer = get_token_serializer()
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'student_id': student.id if student else None,
        'iat': int(datetime.utcnow().timestamp())
    }
    return serializer.dumps(payload)


def verify_api_token(token: str, max_age_days: int = 30):
    """
    Verifies the cryptographic signature and expiration of the API token.
    Returns (user, student, error_message).
    """
    serializer = get_token_serializer()
    max_age_seconds = max_age_days * 86400
    try:
        data = serializer.loads(token, max_age=max_age_seconds)
    except SignatureExpired:
        return None, None, 'Authentication token has expired. Please sign in again.'
    except BadSignature:
        return None, None, 'Invalid authentication token signature.'
    except Exception as e:
        return None, None, f'Authentication token decoding failed: {str(e)}'

    user_id = data.get('user_id')
    if not user_id:
        return None, None, 'Invalid token payload.'

    user = User.query.get(user_id)
    if not user:
        return None, None, 'User account associated with token does not exist.'

    if not user.is_active:
        return None, None, 'User account is deactivated. Contact administration.'

    student = None
    if user.role == Role.STUDENT or data.get('student_id'):
        student = Student.query.filter_by(user_id=user.id).first()
        if not student and data.get('student_id'):
            student = Student.query.get(data.get('student_id'))

    return user, student, None


def api_auth_required(f):
    """
    Decorator for REST API routes to enforce secure token or session authentication.
    Extracts Bearer token from 'Authorization' header, 'X-Auth-Token' header, or query param.
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Check Authorization header: "Bearer <token>"
        auth_header = request.headers.get('Authorization', '')
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()
        elif request.headers.get('X-Auth-Token'):
            token = request.headers.get('X-Auth-Token').strip()

        if token:
            user, student, error_msg = verify_api_token(token)
            if error_msg or not user:
                return jsonify({
                    'success': False,
                    'error': 'Unauthorized',
                    'message': error_msg or 'Authentication failed'
                }), 401
            g.current_user = user
            g.current_student = student
            return f(*args, **kwargs)

        if token:
            user, student, error_msg = verify_api_token(token)
            if error_msg or not user:
                return jsonify({
                    'success': False,
                    'error': 'Unauthorized',
                    'message': error_msg or 'Authentication failed'
                }), 401
            g.current_user = user
            g.current_student = student
            return f(*args, **kwargs)

        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Missing or invalid Authorization header. Pass Bearer <token>.'
        }), 401

    return decorated_function


def api_role_required(*allowed_roles):
    """
    Decorator requiring authentication AND that the authenticated user's role
    matches one of the allowed roles.
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. First authenticate
            auth_header = request.headers.get('Authorization', '')
            token = None
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ', 1)[1].strip()
            elif request.headers.get('X-Auth-Token'):
                token = request.headers.get('X-Auth-Token').strip()

            if not token:
                return jsonify({
                    'success': False,
                    'error': 'Unauthorized',
                    'message': 'Authorization header required. Pass Bearer <token>.'
                }), 401

            user, student, error_msg = verify_api_token(token)
            if error_msg or not user:
                return jsonify({
                    'success': False,
                    'error': 'Unauthorized',
                    'message': error_msg or 'Authentication failed'
                }), 401

            if not user.is_active:
                return jsonify({
                    'success': False,
                    'error': 'Forbidden',
                    'message': 'User account is inactive. Contact administrator.'
                }), 403

            # Normalize role strings
            user_role_str = str(getattr(user, 'role', '')).upper()
            allowed_role_strs = [str(r).upper() for r in allowed_roles]

            if user_role_str not in allowed_role_strs:
                return jsonify({
                    'success': False,
                    'error': 'Forbidden',
                    'message': f'Access restricted to authorized roles: {", ".join(allowed_role_strs)}'
                }), 403

            g.current_user = user
            g.current_student = student
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def api_admin_required(f):
    """Decorator requiring ADMIN role."""
    return api_role_required(Role.ADMIN)(f)


def api_hod_required(f):
    """Decorator requiring ADMIN or HOD role."""
    return api_role_required(Role.ADMIN, Role.HOD)(f)


def api_faculty_required(f):
    """Decorator requiring ADMIN, HOD, or FACULTY role."""
    return api_role_required(Role.ADMIN, Role.HOD, Role.FACULTY)(f)


def api_student_required(f):
    """
    Decorator requiring an authenticated active Student.
    Ensures g.current_student is populated and securely authorizes student-only data access.
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # First ensure auth
        auth_header = request.headers.get('Authorization', '')
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()
        elif request.headers.get('X-Auth-Token'):
            token = request.headers.get('X-Auth-Token').strip()

        if not token:
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': 'Authorization header required. Pass Bearer <token>.'
            }), 401

        user, student, error_msg = verify_api_token(token)
        if error_msg or not user:
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': error_msg or 'Authentication failed'
            }), 401

        if not user.is_active:
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'Account is inactive. Contact administrator.'
            }), 403

        if not student:
            if user.role != Role.STUDENT:
                return jsonify({
                    'success': False,
                    'error': 'Forbidden',
                    'message': 'This endpoint is restricted to authenticated students.'
                }), 403
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'No student academic profile is linked with this account.'
            }), 403

        g.current_user = user
        g.current_student = student
        return f(*args, **kwargs)

    return decorated_function
