import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


def resolve_database_uri():
    """
    Resolves the database URI with Render PostgreSQL compatibility.
    Fixes the 'postgres://' schema prefix to 'postgresql://' as required by SQLAlchemy 1.4+.
    """
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.strip():
        db_url = db_url.strip()
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return db_url
    return f"sqlite:///{os.path.join(basedir, 'campus_connect.db')}"


class Config:
    """Base Configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'campus-connect-dev-secret-key-change-in-prod-2026'
    
    SQLALCHEMY_DATABASE_URI = resolve_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    
    # Upload configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH') or 16 * 1024 * 1024)  # 16 MB max upload
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
    ALLOWED_DOC_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png', 'txt'}
    
    # Session security (Configured for iframe & cross-site embedding in AI Studio)
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_NAME = 'campus_connect_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_PARTITIONED = True
    REMEMBER_COOKIE_NAME = 'campus_connect_remember'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'None'
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_DURATION = timedelta(days=14)

    # CSRF Protection Settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SSL_STRICT = False
    WTF_CSRF_TIME_LIMIT = None  # Prevents CSRF expiry during long form filling
    WTF_CSRF_CHECK_DEFAULT = True
    
    # Application settings
    APP_NAME = "Campus Connect"
    COLLEGE_NAME = "Sharad Institute of Technology"
    COLLEGE_SHORT_NAME = "SITCOE"
    COLLEGE_ADDRESS = "Yadrav (Ichalkaranji), Maharashtra - 416145"
    COLLEGE_EMAIL = "contact@sitcoe.org.in"
    COLLEGE_PHONE = "+91 2322 253000"

    @classmethod
    def init_app(cls, app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'
    SQLALCHEMY_DATABASE_URI = resolve_database_uri()


class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = 'production'
    SQLALCHEMY_DATABASE_URI = resolve_database_uri()

    @classmethod
    def init_app(cls, app):
        db_url = os.environ.get('DATABASE_URL')
        if not db_url and (os.environ.get('RENDER') or os.environ.get('FLASK_ENV') == 'production'):
            raise RuntimeError(
                "CRITICAL: DATABASE_URL environment variable is missing or empty in production mode on Render. "
                "Please configure your Render PostgreSQL connection string in the Render Dashboard."
            )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


def is_production_env():
    return (
        os.environ.get('FLASK_ENV') == 'production' or
        os.environ.get('RENDER') is not None or
        (os.environ.get('DATABASE_URL') is not None and os.environ.get('FLASK_ENV') != 'development')
    )


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig if is_production_env() else DevelopmentConfig
}
