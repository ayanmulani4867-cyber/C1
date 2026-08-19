import unittest
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from werkzeug.security import check_password_hash
from app import create_app
from app.extensions import db
from app.models.user import User, Role
from app.utils.db_ops import initialize_database_schema, seed_database_safely


class TestAuthAdminFlow(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_01_first_time_init_creates_hashed_admin(self):
        """Verify initialization creates admin with hashed password, active status and ADMIN role."""
        # Run initialization
        result = initialize_database_schema()
        self.assertTrue(result['success'])
        
        # Verify user in database
        admin = User.query.filter_by(username='admin').first()
        self.assertIsNotNone(admin)
        self.assertEqual(admin.role, Role.ADMIN)
        self.assertTrue(admin.is_active)
        self.assertEqual(admin.username, 'admin')
        self.assertNotEqual(admin.password_hash, 'admin')
        self.assertTrue(check_password_hash(admin.password_hash, 'admin'))
        self.assertTrue(admin.verify_password('admin'))
        self.assertFalse(admin.verify_password('wrong_password'))

    def test_02_idempotency_preserves_password_and_no_duplicates(self):
        """Verify re-running init_db does not duplicate admin or overwrite changed password."""
        initialize_database_schema()
        
        # Admin changes their password to custom secret
        admin = User.query.filter_by(username='admin').first()
        admin.set_password('CustomProductionSecret999!')
        db.session.commit()

        # Re-run initialization
        result_2 = initialize_database_schema()
        self.assertTrue(result_2['success'])

        # Verify only 1 admin exists and password was NOT overwritten
        admin_count = User.query.filter_by(username='admin').count()
        self.assertEqual(admin_count, 1)
        
        reloaded_admin = User.query.filter_by(username='admin').first()
        self.assertTrue(reloaded_admin.verify_password('CustomProductionSecret999!'))
        self.assertFalse(reloaded_admin.verify_password('admin'))

    def test_03_login_admin_redirects_to_dashboard(self):
        """Verify login with admin/admin redirects to /admin/dashboard and grants access."""
        initialize_database_schema()

        # POST credentials to login
        res = self.client.post('/auth/login', data={
            'identifier': 'admin',
            'password': 'admin'
        }, follow_redirects=False)

        # Should redirect to admin dashboard
        self.assertEqual(res.status_code, 302)
        self.assertIn('/admin/dashboard', res.headers.get('Location', ''))

        # Follow redirect and verify HTTP 200 on dashboard
        res_dash = self.client.get('/admin/dashboard')
        self.assertEqual(res_dash.status_code, 200)
        self.assertIn(b'Administrator Dashboard', res_dash.data)

    def test_04_health_endpoint_safe_response(self):
        """Verify GET /health returns exact {"status": "ok"} with no credentials."""
        res = self.client.get('/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data, {'status': 'ok'})

    def test_05_role_based_access_control(self):
        """Verify student cannot access admin dashboard."""
        seed_database_safely()

        # Login as student
        res = self.client.post('/auth/login', data={
            'identifier': 'student',
            'password': 'student123'
        }, follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn('/student/dashboard', res.headers.get('Location', ''))

        # Student attempting to access admin dashboard -> 403 Forbidden
        res_admin = self.client.get('/admin/dashboard')
        self.assertEqual(res_admin.status_code, 403)


if __name__ == '__main__':
    unittest.main()
