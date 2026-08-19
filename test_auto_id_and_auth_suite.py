"""
Campus Connect ERP - End-to-End Verification Test Suite
Tests:
1. Automatic Student ID, Admission No, Enrollment No, and Roll No generation on enrollment.
2. Automatic Faculty Employee ID generation on registration.
3. Multi-identifier authentication (Email, Student ID, Admission No, Enrollment No, Employee ID).
4. Password set to mobile number with must_change_password enforcement.
5. Android mobile API restriction (students only).
6. Dual casing (snake_case + camelCase) in API responses.
7. Admin automated registration API endpoints.
"""
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import unittest
from datetime import date
from app import create_app
from app.extensions import db
from app.models.user import User, Role
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.department import Department
from app.models.course import Course
from app.models.semester import Semester
from app.models.academic_session import AcademicSession
from app.models.class_division import ClassDivision
from app.utils.id_generator import (
    generate_student_id,
    generate_admission_number,
    generate_enrollment_number,
    generate_roll_number,
    generate_faculty_employee_id,
    backfill_missing_identifiers
)
from app.utils.db_ops import initialize_database_schema, seed_database_safely


class AutoIdAndAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        db.create_all()
        initialize_database_schema()
        seed_database_safely()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_id_generator_functions(self):
        """Test individual deterministic ID generation functions."""
        stu_id1 = generate_student_id(academic_year=2026)
        self.assertTrue(stu_id1.startswith("STU2026"))
        self.assertEqual(len(stu_id1), 11)  # STU20260001 (11 chars)

        adm_id1 = generate_admission_number(academic_year=2026)
        self.assertTrue(adm_id1.startswith("ADM2026"))
        self.assertEqual(len(adm_id1), 11)

        enr_id1 = generate_enrollment_number(academic_year=2026)
        self.assertTrue(enr_id1.startswith("ENR2026"))
        self.assertEqual(len(enr_id1), 11)

        emp_id1 = generate_faculty_employee_id(year=2026)
        self.assertTrue(emp_id1.startswith("EMP2026"))
        self.assertEqual(len(emp_id1), 11)

        # Roll Number generation
        dept = Department.query.filter_by(code='CSE').first() or Department.query.first()
        roll1 = generate_roll_number(department_id=dept.id)
        self.assertTrue(roll1.startswith(f"{dept.code}-"))

    def test_student_enrollment_web_flow(self):
        """Test Admin enrolling student via web form with omitted IDs."""
        # 1. Login as Admin
        login_res = self.client.post('/auth/login', data={
            'login_id': 'admin',
            'password': 'admin'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)

        dept = Department.query.first()
        course = Course.query.filter_by(department_id=dept.id).first() or Course.query.first()
        sem = Semester.query.first()
        sess = AcademicSession.query.filter_by(is_current=True).first() or AcademicSession.query.first()

        # Submit new student without entering student_id, admission_no, enrollment_no, roll_no
        res = self.client.post('/students/create', data={
            'first_name': 'Aarav',
            'last_name': 'Sharma',
            'gender': 'Male',
            'college_email': 'aarav.sharma@campusconnect.edu',
            'mobile': '9876543210',
            'department_id': dept.id,
            'course_id': course.id,
            'semester_id': sem.id,
            'session_id': sess.id,
            'status': 'Active'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Verify Student in database
        student = Student.query.filter_by(college_email='aarav.sharma@campusconnect.edu').first()
        self.assertIsNotNone(student)
        self.assertTrue(student.student_id.startswith("STU"))
        self.assertTrue(student.admission_no.startswith("ADM"))
        self.assertTrue(student.enrollment_no.startswith("ENR"))
        self.assertIsNotNone(student.roll_no)
        self.assertEqual(student.mobile, '9876543210')

        # Verify User credentials
        user = student.user
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'aarav.sharma@campusconnect.edu')
        self.assertTrue(user.must_change_password)
        self.assertTrue(user.check_password('9876543210'))

        # Verify multi-identifier login
        # 1. Login with College Email + Mobile Password
        self.client.get('/auth/logout')
        res_email = self.client.post('/auth/login', data={
            'login_id': 'aarav.sharma@campusconnect.edu',
            'password': '9876543210'
        }, follow_redirects=True)
        self.assertEqual(res_email.status_code, 200)
        # Forced password change redirect on first login
        self.assertIn(b'change_password', res_email.data.lower() or b'')

        # 2. Login with Student ID
        self.client.get('/auth/logout')
        res_stuid = self.client.post('/auth/login', data={
            'login_id': student.student_id,
            'password': '9876543210'
        }, follow_redirects=True)
        self.assertEqual(res_stuid.status_code, 200)

        # 3. Login with Admission No
        self.client.get('/auth/logout')
        res_adm = self.client.post('/auth/login', data={
            'login_id': student.admission_no,
            'password': '9876543210'
        }, follow_redirects=True)
        self.assertEqual(res_adm.status_code, 200)

        # 4. Login with Enrollment No
        self.client.get('/auth/logout')
        res_enr = self.client.post('/auth/login', data={
            'login_id': student.enrollment_no,
            'password': '9876543210'
        }, follow_redirects=True)
        self.assertEqual(res_enr.status_code, 200)

    def test_faculty_registration_web_flow(self):
        """Test Admin adding faculty member with automated Employee ID."""
        # 1. Login as Admin
        self.client.post('/auth/login', data={
            'login_id': 'admin',
            'password': 'admin'
        }, follow_redirects=True)

        dept = Department.query.first()

        res = self.client.post('/faculty/create', data={
            'first_name': 'Vikram',
            'last_name': 'Mehta',
            'gender': 'Male',
            'official_email': 'vikram.mehta@campusconnect.edu',
            'mobile': '9123456780',
            'department_id': dept.id,
            'designation': 'Assistant Professor',
            'status': 'Active'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        faculty = Faculty.query.filter_by(official_email='vikram.mehta@campusconnect.edu').first()
        self.assertIsNotNone(faculty)
        self.assertTrue(faculty.employee_id.startswith("EMP"))
        self.assertEqual(faculty.mobile, '9123456780')

        user = faculty.user
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'vikram.mehta@campusconnect.edu')
        self.assertTrue(user.must_change_password)
        self.assertTrue(user.check_password('9123456780'))

        # Login with Employee ID
        self.client.get('/auth/logout')
        res_emp = self.client.post('/auth/login', data={
            'login_id': faculty.employee_id,
            'password': '9123456780'
        }, follow_redirects=True)
        self.assertEqual(res_emp.status_code, 200)

    def test_api_admin_enrollment_and_mobile_login(self):
        """Test the automated admin REST API endpoints and mobile student-only restrictions."""
        dept = Department.query.first()
        course = Course.query.filter_by(department_id=dept.id).first() or Course.query.first()

        # 1. Enroll student via REST API
        enroll_res = self.client.post('/api/admin/students', json={
            'firstName': 'Priya',
            'lastName': 'Patel',
            'gender': 'Female',
            'collegeEmail': 'priya.patel@campusconnect.edu',
            'mobile': '9988776655',
            'departmentId': dept.id,
            'courseId': course.id
        })
        self.assertEqual(enroll_res.status_code, 201)
        enroll_json = enroll_res.get_json()
        self.assertTrue(enroll_json['success'])
        self.assertIn('studentId', enroll_json['student'])
        self.assertIn('admissionNumber', enroll_json['student'])
        self.assertIn('enrollmentNumber', enroll_json['student'])
        self.assertIn('rollNumber', enroll_json['student'])
        self.assertTrue(enroll_json['student']['studentId'].startswith("STU"))

        # 2. Test Mobile Login with Student ID & mobile password
        login_res = self.client.post('/api/android/login', json={
            'studentId': enroll_json['student']['studentId'],
            'password': '9988776655',
            'platform': 'android'
        })
        self.assertEqual(login_res.status_code, 200)
        login_json = login_res.get_json()
        self.assertTrue(login_json['success'])
        self.assertIn('token', login_json)
        self.assertTrue(login_json['mustChangePassword'])
        self.assertEqual(login_json['student']['collegeEmail'], 'priya.patel@campusconnect.edu')
        self.assertEqual(login_json['student']['firstName'], 'Priya')

        # 3. Test Student Profile API with Bearer token
        token = login_json['token']
        profile_res = self.client.get('/api/student/profile', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(profile_res.status_code, 200)
        profile_json = profile_res.get_json()
        self.assertTrue(profile_json['success'])
        self.assertEqual(profile_json['profile']['studentId'], enroll_json['student']['studentId'])
        self.assertEqual(profile_json['profile']['admissionNumber'], enroll_json['student']['admissionNumber'])

        # 4. Test Mobile Security Restriction: Admin attempting mobile login receives 403 Forbidden
        admin_mobile_res = self.client.post('/api/android/login', json={
            'username': 'admin',
            'password': 'admin',
            'platform': 'android'
        })
        self.assertEqual(admin_mobile_res.status_code, 403)
        self.assertIn('Only student accounts', admin_mobile_res.get_json()['message'])


if __name__ == '__main__':
    unittest.main()
