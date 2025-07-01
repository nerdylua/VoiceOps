"""
Logging utility for VoiceOps Backend
Provides structured logging with file rotation and colored console output
"""

import logging
import logging.handlers
import colorlog
import os
from datetime import datetime
from config.settings import Config

def setup_logger():
    """Setup and configure logging for VoiceOps"""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(Config.LOG_FILE_PATH)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create main logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create colored console handler
    console_handler = colorlog.StreamHandler()
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Create rotating file handler
    if Config.LOG_FILE_PATH:
        file_handler = logging.handlers.RotatingFileHandler(
            Config.LOG_FILE_PATH,
            maxBytes=Config.LOG_MAX_SIZE,
            backupCount=Config.LOG_BACKUP_COUNT
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    logger.info("Logger initialized successfully")
    return logger 