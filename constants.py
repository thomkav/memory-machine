"""
Stores all the constants used in the project
"""

from pathlib import Path


class FilePaths:

    ROOT_DIR = Path(__file__).parent

    COPILOT_DIR = ROOT_DIR / ".github"

    COPILOT_INSTRUCTIONS = COPILOT_DIR / "copilot-instructions.md"

    COPILIT_EDIT_LOG_DIR = COPILOT_DIR / "edit-logs"

    COPILOT_FILE_VISIBILITY_LOG = COPILIT_EDIT_LOG_DIR / "file-visibility.log"
