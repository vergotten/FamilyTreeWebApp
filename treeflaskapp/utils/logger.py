import os
import logging

def setup_logger(name, log_file, level=logging.INFO):
    """Set up a logger for the specified name and log file."""
    # Get the directory of the root of the application
    root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    # Create a /logs directory in the root of the application
    logs_dir = os.path.join(root_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Specify the log file path
    log_file = os.path.join(logs_dir, log_file)

    # Create a custom logger
    logger = logging.getLogger(name)

    # Set the level of this logger
    logger.setLevel(level)

    # Create file handler which logs messages
    file_handler = logging.FileHandler(log_file)

    # Create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to logger
    logger.addHandler(file_handler)

    return logger
