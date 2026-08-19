import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.utils.db_ops import initialize_database_schema, seed_database_safely


def init_database():
    """Initializes database tables and seeds baseline institutional data safely."""
    is_prod = (
        os.environ.get('FLASK_ENV') == 'production' or
        os.environ.get('RENDER') is not None or
        (os.environ.get('DATABASE_URL') is not None and os.environ.get('FLASK_ENV') != 'development')
    )
    config_name = 'production' if is_prod else os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)
    
    with app.app_context():
        print(f"Initializing database using environment: {config_name}...")
        init_result = initialize_database_schema()
        print(f"Initialization Status: {init_result.get('status')}")
        print(f"Admin Account: {init_result.get('admin_user', {}).get('username')} ({init_result.get('admin_user', {}).get('status')})")
        
        print("Running idempotent institutional database seeding...")
        seed_result = seed_database_safely()
        print(f"Seeding Status: {seed_result.get('status')}")
        print(f"Message: {seed_result.get('message')}")
        print(f"Record Counts: {seed_result.get('counts', {})}")


if __name__ == '__main__':
    init_database()

