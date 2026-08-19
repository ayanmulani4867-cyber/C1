"""
Comprehensive Verification Test Suite for CampusConnect ERP Authentication and Session System.
Tests all 16 verification criteria required for multi-role session persistence and authorization.
"""
import os
import sys
import json
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User, Role
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.department import Department
from app.models.course import Course
from app.models.semester import Semester
from app.models.academic_session import AcademicSession
from app.utils.db_ops import initialize_database_schema, seed_database_safely
from app.utils.api_auth import generate_api_token, verify_api_token


class CampusConnectAuthTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        db.create_all()
        initialize_database_schema()
        seed_database_safely()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        self.client = self.app.test_client()

    # -------------------------------------------------------------
    # 1. ADMIN LOGIN, REFRESH, LOGOUT
    # -------------------------------------------------------------
    def test_01_admin_auth_lifecycle(self):
        # 1. Admin Login
        login_res = self.client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'admin'
        })
        self.assertEqual(login_res.status_code, 200)
        data = login_res.get_json()
        self.assertTrue(data['success'])
        admin_token = data['token']
        self.assertEqual(data['user']['role'], Role.ADMIN)
        self.assertEqual(data['user']['username'], 'admin')

        # 2. Admin Refresh (Session Restoration via /api/auth/me)
        me_res = self.client.get('/api/auth/me', headers={
            'Authorization': f'Bearer {admin_token}'
        })
        self.assertEqual(me_res.status_code, 200)
        me_data = me_res.get_json()
        self.assertTrue(me_data['success'])
        self.assertEqual(me_data['user']['role'], Role.ADMIN)
        self.assertEqual(me_data['user']['username'], 'admin')

        # 3. Admin Logout
        logout_res = self.client.post('/api/auth/logout', headers={
            'Authorization': f'Bearer {admin_token}'
        })
        self.assertEqual(logout_res.status_code, 200)

    # -------------------------------------------------------------
    # 2. HOD LOGIN, REFRESH, LOGOUT
    # -------------------------------------------------------------
    def test_02_hod_auth_lifecycle(self):
        # 4. HOD Login
        login_res = self.client.post('/api/auth/login', json={
            'username': 'hod_cse',
            'password': 'hod123'
        })
        self.assertEqual(login_res.status_code, 200)
        data = login_res.get_json()
        self.assertTrue(data['success'])
        hod_token = data['token']
        self.assertEqual(data['user']['role'], Role.HOD)
        self.assertIsNotNone(data.get('faculty'))
        self.assertTrue('HOD' in data['faculty']['designation'].upper() or 'HEAD OF DEPARTMENT' in data['faculty']['designation'].upper())

        # 5. HOD Refresh (Session Restoration via /api/auth/me)
        me_res = self.client.get('/api/auth/me', headers={
            'Authorization': f'Bearer {hod_token}'
        })
        self.assertEqual(me_res.status_code, 200)
        me_data = me_res.get_json()
        self.assertTrue(me_data['success'])
        self.assertEqual(me_data['user']['role'], Role.HOD)
        self.assertEqual(me_data['faculty']['faculty_id'], 'FAC-CSE-001')

        # 6. HOD Logout
        logout_res = self.client.post('/api/auth/logout', headers={
            'Authorization': f'Bearer {hod_token}'
        })
        self.assertEqual(logout_res.status_code, 200)

    # -------------------------------------------------------------
    # 3. FACULTY LOGIN, REFRESH, LOGOUT
    # -------------------------------------------------------------
    def test_03_faculty_auth_lifecycle(self):
        # 7. Faculty Login
        login_res = self.client.post('/api/auth/login', json={
            'username': 'faculty',
            'password': 'faculty123'
        })
        self.assertEqual(login_res.status_code, 200)
        data = login_res.get_json()
        self.assertTrue(data['success'])
        fac_token = data['token']
        self.assertEqual(data['user']['role'], Role.FACULTY)
        self.assertIsNotNone(data.get('faculty'))

        # 8. Faculty Refresh (Session Restoration via /api/auth/me)
        me_res = self.client.get('/api/auth/me', headers={
            'Authorization': f'Bearer {fac_token}'
        })
        self.assertEqual(me_res.status_code, 200)
        me_data = me_res.get_json()
        self.assertTrue(me_data['success'])
        self.assertEqual(me_data['user']['role'], Role.FACULTY)
        self.assertEqual(me_data['faculty']['faculty_id'], 'FAC-CSE-002')

        # 9. Faculty Logout
        logout_res = self.client.post('/api/auth/logout', headers={
            'Authorization': f'Bearer {fac_token}'
        })
        self.assertEqual(logout_res.status_code, 200)

    # -------------------------------------------------------------
    # 4. STUDENT LOGIN, REFRESH, LOGOUT
    # -------------------------------------------------------------
    def test_04_student_auth_lifecycle(self):
        # 10. Student Login
        login_res = self.client.post('/api/auth/login', json={
            'username': 'student',
            'password': 'student123'
        })
        self.assertEqual(login_res.status_code, 200)
        data = login_res.get_json()
        self.assertTrue(data['success'])
        stu_token = data['token']
        self.assertEqual(data['user']['role'], Role.STUDENT)
        self.assertIsNotNone(data.get('student'))
        self.assertEqual(data['student']['student_id'], 'STD-2023-0101')

        # 11. Student Refresh (Session Restoration via /api/auth/me)
        me_res = self.client.get('/api/auth/me', headers={
            'Authorization': f'Bearer {stu_token}'
        })
        self.assertEqual(me_res.status_code, 200)
        me_data = me_res.get_json()
        self.assertTrue(me_data['success'])
        self.assertEqual(me_data['user']['role'], Role.STUDENT)
        self.assertEqual(me_data['student']['roll_no'], '23CS401')

        # 12. Student Logout
        logout_res = self.client.post('/api/auth/logout', headers={
            'Authorization': f'Bearer {stu_token}'
        })
        self.assertEqual(logout_res.status_code, 200)

    # -------------------------------------------------------------
    # 5. CROSS-BROWSER SESSION ISOLATION
    # -------------------------------------------------------------
    def test_05_cross_browser_session_isolation(self):
        # Simulate 4 different browsers logging in simultaneously
        admin_login = self.client.post('/api/auth/login', json={'username': 'admin', 'password': 'admin'}).get_json()
        hod_login = self.client.post('/api/auth/login', json={'username': 'hod_cse', 'password': 'hod123'}).get_json()
        faculty_login = self.client.post('/api/auth/login', json={'username': 'faculty', 'password': 'faculty123'}).get_json()
        student_login = self.client.post('/api/auth/login', json={'username': 'student', 'password': 'student123'}).get_json()

        admin_token = admin_login['token']
        hod_token = hod_login['token']
        faculty_token = faculty_login['token']
        student_token = student_login['token']

        # Query /api/auth/me for each simulated device / browser
        # Browser A (Admin)
        res_a = self.client.get('/api/auth/me', headers={'Authorization': f'Bearer {admin_token}'}).get_json()
        self.assertEqual(res_a['user']['role'], Role.ADMIN)

        # Browser B (Student)
        res_b = self.client.get('/api/auth/me', headers={'Authorization': f'Bearer {student_token}'}).get_json()
        self.assertEqual(res_b['user']['role'], Role.STUDENT)

        # Browser C (Faculty)
        res_c = self.client.get('/api/auth/me', headers={'Authorization': f'Bearer {faculty_token}'}).get_json()
        self.assertEqual(res_c['user']['role'], Role.FACULTY)

        # Browser D (HOD)
        res_d = self.client.get('/api/auth/me', headers={'Authorization': f'Bearer {hod_token}'}).get_json()
        self.assertEqual(res_d['user']['role'], Role.HOD)

        # Re-verify Browser A to ensure no session cross-contamination
        res_a_again = self.client.get('/api/auth/me', headers={'Authorization': f'Bearer {admin_token}'}).get_json()
        self.assertEqual(res_a_again['user']['role'], Role.ADMIN)
        self.assertEqual(res_a_again['user']['username'], 'admin')

    # -------------------------------------------------------------
    # 6. PROTECTED API AUTHORIZATION & ROLE ENFORCEMENT
    # -------------------------------------------------------------
    def test_06_role_authorization_enforcement(self):
        admin_token = self.client.post('/api/auth/login', json={'username': 'admin', 'password': 'admin'}).get_json()['token']
        hod_token = self.client.post('/api/auth/login', json={'username': 'hod_cse', 'password': 'hod123'}).get_json()['token']
        faculty_token = self.client.post('/api/auth/login', json={'username': 'faculty', 'password': 'faculty123'}).get_json()['token']
        student_token = self.client.post('/api/auth/login', json={'username': 'student', 'password': 'student123'}).get_json()['token']

        # 14a. Student -> Admin API (/api/admin/students) => 403 Forbidden
        stu_to_admin_res = self.client.post('/api/admin/students', headers={
            'Authorization': f'Bearer {student_token}'
        }, json={
            'first_name': 'Unauthorized',
            'last_name': 'Test',
            'college_email': 'unauth.student@campusconnect.edu',
            'mobile': '9876543210'
        })
        self.assertEqual(stu_to_admin_res.status_code, 403)
        self.assertFalse(stu_to_admin_res.get_json()['success'])

        # 14b. Faculty -> Admin API (/api/admin/students) => 403 Forbidden
        fac_to_admin_res = self.client.post('/api/admin/students', headers={
            'Authorization': f'Bearer {faculty_token}'
        }, json={
            'first_name': 'Unauthorized',
            'last_name': 'Faculty',
            'college_email': 'unauth.fac@campusconnect.edu',
            'mobile': '9876543210'
        })
        self.assertEqual(fac_to_admin_res.status_code, 403)
        self.assertFalse(fac_to_admin_res.get_json()['success'])

        # 14c. HOD -> Admin API (/api/admin/students) => 403 Forbidden
        hod_to_admin_res = self.client.post('/api/admin/students', headers={
            'Authorization': f'Bearer {hod_token}'
        }, json={
            'first_name': 'Unauthorized',
            'last_name': 'HOD',
            'college_email': 'unauth.hod@campusconnect.edu',
            'mobile': '9876543210'
        })
        self.assertEqual(hod_to_admin_res.status_code, 403)

        # 14d. Admin -> Admin API (/api/admin/students) => 200/201 ALLOWED
        admin_create_res = self.client.post('/api/admin/students', headers={
            'Authorization': f'Bearer {admin_token}'
        }, json={
            'first_name': 'Authorized',
            'last_name': 'Enrollee',
            'college_email': 'authorized.enrollee@campusconnect.edu',
            'mobile': '9876599999',
            'department_id': 'dept-cse'
        })
        self.assertIn(admin_create_res.status_code, [200, 201])
        self.assertTrue(admin_create_res.get_json()['success'])

    # -------------------------------------------------------------
    # 7. TAMPERING & SECURITY CHECKS
    # -------------------------------------------------------------
    def test_07_tampering_and_direct_url_security(self):
        # 15. Fake/Manipulated Bearer token => 401 Unauthorized
        tampered_res = self.client.get('/api/auth/me', headers={
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake.signature'
        })
        self.assertEqual(tampered_res.status_code, 401)
        self.assertFalse(tampered_res.get_json()['success'])

        # 16. Unauthenticated Direct API Access => 401 Unauthorized
        no_auth_res = self.client.get('/api/auth/me')
        self.assertEqual(no_auth_res.status_code, 401)
        self.assertFalse(no_auth_res.get_json()['success'])

        no_auth_admin = self.client.post('/api/admin/students', json={'first_name': 'Test'})
        self.assertEqual(no_auth_admin.status_code, 401)


if __name__ == '__main__':
    unittest.main()
