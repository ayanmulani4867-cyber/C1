"""
Comprehensive Test Suite for Campus Connect Student REST APIs.
Validates all endpoints consumed by the native Android application,
including Bearer token authentication, student authorization isolation,
data schema completeness, and error handling.
"""
import json
import os
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User, Role
from app.models.student import Student
from app.models.assignment import Assignment
from app.models.fee import StudentFee
from app.models.event import Event


def run_tests():
    app = create_app('development')
    client = app.test_client()

    print("=" * 70)
    print("CAMPUS CONNECT - NATIVE ANDROID STUDENT REST API TEST SUITE")
    print("=" * 70)

    # -------------------------------------------------------------
    # 1. Health & Config Tests
    # -------------------------------------------------------------
    print("\n[TEST 1] Testing /api/v1/health...")
    res = client.get('/api/v1/health')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.get_json()
    assert data['status'] == 'healthy'
    print("  ✓ Health check passed.")

    print("\n[TEST 2] Testing /api/v1/config...")
    res = client.get('/api/v1/config')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'institute' in data
    print(f"  ✓ Config retrieved for: {data['institute']['name']}")

    # -------------------------------------------------------------
    # 2. Authentication & Authorization Security Tests
    # -------------------------------------------------------------
    print("\n[TEST 3] Testing unauthenticated access to protected student endpoints...")
    unauth_endpoints = [
        '/api/v1/student/profile',
        '/api/v1/student/dashboard',
        '/api/v1/student/timetable',
        '/api/v1/student/attendance',
        '/api/v1/student/assignments',
        '/api/v1/student/exams',
        '/api/v1/student/results',
        '/api/v1/student/fees',
        '/api/v1/student/certificates',
        '/api/v1/student/leaves',
        '/api/v1/student/grievances',
        '/api/v1/student/notices',
        '/api/v1/student/events',
        '/api/v1/student/notifications',
    ]
    for ep in unauth_endpoints:
        r = client.get(ep)
        assert r.status_code == 401, f"Expected 401 for unauthenticated {ep}, got {r.status_code}"
    print("  ✓ All protected student endpoints correctly reject unauthenticated requests with 401.")

    print("\n[TEST 4] Testing invalid login credentials...")
    bad_login = client.post('/api/v1/auth/login', json={'username': 'student', 'password': 'wrongpassword'})
    assert bad_login.status_code == 401
    assert bad_login.get_json()['success'] is False
    print("  ✓ Invalid login credentials rejected with 401.")

    print("\n[TEST 5] Testing valid Student login...")
    login_res = client.post('/api/v1/auth/login', json={'username': 'student', 'password': 'student123'})
    assert login_res.status_code == 200, f"Login failed: {login_res.data.decode('utf-8')}"
    login_data = login_res.get_json()
    assert login_data['success'] is True
    token = login_data['token']
    assert token, "Token not returned"
    assert login_data['user']['role'] == Role.STUDENT
    assert login_data['student']['full_name'] == 'Aarav Patel'
    print(f"  ✓ Login successful for student: {login_data['student']['full_name']} (Roll: {login_data['student']['roll_no']})")

    headers = {'Authorization': f'Bearer {token}'}

    print("\n[TEST 6] Testing Faculty token cannot access Student-only endpoints...")
    fac_login = client.post('/api/v1/auth/login', json={'username': 'faculty', 'password': 'faculty123'})
    if fac_login.status_code == 200:
        fac_token = fac_login.get_json()['token']
        fac_headers = {'Authorization': f'Bearer {fac_token}'}
        fac_res = client.get('/api/v1/student/profile', headers=fac_headers)
        assert fac_res.status_code == 403, f"Expected 403 for faculty accessing student profile, got {fac_res.status_code}"
        print("  ✓ Role isolation enforced: Non-students receive 403 Forbidden.")

    # -------------------------------------------------------------
    # 3. Student Profile & Digital ID
    # -------------------------------------------------------------
    print("\n[TEST 7] Testing GET /api/v1/student/profile...")
    res = client.get('/api/v1/student/profile', headers=headers)
    assert res.status_code == 200
    p = res.get_json()['profile']
    assert p['full_name'] == 'Aarav Patel'
    assert p['academic']['department_name'] == 'Computer Science & Engineering'
    assert p['academic']['semester_number'] == 4
    assert p['academic']['division_name'] == 'A'
    assert 'emergency_contact' in p
    assert 'address' in p
    print(f"  ✓ Full profile payload valid for {p['full_name']} ({p['academic']['course_code']}).")

    print("\n[TEST 8] Testing GET /api/v1/student/id-card...")
    res = client.get('/api/v1/student/id-card', headers=headers)
    assert res.status_code == 200
    id_data = res.get_json()['id_card']
    assert 'qr_verification_code' in id_data
    assert id_data['roll_no'] == '23CS401'
    print("  ✓ Digital ID Card generated with QR verification payload.")

    # -------------------------------------------------------------
    # 4. Student Dashboard
    # -------------------------------------------------------------
    print("\n[TEST 9] Testing GET /api/v1/student/dashboard...")
    res = client.get('/api/v1/student/dashboard', headers=headers)
    assert res.status_code == 200
    dash = res.get_json()['dashboard']
    assert 'attendance' in dash
    assert 'academics' in dash
    assert 'fees' in dash
    assert 'today_schedule' in dash
    assert 'upcoming_exams' in dash
    print(f"  ✓ Dashboard bundle verified (Attendance: {dash['attendance']['percentage']}%, CGPA: {dash['academics']['cgpa']}).")

    # -------------------------------------------------------------
    # 5. Timetable & Schedule
    # -------------------------------------------------------------
    print("\n[TEST 10] Testing GET /api/v1/student/timetable & /today...")
    res = client.get('/api/v1/student/timetable', headers=headers)
    assert res.status_code == 200
    tt = res.get_json()
    assert 'timetable_by_day' in tt
    assert len(tt['timetable_by_day']['Monday']) > 0
    print(f"  ✓ Weekly timetable retrieved ({len(tt['timetable_by_day']['Monday'])} classes on Monday).")

    res_today = client.get('/api/v1/student/timetable/today', headers=headers)
    assert res_today.status_code == 200
    print("  ✓ Today's lecture schedule retrieved.")

    # -------------------------------------------------------------
    # 6. Attendance Analytics
    # -------------------------------------------------------------
    print("\n[TEST 11] Testing GET /api/v1/student/attendance...")
    res = client.get('/api/v1/student/attendance', headers=headers)
    assert res.status_code == 200
    att = res.get_json()
    assert 'summary' in att
    assert 'subject_breakdown' in att
    assert 'recent_history' in att
    assert len(att['subject_breakdown']) > 0
    print(f"  ✓ Attendance summary ({att['summary']['overall_percentage']}%) and {len(att['recent_history'])} session logs verified.")

    # -------------------------------------------------------------
    # 7. Assignments & Submissions
    # -------------------------------------------------------------
    print("\n[TEST 12] Testing GET & POST /api/v1/student/assignments...")
    res = client.get('/api/v1/student/assignments', headers=headers)
    assert res.status_code == 200
    assignments = res.get_json()['assignments']
    assert len(assignments) >= 1
    a_id = assignments[0]['id']
    print(f"  ✓ Found {len(assignments)} assignments for student's class division.")

    # Test assignment submission
    subm_res = client.post(f'/api/v1/student/assignments/{a_id}/submit', headers=headers, json={
        'submission_text': 'Updated lab assignment submission via Android REST API.'
    })
    assert subm_res.status_code == 200
    assert subm_res.get_json()['success'] is True
    print("  ✓ Assignment submission endpoint verified.")

    # -------------------------------------------------------------
    # 8. Study Materials
    # -------------------------------------------------------------
    print("\n[TEST 13] Testing GET /api/v1/student/study-materials...")
    res = client.get('/api/v1/student/study-materials', headers=headers)
    assert res.status_code == 200
    materials = res.get_json()['materials']
    assert len(materials) >= 1
    print(f"  ✓ Retrieved {len(materials)} study material repository items.")

    # -------------------------------------------------------------
    # 9. Examinations & Results
    # -------------------------------------------------------------
    print("\n[TEST 14] Testing GET /api/v1/student/exams & /results...")
    res_exams = client.get('/api/v1/student/exams', headers=headers)
    assert res_exams.status_code == 200
    exams_data = res_exams.get_json()
    assert len(exams_data['upcoming_exams']) + len(exams_data['past_exams']) > 0
    print(f"  ✓ Exam schedules retrieved ({len(exams_data['upcoming_exams'])} upcoming, {len(exams_data['past_exams'])} past).")

    res_results = client.get('/api/v1/student/results', headers=headers)
    assert res_results.status_code == 200
    results_data = res_results.get_json()
    assert len(results_data['grade_cards']) > 0
    assert results_data['summary']['cgpa'] is not None
    print(f"  ✓ Published grade cards retrieved (CGPA: {results_data['summary']['cgpa']}, Grade: {results_data['grade_cards'][0]['grade']}).")

    # -------------------------------------------------------------
    # 10. Fees & Payment History & Online Payment
    # -------------------------------------------------------------
    print("\n[TEST 15] Testing GET /api/v1/student/fees & /history...")
    res_fees = client.get('/api/v1/student/fees', headers=headers)
    assert res_fees.status_code == 200
    fee_data = res_fees.get_json()
    assert len(fee_data['fees']) > 0
    student_fee_id = fee_data['fees'][0]['id']
    pending_amt = fee_data['fees'][0]['pending_amount']
    print(f"  ✓ Fee record retrieved: Total ₹{fee_data['fees'][0]['total_amount']}, Pending ₹{pending_amt}.")

    res_hist = client.get('/api/v1/student/fees/history', headers=headers)
    assert res_hist.status_code == 200
    print(f"  ✓ Payment history retrieved ({len(res_hist.get_json()['payment_history'])} transactions).")

    if pending_amt > 0:
        pay_amt = min(5000.0, pending_amt)
        pay_res = client.post('/api/v1/student/fees/pay', headers=headers, json={
            'student_fee_id': student_fee_id,
            'amount': pay_amt,
            'payment_mode': 'UPI - Google Pay'
        })
        assert pay_res.status_code == 200
        pay_json = pay_res.get_json()
        assert pay_json['success'] is True
        assert 'receipt' in pay_json
        print(f"  ✓ Fee payment of ₹{pay_amt} recorded. Receipt No: {pay_json['receipt']['receipt_number']}.")

    # -------------------------------------------------------------
    # 11. Certificates
    # -------------------------------------------------------------
    print("\n[TEST 16] Testing GET & POST /api/v1/student/certificates...")
    res_certs = client.get('/api/v1/student/certificates', headers=headers)
    assert res_certs.status_code == 200
    print(f"  ✓ Certificate requests listed ({len(res_certs.get_json()['certificates'])} records).")

    app_res = client.post('/api/v1/student/certificates/apply', headers=headers, json={
        'certificate_type': 'Character Certificate',
        'purpose': 'Internship application at research laboratory'
    })
    assert app_res.status_code == 200
    assert app_res.get_json()['success'] is True
    print("  ✓ Certificate request application submitted.")

    # -------------------------------------------------------------
    # 12. Leaves
    # -------------------------------------------------------------
    print("\n[TEST 17] Testing GET & POST /api/v1/student/leaves...")
    res_leaves = client.get('/api/v1/student/leaves', headers=headers)
    assert res_leaves.status_code == 200
    print(f"  ✓ Leave records listed ({len(res_leaves.get_json()['leaves'])} records).")

    leave_res = client.post('/api/v1/student/leaves/apply', headers=headers, json={
        'leave_type': 'Casual',
        'start_date': '2026-04-10',
        'end_date': '2026-04-11',
        'reason': 'Attending sibling wedding ceremony in hometown.'
    })
    assert leave_res.status_code == 200
    assert leave_res.get_json()['success'] is True
    print("  ✓ Leave application submitted.")

    # -------------------------------------------------------------
    # 13. Grievances
    # -------------------------------------------------------------
    print("\n[TEST 18] Testing GET & POST /api/v1/student/grievances...")
    res_griev = client.get('/api/v1/student/grievances', headers=headers)
    assert res_griev.status_code == 200
    print(f"  ✓ Grievances listed ({len(res_griev.get_json()['grievances'])} tickets).")

    tkt_res = client.post('/api/v1/student/grievances/submit', headers=headers, json={
        'category': 'Academic',
        'title': 'Request for DBMS query optimization workshop',
        'description': 'Kindly organize an advanced indexing workshop before semester exams.',
        'priority': 'Medium'
    })
    assert tkt_res.status_code == 200
    assert tkt_res.get_json()['success'] is True
    print(f"  ✓ Grievance submitted (Ticket: {tkt_res.get_json()['ticket_number']}).")

    # -------------------------------------------------------------
    # 14. Notices, Events & Notifications
    # -------------------------------------------------------------
    print("\n[TEST 19] Testing Notices & Events...")
    res_notices = client.get('/api/v1/student/notices', headers=headers)
    assert res_notices.status_code == 200
    notices_list = res_notices.get_json()['notices']
    assert len(notices_list) > 0
    print(f"  ✓ Notices retrieved ({len(notices_list)} notices).")

    res_events = client.get('/api/v1/student/events', headers=headers)
    assert res_events.status_code == 200
    events_list = res_events.get_json()['events']
    assert len(events_list) > 0
    event_id = events_list[0]['id']
    print(f"  ✓ Events retrieved ({len(events_list)} events).")

    # Toggle event registration
    reg_res = client.post(f'/api/v1/student/events/{event_id}/register', headers=headers)
    assert reg_res.status_code == 200
    print(f"  ✓ Event registration toggled ({reg_res.get_json()['message']}).")

    print("\n[TEST 20] Testing Notifications & Feedback...")
    res_notif = client.get('/api/v1/student/notifications', headers=headers)
    assert res_notif.status_code == 200
    notif_list = res_notif.get_json()['notifications']
    print(f"  ✓ Notifications retrieved ({len(notif_list)} notifications).")

    read_all = client.post('/api/v1/student/notifications/read-all', headers=headers)
    assert read_all.status_code == 200
    print("  ✓ Mark all notifications as read verified.")

    # Feedback subjects & submit
    res_fb_sub = client.get('/api/v1/student/feedback/subjects', headers=headers)
    assert res_fb_sub.status_code == 200
    fb_sub_list = res_fb_sub.get_json()['subjects']
    if len(fb_sub_list) > 0:
        target_sub = fb_sub_list[0]
        fb_post = client.post('/api/v1/student/feedback/submit', headers=headers, json={
            'faculty_id': target_sub['faculty_id'],
            'rating': 5,
            'clarity_rating': 5,
            'punctuality_rating': 5,
            'helpfulness_rating': 5,
            'comments': 'Great teaching methodologies and practical assignments.',
            'is_anonymous': False
        })
        assert fb_post.status_code == 200
        print("  ✓ Student feedback submitted.")

    print("\n" + "=" * 70)
    print("ALL 20 STUDENT REST API & SECURITY TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)


if __name__ == '__main__':
    run_tests()
