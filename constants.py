"""
Constants module for the Memory Machine project.

This module contains classes that register string literals as constants
to be used throughout the application for consistency and maintainability.
"""

from pathlib import Path
from typing import ClassVar


class FilePaths:
    """Constants for file paths."""
    ROOT_DIR = Path(__file__).parent
    COPILOT_DIR = ROOT_DIR / ".github"
    COPILOT_INSTRUCTIONS = COPILOT_DIR / "copilot-instructions.md"
    COPILIT_EDIT_LOG_DIR = COPILOT_DIR / "edit-logs"
    COPILOT_FILE_VISIBILITY_LOG = COPILIT_EDIT_LOG_DIR / "file-visibility.log"


class MessageKeys:
    """Constants for message dictionary keys."""
    ID: ClassVar[str] = 'id'
    SENDER: ClassVar[str] = 'sender'
    SUBJECT: ClassVar[str] = 'subject'
    SNIPPET: ClassVar[str] = 'snippet'
    INTERNAL_DATE: ClassVar[str] = 'internalDate'
    PAYLOAD: ClassVar[str] = 'payload'
    HEADERS: ClassVar[str] = 'headers'


class HeaderKeys:
    """Constants for header dictionary keys."""
    NAME: ClassVar[str] = 'name'
    VALUE: ClassVar[str] = 'value'
    FROM: ClassVar[str] = 'From'
    SUBJECT: ClassVar[str] = 'Subject'
    DATE: ClassVar[str] = 'Date'


class PayloadKeys:
    """Constants for payload dictionary keys."""
    PARTS: ClassVar[str] = 'parts'
    FILENAME: ClassVar[str] = 'filename'
    BODY: ClassVar[str] = 'body'
    ATTACHMENT_ID: ClassVar[str] = 'attachmentId'
    DATA: ClassVar[str] = 'data'


class AttachmentInfoKeys:
    """Constants for attachment info dictionary keys."""
    FILENAME: ClassVar[str] = 'filename'
    LOCAL_PATH: ClassVar[str] = 'local_path'
    SENDER: ClassVar[str] = 'sender'
    SUBJECT: ClassVar[str] = 'subject'
    DATE: ClassVar[str] = 'date'
    MESSAGE_ID: ClassVar[str] = 'message_id'
    SIZE: ClassVar[str] = 'size'
    TIMESTAMP: ClassVar[str] = 'timestamp'
    DETERMINISTIC_ID: ClassVar[str] = 'deterministic_id'
    S3_BUCKET: ClassVar[str] = 's3_bucket'
    S3_KEY: ClassVar[str] = 's3_key'
    S3_URL: ClassVar[str] = 's3_url'


class MongoDBKeys:
    """Constants for MongoDB document keys."""
    MESSAGE_ID: ClassVar[str] = 'message_id'
    FILENAME: ClassVar[str] = 'filename'
    ORIGINAL_FILENAME: ClassVar[str] = 'original_filename'
    SENDER: ClassVar[str] = 'sender'
    SENDER_EMAIL: ClassVar[str] = 'sender_email'
    SUBJECT: ClassVar[str] = 'subject'
    DATE_RECEIVED: ClassVar[str] = 'date_received'
    SIZE_BYTES: ClassVar[str] = 'size_bytes'
    TIMESTAMP: ClassVar[str] = 'timestamp'
    PROCESSED_AT: ClassVar[str] = 'processed_at'
    S3_BUCKET: ClassVar[str] = 's3_bucket'
    S3_KEY: ClassVar[str] = 's3_key'
    S3_URL: ClassVar[str] = 's3_url'
    CONTENT_TYPE: ClassVar[str] = 'content_type'
    PROCESSED_BY: ClassVar[str] = 'processed_by'
    ATTACHMENTS: ClassVar[str] = 'attachments'
