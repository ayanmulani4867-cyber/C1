import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from app.extensions import db
    import app.models

    app = create_app('development')
    print("SUCCESS: create_app() succeeded.")

    with app.app_context():
        print("Checking DB tables creation...")
        db.create_all()
        print("SUCCESS: db.create_all() succeeded.")

        # Check all routes and endpoints
        print(f"Total routes registered: {len(list(app.url_map.iter_rules()))}")
        for rule in app.url_map.iter_rules():
            print(f"  {rule.endpoint} -> {rule.rule}")

except Exception as e:
    import traceback
    print("ERROR OCCURRED:")
    traceback.print_exc()
    sys.exit(1)
