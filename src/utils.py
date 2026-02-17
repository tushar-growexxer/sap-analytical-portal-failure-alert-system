import logging
import sys
import os
from src import config

def setup_logger(name="app"):
    """
    Configures a logger that outputs to console and logs/logs.txt file.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Check if handler exists to avoid duplicate logs
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler for continuous logging
        os.makedirs(config.LOG_DIRECTORY, exist_ok=True)
        file_handler = logging.FileHandler(config.LOG_FILE_PATH, mode='a', encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger