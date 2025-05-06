"""
Gmail to S3 File Uploader
This script queries a Gmail account for messages,
downloads any attachments, and uploads them to an S3 bucket as well as saves metadata to MongoDB.
"""
import os

from constants import FilePaths, S3Constants
from custom_logging import getLogger
from gmail.processor import GmailMessageProcessor

logger = getLogger(__name__)


if __name__ == "__main__":
    # Configuration
    CHECK_INTERVAL = None  # Time interval to check for new emails (None for immediate)
    REPLACE_EXISTING = True  # Set to True to replace existing documents
    DRY_RUN = True  # Set to True for a dry run (no actual uploads to S3 or MongoDB)
    EMAIL_FILTER = os.getenv("EMAIL_FILTER", None)  # Optional email filter
    if EMAIL_FILTER:
        logger.info(f"Using email filter: {EMAIL_FILTER}")
    else:
        logger.info("No email filter provided.")

    # Create and run the uploader
    processor = GmailMessageProcessor(
        credentials_file=FilePaths.GOOGLE_CLOUD_API_CREDENTIALS,
        token_file=FilePaths.GOOGLE_CLOUD_API_TOKEN,
        dest_s3_bucket_name=S3Constants.BUCKET_NAME,
        check_interval=CHECK_INTERVAL,
        replace_existing=REPLACE_EXISTING,
    )

    processor.process_emails(
        dry_run=DRY_RUN,
        email_filter=EMAIL_FILTER,
    )
