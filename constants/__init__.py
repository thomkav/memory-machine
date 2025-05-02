"""
Constants module for the Memory Machine project.

This module contains classes that register string literals as constants
to be used throughout the application for consistency and maintainability.
"""

from pathlib import Path

from constants.gmail import *  # noqa: F401, F403
from constants.mongodb import *  # noqa: F401, F403
from constants.s3 import *  # noqa: F401, F403


class FilePaths:
    """Constants for file paths."""

    ROOT_DIR = Path(__file__).parent.parent

    # Copilot-related paths
    COPILOT_DIR = ROOT_DIR / ".github"
    COPILOT_INSTRUCTIONS = COPILOT_DIR / "copilot-instructions.md"
    COPILIT_EDIT_LOG_DIR = COPILOT_DIR / "edit-logs"
    COPILOT_FILE_VISIBILITY_LOG = COPILIT_EDIT_LOG_DIR / "file-visibility.log"

    # Gmail-related paths
    GMAIL_DIR = ROOT_DIR / "gmail"
    GOOGLE_CLOUD_API_CREDENTIALS = GMAIL_DIR / "google-cloud-api-credentials.json"
    GOOGLE_CLOUD_API_TOKEN = GMAIL_DIR / "google-cloud-api-token.pickle"
    PARSED_EMAILS_DIR = GMAIL_DIR / "parsed-emails"
    PARSED_EMAILS_DIR.mkdir(parents=True, exist_ok=True)
