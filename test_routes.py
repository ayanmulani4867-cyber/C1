import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import User

app = create_app('development')
client = app.test_client()

print("--- Testing Anonymous Routes ---")
anonymous_routes = [
    ('/', 200),
    ('/about', 200),
    ('/contact', 200),
    ('/auth/login', 200),
    ('/notices/', 200),
]

for url, expected in anonymous_routes:
    res = client.get(url)
    status = res.status_code
    print(f"GET {url} -> {status} {'✓' if status == expected else '✗ ERROR'}")
    if status != expected:
        print(f"  Error details: {res.data.decode('utf-8')[:500]}")

roles_to_test = [
    ('admin', 'admin123', [
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
        '/timetable/',
        '/assignments/',
        '/exams/',
        '/exams/results',
        '/fees/',
        '/fees/dues',
        '/leaves/',
        '/notices/',
        '/feedback/',
        '/certificates/',
        '/reports/',
    ]),
    ('hod_cse', 'hod123', [
        '/faculty/dashboard',
        '/student/list',
        '/faculty/list',
        '/attendance/',
        '/timetable/',
        '/assignments/',
        '/exams/',
        '/exams/results',
        '/leaves/',
        '/notices/',
        '/feedback/',
    ]),
    ('faculty', 'faculty123', [
        '/faculty/dashboard',
        '/attendance/',
        '/attendance/mark',
        '/timetable/',
        '/assignments/',
        '/assignments/create',
        '/exams/',
        '/exams/results',
        '/leaves/',
        '/notices/',
        '/feedback/',
    ]),
    ('student', 'student123', [
        '/student/dashboard',
        '/attendance/',
        '/timetable/',
        '/assignments/',
        '/exams/',
        '/exams/results',
        '/fees/',
        '/leaves/',
        '/leaves/apply',
        '/notices/',
        '/feedback/',
        '/certificates/',
        '/certificates/request',
    ]),
]

for username, password, urls in roles_to_test:
    print(f"\n--- Testing Authenticated Role: {username} ---")
    # Login via demo login endpoint or post
    login_res = client.get(f"/demo-login/{username}", follow_redirects=True)
    if login_res.status_code != 200:
        print(f"Demo login for {username} returned {login_res.status_code}")
    
    for url in urls:
        res = client.get(url)
        status = res.status_code
        print(f"[{username}] GET {url} -> {status} {'✓' if status in (200, 302) else '✗ ERROR'}")
        if status not in (200, 302):
            print(f"  Error details: {res.data.decode('utf-8')[:600]}")

print("\n--- Route testing complete ---")
