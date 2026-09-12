"""
Comprehensive Automated Test Suite for Stitch Frontend + Flask Backend + Firebase RTDB Integration
Tests all 35 acceptance criteria points systematically using Flask Test Client.
"""
import unittest
import json
from app import create_app
from app.extensions import db
from app.models.user import User, Role
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.department import Department
from app.models.course import Course
from app.models.subject import Subject
from app.services import firebase_service


class TestStitchIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        cls.client = cls.app.test_client()

        db.create_all()

        # Create master admin
        cls.admin = User.query.filter_by(username='admin').first()
        if not cls.admin:
            cls.admin = User(
                username='admin',
                email='admin@sitcoe.ac.in',
                first_name='System',
                last_name='Admin',
                role=Role.ADMIN,
                is_active=True
            )
            db.session.add(cls.admin)
        cls.admin.set_password('Admin@123')

        # Create HOD
        cls.hod_user = User.query.filter_by(username='hod_cse').first()
        if not cls.hod_user:
            cls.hod_user = User(
                username='hod_cse',
                email='hod.cse@sitcoe.ac.in',
                first_name='Dr. Rajesh',
                last_name='Sharma',
                role=Role.HOD,
                is_active=True
            )
            db.session.add(cls.hod_user)
        cls.hod_user.set_password('Hod@123')

        # Create Faculty
        cls.faculty_user = User.query.filter_by(username='faculty1').first()
        if not cls.faculty_user:
            cls.faculty_user = User(
                username='faculty1',
                email='faculty1@sitcoe.ac.in',
                first_name='Prof. Amit',
                last_name='Deshmukh',
                role=Role.FACULTY,
                is_active=True
            )
            db.session.add(cls.faculty_user)
        cls.faculty_user.set_password('Faculty@123')

        # Create Student
        cls.student_user = User.query.filter_by(username='student1').first()
        if not cls.student_user:
            cls.student_user = User(
                username='student1',
                email='student1@sitcoe.ac.in',
                first_name='Rohan',
                last_name='Kulkarni',
                role=Role.STUDENT,
                is_active=True
            )
            db.session.add(cls.student_user)
        cls.student_user.set_password('Student@123')

        # Create initial Department
        cls.dept = Department.query.filter_by(code='CSE').first()
        if not cls.dept:
            cls.dept = Department(name='Computer Science & Engineering', code='CSE', is_active=True)
            db.session.add(cls.dept)
            db.session.flush()

        # Create initial Course
        cls.course = Course.query.filter_by(code='BTECH_CSE').first()
        if not cls.course:
            cls.course = Course(name='B.Tech CSE', code='BTECH_CSE', department_id=cls.dept.id, duration_years=4, is_active=True)
            db.session.add(cls.course)
            db.session.flush()

        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        cls.app_context.pop()

    def login_as(self, username, password):
        """Helper to log in using real /api/login endpoint."""
        return self.client.post('/api/login', json={
            'identifier': username,
            'password': password
        })

    # 1. System Health & Firebase Status
    def test_01_health_and_firebase_status(self):
        resp = self.client.get('/health')
        self.assertEqual(resp.status_code, 200)

        fb_resp = self.client.get('/api/firebase/status')
        self.assertEqual(fb_resp.status_code, 200)
        data = fb_resp.get_json()
        self.assertIn('database_url', data)
        self.assertIn('campus-connect-4e66c-default-rtdb.firebaseio.com', data['database_url'])

    # 2. Login with valid and invalid credentials
    def test_02_authentication(self):
        # Invalid credentials
        bad_resp = self.login_as('admin', 'WrongPassword!')
        self.assertEqual(bad_resp.status_code, 401)

        # Valid Admin login
        admin_resp = self.login_as('admin', 'Admin@123')
        self.assertEqual(admin_resp.status_code, 200)
        data = admin_resp.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['role'], 'ADMIN')

    # 3. Stitch Frontend Page Serving
    def test_03_stitch_pages_served(self):
        # Ensure logged out so /login renders directly instead of redirecting
        self.client.get('/auth/logout')
        resp = self.client.get('/login')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'SHARAD INSTITUTE OF TECHNOLOGY', resp.data)
        self.assertIn(b'/static/js/stitch_connector.js', resp.data)

    # 4. Role Authorization & 403 enforcement
    def test_04_role_authorization_and_403(self):
        # Unauthenticated access to /admin/dashboard redirects to login
        self.client.get('/auth/logout')
        unauth_resp = self.client.get('/admin/dashboard')
        self.assertEqual(unauth_resp.status_code, 302)

        # Login as student
        self.login_as('student1', 'Student@123')

        # Student accessing student dashboard -> 200
        student_page = self.client.get('/student/dashboard')
        self.assertEqual(student_page.status_code, 200)
        self.assertIn(b'/static/js/stitch_connector.js', student_page.data)

        # Student attempting to access /admin/dashboard -> 403 Forbidden
        admin_attempt = self.client.get('/admin/dashboard')
        self.assertEqual(admin_attempt.status_code, 403)
        self.assertIn(b'403 Forbidden', admin_attempt.data)

        # Student attempting to access /admin/students API -> 403 Forbidden
        api_attempt = self.client.post('/api/students', json={'first_name': 'Hacker'})
        self.assertEqual(api_attempt.status_code, 403)

    # 5. Admin Full Access & Dashboard Stats
    def test_05_admin_dashboard_stats(self):
        self.login_as('admin', 'Admin@123')
        resp = self.client.get('/admin/dashboard')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Executive Governance &amp; Operations', resp.data)

        stats_resp = self.client.get('/api/dashboard/stats')
        self.assertEqual(stats_resp.status_code, 200)
        stats = stats_resp.get_json()
        self.assertEqual(stats['role'], 'ADMIN')
        self.assertIn('total_students', stats)
        self.assertIn('total_faculty', stats)

    # 6. Student CRUD
    def test_06_student_crud(self):
        self.login_as('admin', 'Admin@123')

        # Create
        create_resp = self.client.post('/api/students', json={
            'student_id': '24SIT999',
            'first_name': 'Priya',
            'last_name': 'Sharma',
            'email': 'priya.sharma@sitcoe.ac.in',
            'semester': 4,
            'cgpa': 9.15,
            'attendance_percentage': 92.5
        })
        self.assertEqual(create_resp.status_code, 201)
        created_data = create_resp.get_json()
        self.assertTrue(created_data['success'])
        student_id = created_data['student']['id']

        # Read
        list_resp = self.client.get('/api/students')
        self.assertEqual(list_resp.status_code, 200)
        students = list_resp.get_json()
        self.assertTrue(any(s['id'] == student_id for s in students))

        # Update
        up_resp = self.client.put(f'/api/students/{student_id}', json={
            'first_name': 'Priyanka',
            'cgpa': 9.40
        })
        self.assertEqual(up_resp.status_code, 200)
        up_data = up_resp.get_json()
        self.assertEqual(up_data['student']['first_name'], 'Priyanka')

        # Delete
        del_resp = self.client.delete(f'/api/students/{student_id}')
        self.assertEqual(del_resp.status_code, 200)
        self.assertTrue(del_resp.get_json()['success'])

    # 7. Faculty CRUD
    def test_07_faculty_crud(self):
        self.login_as('admin', 'Admin@123')

        # Create
        create_resp = self.client.post('/api/faculty', json={
            'employee_id': 'FAC_TEST_01',
            'first_name': 'Dr. Vikram',
            'last_name': 'Mehta',
            'email': 'vikram.mehta@sitcoe.ac.in',
            'designation': 'Associate Professor',
            'qualification': 'Ph.D in AI/ML'
        })
        self.assertEqual(create_resp.status_code, 201)
        fac_id = create_resp.get_json()['faculty']['id']

        # Read
        list_resp = self.client.get('/api/faculty')
        self.assertEqual(list_resp.status_code, 200)

        # Delete
        del_resp = self.client.delete(f'/api/faculty/{fac_id}')
        self.assertEqual(del_resp.status_code, 200)

    # 8. Department CRUD
    def test_08_department_crud(self):
        self.login_as('admin', 'Admin@123')

        create_resp = self.client.post('/api/departments', json={
            'name': 'Robotics and Automation',
            'code': 'ROBO'
        })
        self.assertEqual(create_resp.status_code, 201)
        dept_id = create_resp.get_json()['department']['id']

        # Read
        list_resp = self.client.get('/api/departments')
        self.assertEqual(list_resp.status_code, 200)

        # Delete
        del_resp = self.client.delete(f'/api/departments/{dept_id}')
        self.assertEqual(del_resp.status_code, 200)

    # 9. Course & Subject CRUD
    def test_09_course_and_subject_crud(self):
        self.login_as('admin', 'Admin@123')

        # Course
        c_resp = self.client.post('/api/courses', json={
            'name': 'M.Tech Data Science',
            'code': 'MTECH_DS'
        })
        self.assertEqual(c_resp.status_code, 201)
        c_id = c_resp.get_json()['course']['id']

        # Subject
        s_resp = self.client.post('/api/subjects', json={
            'name': 'Deep Learning Neural Networks',
            'code': 'DL101',
            'credits': 4
        })
        self.assertEqual(s_resp.status_code, 201)
        s_id = s_resp.get_json()['subject']['id']

        # Cleanup
        self.client.delete(f'/api/subjects/{s_id}')
        self.client.delete(f'/api/courses/{c_id}')

    # 10. Attendance & Results Recording
    def test_10_attendance_and_results(self):
        self.login_as('admin', 'Admin@123')

        # Attendance
        att_post = self.client.post('/api/attendance', json={
            'records': [
                {'student_id': 1, 'state': 'Present'},
                {'student_id': 2, 'state': 'Present'}
            ]
        })
        self.assertEqual(att_post.status_code, 201)

        att_get = self.client.get('/api/attendance')
        self.assertEqual(att_get.status_code, 200)

        # Results
        res_post = self.client.post('/api/results', json={
            'subject': 'Operating Systems',
            'results': [
                {'student_id': 1, 'cie1': 19, 'cie2': 18, 'tw': 23, 'ese': 55}
            ]
        })
        self.assertEqual(res_post.status_code, 201)

        res_get = self.client.get('/api/results')
        self.assertEqual(res_get.status_code, 200)

    # 11. Notices, Materials & Events
    def test_11_notices_materials_events(self):
        self.login_as('admin', 'Admin@123')

        # Notice
        n_resp = self.client.post('/api/notices', json={
            'title': 'Autonomous Examination Form Notice',
            'content': 'All students must verify their examination forms by Friday.',
            'category': 'Examination'
        })
        self.assertEqual(n_resp.status_code, 201)
        nid = n_resp.get_json()['notice']['id']

        # Material
        m_resp = self.client.post('/api/study-materials', json={
            'title': 'Module 3 Lecture Slides',
            'description': 'Distributed Architecture notes.'
        })
        self.assertEqual(m_resp.status_code, 201)
        mid = m_resp.get_json()['material']['id']

        # Event
        e_resp = self.client.post('/api/events', json={
            'title': 'Annual Tech Symposium 2025',
            'venue': 'APJ Abdul Kalam Auditorium',
            'description': 'Inter-collegiate engineering hackathon.'
        })
        self.assertEqual(e_resp.status_code, 201)
        eid = e_resp.get_json()['event']['id']

        # Cleanup
        self.client.delete(f'/api/notices/{nid}')
        self.client.delete(f'/api/study-materials/{mid}')
        self.client.delete(f'/api/events/{eid}')

    # 12. Profile, Settings, Notifications
    def test_12_profile_and_settings(self):
        self.login_as('admin', 'Admin@123')

        # Profile update
        prof_resp = self.client.post('/api/profile', json={
            'first_name': 'Lead',
            'last_name': 'Administrator',
            'phone': '+91 99999 11111'
        })
        self.assertEqual(prof_resp.status_code, 200)

        # Settings
        set_resp = self.client.post('/api/settings', json={
            'maintenance_mode': False,
            'academic_year': '2024-25'
        })
        self.assertEqual(set_resp.status_code, 200)

        # Notifications
        notif_resp = self.client.get('/api/notifications')
        self.assertEqual(notif_resp.status_code, 200)

    # 13. Logout
    def test_13_logout(self):
        resp = self.client.post('/api/auth/logout')
        self.assertEqual(resp.status_code, 200)


if __name__ == '__main__':
    unittest.main()
