import unittest
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date, timedelta
from app import create_app
from app.extensions import db
from app.models.user import User, Role
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.department import Department
from app.models.course import Course
from app.models.academic import Semester, AcademicSession, ClassDivision
from app.models.subject import Subject
from app.models.complaint import Complaint
from app.models.event import Event, EventRegistration
from app.models.fee import FeeStructure, StudentFee, FeePayment
from app.models.leave import LeaveRequest
from app.models.certificate import CertificateRequest
from app.models.feedback import Feedback
from app.models.notice import Notice


class CampusConnectERPTestSuite(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Master admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@campusconnect.edu',
                first_name='Administrator',
                last_name='',
                role=Role.ADMIN,
                must_change_password=False,
                is_active=True
            )
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()

        # Create department
        dept = Department.query.filter_by(code='CSE').first()
        if not dept:
            dept = Department(name='Computer Science and Engineering', code='CSE')
            db.session.add(dept)
            db.session.commit()

        # Create course
        course = Course.query.filter_by(code='BTECH-CSE').first()
        if not course:
            course = Course(name='B.Tech in Computer Science', code='BTECH-CSE', department_id=dept.id, duration_years=4, total_semesters=8)
            db.session.add(course)
            db.session.commit()

        # Create session & semester
        session = AcademicSession.query.filter_by(name='2025-26').first()
        if not session:
            session = AcademicSession(name='2025-26', start_year=2025, end_year=2026, is_current=True)
            db.session.add(session)
            db.session.commit()

        sem = Semester.query.filter_by(number=1).first()
        if not sem:
            sem = Semester(number=1, name='Semester 1', is_active=True)
            db.session.add(sem)
            db.session.commit()

        # Create class division
        division = ClassDivision(name='A', department_id=dept.id, course_id=course.id, semester_id=sem.id, session_id=session.id, room_number='Room 201')
        db.session.add(division)
        db.session.commit()

        # Create subject
        subj = Subject(name='Data Structures & Algorithms', code='CS201', course_id=course.id, semester_id=sem.id, department_id=dept.id, credits=4, subject_type='Theory')
        db.session.add(subj)
        db.session.commit()

        # Create faculty user
        fac_user = User(username='prof_sharma', email='sharma@campusconnect.edu', first_name='Rajesh', last_name='Sharma', role=Role.FACULTY, is_active=True)
        fac_user.set_password('faculty123')
        db.session.add(fac_user)
        db.session.commit()

        faculty = Faculty(
            user_id=fac_user.id,
            faculty_id='FAC-CSE-001',
            employee_id='EMP-CSE-001',
            first_name='Rajesh',
            last_name='Sharma',
            full_name='Rajesh Sharma',
            official_email=fac_user.email,
            mobile='9876543210',
            department_id=dept.id,
            designation='Professor'
        )
        db.session.add(faculty)
        db.session.commit()

        # Create student user
        std_user = User(username='std_rahul', email='rahul@campusconnect.edu', first_name='Rahul', last_name='Verma', role=Role.STUDENT, is_active=True)
        std_user.set_password('student123')
        db.session.add(std_user)
        db.session.commit()

        student = Student(
            user_id=std_user.id,
            student_id='STU-2025-001',
            enrollment_no='ENR-2025-001',
            admission_no='ADM-2025-001',
            first_name='Rahul',
            last_name='Verma',
            full_name='Rahul Verma',
            college_email=std_user.email,
            mobile='9876543211',
            department_id=dept.id,
            course_id=course.id,
            semester_id=sem.id,
            session_id=session.id,
            division_id=division.id,
            roll_no='2025-CSE-001',
            dob=date(2004, 5, 12),
            gender='Male'
        )
        db.session.add(student)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_admin_initial_login_and_dashboard_access(self):
        """Verify that logging in with initial admin/admin credentials grants direct dashboard access."""
        response = self.client.post('/auth/login', data={
            'identifier': 'admin',
            'password': 'admin'
        }, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/dashboard', response.headers.get('Location', ''))

        dash_response = self.client.get('/admin/dashboard', follow_redirects=False)
        self.assertEqual(dash_response.status_code, 200)
        self.assertIn(b'Administrator Dashboard', dash_response.data)

        # Verify password change works as expected
        change_resp = self.client.post('/auth/change-password', data={
            'old_password': 'admin',
            'new_password': 'AdminSecurePass2026!',
            'confirm_password': 'AdminSecurePass2026!'
        }, follow_redirects=True)
        self.assertEqual(change_resp.status_code, 200)

        admin = User.query.filter_by(username='admin').first()
        self.assertTrue(admin.verify_password('AdminSecurePass2026!'))

    def test_role_based_access_control(self):
        """Verify student cannot access admin-only and faculty-only endpoints."""
        self.client.post('/auth/login', data={
            'username': 'std_rahul',
            'password': 'student123'
        }, follow_redirects=True)

        resp = self.client.get('/academic/departments/create', follow_redirects=True)
        self.assertEqual(resp.status_code, 403)
        self.assertIn(b'Access Denied', resp.data)

        resp2 = self.client.get('/student/create', follow_redirects=True)
        self.assertEqual(resp2.status_code, 403)
        self.assertIn(b'Access Denied', resp2.data)

    def test_api_endpoints(self):
        """Verify REST API health, stats, and cascade dropdown helpers."""
        health = self.client.get('/api/v1/health')
        self.assertEqual(health.status_code, 200)
        self.assertIn(health.json['status'], ('ok', 'healthy'))

        stats = self.client.get('/api/v1/stats')
        self.assertEqual(stats.status_code, 200)
        self.assertIn('total_students', stats.json)
        self.assertGreaterEqual(stats.json['total_students'], 1)

        # Login as student to test protected cascade dropdown API routes
        self.client.post('/auth/login', data={'username': 'std_rahul', 'password': 'student123'})
        dept = Department.query.first()
        courses_resp = self.client.get(f'/api/v1/courses-by-department/{dept.id}')
        self.assertEqual(courses_resp.status_code, 200)
        self.assertGreaterEqual(len(courses_resp.json), 1)

    def test_complaint_and_resolution_flow(self):
        """Verify grievance creation by student and review/resolution by admin."""
        # 1. Student submits complaint
        self.client.post('/auth/login', data={'username': 'std_rahul', 'password': 'student123'})
        submit_resp = self.client.post('/complaints/submit', data={
            'category': 'Hostel',
            'title': 'Hot water issue in Wing B',
            'description': 'The solar water heater is malfunctioning in early morning.',
            'priority': 'Medium'
        }, follow_redirects=True)
        self.assertEqual(submit_resp.status_code, 200)

        complaint = Complaint.query.filter_by(title='Hot water issue in Wing B').first()
        self.assertIsNotNone(complaint)
        self.assertEqual(complaint.status, 'Submitted')

        # Logout student
        self.client.get('/auth/logout', follow_redirects=True)

        # 2. Admin logs in and changes status / adds resolution
        admin = User.query.filter_by(username='admin').first()
        admin.must_change_password = False
        db.session.commit()

        self.client.post('/auth/login', data={'username': 'admin', 'password': 'admin'})
        review_resp = self.client.post(f'/complaints/{complaint.id}/review', data={
            'status': 'Resolved',
            'priority': 'Medium',
            'resolution_notes': 'Maintenance team repaired the thermostat valve.'
        }, follow_redirects=True)
        self.assertEqual(review_resp.status_code, 200)

        updated_complaint = Complaint.query.get(complaint.id)
        self.assertEqual(updated_complaint.status, 'Resolved')
        self.assertIn('Maintenance', updated_complaint.resolution_notes)

    def test_event_creation_and_registration(self):
        """Verify event creation by admin and student registration."""
        admin = User.query.filter_by(username='admin').first()
        admin.must_change_password = False
        db.session.commit()

        # Admin creates event
        self.client.post('/auth/login', data={'username': 'admin', 'password': 'admin'})
        create_resp = self.client.post('/events/create', data={
            'title': 'AI Hackathon 2026',
            'event_type': 'Hackathon',
            'venue': 'Main Auditorium',
            'description': '24-hour innovation hackathon with generative AI.',
            'start_datetime': '2026-09-10T09:00',
            'end_datetime': '2026-09-11T17:00',
            'max_participants': 100,
            'is_open_for_registration': 'y'
        }, follow_redirects=True)
        self.assertEqual(create_resp.status_code, 200)

        event = Event.query.filter_by(title='AI Hackathon 2026').first()
        self.assertIsNotNone(event)

        # Logout admin
        self.client.get('/auth/logout', follow_redirects=True)

        # Student registers for event
        self.client.post('/auth/login', data={'username': 'std_rahul', 'password': 'student123'})
        reg_resp = self.client.post(f'/events/{event.id}/register', follow_redirects=True)
        self.assertEqual(reg_resp.status_code, 200)

        student = Student.query.first()
        registration = EventRegistration.query.filter_by(event_id=event.id, student_id=student.id).first()
        self.assertIsNotNone(registration)
        self.assertEqual(registration.status, 'Confirmed')

    def test_fee_management_and_balance_update(self):
        """Verify fee structure assignment and payment balance calculation."""
        course = Course.query.first()
        sem = Semester.query.first()
        session = AcademicSession.query.first()
        student = Student.query.first()

        fee_struct = FeeStructure(
            title='Semester 1 Tuition & Lab Fee',
            course_id=course.id,
            semester_id=sem.id,
            session_id=session.id,
            tuition_fee=45000.0,
            exam_fee=3000.0,
            lab_fee=5000.0,
            library_fee=2000.0,
            other_fee=1000.0,
            total_amount=56000.0,
            due_date=date(2026, 9, 30)
        )
        db.session.add(fee_struct)
        db.session.commit()

        student_fee = StudentFee(
            student_id=student.id,
            fee_structure_id=fee_struct.id,
            total_amount=56000.0,
            net_payable=56000.0,
            pending_amount=56000.0,
            status='Pending'
        )
        db.session.add(student_fee)
        db.session.commit()

        # Add partial payment
        payment1 = FeePayment(
            student_fee_id=student_fee.id,
            student_id=student.id,
            receipt_number='REC-TEST-001',
            amount=30000.0,
            payment_mode='Online',
            transaction_id='TXN12345678',
            payment_date=datetime.utcnow(),
            status='Success'
        )
        db.session.add(payment1)
        db.session.commit()

        student_fee.update_balance()
        db.session.commit()

        self.assertEqual(student_fee.paid_amount, 30000.0)
        self.assertEqual(student_fee.pending_amount, 26000.0)
        self.assertEqual(student_fee.status, 'Partial')

        # Add remaining payment
        payment2 = FeePayment(
            student_fee_id=student_fee.id,
            student_id=student.id,
            receipt_number='REC-TEST-002',
            amount=26000.0,
            payment_mode='UPI',
            transaction_id='TXN87654321',
            payment_date=datetime.utcnow(),
            status='Success'
        )
        db.session.add(payment2)
        db.session.commit()

        student_fee.update_balance()
        db.session.commit()

        self.assertEqual(student_fee.paid_amount, 56000.0)
        self.assertEqual(student_fee.pending_amount, 0.0)
        self.assertEqual(student_fee.status, 'Paid')


if __name__ == '__main__':
    unittest.main()
