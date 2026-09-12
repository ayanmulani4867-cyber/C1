"""
Firebase Realtime Database Isolated CRUD Verification Script
Tests CREATE, READ, UPDATE, DELETE strictly on /_test_connection/
against https://campus-connect-4e66c-default-rtdb.firebaseio.com/
without corrupting production data and without local fallback.
"""
import os
import sys
import uuid
from datetime import datetime

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services import firebase_service

def run_isolated_firebase_test():
    print("=" * 60)
    print("FIREBASE REALTIME DATABASE ISOLATED CRUD TEST")
    print("Target Database: https://campus-connect-4e66c-default-rtdb.firebaseio.com/")
    print("Path: /_test_connection/")
    print("=" * 60)
    
    # 1. Inspect Environment Variables
    db_url = os.environ.get('FIREBASE_DATABASE_URL', 'https://campus-connect-4e66c-default-rtdb.firebaseio.com/')
    service_key = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY')
    db_secret = os.environ.get('FIREBASE_DATABASE_SECRET')
    
    print("\n[Step 1] Environment Variables Inspection:")
    print(f"  - FIREBASE_DATABASE_URL: {db_url}")
    print(f"  - FIREBASE_SERVICE_ACCOUNT_KEY: {'[CONFIGURED]' if service_key else '[MISSING/NOT SET]'}")
    print(f"  - FIREBASE_DATABASE_SECRET: {'[CONFIGURED]' if db_secret else '[MISSING/NOT SET]'}")
    
    # 2. Attempt Connection
    print("\n[Step 2] Initializing Firebase Connection (No fallback allowed)...")
    connected = firebase_service.init_firebase()
    print(f"  - is_firebase_connected(): {firebase_service.is_firebase_connected()}")
    
    test_id = f"test_{uuid.uuid4().hex[:8]}"
    test_path = f"_test_connection/{test_id}"
    test_data = {
        "test_id": test_id,
        "message": "Campus Connect Production Audit Probe",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "created"
    }
    
    print(f"\n[Step 3] Testing CREATE at /{test_path}...")
    create_success = firebase_service._rtdb_set(test_path, test_data)
    if not create_success:
        print("  [FAIL] CREATE FAILED: Unable to write to Firebase Realtime Database.")
        print("  Diagnosing root cause...")
        # Direct probe via requests to get exact server response
        import requests
        url = f"{db_url.rstrip('/')}/{test_path}.json"
        params = {}
        if db_secret:
            params['auth'] = db_secret
        try:
            resp = requests.put(url, params=params, json=test_data, timeout=5)
            print(f"  Firebase HTTP Status Code: {resp.status_code}")
            print(f"  Firebase HTTP Response: {resp.text.strip()}")
            if resp.status_code == 401:
                print("\n  [DIAGNOSIS] Firebase returned HTTP 401 Unauthorized / Permission Denied.")
                print("  Reason: Authentication credential is required to access secured database rules.")
        except Exception as ex:
            print(f"  Connection probe error: {ex}")
        return False

    print("  [PASS] CREATE SUCCESSFUL: Record written to Firebase Realtime Database.")
    
    print(f"\n[Step 4] Testing READ at /{test_path}...")
    read_data = firebase_service._rtdb_get(test_path)
    if read_data and read_data.get("test_id") == test_id:
        print(f"  [PASS] READ SUCCESSFUL: Retrieved record from Firebase: {read_data}")
    else:
        print(f"  [FAIL] READ FAILED: Expected {test_id}, got: {read_data}")
        return False

    print(f"\n[Step 5] Testing UPDATE at /{test_path}...")
    update_payload = {"status": "updated_verified", "updated_at": datetime.utcnow().isoformat()}
    update_success = firebase_service._rtdb_update(test_path, update_payload)
    if update_success:
        verified_data = firebase_service._rtdb_get(test_path)
        if verified_data and verified_data.get("status") == "updated_verified":
            print(f"  [PASS] UPDATE SUCCESSFUL: Verified updated state: {verified_data}")
        else:
            print("  [FAIL] UPDATE FAILED: Value mismatch after patch.")
            return False
    else:
        print("  [FAIL] UPDATE FAILED.")
        return False

    print(f"\n[Step 6] Testing DELETE at /{test_path}...")
    delete_success = firebase_service._rtdb_delete(test_path)
    if delete_success:
        post_delete_read = firebase_service._rtdb_get(test_path)
        if post_delete_read is None:
            print(f"  [PASS] DELETE SUCCESSFUL: Verified path /{test_path} is completely removed from Firebase.")
        else:
            print(f"  [FAIL] DELETE FAILED: Node still exists: {post_delete_read}")
            return False
    else:
        print("  [FAIL] DELETE FAILED.")
        return False

    print("\n" + "=" * 60)
    print("[PASS] ALL 4 ISOLATED FIREBASE CRUD OPERATIONS PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_isolated_firebase_test()
    sys.exit(0 if success else 1)
