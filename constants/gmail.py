class GmailAPIMessageKeys:
    """Class representing keys for the MessageResponse."""

    ID = "id"
    THREAD_ID = "threadId"
    LABEL_IDS = "labelIds"
    SNIPPET = "snippet"
    PAYLOAD = "payload"
    SIZE_ESTIMATE = "sizeEstimate"
    HISTORY_ID = "historyId"
    INTERNAL_DATE = "internalDate"


class GmailAPIHeaderKeys:
    """Constants for header dictionary keys."""

    NAME: str = "name"
    VALUE: str = "value"
    FROM: str = "From"
    SUBJECT: str = "Subject"
    DATE: str = "Date"


class GmailAPIPayloadKeys:
    """Constants for payload dictionary keys."""

    PARTS: str = "parts"
    FILENAME: str = "filename"
    BODY: str = "body"
    ATTACHMENT_ID: str = "attachmentId"
    DATA: str = "data"
    HEADERS: str = "headers"


class ListMessagesKeys:
    """Class representing keys for the ListMessagesResponse."""

    ID = "id"
    THREAD_ID = "threadId"
