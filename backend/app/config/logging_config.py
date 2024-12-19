import logging
import os
from flask import current_app
from logging.handlers import RotatingFileHandler

def setup_logger(logger_name, log_file, level=logging.INFO, max_bytes=1000000, backup_count=5, log_format=None):
    """
    Sets up a logger with specified configurations.

    Args:
        logger_name (str): Name of the logger.
        log_file (str): Path to the log file.
        level (int): Logging level (e.g., logging.INFO).
        max_bytes (int): Maximum size of the log file in bytes.
        backup_count (int): Number of backup log files to keep.
        log_format (str, optional): Custom log format. Defaults to a standard format.

    Returns:
        logging.Logger: Configured logger object.
    """
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
            log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'

        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger

def initialize_loggers(app):
    """
    Initialize a logger with specified configurations.

    Args:
        None

    Returns:
        None
    """
    
    try:
        log_dir = app.config['LOG_DIR']
        log_level = getattr(logging, app.config['LOG_LEVEL'].upper(), logging.INFO)
        max_bytes = app.config['LOG_MAX_BYTES']
        backup_count = app.config['LOG_BACKUP_COUNT']
    except KeyError as e:
        raise RuntimeError(f"Missing logging configuration key: {e}")
    
    # Convert integer log level to string and ensure log_level is valid
    if isinstance(log_level, int):
        log_level = logging.getLevelName(log_level)
    if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        raise RuntimeError(f"Invalid log level: {log_level}")

    # Ensure log directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

   # Set up application loggers
    app.logger = setup_logger(
        'app_logger',
        log_file=os.path.join(log_dir, 'app.log'),
        level=log_level,
        max_bytes=max_bytes,
        backup_count=backup_count,
        log_format='%(asctime)s - %(name)s - %(levelname)s - [APP] %(message)s'
    )

    app.security_logger = setup_logger(
        'security_logger',
        log_file=os.path.join(log_dir, 'security.log'),
        level=log_level,
        max_bytes=max_bytes,
        backup_count=backup_count,
        log_format='%(asctime)s - %(name)s - %(levelname)s - [SECURITY] %(message)s'
    )

    app.frontend_logger = setup_logger(
        'frontend_logger',
        log_file=os.path.join(log_dir, 'frontend_error.log'),
        level=log_level,
        max_bytes=max_bytes,
        backup_count=10,
        log_format='%(asctime)s - %(levelname)s - [FRONTEND] %(message)s'
    )

    # Redirect Flask's internal logger to the app logger
    flask_logger = logging.getLogger('werkzeug')
    flask_logger.handlers = []  # Clear default handlers
    flask_logger.addHandler(app.logger.handlers[0])  # Use app logger's handler

# Add these functions to retrieve the loggers
def get_app_logger():
    return logging.getLogger('app_logger')

def get_security_logger():
    return logging.getLogger('security_logger')

def get_frontend_logger():
    return logging.getLogger('frontend_logger')