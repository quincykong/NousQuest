import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    APP_NAME = "NousQuest"
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'OpenClass_2024'
    JWT_SECRET_KEY = 'NousQuest-2024'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    SEND_FILE_MAX_AGE_DEFAULT = 0
    # Logger
    LOG_MAX_BYTES = 100000000  # 100 MB
    LOG_BACKUP_COUNT = 5
    LOG_LEVEL = 'INFO'  # Can be 'DEBUG', 'INFO', etc.
    LOG_DIR = os.path.join(os.path.dirname(__file__), 'log/')