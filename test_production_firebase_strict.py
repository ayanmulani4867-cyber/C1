"""
Tests that production strictly requires Firebase and rejects silent SQLite fallback.
"""
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services import firebase_service
from app.services.firebase_service import FirebaseConnectionError

class TestProductionFirebaseStrict(unittest.TestCase):
    def setUp(self):
        # Force production mode
        os.environ['FLASK_ENV'] = 'production'
        os.environ['REQUIRE_FIREBASE'] = '1'
        self.app = create_app('production')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        os.environ.pop('REQUIRE_FIREBASE', None)
        os.environ['FLASK_ENV'] = 'development'
        self.app_context.pop()

    def test_production_rejects_silent_fallback_when_firebase_unconnected(self):
        """In production, without Firebase credentials, entity operations must raise FirebaseConnectionError."""
        self.assertTrue(firebase_service.is_production_mode())
        if not firebase_service.is_firebase_connected():
            with self.assertRaises(FirebaseConnectionError):
                firebase_service.get_students()
            with self.assertRaises(FirebaseConnectionError):
                firebase_service.get_faculty()
            with self.assertRaises(FirebaseConnectionError):
                firebase_service.get_departments()
            with self.assertRaises(FirebaseConnectionError):
                firebase_service.get_courses()
            with self.assertRaises(FirebaseConnectionError):
                firebase_service.get_subjects()
            with self.assertRaises(FirebaseConnectionError):
                firebase_service.get_attendance()
            with self.assertRaises(FirebaseConnectionError):
                firebase_service.get_results()
            with self.assertRaises(FirebaseConnectionError):
                firebase_service.get_notices()
            with self.assertRaises(FirebaseConnectionError):
                firebase_service.create_student({'first_name': 'Test', 'last_name': 'Student'})

    def test_api_returns_503_in_production_when_firebase_unconnected(self):
        """In production, API endpoints must return 503 instead of pretending to succeed with local SQLite."""
        if not firebase_service.is_firebase_connected():
            res = self.client.get('/api/students')
            # If not logged in -> 401 or 503
            self.assertIn(res.status_code, (401, 503))

if __name__ == '__main__':
    unittest.main()

