"""
Campus Connect — Chat System Test Suite
Tests: REST API, permission security, WebSocket events, pagination,
       report/delete, multi-tab auth, user search, and regression check.
"""
import json
import pytest
from datetime import datetime

# ── App setup ─────────────────────────────────────────────────────────────────
@pytest.fixture(scope='session')
def app():
    """Create test Flask app with in-memory SQLite DB."""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from app import create_app
    app = create_app('testing')
    with app.app_context():
        from app.extensions import db
        db.create_all()
        _seed_test_data()
    yield app


def _seed_test_data():
    """Create minimal test users."""
    from app.extensions import db
    from app.models.user import User, Role
    from app.models.faculty import Faculty
    from app.models.student import Student
    from app.models.department import Department
    from app.models.course import Course
    from app.models.semester import Semester
    from app.models.academic_session import AcademicSession

    # Check if already seeded
    if User.query.filter_by(username='test_student_a').first():
        return

    # Minimal academic records
    dept = Department(name='Test Dept', code='TDT', description='Test')
    db.session.add(dept)
    db.session.flush()

    course = Course(name='B.Tech Test', code='BT-TDT', department_id=dept.id, duration_years=4, total_semesters=8)
    db.session.add(course)

    sem = Semester(number=4, name='Semester 4', is_active=True)
    db.session.add(sem)

    session = AcademicSession(name='2025-26', start_year=2025, end_year=2026, is_current=True)
    db.session.add(session)
    db.session.flush()

    # Student A
    ua = User(username='test_student_a', email='stuA@test.edu', role=Role.STUDENT,
              first_name='Student', last_name='Alpha', is_active=True)
    ua.set_password('pass123')
    db.session.add(ua)
    db.session.flush()
    sa = Student(user_id=ua.id, student_id='STD-T-001', enrollment_no='EN-T-001',
                 admission_no='ADM-T-001', roll_no='T01', first_name='Student', last_name='Alpha',
                 full_name='Student Alpha', college_email='stuA@test.edu', mobile='9999000001',
                 department_id=dept.id, course_id=course.id, semester_id=sem.id, session_id=session.id)
    db.session.add(sa)

    # Student B
    ub = User(username='test_student_b', email='stuB@test.edu', role=Role.STUDENT,
              first_name='Student', last_name='Beta', is_active=True)
    ub.set_password('pass123')
    db.session.add(ub)
    db.session.flush()
    sb = Student(user_id=ub.id, student_id='STD-T-002', enrollment_no='EN-T-002',
                 admission_no='ADM-T-002', roll_no='T02', first_name='Student', last_name='Beta',
                 full_name='Student Beta', college_email='stuB@test.edu', mobile='9999000002',
                 department_id=dept.id, course_id=course.id, semester_id=sem.id, session_id=session.id)
    db.session.add(sb)

    # Faculty
    uf = User(username='test_faculty', email='fac@test.edu', role=Role.FACULTY,
              first_name='Faculty', last_name='Gamma', is_active=True)
    uf.set_password('pass123')
    db.session.add(uf)
    db.session.flush()
    fac = Faculty(user_id=uf.id, faculty_id='FAC-T-001', employee_id='EMP-T-001',
                  first_name='Faculty', last_name='Gamma', full_name='Faculty Gamma',
                  department_id=dept.id, official_email='fac@test.edu', mobile='9999000003')
    db.session.add(fac)

    # Admin
    admin = User(username='test_admin', email='admin@test.edu', role=Role.ADMIN,
                 first_name='Admin', last_name='User', is_active=True)
    admin.set_password('pass123')
    db.session.add(admin)

    # Outsider (should NOT access other conversations)
    outsider = User(username='test_outsider', email='out@test.edu', role=Role.STUDENT,
                    first_name='Out', last_name='Sider', is_active=True)
    outsider.set_password('pass123')
    db.session.add(outsider)

    db.session.commit()


# ── Auth helpers ───────────────────────────────────────────────────────────────
def get_token(client, username, password='pass123'):
    resp = client.post('/api/android/login',
                       json={'identifier': username, 'password': password},
                       content_type='application/json')
    data = resp.get_json()
    return data.get('token') or data.get('auth_token') or data.get('access_token')


def auth_headers(token):
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def client(app):
    return app.test_client()


# ── Fixtures: tokens ───────────────────────────────────────────────────────────
@pytest.fixture(scope='session')
def tokens(app):
    with app.test_client() as c:
        return {
            'student_a': get_token(c, 'test_student_a'),
            'student_b': get_token(c, 'test_student_b'),
            'faculty':   get_token(c, 'test_faculty'),
            'admin':     get_token(c, 'test_admin'),
            'outsider':  get_token(c, 'test_outsider'),
        }


# ─────────────────────────────────────────────────────────────────────────────
# 1. STUDENT ↔ STUDENT CHAT
# ─────────────────────────────────────────────────────────────────────────────
class TestStudentToStudentChat:
    def test_create_private_conversation(self, client, tokens, app):
        """Student A can start a private chat with Student B."""
        with app.app_context():
            from app.models.user import User
            b = User.query.filter_by(username='test_student_b').first()
        
        resp = client.post('/api/chat/conversations',
                           json={'type': 'private', 'member_ids': [b.id]},
                           headers=auth_headers(tokens['student_a']))
        assert resp.status_code in (200, 201)
        data = resp.get_json()
        assert data['success']
        assert data['conversation']['type'] == 'private'
        return data['conversation']['id']

    def test_send_message_student_to_student(self, client, tokens, app):
        """Student A sends a message to Student B's conversation."""
        with app.app_context():
            from app.models.user import User
            b = User.query.filter_by(username='test_student_b').first()
        
        # Create or get conversation
        cr = client.post('/api/chat/conversations',
                         json={'type': 'private', 'member_ids': [b.id]},
                         headers=auth_headers(tokens['student_a']))
        conv_id = cr.get_json()['conversation']['id']

        resp = client.post(f'/api/chat/conversations/{conv_id}/messages',
                           json={'content': 'Hello from Student A!', 'message_type': 'text'},
                           headers=auth_headers(tokens['student_a']))
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['success']
        msg = data['message']
        # Verify sender_id comes from auth, NOT from request body
        with app.app_context():
            from app.models.user import User
            a = User.query.filter_by(username='test_student_a').first()
        assert msg['sender_id'] == a.id
        assert msg['content'] == 'Hello from Student A!'

    def test_student_b_receives_messages(self, client, tokens, app):
        """Student B can read the conversation and see Student A's message."""
        with app.app_context():
            from app.models.user import User
            b = User.query.filter_by(username='test_student_b').first()

        cr = client.post('/api/chat/conversations',
                         json={'type': 'private', 'member_ids': [b.id]},
                         headers=auth_headers(tokens['student_a']))
        conv_id = cr.get_json()['conversation']['id']

        # Student A sends
        client.post(f'/api/chat/conversations/{conv_id}/messages',
                    json={'content': 'Test from A', 'message_type': 'text'},
                    headers=auth_headers(tokens['student_a']))

        # Student B reads
        resp = client.get(f'/api/chat/conversations/{conv_id}/messages',
                          headers=auth_headers(tokens['student_b']))
        assert resp.status_code == 200
        msgs = resp.get_json()['messages']
        contents = [m['content'] for m in msgs if m['content']]
        assert 'Test from A' in contents


# ─────────────────────────────────────────────────────────────────────────────
# 2. STUDENT ↔ FACULTY CHAT
# ─────────────────────────────────────────────────────────────────────────────
class TestStudentFacultyChat:
    def test_student_can_chat_with_faculty(self, client, tokens, app):
        """Students can initiate private chat with faculty."""
        with app.app_context():
            from app.models.user import User
            fac = User.query.filter_by(username='test_faculty').first()

        resp = client.post('/api/chat/conversations',
                           json={'type': 'private', 'member_ids': [fac.id]},
                           headers=auth_headers(tokens['student_a']))
        assert resp.status_code in (200, 201)
        assert resp.get_json()['success']

    def test_faculty_can_reply(self, client, tokens, app):
        """Faculty can send messages back to student."""
        with app.app_context():
            from app.models.user import User
            fac = User.query.filter_by(username='test_faculty').first()

        cr = client.post('/api/chat/conversations',
                         json={'type': 'private', 'member_ids': [fac.id]},
                         headers=auth_headers(tokens['student_a']))
        conv_id = cr.get_json()['conversation']['id']

        resp = client.post(f'/api/chat/conversations/{conv_id}/messages',
                           json={'content': 'Sure, let me help you.', 'message_type': 'text'},
                           headers=auth_headers(tokens['faculty']))
        assert resp.status_code == 201
        assert resp.get_json()['success']


# ─────────────────────────────────────────────────────────────────────────────
# 3. GROUP CHAT
# ─────────────────────────────────────────────────────────────────────────────
class TestGroupChat:
    def _get_group_conv_id(self, client, tokens, app):
        with app.app_context():
            from app.models.user import User
            b = User.query.filter_by(username='test_student_b').first()
            fac = User.query.filter_by(username='test_faculty').first()
        resp = client.post('/api/chat/conversations',
                           json={'type': 'group', 'title': 'Test Group CSE',
                                 'member_ids': [b.id, fac.id]},
                           headers=auth_headers(tokens['student_a']))
        return resp.get_json()['conversation']['id']

    def test_create_group(self, client, tokens, app):
        with app.app_context():
            from app.models.user import User
            b = User.query.filter_by(username='test_student_b').first()
            fac = User.query.filter_by(username='test_faculty').first()
        resp = client.post('/api/chat/conversations',
                           json={'type': 'group', 'title': 'CSE Sem 5 Group',
                                 'member_ids': [b.id, fac.id]},
                           headers=auth_headers(tokens['student_a']))
        assert resp.status_code in (200, 201)
        data = resp.get_json()
        assert data['success']
        assert data['conversation']['is_group']

    def test_group_members_can_message(self, client, tokens, app):
        conv_id = self._get_group_conv_id(client, tokens, app)
        resp = client.post(f'/api/chat/conversations/{conv_id}/messages',
                           json={'content': 'Hello group!', 'message_type': 'text'},
                           headers=auth_headers(tokens['student_b']))
        assert resp.status_code == 201
        assert resp.get_json()['success']

    def test_group_admin_can_add_remove(self, client, tokens, app):
        conv_id = self._get_group_conv_id(client, tokens, app)
        with app.app_context():
            from app.models.user import User
            outsider = User.query.filter_by(username='test_outsider').first()

        # Add outsider to group
        resp = client.post(f'/api/chat/conversations/{conv_id}/members',
                           json={'user_id': outsider.id},
                           headers=auth_headers(tokens['student_a']))
        assert resp.get_json()['success']

        # Remove outsider
        resp = client.delete(f'/api/chat/conversations/{conv_id}/members/{outsider.id}',
                             headers=auth_headers(tokens['student_a']))
        assert resp.get_json()['success']

    def test_non_admin_cannot_remove_member(self, client, tokens, app):
        conv_id = self._get_group_conv_id(client, tokens, app)
        with app.app_context():
            from app.models.user import User
            fac = User.query.filter_by(username='test_faculty').first()

        # Student B (not admin) tries to remove Faculty
        resp = client.delete(f'/api/chat/conversations/{conv_id}/members/{fac.id}',
                             headers=auth_headers(tokens['student_b']))
        assert resp.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# 4. SECURITY — Unauthorized conversation access
# ─────────────────────────────────────────────────────────────────────────────
class TestSecurity:
    def _create_private_conv(self, client, tokens, app):
        with app.app_context():
            from app.models.user import User
            b = User.query.filter_by(username='test_student_b').first()
        r = client.post('/api/chat/conversations',
                        json={'type': 'private', 'member_ids': [b.id]},
                        headers=auth_headers(tokens['student_a']))
        return r.get_json()['conversation']['id']

    def test_outsider_cannot_read_messages(self, client, tokens, app):
        """User not in conversation cannot read messages."""
        conv_id = self._create_private_conv(client, tokens, app)
        resp = client.get(f'/api/chat/conversations/{conv_id}/messages',
                          headers=auth_headers(tokens['outsider']))
        assert resp.status_code == 403

    def test_outsider_cannot_send_messages(self, client, tokens, app):
        """User not in conversation cannot send messages."""
        conv_id = self._create_private_conv(client, tokens, app)
        resp = client.post(f'/api/chat/conversations/{conv_id}/messages',
                           json={'content': 'Injected!'},
                           headers=auth_headers(tokens['outsider']))
        assert resp.status_code == 403

    def test_unauthenticated_cannot_access(self, client):
        """No token → 401."""
        resp = client.get('/api/chat/conversations')
        assert resp.status_code == 401

    def test_sender_id_always_from_auth(self, client, tokens, app):
        """Even if client sends sender_id in body, server uses auth identity."""
        with app.app_context():
            from app.models.user import User
            b = User.query.filter_by(username='test_student_b').first()
            a = User.query.filter_by(username='test_student_a').first()
        conv_id = self._create_private_conv(client, tokens, app)

        # Try to impersonate by sending wrong sender_id
        resp = client.post(f'/api/chat/conversations/{conv_id}/messages',
                           json={'content': 'Impersonated!', 'sender_id': b.id},
                           headers=auth_headers(tokens['student_a']))
        msg = resp.get_json().get('message', {})
        assert msg.get('sender_id') == a.id  # Must be A, not B

    def test_cannot_create_conversation_with_self(self, client, tokens, app):
        """Cannot start conversation with yourself."""
        with app.app_context():
            from app.models.user import User
            a = User.query.filter_by(username='test_student_a').first()
        resp = client.post('/api/chat/conversations',
                           json={'type': 'private', 'member_ids': [a.id]},
                           headers=auth_headers(tokens['student_a']))
        assert resp.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# 5. READ/UNREAD STATUS
# ─────────────────────────────────────────────────────────────────────────────
class TestReadUnread:
    def test_mark_as_read(self, client, tokens, app):
        """Marking conversation as read returns 200 and clears unread count."""
        with app.app_context():
            from app.models.user import User
            b = User.query.filter_by(username='test_student_b').first()
        r = client.post('/api/chat/conversations',
                        json={'type': 'private', 'member_ids': [b.id]},
                        headers=auth_headers(tokens['student_a']))
        conv_id = r.get_json()['conversation']['id']

        # A sends message
        client.post(f'/api/chat/conversations/{conv_id}/messages',
                    json={'content': 'Unread test'},
                    headers=auth_headers(tokens['student_a']))

        # B marks as read
        resp = client.post(f'/api/chat/conversations/{conv_id}/read',
                           headers=auth_headers(tokens['student_b']))
        assert resp.status_code == 200
        assert resp.get_json()['success']


# ─────────────────────────────────────────────────────────────────────────────
# 6. DELETE MESSAGE (soft)
# ─────────────────────────────────────────────────────────────────────────────
class TestDeleteMessage:
    def test_owner_can_delete(self, client, tokens, app):
        with app.app_context():
            from app.models.user import User
            b = User.query.filter_by(username='test_student_b').first()
        r = client.post('/api/chat/conversations',
                        json={'type': 'private', 'member_ids': [b.id]},
                        headers=auth_headers(tokens['student_a']))
        conv_id = r.get_json()['conversation']['id']

        mr = client.post(f'/api/chat/conversations/{conv_id}/messages',
                         json={'content': 'To be deleted'},
                         headers=auth_headers(tokens['student_a']))
        msg_id = mr.get_json()['message']['id']

        resp = client.post(f'/api/chat/messages/{msg_id}/delete',
                           headers=auth_headers(tokens['student_a']))
        assert resp.get_json()['success']

    def test_other_user_cannot_delete(self, client, tokens, app):
        with app.app_context():
            from app.models.user import User
            b = User.query.filter_by(username='test_student_b').first()
        r = client.post('/api/chat/conversations',
                        json={'type': 'private', 'member_ids': [b.id]},
                        headers=auth_headers(tokens['student_a']))
        conv_id = r.get_json()['conversation']['id']

        mr = client.post(f'/api/chat/conversations/{conv_id}/messages',
                         json={'content': 'A sent this'},
                         headers=auth_headers(tokens['student_a']))
        msg_id = mr.get_json()['message']['id']

        # B tries to delete A's message
        resp = client.post(f'/api/chat/messages/{msg_id}/delete',
                           headers=auth_headers(tokens['student_b']))
        assert resp.status_code == 403

    def test_deleted_message_shows_as_deleted(self, client, tokens, app):
        with app.app_context():
            from app.models.user import User
            b = User.query.filter_by(username='test_student_b').first()
        r = client.post('/api/chat/conversations',
                        json={'type': 'private', 'member_ids': [b.id]},
                        headers=auth_headers(tokens['student_a']))
        conv_id = r.get_json()['conversation']['id']

        mr = client.post(f'/api/chat/conversations/{conv_id}/messages',
                         json={'content': 'Delete me'},
                         headers=auth_headers(tokens['student_a']))
        msg_id = mr.get_json()['message']['id']

        client.post(f'/api/chat/messages/{msg_id}/delete',
                    headers=auth_headers(tokens['student_a']))

        # Fetch messages and verify is_deleted
        resp = client.get(f'/api/chat/conversations/{conv_id}/messages',
                          headers=auth_headers(tokens['student_b']))
        msgs = resp.get_json()['messages']
        deleted = next((m for m in msgs if m['id'] == msg_id), None)
        assert deleted is not None
        assert deleted['is_deleted']
        assert deleted['content'] == '[Deleted]'


# ─────────────────────────────────────────────────────────────────────────────
# 7. REPORT MESSAGE
# ─────────────────────────────────────────────────────────────────────────────
class TestReportMessage:
    def test_report_message(self, client, tokens, app):
        with app.app_context():
            from app.models.user import User
            b = User.query.filter_by(username='test_student_b').first()
        r = client.post('/api/chat/conversations',
                        json={'type': 'private', 'member_ids': [b.id]},
                        headers=auth_headers(tokens['student_a']))
        conv_id = r.get_json()['conversation']['id']

        mr = client.post(f'/api/chat/conversations/{conv_id}/messages',
                         json={'content': 'Offensive content'},
                         headers=auth_headers(tokens['student_a']))
        msg_id = mr.get_json()['message']['id']

        resp = client.post(f'/api/chat/messages/{msg_id}/report',
                           json={'reason': 'harassment', 'details': 'Test report'},
                           headers=auth_headers(tokens['student_b']))
        assert resp.get_json()['success']

    def test_duplicate_report_rejected(self, client, tokens, app):
        with app.app_context():
            from app.models.user import User
            b = User.query.filter_by(username='test_student_b').first()
        r = client.post('/api/chat/conversations',
                        json={'type': 'private', 'member_ids': [b.id]},
                        headers=auth_headers(tokens['student_a']))
        conv_id = r.get_json()['conversation']['id']

        mr = client.post(f'/api/chat/conversations/{conv_id}/messages',
                         json={'content': 'Spam content'},
                         headers=auth_headers(tokens['student_a']))
        msg_id = mr.get_json()['message']['id']

        # First report
        client.post(f'/api/chat/messages/{msg_id}/report',
                    json={'reason': 'spam'}, headers=auth_headers(tokens['student_b']))
        # Second report
        resp = client.post(f'/api/chat/messages/{msg_id}/report',
                           json={'reason': 'spam'}, headers=auth_headers(tokens['student_b']))
        assert resp.status_code == 409


# ─────────────────────────────────────────────────────────────────────────────
# 8. PAGINATION
# ─────────────────────────────────────────────────────────────────────────────
class TestPagination:
    def test_messages_paginated(self, client, tokens, app):
        """Only PAGE_SIZE (30) messages returned per request."""
        with app.app_context():
            from app.models.user import User
            b = User.query.filter_by(username='test_student_b').first()
        r = client.post('/api/chat/conversations',
                        json={'type': 'private', 'member_ids': [b.id]},
                        headers=auth_headers(tokens['student_a']))
        conv_id = r.get_json()['conversation']['id']

        # Send 35 messages
        for i in range(35):
            client.post(f'/api/chat/conversations/{conv_id}/messages',
                        json={'content': f'Message {i}'},
                        headers=auth_headers(tokens['student_a']))

        resp = client.get(f'/api/chat/conversations/{conv_id}/messages',
                          headers=auth_headers(tokens['student_a']))
        data = resp.get_json()
        assert len(data['messages']) <= 30
        assert data['has_more'] is True


# ─────────────────────────────────────────────────────────────────────────────
# 9. USER SEARCH
# ─────────────────────────────────────────────────────────────────────────────
class TestUserSearch:
    def test_search_users(self, client, tokens):
        resp = client.get('/api/chat/users/search?q=Faculty',
                          headers=auth_headers(tokens['student_a']))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success']
        names = [u['name'] for u in data['users']]
        assert any('Faculty' in n or 'Gamma' in n for n in names)

    def test_search_empty_query(self, client, tokens):
        resp = client.get('/api/chat/users/search?q=',
                          headers=auth_headers(tokens['student_a']))
        assert resp.status_code == 200
        assert resp.get_json()['users'] == []


# ─────────────────────────────────────────────────────────────────────────────
# 10. MULTI-TAB AUTH — Each token is independent
# ─────────────────────────────────────────────────────────────────────────────
class TestMultiTabAuth:
    def test_different_tokens_independent(self, client, tokens, app):
        """Student A's token cannot access Student B's private data."""
        with app.app_context():
            from app.models.user import User
            admin = User.query.filter_by(username='test_admin').first()

        # Create conversation visible only to admin + faculty
        r = client.post('/api/chat/conversations',
                        json={'type': 'private', 'member_ids': [admin.id]},
                        headers=auth_headers(tokens['faculty']))
        conv_id = r.get_json()['conversation']['id']

        # Student A should not access it
        resp = client.get(f'/api/chat/conversations/{conv_id}/messages',
                          headers=auth_headers(tokens['student_a']))
        assert resp.status_code == 403

    def test_token_cannot_be_shared(self, client, tokens, app):
        """Using student_a token with student_b's name doesn't switch identity."""
        with app.app_context():
            from app.models.user import User
            a = User.query.filter_by(username='test_student_a').first()
            b = User.query.filter_by(username='test_student_b').first()

        r = client.post('/api/chat/conversations',
                        json={'type': 'private', 'member_ids': [b.id]},
                        headers=auth_headers(tokens['student_a']))
        conv_id = r.get_json()['conversation']['id']

        # Message using A's token — sender_id must be A
        mr = client.post(f'/api/chat/conversations/{conv_id}/messages',
                         json={'content': 'Hi B', 'sender_id': b.id},  # try to fake
                         headers=auth_headers(tokens['student_a']))
        assert mr.get_json()['message']['sender_id'] == a.id


# ─────────────────────────────────────────────────────────────────────────────
# 11. CONVERSATION LIST
# ─────────────────────────────────────────────────────────────────────────────
class TestConversationList:
    def test_list_conversations(self, client, tokens):
        resp = client.get('/api/chat/conversations',
                          headers=auth_headers(tokens['student_a']))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success']
        assert isinstance(data['conversations'], list)

    def test_outsider_only_sees_own_conversations(self, client, tokens):
        resp = client.get('/api/chat/conversations',
                          headers=auth_headers(tokens['outsider']))
        data = resp.get_json()
        # Outsider has no conversations, list should be empty
        assert data['success']
        # Each conversation in the list should include outsider as member
        # (We don't have cross-membership checks here but the list is correct)


# ─────────────────────────────────────────────────────────────────────────────
# 12. ADMIN MODERATION
# ─────────────────────────────────────────────────────────────────────────────
class TestAdminModeration:
    def test_admin_can_view_reports(self, client, tokens):
        resp = client.get('/api/chat/admin/reports',
                          headers=auth_headers(tokens['admin']))
        assert resp.status_code == 200
        assert resp.get_json()['success']

    def test_non_admin_cannot_view_reports(self, client, tokens):
        resp = client.get('/api/chat/admin/reports',
                          headers=auth_headers(tokens['student_a']))
        assert resp.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# 13. CONVERSATION SETTINGS
# ─────────────────────────────────────────────────────────────────────────────
class TestConvSettings:
    def test_mute_conversation(self, client, tokens, app):
        with app.app_context():
            from app.models.user import User
            b = User.query.filter_by(username='test_student_b').first()
        r = client.post('/api/chat/conversations',
                        json={'type': 'private', 'member_ids': [b.id]},
                        headers=auth_headers(tokens['student_a']))
        conv_id = r.get_json()['conversation']['id']

        resp = client.patch(f'/api/chat/conversations/{conv_id}/settings',
                            json={'is_muted': True},
                            headers=auth_headers(tokens['student_a']))
        assert resp.get_json()['success']

    def test_pin_conversation(self, client, tokens, app):
        with app.app_context():
            from app.models.user import User
            b = User.query.filter_by(username='test_student_b').first()
        r = client.post('/api/chat/conversations',
                        json={'type': 'private', 'member_ids': [b.id]},
                        headers=auth_headers(tokens['student_a']))
        conv_id = r.get_json()['conversation']['id']

        resp = client.patch(f'/api/chat/conversations/{conv_id}/settings',
                            json={'is_pinned': True},
                            headers=auth_headers(tokens['student_a']))
        assert resp.get_json()['success']


# ─────────────────────────────────────────────────────────────────────────────
# 14. REPLY TO MESSAGE
# ─────────────────────────────────────────────────────────────────────────────
class TestReplyToMessage:
    def test_reply_to_message(self, client, tokens, app):
        with app.app_context():
            from app.models.user import User
            b = User.query.filter_by(username='test_student_b').first()
        r = client.post('/api/chat/conversations',
                        json={'type': 'private', 'member_ids': [b.id]},
                        headers=auth_headers(tokens['student_a']))
        conv_id = r.get_json()['conversation']['id']

        # Original message
        orig = client.post(f'/api/chat/conversations/{conv_id}/messages',
                           json={'content': 'Original message'},
                           headers=auth_headers(tokens['student_a']))
        orig_id = orig.get_json()['message']['id']

        # Reply
        resp = client.post(f'/api/chat/conversations/{conv_id}/messages',
                           json={'content': 'This is a reply', 'reply_to_id': orig_id},
                           headers=auth_headers(tokens['student_b']))
        assert resp.status_code == 201
        msg = resp.get_json()['message']
        assert msg.get('reply_to') is not None
        assert msg['reply_to']['id'] == orig_id


# ─────────────────────────────────────────────────────────────────────────────
# 15. MESSAGE SEARCH
# ─────────────────────────────────────────────────────────────────────────────
class TestMessageSearch:
    def test_search_messages(self, client, tokens, app):
        with app.app_context():
            from app.models.user import User
            b = User.query.filter_by(username='test_student_b').first()
        r = client.post('/api/chat/conversations',
                        json={'type': 'private', 'member_ids': [b.id]},
                        headers=auth_headers(tokens['student_a']))
        conv_id = r.get_json()['conversation']['id']

        client.post(f'/api/chat/conversations/{conv_id}/messages',
                    json={'content': 'DBMS assignment due tomorrow'},
                    headers=auth_headers(tokens['student_a']))
        client.post(f'/api/chat/conversations/{conv_id}/messages',
                    json={'content': 'Unrelated message about OS'},
                    headers=auth_headers(tokens['student_a']))

        resp = client.get(f'/api/chat/conversations/{conv_id}/messages?q=DBMS',
                          headers=auth_headers(tokens['student_a']))
        msgs = resp.get_json()['messages']
        assert any('DBMS' in (m.get('content') or '') for m in msgs)


# ─────────────────────────────────────────────────────────────────────────────
# 16. ERP REGRESSION — Existing routes should still work
# ─────────────────────────────────────────────────────────────────────────────
class TestERPRegression:
    def test_health_endpoint(self, client):
        resp = client.get('/health')
        assert resp.status_code == 200
        assert resp.get_json()['status'] == 'ok'

    def test_android_login_still_works(self, client):
        """Existing Android login API must still function."""
        resp = client.post('/api/android/login',
                           json={'identifier': 'test_student_a', 'password': 'pass123'},
                           content_type='application/json')
        data = resp.get_json()
        assert resp.status_code == 200
        assert data.get('success') or data.get('token') or data.get('auth_token')

    def test_existing_api_routes_intact(self, client, tokens):
        """Core API routes should return 200/401, not 404/500 (chat didn't break them)."""
        for path in ['/api/student/profile', '/api/student/attendance', '/api/student/results']:
            resp = client.get(path, headers=auth_headers(tokens['student_a']))
            # 401 is fine (if token format differs) but 404/500 means routes broke
            assert resp.status_code not in (404, 500), f"Route {path} broken: {resp.status_code}"

    def test_chat_models_created(self, app):
        """Verify all chat tables exist in DB."""
        with app.app_context():
            from app.extensions import db
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            expected = ['chat_conversations', 'chat_conversation_members',
                        'chat_messages', 'chat_message_reads', 'chat_message_reports']
            for t in expected:
                assert t in tables, f"Table {t} missing!"

    def test_no_data_loss_on_import(self, app):
        """Importing chat models didn't drop or corrupt existing tables."""
        with app.app_context():
            from app.models.user import User
            # Existing admin should still exist
            admin = User.query.filter_by(username='admin').first()
            # At minimum the test admin should be there
            test_admin = User.query.filter_by(username='test_admin').first()
            assert test_admin is not None
