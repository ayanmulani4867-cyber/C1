import unittest
import io
import os
import sys
from datetime import date, datetime, timedelta

# Ensure project root is in sys.path
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
from app.models.class_division import ClassDivision
from app.models.subject import Subject
from app.models.attendance import AttendanceSession, AttendanceRecord
from app.models.assignment import Assignment, AssignmentSubmission, StudyMaterial
from app.models.exam import Exam, ExamResult
from app.models.fee import FeeStructure, StudentFee, FeePayment
from app.models.leave import LeaveRequest
from app.models.certificate import CertificateRequest
from app.models.complaint import Complaint
from app.models.notice import Notice
from app.models.event import CampusEvent
from app.models.feedback import Feedback
from app.utils.db_ops import initialize_database_schema, seed_database_safely

class FullERPWorkflowTests(unittest.TestCase):
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

    def test_01_student_full_profile_and_id_card(self):
        self.login('admin', 'admin')
        student = Student.query.first()
        self.assertIsNotNone(student)

        # View student profile
        res = self.client.get(f'/student/{student.id}')
        self.assertEqual(res.status_code, 200)

        # Download ID card
        res = self.client.get(f'/student/{student.id}/id-card')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, 'application/pdf')

    def test_02_faculty_profile_and_detail(self):
        self.login('admin', 'admin')
        faculty = Faculty.query.first()
        self.assertIsNotNone(faculty)

        res = self.client.get(f'/faculty/{faculty.id}')
        self.assertEqual(res.status_code, 200)

    def test_03_attendance_mark_flow(self):
        self.login('faculty', 'faculty123')
        div = ClassDivision.query.first()
        subj = Subject.query.first()

        res = self.client.get(f'/attendance/mark?class_division_id={div.id}&subject_id={subj.id}')
        self.assertEqual(res.status_code, 200)

        student = Student.query.filter_by(class_division_id=div.id).first()
        if student:
            post_data = {
                'class_division_id': div.id,
                'subject_id': subj.id,
                'date': date.today().strftime('%Y-%m-%d'),
                'time_slot': '09:00 - 10:00',
                f'status_{student.id}': 'Present',
                f'remarks_{student.id}': 'On time'
            }
            res = self.client.post('/attendance/mark', data=post_data, follow_redirects=True)
            self.assertEqual(res.status_code, 200)

    def test_04_assignment_and_submission_flow(self):
        self.login('faculty', 'faculty123')
        div = ClassDivision.query.first()
        subj = Subject.query.first()

        # Create Assignment
        res = self.client.post('/assignments/create', data={
            'title': 'Test Assignment 1',
            'description': 'Solve questions 1 through 5',
            'subject_id': subj.id,
            'class_division_id': div.id,
            'due_date': (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'max_marks': 25.0
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        assignment = Assignment.query.filter_by(title='Test Assignment 1').first()
        self.assertIsNotNone(assignment)

        # Student submits assignment
        self.login('student', 'student123')
        res = self.client.post(f'/assignments/{assignment.id}/submit', data={
            'submission_text': 'Here is my submission text answer.'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Faculty grades assignment
        self.login('faculty', 'faculty123')
        sub = AssignmentSubmission.query.filter_by(assignment_id=assignment.id).first()
        self.assertIsNotNone(sub)
        res = self.client.post(f'/assignments/submission/{sub.id}/grade', data={
            'marks_obtained': 23.5,
            'feedback': 'Good work!'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

    def test_05_fee_payment_and_receipt_download(self):
        self.login('admin', 'admin')
        student = Student.query.first()
        fee_rec = StudentFee.query.filter_by(student_id=student.id).first()
        self.assertIsNotNone(fee_rec)

        # Collect fee payment
        res = self.client.post(f'/fees/pay/{fee_rec.id}', data={
            'amount': 5000.0,
            'payment_mode': 'Cash',
            'transaction_reference': 'CASH-REC-1001',
            'payment_date': date.today().strftime('%Y-%m-%d'),
            'remarks': 'Installment payment received'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        payment = FeePayment.query.filter_by(student_fee_id=fee_rec.id).first()
        self.assertIsNotNone(payment)

        # Download Receipt PDF
        res = self.client.get(f'/fees/receipt/{payment.id}')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, 'application/pdf')

    def test_06_leave_apply_and_approval(self):
        self.login('student', 'student123')
        res = self.client.post('/leaves/apply', data={
            'leave_type': 'Sick Leave',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=2)).strftime('%Y-%m-%d'),
            'reason': 'Medical checkup and viral fever recovery'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        leave = LeaveRequest.query.order_by(LeaveRequest.id.desc()).first()
        self.assertIsNotNone(leave)

        # Admin approves leave
        self.login('admin', 'admin')
        res = self.client.post(f'/leaves/{leave.id}/approve', data={
            'action': 'Approve',
            'admin_remarks': 'Approved based on medical note.'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

    def test_07_certificate_request_and_processing(self):
        self.login('student', 'student123')
        res = self.client.post('/certificates/request', data={
            'certificate_type': 'Bonafide Certificate',
            'purpose': 'Passport application verification',
            'delivery_mode': 'Digital PDF Download'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        cert = CertificateRequest.query.order_by(CertificateRequest.id.desc()).first()
        self.assertIsNotNone(cert)

        # Admin approves certificate
        self.login('admin', 'admin')
        res = self.client.post(f'/certificates/{cert.id}/status', data={
            'status': 'Approved',
            'remarks': 'Verified record and approved.'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Download certificate
        res = self.client.get(f'/certificates/{cert.id}/download')
        self.assertEqual(res.status_code, 200)

    def test_08_complaints_and_resolution(self):
        self.login('student', 'student123')
        res = self.client.post('/complaints/submit', data={
            'category': 'Hostel',
            'subject': 'Water heater maintenance in Block B',
            'description': 'The water heater on the 2nd floor is not functioning properly.',
            'is_anonymous': False
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        comp = Complaint.query.order_by(Complaint.id.desc()).first()
        self.assertIsNotNone(comp)

        # Admin resolves complaint
        self.login('admin', 'admin')
        res = self.client.post(f'/complaints/{comp.id}/resolve', data={
            'status': 'Resolved',
            'resolution_notes': 'Maintenance team dispatched and repaired the heater.'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

    def test_09_notices_and_events(self):
        self.login('admin', 'admin')
        # Create notice
        res = self.client.post('/notices/create', data={
            'title': 'Campus Tech Expo Announcement',
            'content': 'All departments are invited to submit project entries.',
            'target_audience': 'ALL',
            'priority': 'Important',
            'publish_date': date.today().strftime('%Y-%m-%d')
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Create event
        start_time = (datetime.utcnow() + timedelta(days=3)).strftime('%Y-%m-%dT10:00')
        end_time = (datetime.utcnow() + timedelta(days=3, hours=4)).strftime('%Y-%m-%dT14:00')
        res = self.client.post('/events/create', data={
            'title': 'AI in Healthcare Workshop',
            'event_type': 'Workshop',
            'venue': 'Seminar Hall 3',
            'description': 'Hands-on exploration of medical image analysis with AI.',
            'start_datetime': start_time,
            'end_datetime': end_time,
            'max_participants': 50,
            'is_open_for_registration': True
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        event = CampusEvent.query.filter_by(title='AI in Healthcare Workshop').first()
        self.assertIsNotNone(event)

        # Student registers for event
        self.login('student', 'student123')
        res = self.client.post(f'/events/{event.id}/register', follow_redirects=True)
        self.assertEqual(res.status_code, 200)

    def test_10_feedback_submission(self):
        self.login('student', 'student123')
        faculty = Faculty.query.first()
        res = self.client.post('/feedback/submit', data={
            'feedback_type': 'Faculty',
            'faculty_id': faculty.id,
            'rating': '5',
            'clarity_rating': '5',
            'punctuality_rating': '5',
            'helpfulness_rating': '5',
            'comments': 'Excellent lectures and very clear explanations.',
            'is_anonymous': False
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

    def test_11_exam_results_and_marksheets(self):
        self.login('admin', 'admin')
        student = Student.query.first()
        self.assertIsNotNone(student)

        res = self.client.get(f'/exams/student/{student.id}')
        self.assertEqual(res.status_code, 200)

        res = self.client.get(f'/exams/student/{student.id}/marksheet')
        self.assertEqual(res.status_code, 200)

    def test_12_reports_and_exports(self):
        self.login('admin', 'admin')
        res = self.client.get('/reports/')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/reports/export/students')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/reports/export/faculty')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/reports/export/attendance')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/reports/export/fees')
        self.assertEqual(res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
