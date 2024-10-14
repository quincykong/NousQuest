import logging
import os
from flask import current_app
from logging.handlers import RotatingFileHandler

def setup_logger(logger_name, log_file, level=logging.INFO, max_bytes=1000000, backup_count=5, log_format=None):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Ensure the log directory exists
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Check if the logger already has handlers to avoid duplicate logs
    if not logger.hasHandlers():
        handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)

        # Use a default format if no custom format is provided
        if log_format is None:
            log_format = '%(asctime)s - %(levelname)s - %(message)s'

        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger

def initialize_loggers(app):
    log_dir = app.config['LOG_DIR']
    log_level = getattr(logging, app.config['LOG_LEVEL'])
    max_bytes = app.config['LOG_MAX_BYTES']
    backup_count = app.config['LOG_BACKUP_COUNT']

    # Initialize all loggers here
    setup_logger(
        logger_name='app_logger',
        log_file=os.path.join(log_dir, 'app.log'),
        level=log_level,
        max_bytes=max_bytes,
        backup_count=backup_count,
        log_format='%(asctime)s - %(name)s - %(levelname)s - [APP] %(message)s'
    )

    setup_logger(
        logger_name='security_logger',
        log_file=os.path.join(log_dir, 'security.log'),
        level=log_level,
        max_bytes=max_bytes,
        backup_count=backup_count,
        log_format='%(asctime)s - %(name)s - %(levelname)s - [SECURITY] %(message)s'
    )

    setup_logger(
        logger_name='frontend_logger',
        log_file=os.path.join(log_dir, 'frontend_error.log'),
        level=log_level,
        max_bytes=max_bytes,
        backup_count=10,
        log_format='%(asctime)s - %(levelname)s - [FRONTEND] %(message)s'
    )

# Accessor functions to get the loggers
def get_app_logger():
    return logging.getLogger('app_logger')

def get_security_logger():
    return logging.getLogger('security_logger')

def get_frontend_logger():
    return logging.getLogger('frontend_logger')
