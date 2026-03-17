import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Core
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://ctf:ctf@localhost:5432/ctfdb'
    )
    # Render.com uses postgres:// – normalise
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Mail
    MAIL_SERVER   = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT     = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS  = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL  = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'ctf@arena.local')
    MAIL_SUPPRESS_SEND = os.environ.get('MAIL_SUPPRESS_SEND', 'False').lower() == 'true'
    MAIL_TIMEOUT = 10  # don't hang forever if Gmail is slow


    # CTF Settings
    FLAG_PREFIX          = os.environ.get('FLAG_PREFIX', 'THA')
    CTF_NAME             = os.environ.get('CTF_NAME', 'Dragon Ball Z Cyber Arena')
    MAX_TEAM_SIZE        = int(os.environ.get('MAX_TEAM_SIZE', 3))
    MAX_ATTEMPTS         = int(os.environ.get('MAX_ATTEMPTS', 10))
    PENALTY_POINTS       = int(os.environ.get('PENALTY_POINTS', 10))
    SUBMISSION_RATE_LIMIT = '1 per second'

    # Admin
    ADMIN_EMAIL    = os.environ.get('ADMIN_EMAIL', 'admin@ctf.local')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'ChangeMe123!')

    # Cache
    SCOREBOARD_CACHE_TTL = int(os.environ.get('SCOREBOARD_CACHE_TTL', 10))

    # Dynamic flags
    DYNAMIC_FLAG_SECRET = os.environ.get('DYNAMIC_FLAG_SECRET', 'dynamic-secret-key')

    # Upload
    UPLOAD_FOLDER   = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'static', 'uploads'))
    MAX_CONTENT_LENGTH = 64 * 1024 * 1024  # 64 MB

    # Freeze scoreboard 1 hour before end
    FREEZE_MINUTES_BEFORE_END = int(os.environ.get('FREEZE_MINUTES_BEFORE_END', 60))


class DevelopmentConfig(Config):
    DEBUG = True
    


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
