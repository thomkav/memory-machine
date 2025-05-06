class MongoDatabaseNames:
    EMAIL: str = "email"


class MongoDBCollections:
    MESSAGES: str = "messages"


class MessageDocumentKeys:
    """Constants for MongoDB document keys."""

    MESSAGE_ID: str = "message_id"
    SENDER: str = "sender"
    SNIPPET: str = "snippet"
    SUBJECT: str = "subject"
    BODY: str = "body"
    DATE_RECEIVED: str = "date_received"
    PROCESSED_AT: str = "processed_at"
    CONTENT_TYPE: str = "content_type"
    ATTACHMENTS: str = "attachments"


class PartKeys:
    """Class representing keys for the message part."""

    MIME_TYPE = "mimeType"
    FILENAME = "filename"
    BODY = "body"
    ATTACHMENT_ID = "attachmentId"
    DATA = "data"
    HEADERS = "headers"
    PARTS = "parts"


class AttachmentDocumentKeys:
    FILENAME: str = "filename"
    TEXT_CONTENT: str = "text_content"
    FILE_DATA_SIZE: str = "size"
    MIME_TYPE: str = "content_type"
    S3_BUCKET: str = "s3_bucket"
    S3_KEY: str = "s3_key"
