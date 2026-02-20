"""Gmail service: OAuth2 authentication and email operations."""
import base64
import logging
import os
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

# Read-only + label-write access; intentionally excludes gmail.send
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels",
]

TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"


def get_gmail_service():
    """Return an authenticated Gmail API service object."""
    creds: Optional[Credentials] = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def fetch_unread_emails(service, label: str = "INBOX", max_results: int = 50) -> List[dict]:
    """Fetch unread messages from *label* and return a list of message dicts."""
    logger.info("Fetching up to %d unread emails from '%s'", max_results, label)
    result = (
        service.users()
        .messages()
        .list(userId="me", labelIds=[label], q="is:unread", maxResults=max_results)
        .execute()
    )
    messages = result.get("messages", [])
    detailed = []
    for msg in messages:
        detail = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
        detailed.append(detail)
    logger.info("Retrieved %d messages", len(detailed))
    return detailed


def get_or_create_label(service, label_name: str) -> str:
    """Return the label id for *label_name*, creating it if necessary."""
    existing = service.users().labels().list(userId="me").execute().get("labels", [])
    for lbl in existing:
        if lbl["name"].lower() == label_name.lower():
            return lbl["id"]
    created = (
        service.users()
        .labels()
        .create(userId="me", body={"name": label_name, "labelListVisibility": "labelShow"})
        .execute()
    )
    logger.info("Created Gmail label '%s'", label_name)
    return created["id"]


def move_message_to_label(service, message_id: str, label_id: str) -> None:
    """Add *label_id* to *message_id* and remove it from INBOX."""
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": [label_id], "removeLabelIds": ["INBOX"]},
    ).execute()
    logger.info("Moved message %s to label %s", message_id, label_id)


def extract_body(message: dict) -> str:
    """Return the plain-text body of a Gmail message dict."""
    payload = message.get("payload", {})
    parts = payload.get("parts", [])

    def _decode(data: str) -> str:
        return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")

    # Single-part message
    body_data = payload.get("body", {}).get("data", "")
    if body_data:
        return _decode(body_data)

    # Multi-part: prefer text/plain
    for part in parts:
        if part.get("mimeType") == "text/plain":
            data = part.get("body", {}).get("data", "")
            if data:
                return _decode(data)
    return ""


def get_attachments(service, message: dict) -> List[dict]:
    """Download attachment data for all parts of *message*.

    Returns a list of dicts with keys: filename, mime_type, data (bytes).
    """
    attachments = []
    msg_id = message["id"]
    parts = message.get("payload", {}).get("parts", [])
    for part in parts:
        filename = part.get("filename", "")
        if not filename:
            continue
        attachment_id = part.get("body", {}).get("attachmentId")
        if not attachment_id:
            continue
        att = (
            service.users()
            .messages()
            .attachments()
            .get(userId="me", messageId=msg_id, id=attachment_id)
            .execute()
        )
        data = base64.urlsafe_b64decode(att["data"] + "==")
        attachments.append(
            {"filename": filename, "mime_type": part.get("mimeType", ""), "data": data}
        )
    return attachments
