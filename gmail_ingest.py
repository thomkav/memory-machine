"""
Gmail to S3 File Uploader
This script queries a Gmail account for messages,
downloads any attachments, and uploads them to an S3 bucket as well as saves metadata to MongoDB.
"""

import os
import base64
import pickle
from datetime import datetime

# Gmail API libraries
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# AWS S3 library
import boto3

# MongoDB library
from mongodb import client  # Assuming mongodb.py is in the same directory

# Import constants
from constants import (
    AttachmentInfoKeys,
    FilePaths,
    HeaderKeys,
    MessageKeys,
    MongoDBCollections,
    MongoDatabaseNames,
    MongoDBKeys,
    PayloadKeys,
    S3Constants,
)

# Gmail API scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


class GmailS3Uploader:
    def __init__(
        self,
        credentials_file,
        token_file,
        s3_bucket_name,
        check_interval=60,
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
        self.s3_bucket_name = s3_bucket_name
        self.check_interval = check_interval
        self.replace_existing = replace_existing

        # Initialize services
        self.gmail_service = self._authenticate_gmail()
        self.s3_client = boto3.client("s3")

        # MongoDB connection
        self.mongo_client = client
        self.db = self.mongo_client[MongoDatabaseNames.EMAIL]
        self.attachments_collection = self.db[MongoDBCollections.ATTACHMENTS]

    def _authenticate_gmail(self):
        """Authenticate with Gmail API and return the service."""
        print("Authenticating with Gmail API...")
        creds = None

        # Load credentials from token file if it exists
        if os.path.exists(self.token_file):
            with open(self.token_file, "rb") as token:
                creds = pickle.load(token)

        # If credentials don't exist or are invalid, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save credentials for next run
            with open(self.token_file, "wb") as token:
                pickle.dump(creds, token)

        # Build the Gmail service
        gmail_build = build("gmail", "v1", credentials=creds)
        print("Gmail API authenticated successfully.")
        return gmail_build

    def list_messages(self) -> list[dict]:
        """List all messages in the user's mailbox."""
        try:
            response = (
                self.gmail_service.users()
                .messages()
                .list(
                    userId="me",
                )
                .execute()
            )
            messages = response.get("messages", [])
            return messages
        except Exception as e:
            print(f"Error listing messages: {e}")
            return []

    def get_message(self, msg_id):
        """Get a specific message by its ID."""
        try:
            return (
                self.gmail_service.users()
                .messages()
                .get(userId="me", id=msg_id)
                .execute()
            )
        except Exception as e:
            print(f"Error getting message {msg_id}: {e}")
            return None

    def mark_as_read(self, msg_id):
        """Mark a message as read by removing the UNREAD label."""
        try:
            self.gmail_service.users().messages().modify(
                userId="me", id=msg_id, body={"removeLabelIds": ["UNREAD"]}
            ).execute()
            print(f"Marked message {msg_id} as read")
        except Exception as e:
            print(f"Error marking message {msg_id} as read: {e}")

    def _process_part(
        self,
        part: dict,
        sender: str,
        subject: str,
        date: str,
        msg_id: str,
    ) -> dict:
        """
        Process a part of the message to extract attachment information.

        Args:
            part (dict): Part of the message
            sender (str): Email sender
            subject (str): Email subject
            date (str): Email date
            msg_id (str): Message ID

        Returns:
            (dict | None): Attachment information or None if not found
        """
        filename = part[PayloadKeys.FILENAME]
        attachment_id = part[PayloadKeys.BODY][PayloadKeys.ATTACHMENT_ID]

        # Get the attachment
        attachment = (
            self.gmail_service.users()
            .messages()
            .attachments()
            .get(userId="me", messageId=msg_id, id=attachment_id)
            .execute()
        )

        # Decode the attachment data
        file_data = base64.urlsafe_b64decode(attachment[PayloadKeys.DATA])

        # Create a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = FilePaths.PARSED_EMAILS_DIR / f"{timestamp}_{filename}"

        # Save the file locally
        with open(file_path, "wb") as f:
            f.write(file_data)

        # Store attachment info
        attachment_info_dict = {
            AttachmentInfoKeys.FILENAME: filename,
            AttachmentInfoKeys.LOCAL_PATH: str(file_path),
            AttachmentInfoKeys.SENDER: sender,
            AttachmentInfoKeys.SUBJECT: subject,
            AttachmentInfoKeys.DATE: date,
            AttachmentInfoKeys.MESSAGE_ID: msg_id,
            AttachmentInfoKeys.SIZE: len(file_data),
            AttachmentInfoKeys.TIMESTAMP: timestamp,
        }
        print(f"Downloaded: {filename}")

        # Add message_id to ensure deterministic keys
        attachment_info_dict[AttachmentInfoKeys.DETERMINISTIC_ID] = msg_id
        # Upload to S3
        try:
            self.upload_to_s3(attachment_info_dict)
        except Exception as e:
            print(f"Error uploading {filename} to S3: {e}")

        try:
            # Save metadata to MongoDB
            self.save_attachment_to_mongodb(attachment_info=attachment_info_dict)
            print(f"Saved metadata to MongoDB for {filename}")
        except Exception as e:
            print(
                f"Failed to upload {attachment_info_dict[AttachmentInfoKeys.FILENAME]} to S3."
            )
            print(f"Error saving metadata to MongoDB: {e}")

        return attachment_info_dict

    def process_message(self, message) -> list[dict]:
        """Download any and all attachments from a message."""
        msg_id = message[MessageKeys.ID]
        list_attachments_dicts = []
        try:
            # Get the message details
            msg = self.get_message(msg_id)
            if not msg:
                print(f"Message {msg_id} not found.")
                return []

            # Get headers
            headers = {
                h[HeaderKeys.NAME]: h[HeaderKeys.VALUE]
                for h in msg[MessageKeys.PAYLOAD].get(MessageKeys.HEADERS, [])
            }
            sender = headers.get(HeaderKeys.FROM, "Unknown")
            subject = headers.get(HeaderKeys.SUBJECT, "No Subject")
            date = headers.get(HeaderKeys.DATE, "Unknown Date")

            # Process message parts to find attachments
            if PayloadKeys.PARTS in msg[MessageKeys.PAYLOAD]:
                parts = msg[MessageKeys.PAYLOAD][PayloadKeys.PARTS]
                for part in parts:
                    if (
                        part.get(PayloadKeys.FILENAME)
                        and part.get(PayloadKeys.BODY)
                        and part[PayloadKeys.BODY].get(PayloadKeys.ATTACHMENT_ID)
                    ):

                        # Process the attachment part
                        attachment_info_dict = self._process_part(
                            part=part,
                            sender=sender,
                            subject=subject,
                            date=date,
                            msg_id=msg_id,
                        )

                        list_attachments_dicts.append(attachment_info_dict)

            # Save metadata to MongoDB for the message itself
            message_info = {
                MongoDBKeys.MESSAGE_ID: msg_id,
                MongoDBKeys.SENDER: message.get(MessageKeys.SENDER),
                MongoDBKeys.SUBJECT: message.get(MessageKeys.SUBJECT),
                MongoDBKeys.DATE_RECEIVED: message[MessageKeys.INTERNAL_DATE],
                MongoDBKeys.ATTACHMENTS: list_attachments_dicts,
                MongoDBKeys.PROCESSED_AT: datetime.now(),
                MongoDBKeys.PROCESSED_BY: "GmailS3Uploader",
            }

            # Insert or replace the document in MongoDB
            if self.replace_existing:
                self.attachments_collection.replace_one(
                    {MongoDBKeys.MESSAGE_ID: msg_id}, message_info, upsert=True
                )
            else:
                self.attachments_collection.insert_one(message_info)

            print(f"Saved message metadata to MongoDB for message ID: {msg_id}")

            return list_attachments_dicts

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error downloading attachments from message {msg_id}: {e}")
            return []

    def upload_to_s3(
        self,
        attachment_info: dict,
    ) -> dict | None:
        """Upload an attachment to S3 bucket."""
        local_path = attachment_info[AttachmentInfoKeys.LOCAL_PATH]
        filename = attachment_info[AttachmentInfoKeys.FILENAME]
        sender_email = (
            attachment_info[AttachmentInfoKeys.SENDER].split("<")[-1].split(">")[0]
            if "<" in attachment_info[AttachmentInfoKeys.SENDER]
            else "unknown"
        )  # noqa:E501

        # Create a deterministic key based on message_id + filename
        msg_id = attachment_info[AttachmentInfoKeys.DETERMINISTIC_ID]
        # Create a folder structure based on sender and deterministic ID
        date_folder = datetime.now().strftime("%Y/%m/%d")
        s3_key = f"{sender_email}/{date_folder}/{msg_id}_{filename}"

        # Upload to S3
        self.s3_client.upload_file(local_path, self.s3_bucket_name, s3_key)
        print(f"Uploaded to S3: {s3_key}")

        # Add S3 info to attachment_info
        attachment_info[AttachmentInfoKeys.S3_BUCKET] = self.s3_bucket_name
        attachment_info[AttachmentInfoKeys.S3_KEY] = s3_key
        return attachment_info

    def save_attachment_to_mongodb(self, attachment_info):
        """Save attachment metadata to MongoDB."""
        # Create a document with all relevant metadata
        mongo_doc = {
            MongoDBKeys.MESSAGE_ID: attachment_info[AttachmentInfoKeys.MESSAGE_ID],
            MongoDBKeys.FILENAME: attachment_info[AttachmentInfoKeys.FILENAME],
            MongoDBKeys.ORIGINAL_FILENAME: attachment_info[AttachmentInfoKeys.FILENAME],
            MongoDBKeys.SENDER: attachment_info[AttachmentInfoKeys.SENDER],
            MongoDBKeys.SENDER_EMAIL: (
                attachment_info[AttachmentInfoKeys.SENDER].split("<")[-1].split(">")[0]
                if "<" in attachment_info[AttachmentInfoKeys.SENDER]
                else "unknown"
            ),  # noqa:E501
            MongoDBKeys.DATE_RECEIVED: attachment_info[AttachmentInfoKeys.DATE],
            MongoDBKeys.SIZE_BYTES: attachment_info[AttachmentInfoKeys.SIZE],
            MongoDBKeys.TIMESTAMP: attachment_info[AttachmentInfoKeys.TIMESTAMP],
            MongoDBKeys.PROCESSED_AT: datetime.now(),
            MongoDBKeys.S3_BUCKET: attachment_info.get(
                AttachmentInfoKeys.S3_BUCKET, None
            ),
            MongoDBKeys.S3_KEY: attachment_info.get(AttachmentInfoKeys.S3_KEY, None),
            MongoDBKeys.S3_URL: (
                f"https://{attachment_info[AttachmentInfoKeys.S3_BUCKET]}.s3.amazonaws.com/{attachment_info[AttachmentInfoKeys.S3_KEY]}"  # noqa:E501
                if AttachmentInfoKeys.S3_KEY in attachment_info
                else None
            ),  # noqa:E501
            MongoDBKeys.CONTENT_TYPE: self._guess_content_type(
                attachment_info[AttachmentInfoKeys.FILENAME]
            ),
        }

        # Insert into MongoDB
        result = self.attachments_collection.insert_one(mongo_doc)
        print(
            f"Saved metadata to MongoDB for {attachment_info[AttachmentInfoKeys.FILENAME]} (ID: {result.inserted_id})"
        )
        return result.inserted_id

    def _guess_content_type(self, filename):
        """Guess the content type based on file extension."""
        import mimetypes

        content_type, _ = mimetypes.guess_type(filename)
        return content_type or "application/octet-stream"

    def process_emails(self):
        """Main function to process emails, download attachments, and upload to S3."""
        print("Checking for new emails with attachments...")
        # List unread messages with attachments
        messages = self.list_messages()
        if not messages:
            print("No new messages with attachments found.")
            return
        print(f"Found {len(messages)} unread messages with attachments.")

        for message in messages:
            msg_id = message[MessageKeys.ID]
            print(f"Processing message: {msg_id}")

            # Check if message has already been processed
            if self.is_message_processed(msg_id):
                if not self.replace_existing:
                    print(f"Message {msg_id} has already been processed. Skipping.")
                    continue
                else:
                    print(
                        f"Message {msg_id} has already been processed. Replacing existing document."
                    )

            # Get the message details
            message = self.get_message(msg_id)
            if not message:
                print(f"Message {msg_id} not found.")
                continue

            # Download attachments
            self.process_message(message)

            # Mark the message as read
            self.mark_as_read(msg_id)

            print(f"Finished processing message: {msg_id}")

    def is_message_processed(self, msg_id):
        """Check if a message has already been processed based on its ID."""
        result = self.attachments_collection.find_one({MongoDBKeys.MESSAGE_ID: msg_id})

        if result and self.replace_existing:
            # In replace mode, delete the existing document and associated attachment records
            self.attachments_collection.delete_many({MongoDBKeys.MESSAGE_ID: msg_id})
            return False  # Return False to indicate the message should be processed

        return (
            result is not None
        )  # True if it should be skipped, False if it should be processed

    def run(self):
        """Run the uploader once."""
        self.process_emails()


if __name__ == "__main__":
    # Configuration
    CREDENTIALS_FILE = FilePaths.GOOGLE_CLOUD_API_CREDENTIALS  # Downloaded from Google Cloud Console
    TOKEN_FILE = FilePaths.GOOGLE_CLOUD_API_TOKEN  # Token file to store user credentials for Gmail API
    S3_BUCKET_NAME = S3Constants.BUCKET_NAME  # Your S3 bucket name
    CHECK_INTERVAL = 60  # seconds
    REPLACE_EXISTING = True  # Set to True to replace existing documents

    # Create and run the uploader
    uploader = GmailS3Uploader(
        credentials_file=CREDENTIALS_FILE,
        token_file=TOKEN_FILE,
        s3_bucket_name=S3_BUCKET_NAME,
        check_interval=CHECK_INTERVAL,
        replace_existing=REPLACE_EXISTING,
    )
    uploader.run()
