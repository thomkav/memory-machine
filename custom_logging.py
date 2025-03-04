import logging
import os
from typing import Optional

LOG_DIR = "logs"
LOG_FILE = "application.log"
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

# Ensure the logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

print("Logs will also be saved to:", LOG_PATH)


def getLogger(name: Optional[str] = None) -> logging.Logger:
    # Ensure root logger does not have handlers that could cause duplicates
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Get the logger
    logger = logging.getLogger(name=name)

    # Set the log level
    logger.setLevel(logging.INFO)

    # Remove any existing handlers
    while logger.handlers:
        handler = logger.handlers[0]
        logger.removeHandler(handler)

    # Create a file handler
    fileHandler = logging.FileHandler(LOG_PATH)
    fileHandler.setLevel(logging.INFO)

    # Create a stream handler
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fileHandler.setFormatter(formatter)
    streamHandler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)

    return logger


# Example usage:
if __name__ == "__main__":
    logger = getLogger("example.logger")
    logger.info("This is a test log message.")
