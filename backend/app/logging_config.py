import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    """Configure application and security loggers using app config."""
    log_dir = app.config.get("LOG_DIR", "./log")
    log_max_bytes = app.config.get("LOG_MAX_BYTES", 10 * 1024 * 1024)  # Default 10 MB
    log_backup_count = app.config.get("LOG_BACKUP_COUNT", 3)  # Default 3 backups
    log_level = app.config.get("LOG_LEVEL", "INFO")  # Default INFO

    os.makedirs(log_dir, exist_ok=True)

    # Configure app logger
    app_logger = logging.getLogger("app_logger")
    app_logger.setLevel(log_level)
    app_file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=log_max_bytes,
        backupCount=log_backup_count,
    )
    app_file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    app_logger.addHandler(app_file_handler)

    # Configure security logger
    security_logger = logging.getLogger("security_logger")
    security_logger.setLevel(log_level)
    security_file_handler = RotatingFileHandler(
        os.path.join(log_dir, "security.log"),
        maxBytes=log_max_bytes,
        backupCount=log_backup_count,
    )
    security_file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    security_logger.addHandler(security_file_handler)

    # Optional: Add console handler for debugging
    if app.config.get("DEBUG", False):  # Only log to console in debug mode
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("[%(name)s] %(message)s"))
        app_logger.addHandler(console_handler)
        security_logger.addHandler(console_handler)

    # Attach loggers to the Flask app
    app.app_logger = app_logger
    app.security_logger = security_logger
