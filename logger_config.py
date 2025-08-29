import logging
import os
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

def setup_logger(name, log_file):
    """
    Setup a logger with both file and console handlers.
    
    Args:
        name: The name of the logger
        log_file: The file to log to (will be placed in the logs directory)
    
    Returns:
        A configured logger
    """
    # Create full path for log file
    log_path = logs_dir / log_file
    
    # Create a logger
    logger = logging.getLogger(name)
    
    # Don't configure the same logger twice
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Create handlers
    file_handler = logging.FileHandler(log_path)
    console_handler = logging.StreamHandler()
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
