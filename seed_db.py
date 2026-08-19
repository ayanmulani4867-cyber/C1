"""
Seed script to populate Campus Connect with comprehensive realistic institutional data.
Safe and idempotent: does not drop tables or delete existing production data.
"""
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.utils.db_ops import seed_database_safely


def seed_database():
    is_prod = (
        os.environ.get('FLASK_ENV') == 'production' or
        os.environ.get('RENDER') is not None or
        (os.environ.get('DATABASE_URL') is not None and os.environ.get('FLASK_ENV') != 'development')
    )
    config_name = 'production' if is_prod else os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)
    with app.app_context():
        print(f"Seeding institutional database safely using environment: {config_name}...")
        result = seed_database_safely()
        print(f"Seeding Result: {result.get('message')}")
        print(f"Entity Counts: {result.get('counts')}")


if __name__ == '__main__':
    seed_database()

