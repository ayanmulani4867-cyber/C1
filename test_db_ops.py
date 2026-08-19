"""
Unit tests for database initialization, safe seeding, health checks, and token security.
"""
import unittest
import os
import sys
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User, Role
from app.models.department import Department
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.notice import Notice
from app.utils.db_ops import verify_db_init_token, initialize_database_schema, seed_database_safely


class TestDatabaseOperations(unittest.TestCase):
    def setUp(self):
        os.environ['DB_INIT_TOKEN'] = 'test-secret-token-12345'
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_health_endpoints(self):
        """Verify GET /health returns status ok with no sensitive credentials."""
        res = self.client.get('/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'ok')
        self.assertNotIn('database_url', data)
        self.assertNotIn('password', data)

        res_api = self.client.get('/api/health')
        self.assertEqual(res_api.status_code, 200)
        data_api = res_api.get_json()
        self.assertIn(data_api.get('status'), ('ok', 'healthy'))

    def test_token_verification(self):
        """Verify token authentication security checks."""
        # Valid token
        is_valid, err, code = verify_db_init_token('test-secret-token-12345')
        self.assertTrue(is_valid)
        self.assertIsNone(err)

        # Invalid token
        is_valid, err, code = verify_db_init_token('wrong-token')
        self.assertFalse(is_valid)
        self.assertEqual(code, 401)

        # Missing token
        is_valid, err, code = verify_db_init_token('')
        self.assertFalse(is_valid)
        self.assertEqual(code, 401)

    def test_api_initialize_database_unauthorized(self):
        """Verify initialize-database endpoint blocks unauthorized requests."""
        res = self.client.post('/api/admin/initialize-database')
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertFalse(data.get('success'))

        res_wrong = self.client.post('/api/admin/initialize-database', headers={'X-DB-Init-Token': 'wrong'})
        self.assertEqual(res_wrong.status_code, 401)

    def test_api_initialize_database_success(self):
        """Verify initialize-database endpoint succeeds with valid token."""
        res = self.client.post(
            '/api/admin/initialize-database',
            headers={'X-DB-Init-Token': 'test-secret-token-12345'}
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('status'), 'initialized')
        self.assertEqual(data.get('admin_user', {}).get('username'), 'admin')

        # Verify admin user in database
        admin = User.query.filter_by(username='admin').first()
        self.assertIsNotNone(admin)
        self.assertIn(admin.first_name, ('Administrator', 'Ayan'))
        self.assertEqual(admin.role, Role.ADMIN)
        self.assertTrue(admin.check_password('admin'))

    def test_api_seed_database_success_and_idempotency(self):
        """Verify seed-database runs cleanly and idempotently without duplicate errors."""
        # 1. Run initialization first
        init_res = self.client.post(
            '/api/admin/initialize-database',
            headers={'X-DB-Init-Token': 'test-secret-token-12345'}
        )
        self.assertEqual(init_res.status_code, 200)

        # 2. Run seeding
        seed_res = self.client.post(
            '/api/admin/seed-database',
            headers={'Authorization': 'Bearer test-secret-token-12345'}
        )
        self.assertEqual(seed_res.status_code, 200)
        seed_data = seed_res.get_json()
        self.assertTrue(seed_data.get('success'))
        self.assertEqual(seed_data.get('status'), 'seeded')

        # Verify seeded entities
        dept_count = Department.query.count()
        self.assertGreaterEqual(dept_count, 4)

        student_count = Student.query.count()
        self.assertGreaterEqual(student_count, 1)

        faculty_count = Faculty.query.count()
        self.assertGreaterEqual(faculty_count, 2)

        notice_count = Notice.query.count()
        self.assertGreaterEqual(notice_count, 1)

        # 3. Run seeding a SECOND time to verify idempotency (no crashing, no duplicates of unique items)
        seed_res_2 = self.client.post(
            '/api/admin/seed-database',
            json={'token': 'test-secret-token-12345'}
        )
        self.assertEqual(seed_res_2.status_code, 200)
        seed_data_2 = seed_res_2.get_json()
        self.assertTrue(seed_data_2.get('success'))

        # Counts must remain identical
        self.assertEqual(Department.query.count(), dept_count)
        self.assertEqual(Student.query.count(), student_count)
        self.assertEqual(Faculty.query.count(), faculty_count)


if __name__ == '__main__':
    unittest.main()
