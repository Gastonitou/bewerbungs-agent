"""Gmail integration service for OAuth and email operations."""

import os
import json
import base64
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from email.mime.text import MIMEText

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

from sqlalchemy.orm import Session

from bewerbungs_agent.models import Email, EmailCategory
from bewerbungs_agent.utils.config import get_settings

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels',
]


class GmailService:
    """Service for Gmail integration."""

    def __init__(self):
        """Initialize Gmail service."""
        if not GMAIL_AVAILABLE:
            raise ImportError(
                "Gmail dependencies not available. "
                "Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
            )
        self.settings = get_settings()
        self.creds = None
        self.service = None

    def authenticate(self, token_file: str = "token.json", credentials_file: str = "credentials.json") -> bool:
        """
        Authenticate with Gmail using OAuth2.
        Returns True if successful.
        """
        # Load existing token
        if os.path.exists(token_file):
            self.creds = Credentials.from_authorized_user_file(token_file, SCOPES)

        # Refresh or get new token
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file not found: {credentials_file}\n"
                        "Download from: https://console.cloud.google.com/"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                self.creds = flow.run_local_server(port=8080)

            # Save token for future use
            with open(token_file, 'w') as token:
                token.write(self.creds.to_json())

        # Build service
        self.service = build('gmail', 'v1', credentials=self.creds)
        return True

    def list_messages(
        self,
        query: str = "",
        max_results: int = 100,
        label_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """List messages matching query."""
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        results = self.service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results,
            labelIds=label_ids,
        ).execute()

        messages = results.get('messages', [])
        return messages

    def get_message(self, message_id: str) -> Dict[str, Any]:
        """Get full message details."""
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        message = self.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full',
        ).execute()

        return message

    def extract_email_data(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant data from Gmail message."""
        headers = message.get('payload', {}).get('headers', [])
        
        def get_header(name: str) -> str:
            for header in headers:
                if header['name'].lower() == name.lower():
                    return header['value']
            return ""

        # Extract body
        body = ""
        if 'parts' in message.get('payload', {}):
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(
                        part['body'].get('data', '')
                    ).decode('utf-8')
                    break
        elif 'body' in message.get('payload', {}):
            body = base64.urlsafe_b64decode(
                message['payload']['body'].get('data', '')
            ).decode('utf-8')

        # Parse date
        date_str = get_header('Date')
        received_at = datetime.utcnow()  # Fallback
        # In production, parse date_str properly

        return {
            'message_id': message['id'],
            'thread_id': message.get('threadId', ''),
            'subject': get_header('Subject'),
            'sender': get_header('From'),
            'received_at': received_at,
            'body_text': body,
            'labels': message.get('labelIds', []),
        }

    def classify_email(self, subject: str, body: str) -> tuple[EmailCategory, float]:
        """
        Classify email based on content.
        Returns (category, confidence).
        Simple keyword-based - in production use ML.
        """
        text = (subject + " " + body).lower()
        
        # Rejection indicators
        rejection_keywords = ['unfortunately', 'not selected', 'not moving forward', 'rejected', 'other candidates']
        if any(kw in text for kw in rejection_keywords):
            return EmailCategory.REJECTION, 0.8
        
        # Interview indicators
        interview_keywords = ['interview', 'schedule', 'meeting', 'call', 'available']
        if any(kw in text for kw in interview_keywords):
            return EmailCategory.INTERVIEW, 0.7
        
        # Offer indicators
        offer_keywords = ['offer', 'congratulations', 'pleased to offer', 'job offer']
        if any(kw in text for kw in offer_keywords):
            return EmailCategory.OFFER, 0.9
        
        # Job alert indicators
        job_keywords = ['job alert', 'new jobs', 'position available', 'now hiring']
        if any(kw in text for kw in job_keywords):
            return EmailCategory.JOB_ALERT, 0.6
        
        return EmailCategory.OTHER, 0.3

    def sync_emails(self, db: Session, user_id: int, query: str = "subject:(job OR hiring OR interview)") -> List[Email]:
        """
        Sync emails from Gmail to database.
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        messages = self.list_messages(query=query)
        synced_emails = []

        for msg in messages:
            # Check if already exists
            existing = db.query(Email).filter(
                Email.message_id == msg['id']
            ).first()
            
            if existing:
                continue

            # Get full message
            full_message = self.get_message(msg['id'])
            data = self.extract_email_data(full_message)
            
            # Classify
            category, confidence = self.classify_email(
                data['subject'],
                data['body_text']
            )

            # Create email record
            email = Email(
                user_id=user_id,
                message_id=data['message_id'],
                thread_id=data['thread_id'],
                subject=data['subject'],
                sender=data['sender'],
                received_at=data['received_at'],
                body_text=data['body_text'],
                labels=data['labels'],
                category=category,
                confidence=confidence,
            )
            db.add(email)
            synced_emails.append(email)

        db.commit()
        return synced_emails

    def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
    ) -> Dict[str, Any]:
        """
        Create a draft email (not sent).
        This is SAFE - no automatic sending.
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        draft = self.service.users().drafts().create(
            userId='me',
            body={'message': {'raw': raw}}
        ).execute()

        return draft

    def add_label(self, message_id: str, label_name: str):
        """Add a label to a message."""
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        # Get or create label
        labels = self.service.users().labels().list(userId='me').execute()
        label_id = None
        
        for label in labels.get('labels', []):
            if label['name'] == label_name:
                label_id = label['id']
                break
        
        if not label_id:
            # Create label
            label_obj = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show',
            }
            created = self.service.users().labels().create(
                userId='me',
                body=label_obj
            ).execute()
            label_id = created['id']

        # Add label to message
        self.service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'addLabelIds': [label_id]}
        ).execute()
