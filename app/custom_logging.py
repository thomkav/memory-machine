"""
Module to define a custom logging class for use in the Memory Machine UI.
"""

import logging
import sys

from app.constants import FilePaths

# Define the log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Define the log file
LOG_FILE = FilePaths.REPO_ROOT_DIR / "memory_machine_ui.log"

# Define the log level
LOG_LEVEL = logging.DEBUG


def make_logger(name="memory_machine_ui", level=LOG_LEVEL,
                log_format=LOG_FORMAT, log_file=LOG_FILE):
    """
    Create and configure a logger with file and console handlers.

    Args:
        name (str): Name of the logger
        level: Logging level
        log_format (str): Format string for log messages
        log_file (Path): Path to the log file

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(log_format)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Create the default logger
LOGGER = make_logger()
