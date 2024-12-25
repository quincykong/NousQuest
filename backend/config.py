import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Existing configurations
    APP_NAME = "NousQuest"
    LOG_LEVEL = "DEBUG"
    
    # Flask-Cahce
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_TIMEOUT = 600  # Timeout in seconds
    CACHE_TYPE = "SimpleCache"  # Use SimpleCache for development

    # SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # true=dump sql
    SQLALCHEMY_ECHO = False

    # Uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    SEND_FILE_MAX_AGE_DEFAULT = 0

    # Logger
    LOG_MAX_BYTES = 100000000  # 100 MB
    LOG_BACKUP_COUNT = 5
    LOG_LEVEL = 'DEBUG'  # Can be 'DEBUG', 'INFO', etc.
    LOG_DIR = os.path.join(os.path.dirname(__file__), 'log/')

    SECURITY = {
        "JWT_SECRET_KEY": 'NousQuest-2024',  # Key for JWT token signing
        "JWT_ACCESS_TOKEN_EXPIRES": timedelta(minutes=60),  # Token validity duration
        "JWT_REFRESH_TOKEN_EXPIRES": timedelta(days=7),  # Refresh token duration
        "JWT_TOKEN_LOCATION": ['cookies'],  # Where to look for JWT tokens
        "JWT_COOKIE_SECURE": False,  # Set to True in production
        "JWT_ACCESS_COOKIE_NAME": 'access_token',
        "JWT_REFRESH_COOKIE_NAME": 'refresh_token',
        # CSRF protection
        #   disable below option for temporary
        #   enabled it will hit 401 CSRF double submit tokens do not match error 
        #   which I've spent 2 days to debug and could not fiture out
        #   PostMan can access the api/logout without error
        #   But frontend hit 401
        #
        "JWT_COOKIE_CSRF_PROTECT": True,  # Enable/disable CSRF protection
        "JWT_ACCESS_CSRF_COOKIE_NAME": 'csrf_access_token',  # CSRF cookie for access token
        "JWT_REFRESH_CSRF_COOKIE_NAME": 'csrf_refresh_token',  # CSRF cookie for refresh token
        "JWT_COOKIE_SAMESITE": 'Strict',  # Add same-site cookie setting for enhanced security
    }

class TestingConfig(Config):
    TESTING = True

    # Existing configurations
    APP_NAME = "NousQuest-Testing"
    LOG_LEVEL = "DEBUG"
    
    # Flask-Cahce
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_TIMEOUT = 600  # Timeout in seconds
    CACHE_TYPE = "SimpleCache"  # Use SimpleCache for development

    # SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site_test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # true=dump sql
    SQLALCHEMY_ECHO = False
    # Uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    SEND_FILE_MAX_AGE_DEFAULT = 0

    # Logger
    LOG_MAX_BYTES = 100000000  # 100 MB
    LOG_BACKUP_COUNT = 5
    LOG_LEVEL = 'DEBUG'  # Can be 'DEBUG', 'INFO', etc.
    LOG_DIR = os.path.join(os.path.dirname(__file__), 'log/')

    SECURITY = {
        "JWT_SECRET_KEY": 'NousQuest-2024',  # Key for JWT token signing
        "JWT_ACCESS_TOKEN_EXPIRES": timedelta(minutes=60),  # Token validity duration
        "JWT_REFRESH_TOKEN_EXPIRES": timedelta(days=7),  # Refresh token duration
        "JWT_TOKEN_LOCATION": ['cookies'],  # Where to look for JWT tokens
        "JWT_COOKIE_SECURE": False,  # Set to True in production
        "JWT_ACCESS_COOKIE_NAME": 'access_token',
        "JWT_REFRESH_COOKIE_NAME": 'refresh_token',
        # CSRF protection
        #   disable below option for temporary
        #   enabled it will hit 401 CSRF double submit tokens do not match error 
        #   which I've spent 2 days to debug and could not fiture out
        #   PostMan can access the api/logout without error
        #   But frontend hit 401
        #
        "JWT_COOKIE_CSRF_PROTECT": True,  # Enable/disable CSRF protection
        "JWT_ACCESS_CSRF_COOKIE_NAME": 'csrf_access_token',  # CSRF cookie for access token
        "JWT_REFRESH_CSRF_COOKIE_NAME": 'csrf_refresh_token',  # CSRF cookie for refresh token
        "JWT_COOKIE_SAMESITE": 'Strict',  # Add same-site cookie setting for enhanced security
    }