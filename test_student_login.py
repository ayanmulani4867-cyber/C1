import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import User
from app.models.student import Student
from app.utils.db_ops import initialize_database_schema, seed_database_safely

app = create_app('testing')
with app.app_context():
    initialize_database_schema()
    seed_database_safely()
    
    u = User.query.filter_by(username='student').first()
    print("User student:", u, "Role:", u.role, "Active:", u.is_active, "must_change_password:", u.must_change_password)
    print("Check password 'student123':", u.check_password('student123'))
    
    s = Student.query.filter_by(user_id=u.id).first()
    print("Student record:", s, "ID:", s.id if s else None)

client = app.test_client()
res = client.post('/auth/login', data={'identifier': 'student', 'password': 'student123'}, follow_redirects=False)
print("Login post status:", res.status_code, "Location:", res.headers.get('Location'))

res_dash = client.get('/student/dashboard')
print("Dashboard status:", res_dash.status_code)
if res_dash.status_code != 200:
    print("Dashboard response snippet:\n", res_dash.data.decode('utf-8')[:500])
