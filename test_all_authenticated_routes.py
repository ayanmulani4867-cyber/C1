import unittest
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User, Role
from app.utils.db_ops import initialize_database_schema, seed_database_safely

class ComprehensiveRouteAuditor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        initialize_database_schema()
        seed_database_safely()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        cls.app_context.pop()

    def setUp(self):
        self.client = self.app.test_client()

    def login(self, identifier, password):
        self.client.get('/auth/logout', follow_redirects=True)
        return self.client.post('/auth/login', data={
            'identifier': identifier,
            'password': password
        }, follow_redirects=True)

    def test_01_admin_routes(self):
        login_res = self.login('admin', 'admin')
        self.assertEqual(login_res.status_code, 200)

        admin_routes = [
            '/admin/dashboard',
            '/admin/users',
            '/student/list',
            '/student/create',
            '/faculty/list',
            '/faculty/create',
            '/academic/departments',
            '/academic/courses',
            '/academic/sessions',
            '/academic/divisions',
            '/academic/subjects',
            '/attendance/',
            '/attendance/report',
            '/timetable/',
            '/timetable/manage',
            '/assignments/',
            '/exams/',
            '/exams/results',
            '/fees/',
            '/fees/dues',
            '/fees/structures',
            '/leaves/',
            '/certificates/',
            '/complaints/',
            '/notices/',
            '/notices/create',
            '/events/',
            '/events/create',
            '/feedback/',
            '/feedback/admin',
            '/reports/',
            '/reports/attendance',
            '/reports/results',
            '/reports/fees',
            '/reports/students',
            '/reports/faculty',
        ]

        errors = []
        for url in admin_routes:
            res = self.client.get(url)
            print(f"[Admin] GET {url} -> {res.status_code}")
            if res.status_code >= 400:
                errors.append((url, res.status_code, res.data.decode('utf-8', errors='ignore')[:300]))

        if errors:
            print(f"\n--- ADMIN ROUTE ERRORS ({len(errors)}) ---")
            for url, code, data in errors:
                print(f"FAILED: {url} -> {code}\n{data}\n")
        self.assertEqual(len(errors), 0, f"{len(errors)} admin routes returned errors")

    def test_02_faculty_routes(self):
        login_res = self.login('faculty', 'faculty123')
        self.assertEqual(login_res.status_code, 200)

        faculty_routes = [
            '/faculty/dashboard',
            '/faculty/profile',
            '/attendance/',
            '/attendance/mark',
            '/timetable/',
            '/assignments/',
            '/assignments/create',
            '/exams/',
            '/exams/results',
            '/leaves/',
            '/leaves/apply',
            '/notices/',
            '/events/',
            '/feedback/',
        ]

        errors = []
        for url in faculty_routes:
            res = self.client.get(url)
            print(f"[Faculty] GET {url} -> {res.status_code}")
            if res.status_code >= 400:
                errors.append((url, res.status_code, res.data.decode('utf-8', errors='ignore')[:300]))

        if errors:
            print(f"\n--- FACULTY ROUTE ERRORS ({len(errors)}) ---")
            for url, code, data in errors:
                print(f"FAILED: {url} -> {code}\n{data}\n")
        self.assertEqual(len(errors), 0, f"{len(errors)} faculty routes returned errors")

    def test_03_student_routes(self):
        login_res = self.login('student', 'student123')
        self.assertEqual(login_res.status_code, 200)

        student_routes = [
            '/student/dashboard',
            '/student/profile',
            '/student/id-card',
            '/attendance/',
            '/timetable/',
            '/assignments/',
            '/exams/',
            '/exams/results',
            '/fees/',
            '/leaves/',
            '/leaves/apply',
            '/certificates/',
            '/certificates/request',
            '/complaints/',
            '/complaints/submit',
            '/notices/',
            '/events/',
            '/feedback/',
            '/feedback/submit',
        ]

        errors = []
        for url in student_routes:
            res = self.client.get(url)
            print(f"[Student] GET {url} -> {res.status_code}")
            if res.status_code >= 400:
                errors.append((url, res.status_code, res.data.decode('utf-8', errors='ignore')[:300]))

        if errors:
            print(f"\n--- STUDENT ROUTE ERRORS ({len(errors)}) ---")
            for url, code, data in errors:
                print(f"FAILED: {url} -> {code}\n{data}\n")
        self.assertEqual(len(errors), 0, f"{len(errors)} student routes returned errors")

if __name__ == '__main__':
    unittest.main()
