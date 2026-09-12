import requests

BASE_URL = "http://127.0.0.1:5000"

def test_live_portal():
    session = requests.Session()
    
    print("1. Checking GET /health...")
    r = session.get(f"{BASE_URL}/health")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    print("   -> OK:", r.json())
    
    print("2. Checking GET /login (Stitch UI delivery)...")
    r = session.get(f"{BASE_URL}/login")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    assert "stitch_connector.js" in r.text, "Stitch connector script missing"
    assert "CAMPUS CONNECT" in r.text or "Sign in" in r.text or "password" in r.text
    print("   -> OK: Stitch Login UI served successfully")
    
    print("3. Authenticating as Admin via POST /api/login...")
    login_payload = {"username": "admin", "password": "admin"}
    r = session.post(f"{BASE_URL}/api/login", json=login_payload)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    login_data = r.json()
    assert login_data.get("success"), f"Login failed: {login_data}"
    token = login_data.get("token")
    print(f"   -> OK: Authenticated as {login_data.get('user', {}).get('username')} (Role: {login_data.get('user', {}).get('role')})")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("4. Checking GET /admin/dashboard (Stitch Executive Dashboard)...")
    r = session.get(f"{BASE_URL}/admin/dashboard", headers=headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    assert "Executive Governance" in r.text or "Dashboard" in r.text or "stitch_connector.js" in r.text
    print("   -> OK: Stitch Executive Dashboard rendered with 200")
    
    print("5. Checking GET /admin/students (Stitch Students Directory)...")
    r = session.get(f"{BASE_URL}/admin/students", headers=headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    print("   -> OK: Students Directory page rendered with 200")
    
    print("6. Checking GET /admin/faculty (Stitch Faculty Directory)...")
    r = session.get(f"{BASE_URL}/admin/faculty", headers=headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    print("   -> OK: Faculty Directory page rendered with 200")
    
    print("7. Checking GET /api/dashboard/stats...")
    r = session.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    stats = r.json().get("stats", {})
    print(f"   -> OK: Stats returned: {stats}")
    
    print("8. Checking GET /api/students...")
    r = session.get(f"{BASE_URL}/api/students", headers=headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    res_data = r.json()
    students = res_data if isinstance(res_data, list) else res_data.get("students", [])
    print(f"   -> OK: Loaded {len(students)} students from database")
    
    print("9. Checking GET /api/faculty...")
    r = session.get(f"{BASE_URL}/api/faculty", headers=headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    res_data = r.json()
    faculty = res_data if isinstance(res_data, list) else res_data.get("faculty", [])
    print(f"   -> OK: Loaded {len(faculty)} faculty from database")
    
    print("10. Checking all Stitch Admin and Academic Pages...")
    pages = [
        "/admin/hod",
        "/admin/departments",
        "/admin/courses",
        "/admin/subjects",
        "/attendance",
        "/results",
        "/notices",
        "/materials",
        "/events",
        "/profile",
        "/settings"
    ]
    for page in pages:
        r = session.get(f"{BASE_URL}{page}", headers=headers)
        assert r.status_code == 200, f"Page {page} failed with {r.status_code}"
        assert "stitch_connector.js" in r.text, f"Page {page} missing stitch_connector.js"
        print(f"   -> OK: {page} returned 200 with Stitch connector")

    print("11. Checking API CRUD Endpoints...")
    # Department list
    r = session.get(f"{BASE_URL}/api/departments", headers=headers)
    assert r.status_code == 200
    depts = r.json() if isinstance(r.json(), list) else r.json().get("departments", [])
    print(f"   -> OK: /api/departments loaded {len(depts)} items")

    # Courses list
    r = session.get(f"{BASE_URL}/api/courses", headers=headers)
    assert r.status_code == 200
    courses = r.json() if isinstance(r.json(), list) else r.json().get("courses", [])
    print(f"   -> OK: /api/courses loaded {len(courses)} items")

    # Subjects list
    r = session.get(f"{BASE_URL}/api/subjects", headers=headers)
    assert r.status_code == 200
    subjects = r.json() if isinstance(r.json(), list) else r.json().get("subjects", [])
    print(f"   -> OK: /api/subjects loaded {len(subjects)} items")

    # Attendance list
    r = session.get(f"{BASE_URL}/api/attendance", headers=headers)
    assert r.status_code == 200
    print("   -> OK: /api/attendance loaded")

    # Results list
    r = session.get(f"{BASE_URL}/api/results", headers=headers)
    assert r.status_code == 200
    print("   -> OK: /api/results loaded")

    # Notices list
    r = session.get(f"{BASE_URL}/api/notices", headers=headers)
    assert r.status_code == 200
    print("   -> OK: /api/notices loaded")

    # Materials list
    r = session.get(f"{BASE_URL}/api/materials", headers=headers)
    assert r.status_code == 200
    print("   -> OK: /api/materials loaded")

    # Events list
    r = session.get(f"{BASE_URL}/api/events", headers=headers)
    assert r.status_code == 200
    print("   -> OK: /api/events loaded")

    # Notifications list
    r = session.get(f"{BASE_URL}/api/notifications", headers=headers)
    assert r.status_code == 200
    print("   -> OK: /api/notifications loaded")

    print("12. Checking Role-Based Protection (unauthenticated access to /admin/dashboard)...")
    unauth_session = requests.Session()
    r = unauth_session.get(f"{BASE_URL}/admin/dashboard", allow_redirects=False)
    assert r.status_code in (302, 401, 403), f"Expected redirect or forbidden, got {r.status_code}"
    print("   -> OK: Unauthenticated access properly blocked with status", r.status_code)
    
    print("13. Checking GET /logout...")
    r = session.get(f"{BASE_URL}/logout", allow_redirects=False)
    assert r.status_code in (200, 302), f"Expected 200/302, got {r.status_code}"
    print("   -> OK: Logout executed successfully")

    print("\nALL COMPREHENSIVE LIVE SERVER & ROUTE TESTS PASSED!")

if __name__ == "__main__":
    test_live_portal()
