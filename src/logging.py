import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from src.config import settings

logger = logging.getLogger('file_converter')

def setup_logging():
    log_folder = settings.LOGS_FOLDER
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    log_level = getattr(logging, settings.LOG_LEVEL.upper())
    logger.setLevel(log_level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    file_handler = RotatingFileHandler(
        os.path.join(log_folder, 'app.log'),
        maxBytes=10*1024*1024,
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    logger.handlers = []
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Logging configured (Level: {settings.LOG_LEVEL})")
