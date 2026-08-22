import pytest
from app import create_app
from app.extensions import db
from app.models.user import User, Role
from app.models.student import Student
from app.models.department import Department
from app.models.course import Course
from app.models.semester import Semester
from app.models.class_division import ClassDivision
from app.models.academic_session import AcademicSession
from app.models.mobile_config import (
    MobileAppConfig,
    MobileHomeSection,
    MobileQuickAction,
    MobileBanner,
    MobileFeatureFlag
)
from app.utils.api_auth import generate_api_token


@pytest.fixture
def client():
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            session = AcademicSession(name='2025-2026', start_year=2025, end_year=2026, is_current=True)
            dept = Department(name='Computer Engineering', code='CE')
            db.session.add_all([session, dept])
            db.session.flush()

            course = Course(name='B.Tech CSE', code='CSE', department_id=dept.id, duration_years=4, total_semesters=8)
            db.session.add(course)
            db.session.flush()

            sem = Semester.query.filter_by(number=1).first()
            if not sem:
                sem = Semester(number=1, name='Semester 1')
                db.session.add(sem)
                db.session.flush()

            div = ClassDivision(name='Div A', department_id=dept.id, course_id=course.id, semester_id=sem.id, session_id=session.id)
            db.session.add(div)
            db.session.flush()

            # Student
            user = User(username='STU_TEST_01', email='stutest01@example.com', role=Role.STUDENT, is_active=True)
            user.set_password('Pass1234')
            db.session.add(user)
            db.session.flush()

            student = Student(
                user_id=user.id,
                student_id='STU_TEST_01',
                enrollment_no='ENR_TEST_01',
                admission_number='ADM_TEST_01',
                roll_no='101',
                first_name='Alice',
                last_name='Smith',
                full_name='Alice Smith',
                college_email='stutest01@example.com',
                mobile='9876543210',
                department_id=dept.id,
                course_id=course.id,
                semester_id=sem.id,
                division_id=div.id,
                session_id=session.id,
                status='Active'
            )
            db.session.add(student)

            # Admin
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(username='admin', email='admin@example.com', role=Role.ADMIN, is_active=True)
                db.session.add(admin_user)
            admin_user.set_password('AdminPass123')

            db.session.commit()

            yield client

            db.session.remove()
            db.drop_all()


def test_auth_and_unauthorized_scenarios(client):
    """Test 1: Valid auth vs unauthorized vs invalid token on /api/v1/mobile/config."""
    # A. Unauthorized (no token)
    res_no_auth = client.get('/api/v1/mobile/config')
    assert res_no_auth.status_code == 401
    data_no_auth = res_no_auth.get_json()
    assert data_no_auth['success'] is False

    # B. Invalid / malformed token
    res_bad_token = client.get('/api/v1/mobile/config', headers={'Authorization': 'Bearer invalid.token.xyz'})
    assert res_bad_token.status_code == 401
    assert res_bad_token.get_json()['success'] is False

    # C. Valid Student token
    with client.application.app_context():
        user = User.query.filter_by(username='STU_TEST_01').first()
        token = generate_api_token(user)

    res_valid = client.get('/api/v1/mobile/config', headers={'Authorization': f'Bearer {token}'})
    assert res_valid.status_code == 200
    data = res_valid.get_json()
    assert data['success'] is True
    assert data['config']['maintenance_mode'] is False
    assert len(data['config']['home_sections']) == 7
    assert len(data['config']['quick_actions']) == 8
    assert data['config']['feature_flags']['enable_photo_upload'] is True


def test_erp_admin_control_and_realtime_reflection(client):
    """Test 2: Admin configures sections, maintenance, and banners in ERP; Student receives exact payload."""
    with client.application.app_context():
        user = User.query.filter_by(username='STU_TEST_01').first()
        student_token = generate_api_token(user)

    # 1. Login as Admin
    login_resp = client.post('/auth/login', data={'username': 'admin', 'password': 'AdminPass123'}, follow_redirects=True)
    assert login_resp.status_code == 200

    # 2. Update config via ERP Admin form: Turn ON Maintenance Mode, update min version, reorder sections
    update_resp = client.post('/admin/mobile-management', data={
        'action_type': 'save_config',
        'config_version': '2.0',
        'maintenance_mode': 'on',
        'maintenance_message': 'Campus ERP is undergoing scheduled maintenance.',
        'min_app_version': '1.1.0',
        'update_url': 'https://college.edu/app-download',
        'section_header_enabled': 'on',
        'section_header_order': '1',
        'section_stats_enabled': 'on',
        'section_stats_order': '2',
        'flag_enable_photo_upload_enabled': 'on',
        'action_attendance_enabled': 'on',
        'action_attendance_order': '1'
    }, follow_redirects=True)
    assert update_resp.status_code == 200

    # 3. Create a Banner
    banner_resp = client.post('/admin/mobile-management/banner/create', data={
        'title': 'National Science Exhibition 2026',
        'subtitle': 'Register at Innovation Block',
        'image_url': 'https://college.edu/banner.jpg',
        'action_url': 'events',
        'display_order': '1'
    }, follow_redirects=True)
    assert banner_resp.status_code == 200

    # 4. Student queries /api/v1/mobile/config - verify exact values reflected
    res = client.get('/api/v1/mobile/config', headers={'Authorization': f'Bearer {student_token}'})
    assert res.status_code == 200
    cfg = res.get_json()['config']
    assert cfg['config_version'] == '2.0'
    assert cfg['maintenance_mode'] is True
    assert cfg['maintenance_message'] == 'Campus ERP is undergoing scheduled maintenance.'
    assert cfg['min_app_version'] == '1.1.0'
    assert cfg['update_url'] == 'https://college.edu/app-download'
    assert len(cfg['banners']) == 1
    assert cfg['banners'][0]['title'] == 'National Science Exhibition 2026'
    assert cfg['banners'][0]['action_url'] == 'events'
