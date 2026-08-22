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
from app.models.mobile_config import MobileAppConfig, MobileHomeSection, MobileQuickAction, MobileBanner, MobileFeatureFlag
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
            
            # Setup session & structures
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

            # Create Student & User
            user = User(
                username='STU001',
                email='stu001@example.com',
                role=Role.STUDENT,
                is_active=True
            )
            user.set_password('Password123')
            db.session.add(user)
            db.session.flush()

            student = Student(
                user_id=user.id,
                student_id='STU001',
                enrollment_no='ENR001',
                admission_number='ADM001',
                roll_no='101',
                first_name='John',
                last_name='Doe',
                full_name='John Doe',
                college_email='stu001@example.com',
                mobile='9876543210',
                department_id=dept.id,
                course_id=course.id,
                semester_id=sem.id,
                division_id=div.id,
                session_id=session.id,
                status='Active'
            )
            db.session.add(student)


            # Admin User
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    role=Role.ADMIN,
                    is_active=True
                )
                db.session.add(admin_user)
            admin_user.set_password('AdminPass123')


            db.session.commit()

            yield client

            db.session.remove()
            db.drop_all()


def test_mobile_config_api(client):
    """Verify /api/v1/mobile/config returns valid remote config structure with Bearer token."""
    with client.application.app_context():
        user = User.query.filter_by(username='STU001').first()
        token = generate_api_token(user)

    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/api/v1/mobile/config', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'config' in data
    cfg = data['config']
    assert 'home_sections' in cfg
    assert len(cfg['home_sections']) >= 5
    assert 'quick_actions' in cfg
    assert len(cfg['quick_actions']) >= 5
    assert 'feature_flags' in cfg
    assert cfg['feature_flags']['enable_photo_upload'] is True


def test_admin_mobile_management_view(client):
    """Verify admin can view and update mobile configuration."""
    # Login as admin
    login_resp = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'AdminPass123'
    }, follow_redirects=True)
    assert login_resp.status_code == 200

    # View mobile management
    resp = client.get('/admin/mobile-management')
    assert resp.status_code == 200
    assert b'Mobile App Management' in resp.data

    # Create a mobile banner
    banner_resp = client.post('/admin/mobile-management/banner/create', data={
        'title': 'Hackathon 2026',
        'subtitle': 'Register now',
        'display_order': '1'
    }, follow_redirects=True)
    assert banner_resp.status_code == 200
    assert b'Hackathon 2026' in banner_resp.data
