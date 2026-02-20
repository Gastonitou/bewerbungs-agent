"""
Gmail API client with OAuth2 authentication.

Handles:
- OAuth2 token management
- Reading emails from a specified label
- Moving emails between Gmail labels
- Downloading email attachments
"""

import base64
import os
from typing import Any, Dict, List, Optional, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from agent.logger import get_logger

logger = get_logger("gmail_client")

# The OAuth2 scopes required by the agent
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
]


class GmailClient:
    """Wrapper around the Gmail API."""

    def __init__(
        self,
        credentials_file: str,
        token_file: str,
        email_address: str,
    ) -> None:
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.email_address = email_address
        self._service: Any = None

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate(self) -> None:
        """Authenticate with Gmail using OAuth2 and build the API service."""
        creds: Optional[Credentials] = None

        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            logger.debug("Loaded existing OAuth2 token from %s", self.token_file)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                logger.info("OAuth2 token refreshed.")
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"OAuth2 credentials file not found: {self.credentials_file}. "
                        "Download it from the Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
                logger.info("New OAuth2 token obtained via browser flow.")

            with open(self.token_file, "w", encoding="utf-8") as token_fh:
                token_fh.write(creds.to_json())
            logger.debug("OAuth2 token saved to %s", self.token_file)

        self._service = build("gmail", "v1", credentials=creds)
        logger.info("Gmail API service initialised for %s.", self.email_address)

    @property
    def service(self) -> Any:
        if self._service is None:
            raise RuntimeError("GmailClient is not authenticated. Call authenticate() first.")
        return self._service

    # ------------------------------------------------------------------
    # Label helpers
    # ------------------------------------------------------------------

    def _get_or_create_label(self, label_name: str) -> str:
        """Return the Gmail label ID for *label_name*, creating it if necessary."""
        try:
            result = self.service.users().labels().list(userId="me").execute()
            for lbl in result.get("labels", []):
                if lbl["name"].lower() == label_name.lower():
                    return lbl["id"]

            # Label doesn't exist – create it
            new_label = (
                self.service.users()
                .labels()
                .create(
                    userId="me",
                    body={
                        "name": label_name,
                        "labelListVisibility": "labelShow",
                        "messageListVisibility": "show",
                    },
                )
                .execute()
            )
            logger.info("Created Gmail label '%s' (id=%s).", label_name, new_label["id"])
            return new_label["id"]
        except HttpError as exc:
            logger.error("Error retrieving/creating label '%s': %s", label_name, exc)
            raise

    # ------------------------------------------------------------------
    # Email retrieval
    # ------------------------------------------------------------------

    def list_messages(self, label: str = "INBOX", max_results: int = 50) -> List[Dict]:
        """
        Return a list of message metadata dicts for emails in *label*.

        Each dict contains at least ``id`` and ``threadId``.
        """
        try:
            response = (
                self.service.users()
                .messages()
                .list(userId="me", labelIds=[label], maxResults=max_results)
                .execute()
            )
            messages = response.get("messages", [])
            logger.info("Found %d message(s) in label '%s'.", len(messages), label)
            return messages
        except HttpError as exc:
            logger.error("Error listing messages in label '%s': %s", label, exc)
            raise

    def get_message(self, message_id: str) -> Dict:
        """Fetch the full message payload for *message_id*."""
        try:
            msg = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )
            return msg
        except HttpError as exc:
            logger.error("Error fetching message %s: %s", message_id, exc)
            raise

    @staticmethod
    def extract_body(message: Dict) -> str:
        """
        Extract the plain-text body from a Gmail message payload.

        Falls back to an HTML body if no plain-text part is found.
        """
        payload = message.get("payload", {})

        def _decode(data: str) -> str:
            return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")

        def _find_body(part: Dict) -> Optional[str]:
            mime_type = part.get("mimeType", "")
            body_data = part.get("body", {}).get("data")

            if mime_type == "text/plain" and body_data:
                return _decode(body_data)

            for sub_part in part.get("parts", []):
                result = _find_body(sub_part)
                if result:
                    return result

            # Fall back to HTML if no plain-text found
            if mime_type == "text/html" and body_data:
                return _decode(body_data)

            return None

        body = _find_body(payload)
        return body or ""

    @staticmethod
    def extract_headers(message: Dict) -> Dict[str, str]:
        """Return a dict of header name → value for the message."""
        headers: Dict[str, str] = {}
        for header in message.get("payload", {}).get("headers", []):
            headers[header["name"].lower()] = header["value"]
        return headers

    # ------------------------------------------------------------------
    # Attachment handling
    # ------------------------------------------------------------------

    def list_attachments(self, message: Dict) -> List[Dict]:
        """
        Return a list of attachment metadata dicts.

        Each dict contains ``filename``, ``mime_type``, ``size``, ``attachment_id``,
        and ``message_id``.
        """
        attachments: List[Dict] = []
        message_id = message.get("id", "")

        def _collect(part: Dict) -> None:
            if part.get("filename") and part["body"].get("attachmentId"):
                attachments.append(
                    {
                        "filename": part["filename"],
                        "mime_type": part.get("mimeType", ""),
                        "size": part["body"].get("size", 0),
                        "attachment_id": part["body"]["attachmentId"],
                        "message_id": message_id,
                    }
                )
            for sub in part.get("parts", []):
                _collect(sub)

        _collect(message.get("payload", {}))
        return attachments

    def download_attachment(
        self, message_id: str, attachment_id: str, dest_path: str
    ) -> None:
        """Download an attachment and write it to *dest_path*."""
        try:
            att = (
                self.service.users()
                .messages()
                .attachments()
                .get(userId="me", messageId=message_id, id=attachment_id)
                .execute()
            )
            data = base64.urlsafe_b64decode(att["data"] + "==")
            with open(dest_path, "wb") as fh:
                fh.write(data)
            logger.debug(
                "Downloaded attachment %s (%d bytes) to %s.",
                attachment_id,
                len(data),
                dest_path,
            )
        except HttpError as exc:
            logger.error(
                "Error downloading attachment %s from message %s: %s",
                attachment_id,
                message_id,
                exc,
            )
            raise

    # ------------------------------------------------------------------
    # Email organisation
    # ------------------------------------------------------------------

    def move_to_label(self, message_id: str, target_label_name: str) -> None:
        """
        Move *message_id* to *target_label_name* and remove it from INBOX.

        The label is created automatically if it does not exist.
        """
        label_id = self._get_or_create_label(target_label_name)
        try:
            self.service.users().messages().modify(
                userId="me",
                id=message_id,
                body={
                    "addLabelIds": [label_id],
                    "removeLabelIds": ["INBOX"],
                },
            ).execute()
            logger.info(
                "Moved message %s to label '%s'.", message_id, target_label_name
            )
        except HttpError as exc:
            logger.error(
                "Error moving message %s to label '%s': %s",
                message_id,
                target_label_name,
                exc,
            )
            raise

    def mark_as_read(self, message_id: str) -> None:
        """Remove the UNREAD label from a message."""
        try:
            self.service.users().messages().modify(
                userId="me",
                id=message_id,
                body={"removeLabelIds": ["UNREAD"]},
            ).execute()
            logger.debug("Marked message %s as read.", message_id)
        except HttpError as exc:
            logger.error("Error marking message %s as read: %s", message_id, exc)
            raise
