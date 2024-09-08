import logging
import pika
from logging.handlers import RotatingFileHandler

def create_logger_instance(name, level=logging.INFO, isFrontend=True):
    """Set up a custom logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Check if the logger already has handlers
    if not logger.hasHandlers():
        # Create a console handler
        ch = logging.StreamHandler()
        ch.setLevel(level)
        
        # Create a file handler
        logFileName = 'app.log'
        if (isFrontend):
            logFileName = 'frontend-app.log'
        fh = logging.FileHandler(logFileName)
        fh.setLevel(level)

        # Create a formatter and set it for both handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger
