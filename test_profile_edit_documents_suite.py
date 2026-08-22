import pytest
import io
import os
from datetime import datetime
from app import create_app, db
from app.models.user import User, Role
from app.models.student import Student, StudentDocument
from app.models.faculty import Faculty, FacultyDocument
from app.models.department import Department
from app.models.course import Course
from app.models.academic import Semester, AcademicSession
from app.utils.uploads import format_profile_image_url, format_document_url


@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # Setup departments and courses
            dept = Department.query.filter_by(code="CSE").first()
            if not dept:
                dept = Department(name="Computer Science & Engineering", code="CSE")
                db.session.add(dept)
                db.session.commit()

            course = Course.query.filter_by(code="BT-CSE").first()
            if not course:
                course = Course(name="B.Tech Computer Science", code="BT-CSE", department_id=dept.id)
                db.session.add(course)
                db.session.commit()
            
            sem = Semester.query.filter_by(number=5).first()
            if not sem:
                sem = Semester(name="Semester 5", number=5)
                db.session.add(sem)
                db.session.commit()
            
            session = AcademicSession.query.filter_by(is_current=True).first()
            if not session:
                session = AcademicSession(name="2025-2026", start_year=2025, end_year=2026, is_current=True)
                db.session.add(session)
                db.session.commit()

            # Admin User
            admin_user = User(
                username="admin_test",
                email="admin@sitcoe.org.in",
                role=Role.ADMIN,
                first_name="Admin",
                last_name="System",
                is_active=True
            )
            admin_user.set_password("Admin@123")
            db.session.add(admin_user)
            db.session.commit()

            # Student User & Student
            std_user = User(
                username="std_test",
                email="std@sitcoe.org.in",
                role=Role.STUDENT,
                first_name="Rahul",
                last_name="Patil",
                is_active=True
            )
            std_user.set_password("Student@123")
            db.session.add(std_user)
            db.session.commit()

            std = Student(
                user_id=std_user.id,
                student_id="STU2025001",
                enrollment_no="EN2025001",
                admission_no="ADM2025001",
                roll_number="CSE001",
                first_name="Rahul",
                last_name="Patil",
                full_name="Rahul Patil",
                college_email="std@sitcoe.org.in",
                mobile="9876543210",
                department_id=dept.id,
                course_id=course.id,
                semester_id=sem.id,
                session_id=session.id,
                status="Active"
            )
            db.session.add(std)
            db.session.commit()

            # Faculty User & Faculty
            fac_user = User(
                username="fac_test",
                email="fac@sitcoe.org.in",
                role=Role.FACULTY,
                first_name="Amit",
                last_name="Kulkarni",
                is_active=True
            )
            fac_user.set_password("Faculty@123")
            db.session.add(fac_user)
            db.session.commit()

            fac = Faculty(
                user_id=fac_user.id,
                faculty_id="FAC2025001",
                employee_id="EMP001",
                first_name="Amit",
                last_name="Kulkarni",
                full_name="Amit Kulkarni",
                official_email="fac@sitcoe.org.in",
                mobile="9876543211",
                department_id=dept.id,
                designation="Assistant Professor",
                employment_type="Permanent",
                status="Active"
            )
            db.session.add(fac)
            db.session.commit()

            yield client
            db.session.remove()
            db.drop_all()


def test_url_formatting_utilities():
    """Verify format_profile_image_url and format_document_url normalize paths properly."""
    assert format_profile_image_url(None, "Rahul Patil").startswith("https://ui-avatars.com/")
    assert format_profile_image_url("https://cdn.example.com/photo.jpg") == "https://cdn.example.com/photo.jpg"
    assert format_profile_image_url("/static/uploads/photos/test.jpg") == "/static/uploads/photos/test.jpg"
    assert format_profile_image_url("uploads/photos/test.jpg") == "/static/uploads/photos/test.jpg"
    assert format_profile_image_url("photos/test.jpg") == "/static/uploads/photos/test.jpg"
    assert format_profile_image_url("test.jpg") == "/static/uploads/photos/test.jpg"

    assert format_document_url(None) is None
    assert format_document_url("uploads/documents/doc.pdf") == "/static/uploads/documents/doc.pdf"
    assert format_document_url("documents/doc.pdf") == "/static/uploads/documents/doc.pdf"


def test_student_and_faculty_model_properties(client):
    """Verify model properties return normalized URLs and fallback avatars."""
    std = Student.query.filter_by(student_id="STU2025001").first()
    assert "https://ui-avatars.com" in std.profile_image_url

    std.profile_photo = "uploads/photos/student_1.jpg"
    assert std.profile_image_url == "/static/uploads/photos/student_1.jpg"

    fac = Faculty.query.filter_by(faculty_id="FAC2025001").first()
    assert "https://ui-avatars.com" in fac.profile_image_url

    fac.profile_photo = "uploads/photos/fac_1.jpg"
    assert fac.profile_image_url == "/static/uploads/photos/fac_1.jpg"


def test_student_documents_crud_and_auth(client):
    """Verify document upload, listing, secure download, and deletion for students."""
    # Login as admin
    client.post('/auth/login', data={'username': 'admin_test', 'password': 'Admin@123'}, follow_redirects=True)
    std = Student.query.filter_by(student_id="STU2025001").first()

    # Upload document
    data = {
        'doc_type': '10th Marksheet',
        'title': 'Original 10th Marksheet',
        'document_file': (io.BytesIO(b"%PDF-1.4 test content"), 'marksheet.pdf')
    }
    resp = client.post(f'/student/{std.id}/upload-document', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert resp.status_code == 200

    doc = StudentDocument.query.filter_by(student_id=std.id).first()
    assert doc is not None
    assert doc.title == 'Original 10th Marksheet'
    assert doc.is_verified is True
    assert doc.uploaded_at is not None

    # Test download route
    dl_resp = client.get(f'/student/documents/{doc.id}/download')
    assert dl_resp.status_code == 200
    assert b"%PDF-1.4 test content" in dl_resp.data

    # Test delete route
    del_resp = client.post(f'/student/documents/{doc.id}/delete', follow_redirects=True)
    assert del_resp.status_code == 200
    assert StudentDocument.query.get(doc.id) is None


def test_faculty_documents_crud_and_auth(client):
    """Verify document upload, listing, secure download, and deletion for faculty."""
    client.post('/auth/login', data={'username': 'admin_test', 'password': 'Admin@123'}, follow_redirects=True)
    fac = Faculty.query.filter_by(faculty_id="FAC2025001").first()

    data = {
        'doc_type': 'Degree Certificate',
        'title': 'Master of Technology Degree',
        'document_file': (io.BytesIO(b"%PDF-1.4 faculty certificate"), 'degree.pdf')
    }
    resp = client.post(f'/faculty/{fac.id}/upload-document', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert resp.status_code == 200

    doc = FacultyDocument.query.filter_by(faculty_id=fac.id).first()
    assert doc is not None
    assert doc.title == 'Master of Technology Degree'
    assert doc.is_verified is True

    # Test download route
    dl_resp = client.get(f'/faculty/documents/{doc.id}/download')
    assert dl_resp.status_code == 200
    assert b"%PDF-1.4 faculty certificate" in dl_resp.data

    # Test delete route
    del_resp = client.post(f'/faculty/documents/{doc.id}/delete', follow_redirects=True)
    assert del_resp.status_code == 200
    assert FacultyDocument.query.get(doc.id) is None


def test_api_photo_urls_and_documents(client):
    """Verify REST APIs return normalized image URLs and provide documents endpoint."""
    login_resp = client.post('/api/v1/auth/login', json={'username': 'std_test', 'password': 'Student@123'})
    assert login_resp.status_code == 200
    data = login_resp.get_json()
    token = data['token']
    assert 'profile_photo' in data['student']
    assert data['student']['profile_photo'].startswith(('http://', 'https://', '/static/'))

    # Profile API
    headers = {'Authorization': f'Bearer {token}'}
    prof_resp = client.get('/api/v1/student/profile', headers=headers)
    assert prof_resp.status_code == 200
    prof_data = prof_resp.get_json()
    assert 'profile_photo' in prof_data['profile']

    # Documents API
    docs_resp = client.get('/api/v1/student/documents', headers=headers)
    assert docs_resp.status_code == 200
    assert docs_resp.get_json()['success'] is True


def test_student_and_faculty_list_actions_visible_to_admin(client):
    """Verify that Admin sees View, Edit, and Documents actions on Student and Faculty lists."""
    client.post('/auth/login', data={'username': 'admin_test', 'password': 'Admin@123'}, follow_redirects=True)
    std = Student.query.filter_by(student_id="STU2025001").first()
    fac = Faculty.query.filter_by(faculty_id="FAC2025001").first()

    # 1. Student List
    std_list_resp = client.get('/student')
    assert std_list_resp.status_code == 200
    std_html = std_list_resp.data.decode('utf-8')
    assert f"/student/{std.id}" in std_html
    assert f"/student/{std.id}/edit" in std_html
    assert f"/student/{std.id}/documents" in std_html

    # 2. Faculty List
    fac_list_resp = client.get('/faculty')
    assert fac_list_resp.status_code == 200
    fac_html = fac_list_resp.data.decode('utf-8')
    assert f"/faculty/{fac.id}" in fac_html
    assert f"/faculty/{fac.id}/edit" in fac_html
    assert f"/faculty/{fac.id}/documents" in fac_html


def test_student_edit_get_and_post_persistence(client):
    """Verify that Admin can view student edit form and persist updates."""
    client.post('/auth/login', data={'username': 'admin_test', 'password': 'Admin@123'}, follow_redirects=True)
    std = Student.query.filter_by(student_id="STU2025001").first()

    # 1. GET edit form
    edit_get = client.get(f'/student/{std.id}/edit')
    assert edit_get.status_code == 200
    assert b"Rahul" in edit_get.data
    assert b"Patil" in edit_get.data

    # 2. POST updates
    edit_data = {
        'first_name': 'Rahul-Modified',
        'middle_name': '',
        'last_name': 'Patil',
        'roll_no': 'CSE001-MOD',
        'department_id': std.department_id,
        'course_id': std.course_id,
        'semester_id': std.semester_id,
        'session_id': std.session_id,
        'division_id': 0,
        'mobile': '9988776655',
        'personal_email': 'rahul.mod@example.com',
        'status': 'Active',
        'gender': 'Male',
        'nationality': 'Indian',
        'profile_photo': (io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF updated photo content"), 'new_avatar.jpg')
    }
    edit_post = client.post(f'/student/{std.id}/edit', data=edit_data, content_type='multipart/form-data', follow_redirects=True)
    assert edit_post.status_code == 200

    # Verify persistence
    updated_std = Student.query.get(std.id)
    assert updated_std.first_name == 'Rahul-Modified'
    assert updated_std.mobile == '9988776655'
    assert updated_std.roll_no == 'CSE001-MOD'
    assert updated_std.profile_photo is not None
    assert 'photos/' in updated_std.profile_photo

    # Verify User synchronization
    assert updated_std.user.first_name == 'Rahul-Modified'
    assert updated_std.user.phone == '9988776655'
    assert updated_std.user.profile_image == updated_std.profile_photo


def test_faculty_edit_get_and_post_persistence(client):
    """Verify that Admin can view faculty edit form and persist updates."""
    client.post('/auth/login', data={'username': 'admin_test', 'password': 'Admin@123'}, follow_redirects=True)
    fac = Faculty.query.filter_by(faculty_id="FAC2025001").first()

    # 1. GET edit form
    edit_get = client.get(f'/faculty/{fac.id}/edit')
    assert edit_get.status_code == 200
    assert b"Amit" in edit_get.data
    assert b"Kulkarni" in edit_get.data

    # 2. POST updates
    edit_data = {
        'first_name': 'Amit-Updated',
        'middle_name': '',
        'last_name': 'Kulkarni',
        'designation': 'Associate Professor',
        'department_id': fac.department_id,
        'employment_type': 'Permanent',
        'qualification': 'Ph.D in Computer Science',
        'specialization': 'Artificial Intelligence',
        'experience_years': 8.5,
        'mobile': '9988776644',
        'personal_email': 'amit.ai@sitcoe.org.in',
        'status': 'Active',
        'gender': 'Male',
        'profile_photo': (io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF fac avatar"), 'fac_new.jpg')
    }
    edit_post = client.post(f'/faculty/{fac.id}/edit', data=edit_data, content_type='multipart/form-data', follow_redirects=True)
    assert edit_post.status_code == 200

    # Verify persistence
    updated_fac = Faculty.query.get(fac.id)
    assert updated_fac.first_name == 'Amit-Updated'
    assert updated_fac.designation == 'Associate Professor'
    assert updated_fac.mobile == '9988776644'
    assert updated_fac.experience_years == 8.5
    assert updated_fac.profile_photo is not None

    # Verify User synchronization
    assert updated_fac.user.first_name == 'Amit-Updated'
    assert updated_fac.user.phone == '9988776644'
    assert updated_fac.user.profile_image == updated_fac.profile_photo


def test_edit_routes_security_for_unauthorized_users(client):
    """Verify that Students and Faculty cannot access student/faculty edit endpoints."""
    std = Student.query.filter_by(student_id="STU2025001").first()
    fac = Faculty.query.filter_by(faculty_id="FAC2025001").first()

    # 1. Student login attempt to edit
    client.post('/auth/login', data={'username': 'std_test', 'password': 'Student@123'}, follow_redirects=True)
    resp1 = client.get(f'/student/{std.id}/edit', follow_redirects=False)
    assert resp1.status_code in (302, 403)

    resp2 = client.get(f'/faculty/{fac.id}/edit', follow_redirects=False)
    assert resp2.status_code in (302, 403)

    # 2. Faculty login attempt to edit student
    client.post('/auth/login', data={'username': 'fac_test', 'password': 'Faculty@123'}, follow_redirects=True)
    resp3 = client.get(f'/student/{std.id}/edit', follow_redirects=False)
    assert resp3.status_code in (302, 403)

