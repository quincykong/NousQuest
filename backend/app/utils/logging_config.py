import logging
import os
from flask import Flask
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config.from_object('config.Config')  # Load the config

def setup_logger(logger_name, log_file, level=logging.INFO, max_bytes=1000000, backup_count=5):
    """Set up a logger with rotation and custom settings."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Ensure the log directory exists
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Check if the logger already has handlers to avoid duplicate logs
    if not logger.hasHandlers():
        handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# Create the security logger
security_logger = setup_logger(
    logger_name='security_logger',
    log_file=os.path.join(app.config['LOG_DIR'], 'security.log'),
    level=getattr(logging, app.config['LOG_LEVEL']),  # Convert string to logging level
    max_bytes=app.config['LOG_MAX_BYTES'],
    backup_count=app.config['LOG_BACKUP_COUNT']
)

# Create the app logger
app_logger = setup_logger(
    logger_name='app_logger',
    log_file=os.path.join(app.config['LOG_DIR'], 'app.log'),
    level=getattr(logging, app.config['LOG_LEVEL']),
    max_bytes=app.config['LOG_MAX_BYTES'],
    backup_count=app.config['LOG_BACKUP_COUNT']
)

# Create the frontend error logger
frontend_logger = setup_logger(
    logger_name='frontend_logger',
    log_file=os.path.join(app.config['LOG_DIR'], 'frontend_error.log'),
    level=getattr(logging, app.config['LOG_LEVEL']),
    max_bytes=app.config['LOG_MAX_BYTES'],
    backup_count=app.config['LOG_BACKUP_COUNT']
)
