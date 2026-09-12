import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


def resolve_database_uri():
    """
    Resolves the local/ephemeral database URI.
    On Vercel, /tmp is the only writable local directory.
    Firebase Realtime Database acts as the primary cloud database.
    """
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        return "sqlite:////tmp/campus_connect.db"
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

    # Firebase Realtime Database Configuration
    FIREBASE_DATABASE_URL = os.environ.get('FIREBASE_DATABASE_URL', 'https://campus-connect-4e66c-default-rtdb.firebaseio.com/').rstrip('/') + '/'
    FIREBASE_SERVICE_ACCOUNT_KEY = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY')
    FIREBASE_DATABASE_SECRET = os.environ.get('FIREBASE_DATABASE_SECRET')
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', 'campus-connect-4e66c')
    FIREBASE_CLIENT_EMAIL = os.environ.get('FIREBASE_CLIENT_EMAIL')
    FIREBASE_PRIVATE_KEY = os.environ.get('FIREBASE_PRIVATE_KEY')
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH') or os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Upload configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or (
        '/tmp/uploads' if os.environ.get('VERCEL') else os.path.join(basedir, 'app', 'static', 'uploads')
    )
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
    APP_NAME = "SITCOE"
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
        # In production on Vercel, Firebase Realtime Database is primary
        pass


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


def is_production_env():
    return (
        os.environ.get('FLASK_ENV') == 'production' or
        os.environ.get('VERCEL') is not None or
        os.environ.get('RENDER') is not None
    )


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig if is_production_env() else DevelopmentConfig
}
