import base64
import json
import os
import pickle
import tempfile
import webbrowser
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

import boto3
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from json2html import json2html
from pydantic import BaseModel, ConfigDict

# Import constants
from constants import (
    AttachmentDocumentKeys,
    GmailAPIHeaderKeys,
    GmailAPIMessageKeys,
    GmailAPIPayloadKeys,
    MessageDocumentKeys,
    MongoDatabaseNames,
    MongoDBCollections,
    PartKeys,
)
from custom_logging import getLogger

# MongoDB library
from mongodb import client

logger = getLogger(__name__)


def open_html_in_browser(html_content):
    # Create a temporary file
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")

    # Write the HTML content to the temporary file
    temp.write(html_content.encode("utf-8"))
    temp.close()

    # Get the absolute path to the file
    file_url = "file://" + os.path.abspath(temp.name)

    # Open the file in the browser
    webbrowser.open(file_url)

    # Optional: You might want to set up cleanup of the temp file
    # This depends on your specific needs


# Gmail API scopes
GMAIL_AUTH_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


class Attachment(BaseModel):
    """Class representing attachment information."""

    filename: str
    data: bytes
    s3_bucket: str
    s3_key: str
    text_content: str | None = None
    bytes_len: int | None = None
    mime_type: str | None = None

    def _try_parse_text_content(self):
        """Try to parse the text content from the attachment data."""

        if self.filename.endswith(".md"):
            try:
                self.text_content = self.data.decode("utf-8")
            except UnicodeDecodeError:
                logger.warning(f"Failed to decode attachment data for {self.filename}")
                self.text_content = None

        else:
            try:
                self.text_content = self.data.decode("utf-8")
            except UnicodeDecodeError:
                logger.warning(f"Failed to decode attachment data for {self.filename}")
                self.text_content = None

    def __post_init__(self):
        """Post-initialization to set default values."""

        if self.bytes_len is None:
            self.bytes_len = len(self.data)

        if self.text_content is None:
            self._try_parse_text_content()

    def __repr__(self):
        """String representation of the Attachment object."""
        return f"Attachment(filename={self.filename}, size={self.bytes_len})"

    def to_mongodb_dict(self) -> dict[str, str | int | None]:
        """Convert the attachment to a MongoDB-compatible dictionary."""
        return {
            AttachmentDocumentKeys.FILENAME: self.filename,
            AttachmentDocumentKeys.FILE_DATA_SIZE: len(self.data),
            AttachmentDocumentKeys.S3_BUCKET: self.s3_bucket,
            AttachmentDocumentKeys.S3_KEY: self.s3_key,
            AttachmentDocumentKeys.TEXT_CONTENT: self.text_content,
            AttachmentDocumentKeys.MIME_TYPE: self.mime_type,
        }


class GmailMessage(BaseModel):
    """Class representing a Gmail message."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    id: str
    sender: str
    subject: str
    body: str | None = None
    date_received: str
    thread_id: str
    label_ids: list[str]
    snippet: str
    payload: dict
    size_estimate: int
    history_id: str
    internal_date: str
    attachments: list[Attachment] = []

    def __repr__(self):
        """String representation of the GmailMessage object."""
        return (
            f"GmailMessage(id={self.id}, thread_id={self.thread_id}, "
            f"label_ids={self.label_ids}, snippet={self.snippet})"
        )

    def __str__(self):
        """String representation of the GmailMessage object."""
        return (
            f"Sender: {self.sender}, "
            f"Subject: {self.subject}, "
            f"Date: {self.date_received}, "
            f"Number of Attachments: {len(self.payload.get(GmailAPIPayloadKeys.PARTS, []))}, "
        )

    def to_mongodb_record_dict(
        self,
    ) -> dict:
        """Convert the Gmail message to a MongoDB-compatible dictionary."""
        msg_info = {
            MessageDocumentKeys.MESSAGE_ID: self.id,
            MessageDocumentKeys.SENDER: self.sender,
            MessageDocumentKeys.SUBJECT: self.subject,
            MessageDocumentKeys.SNIPPET: self.snippet,
            MessageDocumentKeys.BODY: self.body,
            MessageDocumentKeys.DATE_RECEIVED: self.date_received,
            MessageDocumentKeys.PROCESSED_AT: datetime.now(),
        }

        # Add attachments to the message record
        msg_info[MessageDocumentKeys.ATTACHMENTS] = [  # type: ignore
            {
                AttachmentDocumentKeys.FILENAME: attachment.filename,
                AttachmentDocumentKeys.TEXT_CONTENT: attachment.text_content,
                AttachmentDocumentKeys.FILE_DATA_SIZE: attachment.bytes_len,
                AttachmentDocumentKeys.S3_KEY: attachment.s3_key,
                AttachmentDocumentKeys.MIME_TYPE: attachment.mime_type,
            }
            for attachment in self.attachments
        ]

        return msg_info

    def to_html(self):
        """Convert the Gmail message to an HTML representation."""
        # Convert the message to a JSON string
        json_str = json.dumps(self.to_mongodb_record_dict(), default=str, indent=4)

        # Convert JSON to HTML using json2html
        html = json2html.convert(json=json_str, table_attributes="border='1'")

        # Return the HTML representation
        return html

    @property
    def parts(self) -> list[dict]:
        """Get the parts of the message payload."""
        return self.payload.get(GmailAPIPayloadKeys.PARTS, [])


class GmailMessageProcessor:
    """
    Class to process Gmail inbox, download attachments, and upload to S3.
    This class handles authentication, message retrieval, attachment downloading,
    and S3 uploading.
    """

    def __init__(
        self,
        credentials_file: Path,
        token_file: Path,
        dest_s3_bucket_name: str,
        check_interval: int | None = None,
        replace_existing=False,
    ):
        """
        Initialize the uploader with necessary credentials and settings.

        Args:
            credentials_file (str): Path to Gmail API credentials file
            token_file (str): Path to store Gmail API token
            s3_bucket_name (str): Name of the S3 bucket to upload files to
            check_interval (int): How often to check for new emails (in seconds)
            replace_existing (bool): Whether to replace existing documents (True) or skip them (False)
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.s3_bucket_name = dest_s3_bucket_name
        self.check_interval = check_interval
        self.replace_existing = replace_existing

        # Initialize services
        self.gmail_service = self.authenticate_gmail()
        self.s3_client = boto3.client("s3")

        # MongoDB connection
        self.mongo_client = client
        self.db = self.mongo_client[MongoDatabaseNames.EMAIL]
        self.messages_collection = self.db[MongoDBCollections.MESSAGES]

    def authenticate_gmail(self):
        """Authenticate with Gmail API and return the service."""
        logger.info("Authenticating with Gmail API...")
        creds = None

        # Load credentials from token file if it exists
        if os.path.exists(self.token_file):
            with open(self.token_file, "rb") as token:
                creds = pickle.load(token)

        # If credentials don't exist or are invalid, get new ones
        if not creds or not creds.valid:
            # if creds and creds.expired and creds.refresh_token:
            #     creds.refresh(Request())
            # else:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, GMAIL_AUTH_SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save credentials for next run
            with open(self.token_file, "wb") as token:
                pickle.dump(creds, token)

        # Build the Gmail service
        gmail_build = build("gmail", "v1", credentials=creds)
        logger.info("Gmail API authenticated successfully.")
        return gmail_build

    def list_messages(
        self,
        sender_filter: str | None = None,
    ) -> list[dict[str, str]]:
        """List all messages in the user's mailbox."""

        if sender_filter:
            # Filter messages by sender
            logger.info(f"Filtering messages by sender: {sender_filter}")
            query = f"from:{sender_filter}"
        else:
            query = None

        try:
            response = (
                self.gmail_service.users()
                .messages()
                .list(
                    userId="me",
                    q=query,
                )
                .execute()
            )
            messages = response.get("messages", [])
            return messages
        except Exception as e:
            logger.error(f"Error listing messages: {e}")
            return []

    def is_message_processed(self, msg_id):
        """Check if a message has already been processed based on its ID."""
        result = self.messages_collection.find_one(
            {MessageDocumentKeys.MESSAGE_ID: msg_id}
        )

        if result and self.replace_existing:
            # In replace mode, delete the existing document and associated attachment records
            self.messages_collection.delete_many(
                {MessageDocumentKeys.MESSAGE_ID: msg_id}
            )
            return False  # Return False to indicate the message should be processed

        return (
            result is not None
        )  # True if it should be skipped, False if it should be processed

    def get_gmail_message(self, msg_id: str) -> GmailMessage | None:
        """Get a specific message by its ID."""

        result = (
            self.gmail_service.users().messages().get(userId="me", id=msg_id).execute()
        )
        if not result:
            logger.warning(f"Message {msg_id} not found.")
            return None

        # Parse the message result into a GmailMessage object
        gmail_message = self._parse_message_from_result(result=result)
        if not gmail_message:
            logger.warning(f"Failed to parse message {msg_id}.")
            return None

        # Check if the message has attachments
        if not gmail_message.payload.get(GmailAPIPayloadKeys.PARTS):
            logger.warning(f"Message {msg_id} has no attachments.")

        else:
            # Process the message parts to extract attachments
            attachments = self._process_parts_into_attachments(
                msg_id=msg_id,
                parts=gmail_message.payload.get(GmailAPIPayloadKeys.PARTS, []),
                dry_run=False,
            )
            if attachments:
                # Add attachments to the message object
                gmail_message.attachments = attachments

        # Search the attachments for the body of the messag, which is usually
        # the first attachment where mime_type is text/plain
        body = None
        for attachment in gmail_message.attachments:
            if attachment.mime_type == "text/plain":
                body = attachment.text_content
                break
        if body:
            gmail_message.body = body
        else:
            logger.warning(f"No body found in attachments for message {msg_id}.")

        return gmail_message

    def _parse_message_from_result(self, result: dict) -> GmailMessage | None:
        """Parse the message result into a GmailMessage object."""

        # Extract relevant fields from the result
        msg_id = result[GmailAPIMessageKeys.ID]
        headers = result[GmailAPIMessageKeys.PAYLOAD][GmailAPIPayloadKeys.HEADERS]

        def search_in_headers(name_to_match: str) -> str | None:
            """Search for a header by name."""
            for header in headers:
                if header[GmailAPIHeaderKeys.NAME] == name_to_match:
                    return header[GmailAPIHeaderKeys.VALUE]
            return None

        try:
            gmail_message = GmailMessage(
                id=result[GmailAPIMessageKeys.ID],
                thread_id=result[GmailAPIMessageKeys.THREAD_ID],
                label_ids=result[GmailAPIMessageKeys.LABEL_IDS],
                snippet=result[GmailAPIMessageKeys.SNIPPET],
                payload=result[GmailAPIMessageKeys.PAYLOAD],
                size_estimate=result[GmailAPIMessageKeys.SIZE_ESTIMATE],
                history_id=result[GmailAPIMessageKeys.HISTORY_ID],
                internal_date=result[GmailAPIMessageKeys.INTERNAL_DATE],
                sender=search_in_headers(GmailAPIHeaderKeys.FROM) or "unknown",
                subject=search_in_headers(GmailAPIHeaderKeys.SUBJECT) or "unknown",
                date_received=search_in_headers(GmailAPIHeaderKeys.DATE) or "unknown",
            )
        except Exception as e:
            logger.error(f"Error parsing message {msg_id}: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return None

        # Log the message details
        logger.info(
            f"Retrieved message: {gmail_message.id} "
            f"from {gmail_message.sender} "
            f"with subject '{gmail_message.subject}' "
            f"received on {gmail_message.date_received}"
        )
        return gmail_message

    def _retrieve_and_store_attachment(
        self,
        msg_id: str,
        part: dict,
        dry_run: bool = False,
    ) -> Attachment | None:
        """
        Process a part of the message to extract attachment information.

        Parameters
        ----------
        part : dict
            The part of the message containing attachment information.

        Returns
        -------
        Attachment | None
            An Attachment object if the part is an attachment, None otherwise.
        """

        # Extract attachment information
        filename = part[PartKeys.FILENAME]

        body = part[PartKeys.BODY]

        attachment_id = body.get(PartKeys.ATTACHMENT_ID)

        text_content = None
        if not attachment_id:
            bytes_str: str = body.get(PartKeys.DATA)
            if not bytes_str:
                logger.warning(
                    f"No data found for attachment {filename} (no attachment ID)"
                )
                return None

            # Decode the str, which is base64 encoded
            data = base64.urlsafe_b64decode(bytes_str)
            text_content = data.decode("utf-8", errors="ignore")
            if not text_content:
                logger.warning(
                    f"No text content found for attachment {filename} (no attachment ID)"
                )
                return None

        else:
            # Get the attachment
            result = (
                self.gmail_service.users()
                .messages()
                .attachments()
                .get(
                    userId="me",
                    id=attachment_id,
                    messageId=msg_id,
                )
                .execute()
            )

            # Decode the attachment data
            data = base64.urlsafe_b64decode(result[GmailAPIPayloadKeys.DATA])
            if not data:
                logger.warning(
                    f"No data found for attachment {filename} (ID: {attachment_id})"
                )
                return None

        # Save the attachment to s3
        s3_key = f"{attachment_id}/{filename}"
        if not dry_run:
            with NamedTemporaryFile(delete=False) as temp_file:
                # Write the file data to a temporary file
                temp_file.write(data)

                # Upload to S3
                self.s3_client.upload_file(
                    Filename=temp_file.name,
                    Bucket=self.s3_bucket_name,
                    Key=s3_key,
                )
                logger.info(f"Uploaded to S3: {s3_key}")
        else:
            # For dry run, just log the file data size
            logger.info(f"Dry run: {filename} ({len(data)} bytes)")

        # Create an Attachment object
        attachment = Attachment(
            filename=filename,
            data=data,
            text_content=text_content,
            s3_bucket=self.s3_bucket_name,
            s3_key=s3_key,
            mime_type=part.get(PartKeys.MIME_TYPE),
        )

        return attachment

    def _process_parts_into_attachments(
        self,
        msg_id: str,
        parts: list[dict],
        dry_run: bool = False,
    ) -> list[Attachment]:
        """Process a Gmail message to extract attachments and save metadata."""

        attachment_list = []

        if not parts:
            logger.warning("No parts found in the message payload.")
            return []
        for part in parts:
            # Process the attachment part
            attachment = self._retrieve_and_store_attachment(
                msg_id=msg_id,
                part=part,
                dry_run=dry_run,
            )

            if attachment:
                attachment_list.append(attachment)

        if not attachment_list:
            logger.warning("No attachments found in the message parts.")
            return []

        return attachment_list

    def _mark_as_read(self, msg_id):
        """Mark a message as read by removing the UNREAD label."""
        try:
            self.gmail_service.users().messages().modify(
                userId="me", id=msg_id, body={"removeLabelIds": ["UNREAD"]}
            ).execute()
            logger.info(f"Marked message {msg_id} as read")
        except Exception as e:
            logger.error(f"Error marking message {msg_id} as read: {e}")

    def _infer_content_type(self, filename):
        """Guess the content type based on file extension."""
        import mimetypes

        content_type, _ = mimetypes.guess_type(filename)
        return content_type or "application/octet-stream"

    def process_emails(
        self,
        email_filter: str | None = None,
        dry_run: bool = False,
    ):
        """
        Main function to process emails, download attachments, and upload to S3.

        Parameters
        ----------
        dry_run : bool
            If True, perform a dry run without uploading to S3 or MongoDB.

        Returns
        -------
        None
        """
        logger.info("Checking for new emails with attachments...")
        # List unread messages with attachments
        list_messages = self.list_messages(
            sender_filter=email_filter,
        )
        if not list_messages:
            logger.info("No new messages with attachments found.")
            return
        logger.info(f"Found {len(list_messages)} unread messages with attachments.")

        list_html_content = []

        for message in list_messages:
            msg_id = message[GmailAPIMessageKeys.ID]
            logger.info(f"Processing message: {msg_id}")

            # Check if message has already been processed
            if self.is_message_processed(msg_id):
                if dry_run:
                    logger.info(
                        f"Message {msg_id} has already been processed, but dry run is enabled."
                        f" Continuing to process."
                    )
                else:
                    if not self.replace_existing:
                        logger.info(
                            f"Message {msg_id} has already been processed. Skipping."
                        )
                        continue
                    else:
                        logger.info(
                            f"Message {msg_id} has already been processed. Replacing existing document."
                        )

            # Get the message details
            gmail_message = self.get_gmail_message(msg_id=msg_id)
            if not gmail_message:
                logger.info(f"Message {msg_id} not found.")
                continue

            # Insert the message into MongoDB
            message_record = gmail_message.to_mongodb_record_dict()
            if not dry_run:
                self.messages_collection.insert_one(message_record)
                logger.info(f"Inserted message {msg_id} into MongoDB.")
            else:
                logger.info(f"Dry run: {gmail_message}")

            # Add the message to the HTML content
            html_content = gmail_message.to_html()
            list_html_content.append(html_content)

            # Mark the message as read
            self._mark_as_read(msg_id)

            logger.info(f"Finished processing message: {msg_id}")

        # Generate HTML content for all messages
        message_separator = "<br><hr><br>"

        html_content = message_separator.join(list_html_content)
        # Convert the HTML content to a string
        html_content = f"""
        <html>
        <body>
            <h1>Gmail Messages</h1>
            <p>Processed messages:</p>
            <table>
                <tr>
                    <th>Message ID</th>
                    <th>Sender</th>
                    <th>Subject</th>
                    <th>Date Received</th>
                    <th>Body</th>
                </tr>
                {html_content}
            </table>
        </body>
        </html>
        """

        open_html_in_browser(html_content)
