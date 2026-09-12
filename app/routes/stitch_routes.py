"""
Campus Connect College ERP - Stitch UI Integration & Role Routing
Connects the Stitch-generated frontend with Flask Backend, Role-Based Access Control,
and Firebase Realtime Database APIs.
"""
import os
import re
from functools import wraps
from flask import Blueprint, request, jsonify, redirect, url_for, current_app, Response, g
from flask_login import current_user, login_required, login_user, logout_user
from app.models.user import Role, User
from app.services import firebase_service

stitch_bp = Blueprint('stitch', __name__)

# Resolve path to Stitch pages
STITCH_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'stitch_campus_connect_college_erp_portal')

PAGE_MAP = {
    'login': 'campus_connect_portal_login_authentication',
    'admin_dashboard': 'executive_dashboard_super_admin',
    'students': 'student_directory_records',
    'faculty': 'faculty_directory_workload_management_1',
    'hod': 'hod_management_department_oversight',
    'departments': 'department_management_academic_hierarchy',
    'courses': 'course_subject_management',
    'attendance': 'attendance_management_tracking',
    'results': 'examination_result_tabulation',
    'materials': 'study_materials_notices_repository',
    'events': 'campus_events_academic_calendar',
    'student_dashboard': 'student_academic_hub_dashboard',
    'student_academics': 'student_attendance_grade_transcript',
    'faculty_dashboard': 'faculty_teaching_evaluation_console',
    'profile': 'user_profile_settings_notifications_center'
}


def render_stitch_page(page_key: str):
    """
    Renders an original Stitch HTML page and injects the unified connector script.
    Preserves 100% of the design, theme, colors, typography, layout, and components.
    """
    folder = PAGE_MAP.get(page_key)
    if not folder:
        return f"Page not found for key: {page_key}", 404

    path = os.path.join(STITCH_DIR, folder, 'code.html')
    if not os.path.exists(path):
        # Check if direct child exists
        alt_path = os.path.join(STITCH_DIR, 'stitch_campus_connect_college_erp_portal', folder, 'code.html')
        if os.path.exists(alt_path):
            path = alt_path
        else:
            return f"Stitch code.html not found at: {path}", 404

    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    # Inject the unified stitch_connector.js before </body>
    script_tag = '<script src="/static/js/stitch_connector.js"></script></body>'
    if '</body>' in html:
        html = html.replace('</body>', script_tag)
    else:
        html += '<script src="/static/js/stitch_connector.js"></script>'

    return Response(html, mimetype='text/html')


def require_roles(*allowed_roles):
    """Enforces server-side role-based access control."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.path.startswith('/api/'):
                    return jsonify({'success': False, 'error': 'Unauthorized', 'message': 'Authentication required.'}), 401
                return redirect(url_for('stitch.page_login', next=request.url))

            user_role = getattr(current_user, 'role', None)
            if user_role not in allowed_roles:
                if request.path.startswith('/api/'):
                    return jsonify({'success': False, 'error': 'Forbidden', 'message': f'Access restricted to roles: {", ".join(allowed_roles)}'}), 403
                return f"""
                <!DOCTYPE html>
                <html><head><title>403 Forbidden - Access Restricted</title>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
                <style>body{{font-family:'Inter',sans-serif;background:#0b1c30;color:#eaf1ff;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;}}
                .card{{background:#131b2e;padding:2.5rem;border-radius:1rem;border:1px solid #213145;max-width:500px;text-align:center;box-shadow:0 10px 25px rgba(0,0,0,0.3);}}
                h1{{color:#ba1a1a;margin-top:0;font-size:2rem;}}p{{color:#bec6e0;line-height:1.6;}}
                a{{display:inline-block;margin-top:1.5rem;background:#1d4ed8;color:#fff;padding:0.75rem 1.5rem;border-radius:0.5rem;text-decoration:none;font-weight:600;}}
                </style></head><body>
                <div class="card">
                <h1>403 Forbidden</h1>
                <p>Your current role <strong>({user_role})</strong> is not authorized to access this administrative resource.</p>
                <a href="/">Return to Dashboard</a>
                </div></body></html>
                """, 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


# =========================================================================
# ROUTE PAGES - SERVING STITCH HTML
# =========================================================================

@stitch_bp.route('/')
def index():
    """Root entrypoint. Directs authenticated users to their role workspace, or login."""
    if current_user.is_authenticated:
        role = getattr(current_user, 'role', Role.STUDENT)
        if role == Role.ADMIN:
            return redirect(url_for('stitch.page_admin_dashboard'))
        elif role == Role.HOD:
            return redirect(url_for('stitch.page_hod'))
        elif role == Role.FACULTY:
            return redirect(url_for('stitch.page_faculty_dashboard'))
        else:
            return redirect(url_for('stitch.page_student_dashboard'))
    return redirect(url_for('stitch.page_login'))


@stitch_bp.route('/login')
def page_login():
    """Serves the Stitch login page."""
    if current_user.is_authenticated:
        return redirect(url_for('stitch.index'))
    return render_stitch_page('login')


@stitch_bp.route('/logout')
@stitch_bp.route('/api/logout')
def stitch_logout():
    """Logs out user and redirects to login or returns json."""
    from flask_login import logout_user
    logout_user()
    if request.is_json or request.headers.get('Accept') == 'application/json':
        return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
    return redirect(url_for('stitch.page_login'))


@stitch_bp.route('/admin/dashboard')
@login_required
@require_roles(Role.ADMIN)
def page_admin_dashboard():
    """Serves Super Admin Executive Dashboard."""
    return render_stitch_page('admin_dashboard')


@stitch_bp.route('/admin/students')
@login_required
@require_roles(Role.ADMIN, Role.HOD)
def page_students():
    """Serves Student Directory & Records."""
    return render_stitch_page('students')


@stitch_bp.route('/admin/faculty')
@login_required
@require_roles(Role.ADMIN, Role.HOD)
def page_faculty():
    """Serves Faculty Directory & Workload."""
    return render_stitch_page('faculty')


@stitch_bp.route('/admin/hod')
@stitch_bp.route('/hod/dashboard')
@login_required
@require_roles(Role.ADMIN, Role.HOD)
def page_hod():
    """Serves HOD Management & Department Oversight."""
    return render_stitch_page('hod')


@stitch_bp.route('/admin/departments')
@login_required
@require_roles(Role.ADMIN, Role.HOD)
def page_departments():
    """Serves Department Management & Hierarchy."""
    return render_stitch_page('departments')


@stitch_bp.route('/admin/courses')
@stitch_bp.route('/admin/subjects')
@login_required
@require_roles(Role.ADMIN, Role.HOD)
def page_courses():
    """Serves Course & Subject Curriculum Management."""
    return render_stitch_page('courses')


@stitch_bp.route('/attendance')
@stitch_bp.route('/admin/attendance')
@stitch_bp.route('/faculty/attendance')
@login_required
@require_roles(Role.ADMIN, Role.HOD, Role.FACULTY)
def page_attendance():
    """Serves Attendance Management & Tracking."""
    return render_stitch_page('attendance')


@stitch_bp.route('/results')
@stitch_bp.route('/exams')
@stitch_bp.route('/faculty/results')
@login_required
@require_roles(Role.ADMIN, Role.HOD, Role.FACULTY)
def page_results():
    """Serves Examination Result Tabulation."""
    return render_stitch_page('results')


@stitch_bp.route('/notices')
@stitch_bp.route('/materials')
@stitch_bp.route('/admin/notices')
@login_required
def page_materials():
    """Serves Study Materials & Official Notices Repository."""
    return render_stitch_page('materials')


@stitch_bp.route('/events')
@stitch_bp.route('/admin/events')
@login_required
def page_events():
    """Serves Campus Events & Academic Calendar."""
    return render_stitch_page('events')


@stitch_bp.route('/student/dashboard')
@login_required
@require_roles(Role.STUDENT, Role.ADMIN)
def page_student_dashboard():
    """Serves Student Academic Hub Dashboard."""
    return render_stitch_page('student_dashboard')


@stitch_bp.route('/student/academics')
@stitch_bp.route('/student/attendance')
@stitch_bp.route('/student/results')
@login_required
@require_roles(Role.STUDENT, Role.ADMIN)
def page_student_academics():
    """Serves Student Attendance & Grade Transcript."""
    return render_stitch_page('student_academics')


@stitch_bp.route('/faculty/dashboard')
@login_required
@require_roles(Role.FACULTY, Role.HOD, Role.ADMIN)
def page_faculty_dashboard():
    """Serves Faculty Teaching Evaluation Console."""
    return render_stitch_page('faculty_dashboard')


@stitch_bp.route('/profile')
@stitch_bp.route('/settings')
@stitch_bp.route('/notifications')
@login_required
def page_profile():
    """Serves User Profile, Settings & Notifications Center."""
    return render_stitch_page('profile')


# =========================================================================
# REST API ENDPOINTS FOR STITCH FRONTEND & FIREBASE RTDB
# =========================================================================

@stitch_bp.route('/api/dashboard/stats', methods=['GET'])
@login_required
def api_dashboard_stats():
    """Returns live stats tailored to user role."""
    role = getattr(current_user, 'role', 'ADMIN').lower()
    stats = firebase_service.get_dashboard_stats(role=role, user_id=current_user.id)
    return jsonify(stats)


@stitch_bp.route('/api/students', methods=['GET', 'POST'])
@login_required
def api_students():
    """Handles Student List (GET) and Student Creation (POST) with Firebase sync."""
    if request.method == 'POST':
        if current_user.role not in (Role.ADMIN, Role.HOD):
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        data = request.get_json(silent=True) or request.form.to_dict()
        student = firebase_service.create_student(data)
        return jsonify({'success': True, 'student': student, 'message': 'Student created successfully.'}), 201

    students = firebase_service.get_students()
    return jsonify(students)


@stitch_bp.route('/api/students/<student_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@login_required
def api_student_detail(student_id):
    """Handles single Student Read, Update, Delete with Firebase sync."""
    if request.method == 'DELETE':
        if current_user.role not in (Role.ADMIN, Role.HOD):
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        success = firebase_service.delete_student(student_id)
        return jsonify({'success': success})

    if request.method in ('PUT', 'PATCH'):
        if current_user.role not in (Role.ADMIN, Role.HOD):
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        data = request.get_json(silent=True) or request.form.to_dict()
        student = firebase_service.update_student(student_id, data)
        return jsonify({'success': bool(student), 'student': student})

    student = firebase_service.get_student(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify(student)


@stitch_bp.route('/api/faculty', methods=['GET', 'POST'])
@login_required
def api_faculty():
    """Handles Faculty List and Creation with Firebase sync."""
    if request.method == 'POST':
        if current_user.role not in (Role.ADMIN, Role.HOD):
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        data = request.get_json(silent=True) or request.form.to_dict()
        faculty = firebase_service.create_faculty(data)
        return jsonify({'success': True, 'faculty': faculty}), 201

    faculty_list = firebase_service.get_faculty()
    return jsonify(faculty_list)


@stitch_bp.route('/api/faculty/<faculty_id>', methods=['PUT', 'PATCH', 'DELETE'])
@login_required
def api_faculty_detail(faculty_id):
    """Handles Faculty Update and Delete."""
    if current_user.role not in (Role.ADMIN, Role.HOD):
        return jsonify({'success': False, 'error': 'Forbidden'}), 403

    if request.method == 'DELETE':
        success = firebase_service.delete_faculty(faculty_id)
        return jsonify({'success': success})

    data = request.get_json(silent=True) or request.form.to_dict()
    fac = firebase_service.update_faculty(faculty_id, data)
    return jsonify({'success': bool(fac), 'faculty': fac})


@stitch_bp.route('/api/hods', methods=['GET'])
@login_required
def api_hods():
    """Fetches HOD list."""
    hods = firebase_service.get_hods()
    return jsonify(hods)


@stitch_bp.route('/api/departments', methods=['GET', 'POST'])
@login_required
def api_departments():
    """Handles Department List and Creation."""
    if request.method == 'POST':
        if current_user.role != Role.ADMIN:
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        data = request.get_json(silent=True) or request.form.to_dict()
        dept = firebase_service.create_department(data)
        return jsonify({'success': True, 'department': dept}), 201

    depts = firebase_service.get_departments()
    return jsonify(depts)


@stitch_bp.route('/api/departments/<dept_id>', methods=['PUT', 'PATCH', 'DELETE'])
@login_required
def api_department_detail(dept_id):
    if current_user.role != Role.ADMIN:
        return jsonify({'success': False, 'error': 'Forbidden'}), 403

    if request.method == 'DELETE':
        success = firebase_service.delete_department(dept_id)
        return jsonify({'success': success})

    data = request.get_json(silent=True) or request.form.to_dict()
    dept = firebase_service.update_department(dept_id, data)
    return jsonify({'success': bool(dept), 'department': dept})


@stitch_bp.route('/api/courses', methods=['GET', 'POST'])
@login_required
def api_courses():
    if request.method == 'POST':
        if current_user.role != Role.ADMIN:
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        data = request.get_json(silent=True) or request.form.to_dict()
        c = firebase_service.create_course(data)
        return jsonify({'success': True, 'course': c}), 201

    return jsonify(firebase_service.get_courses())


@stitch_bp.route('/api/courses/<course_id>', methods=['DELETE'])
@login_required
def api_course_delete(course_id):
    if current_user.role != Role.ADMIN:
        return jsonify({'success': False, 'error': 'Forbidden'}), 403
    return jsonify({'success': firebase_service.delete_course(course_id)})


@stitch_bp.route('/api/subjects', methods=['GET', 'POST'])
@login_required
def api_subjects():
    if request.method == 'POST':
        if current_user.role not in (Role.ADMIN, Role.HOD):
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        data = request.get_json(silent=True) or request.form.to_dict()
        sub = firebase_service.create_subject(data)
        return jsonify({'success': True, 'subject': sub}), 201

    return jsonify(firebase_service.get_subjects())


@stitch_bp.route('/api/subjects/<subject_id>', methods=['DELETE'])
@login_required
def api_subject_delete(subject_id):
    if current_user.role not in (Role.ADMIN, Role.HOD):
        return jsonify({'success': False, 'error': 'Forbidden'}), 403
    return jsonify({'success': firebase_service.delete_subject(subject_id)})


@stitch_bp.route('/api/attendance', methods=['GET', 'POST'])
@login_required
def api_attendance():
    """Attendance tracking API."""
    if request.method == 'POST':
        if current_user.role not in (Role.ADMIN, Role.HOD, Role.FACULTY):
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        data = request.get_json(silent=True) or request.form.to_dict()
        rec = firebase_service.record_attendance(data)
        return jsonify({'success': True, 'data': rec}), 201

    return jsonify(firebase_service.get_attendance())


@stitch_bp.route('/api/results', methods=['GET', 'POST'])
@login_required
def api_results():
    """Examination results API."""
    if request.method == 'POST':
        if current_user.role not in (Role.ADMIN, Role.HOD, Role.FACULTY):
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        data = request.get_json(silent=True) or request.form.to_dict()
        res = firebase_service.record_results(data)
        return jsonify({'success': True, 'data': res}), 201

    return jsonify(firebase_service.get_results())


@stitch_bp.route('/api/notices', methods=['GET', 'POST'])
@login_required
def api_notices():
    """Notices API."""
    if request.method == 'POST':
        if current_user.role not in (Role.ADMIN, Role.HOD, Role.FACULTY):
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        data = request.get_json(silent=True) or request.form.to_dict()
        notice = firebase_service.create_notice(data)
        return jsonify({'success': True, 'notice': notice}), 201

    return jsonify(firebase_service.get_notices())


@stitch_bp.route('/api/notices/<notice_id>', methods=['DELETE'])
@login_required
def api_notice_delete(notice_id):
    if current_user.role not in (Role.ADMIN, Role.HOD, Role.FACULTY):
        return jsonify({'success': False, 'error': 'Forbidden'}), 403
    return jsonify({'success': firebase_service.delete_notice(notice_id)})


@stitch_bp.route('/api/materials', methods=['GET', 'POST'])
@stitch_bp.route('/api/study-materials', methods=['GET', 'POST'])
@login_required
def api_study_materials():
    if request.method == 'POST':
        if current_user.role not in (Role.ADMIN, Role.HOD, Role.FACULTY):
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        data = request.get_json(silent=True) or request.form.to_dict()
        mat = firebase_service.create_study_material(data)
        return jsonify({'success': True, 'material': mat}), 201

    return jsonify(firebase_service.get_study_materials())


@stitch_bp.route('/api/materials/<mat_id>', methods=['DELETE'])
@stitch_bp.route('/api/study-materials/<mat_id>', methods=['DELETE'])
@login_required
def api_study_material_delete(mat_id):
    if current_user.role not in (Role.ADMIN, Role.HOD, Role.FACULTY):
        return jsonify({'success': False, 'error': 'Forbidden'}), 403
    return jsonify({'success': firebase_service.delete_study_material(mat_id)})


@stitch_bp.route('/api/events', methods=['GET', 'POST'])
@login_required
def api_events():
    if request.method == 'POST':
        if current_user.role not in (Role.ADMIN, Role.HOD):
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        data = request.get_json(silent=True) or request.form.to_dict()
        ev = firebase_service.create_event(data)
        return jsonify({'success': True, 'event': ev}), 201

    return jsonify(firebase_service.get_events())


@stitch_bp.route('/api/events/<event_id>', methods=['DELETE'])
@login_required
def api_event_delete(event_id):
    if current_user.role not in (Role.ADMIN, Role.HOD):
        return jsonify({'success': False, 'error': 'Forbidden'}), 403
    return jsonify({'success': firebase_service.delete_event(event_id)})


@stitch_bp.route('/api/notifications', methods=['GET', 'POST'])
@login_required
def api_notifications():
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form.to_dict()
        data['user_id'] = current_user.id
        n = firebase_service.create_notification(data)
        return jsonify({'success': True, 'notification': n}), 201

    return jsonify(firebase_service.get_notifications(user_id=current_user.id))


@stitch_bp.route('/api/settings', methods=['GET', 'POST'])
@login_required
def api_settings():
    if request.method == 'POST':
        if current_user.role != Role.ADMIN:
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        data = request.get_json(silent=True) or request.form.to_dict()
        updated = firebase_service.update_settings(data)
        return jsonify({'success': True, 'settings': updated})

    return jsonify(firebase_service.get_settings())


@stitch_bp.route('/api/profile', methods=['GET', 'POST'])
@login_required
def api_profile():
    from app.extensions import db
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form.to_dict()
        if 'first_name' in data:
            current_user.first_name = data['first_name'].strip()
        if 'last_name' in data:
            current_user.last_name = data['last_name'].strip()
        if 'phone' in data:
            current_user.phone = data['phone'].strip()
        db.session.commit()

        # Sync user profile to Firebase
        firebase_service._rtdb_update(f"users/{current_user.id}", {
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'phone': current_user.phone
        })
        return jsonify({'success': True, 'message': 'Profile updated successfully.'})

    return jsonify({
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'phone': current_user.phone,
            'role': current_user.role
        }
    })


@stitch_bp.route('/api/firebase/status', methods=['GET'])
def api_firebase_status():
    """Returns Firebase Realtime Database connectivity status."""
    return jsonify({
        'firebase_connected': firebase_service.is_firebase_connected(),
        'database_url': firebase_service._database_url,
        'mode': 'Admin SDK' if firebase_service._rtdb_ref is not None else ('REST Secret' if firebase_service._db_secret else 'Dual-Store / Local')
    })


@stitch_bp.route('/api/firebase/sync', methods=['POST'])
@login_required
def api_firebase_sync():
    """Syncs existing institutional data to Firebase Realtime Database."""
    if current_user.role != Role.ADMIN:
        return jsonify({'success': False, 'error': 'Forbidden'}), 403
    res = firebase_service.sync_all_to_firebase()
    return jsonify(res)


@stitch_bp.errorhandler(firebase_service.FirebaseConnectionError)
def handle_firebase_connection_error(e):
    """Explicitly reports Firebase Realtime Database errors in production, preventing silent fallback."""
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Firebase Realtime Database Connection Error',
            'message': str(e),
            'database_url': firebase_service._database_url,
            'resolution': {
                'option_c_recommended': 'Copy Database Secret from Firebase Console > Project Settings > Service Accounts > Database Secrets and set as FIREBASE_DATABASE_SECRET in Vercel.',
                'option_a_service_account': 'In Google Cloud Console, override Organization Policy "Disable Service Account Key Creation" to Off for campus-connect-4e66c, generate key, and set as FIREBASE_SERVICE_ACCOUNT_KEY in Vercel.'
            }
        }), 503
    return f"""<!DOCTYPE html>
<html>
<head><title>Firebase Database Setup - Campus Connect</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
body{{font-family:'Inter',sans-serif;background:#0b1329;color:#fff;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;padding:24px;box-sizing:border-box;}}
.card{{max-width:640px;width:100%;background:#131d36;padding:36px;border-radius:16px;border:1px solid #334155;box-shadow:0 20px 40px rgba(0,0,0,0.6);}}
h2{{color:#38bdf8;margin-top:0;font-size:22px;display:flex;align-items:center;gap:10px;}}
p{{color:#94a3b8;font-size:14px;line-height:1.6;margin:12px 0;}}
.alert{{background:#1e1b4b;border-left:4px solid #6366f1;padding:14px 16px;border-radius:6px;font-size:13px;color:#c7d2fe;margin:16px 0;}}
.options{{display:flex;flex-direction:column;gap:14px;margin:20px 0;}}
.opt-box{{background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:16px;}}
.opt-title{{font-weight:600;color:#f8fafc;font-size:14px;margin-bottom:6px;display:flex;justify-content:space-between;}}
.badge{{background:#10b981;color:#022c22;font-size:11px;font-weight:700;padding:2px 8px;border-radius:12px;text-transform:uppercase;}}
.opt-desc{{color:#94a3b8;font-size:13px;line-height:1.5;margin:0;}}
code{{background:#1e293b;color:#38bdf8;padding:2px 6px;border-radius:4px;font-family:monospace;font-size:12px;}}
</style>
</head>
<body>
<div class="card">
    <h2>Firebase Database Configuration Required</h2>
    <p>The application is live on Vercel, but production database operations strictly require authenticated access to Firebase Realtime Database: <code>{firebase_service._database_url}</code>.</p>
    
    <div class="alert">
        <strong>Why did this appear?</strong> Local SQLite fallback is disabled in production to protect your institutional data from being lost on ephemeral serverless containers.
    </div>

    <div class="options">
        <div class="opt-box">
            <div class="opt-title">Option C: Firebase Database Secret <span class="badge">Recommended</span></div>
            <p class="opt-desc">
                If Google Cloud blocks service account key creation (<em>"Key creation is not allowed on this service account"</em>), use the <strong>Database Secret</strong> instead:<br>
                1. Open <a href="https://console.firebase.google.com/project/campus-connect-4e66c/settings/serviceaccounts/databasesecrets" target="_blank" style="color:#38bdf8;">Firebase Console &gt; Project Settings &gt; Service Accounts &gt; Database Secrets</a>.<br>
                2. Click <strong>Show</strong> next to your secret and copy it.<br>
                3. In Vercel Project Settings &gt; Environment Variables, add <code>FIREBASE_DATABASE_SECRET</code> with the secret value.
            </p>
        </div>

        <div class="opt-box">
            <div class="opt-title">Option A: Firebase Admin Service Account Key</div>
            <p class="opt-desc">
                To enable private key generation in Google Cloud:<br>
                1. Open <a href="https://console.cloud.google.com/iam-admin/orgpolicies/iam-disableServiceAccountKeyCreation?project=campus-connect-4e66c" target="_blank" style="color:#38bdf8;">GCP Org Policies: Disable Service Account Key Creation</a>.<br>
                2. Edit policy &gt; Override parent's policy &gt; Set enforcement to <strong>Off</strong> &gt; Save.<br>
                3. Generate private key in Firebase Console and set as <code>FIREBASE_SERVICE_ACCOUNT_KEY</code> in Vercel.
            </p>
        </div>
    </div>
</div>
</body>
</html>""", 503
