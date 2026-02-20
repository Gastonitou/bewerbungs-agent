"""
Gmail API integration for the Bewerbungs-Agent
"""
import os
import pickle
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .logger import get_logger


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

logger = get_logger('gmail')


class GmailClient:
    """Client for interacting with Gmail API"""
    
    def __init__(self, credentials_file: str, token_file: str):
        """
        Initialize Gmail client
        
        Args:
            credentials_file: Path to OAuth2 credentials file
            token_file: Path to token file
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2"""
        creds = None
        
        # Load token if it exists
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Refreshed Gmail credentials")
                except Exception as e:
                    logger.warning(f"Failed to refresh credentials: {e}")
                    creds = None
            
            # If still no valid credentials, do OAuth flow
            if not creds:
                if not os.path.exists(self.credentials_file):
                    logger.warning(f"Credentials file not found: {self.credentials_file}")
                    logger.info("Running in test mode without real Gmail connection")
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
                logger.info("Completed OAuth2 authentication")
            
            # Save credentials
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        # Build service
        if creds:
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail service initialized")
    
    def list_messages(self, query: str = '', max_results: int = 100) -> List[Dict[str, Any]]:
        """
        List messages matching query
        
        Args:
            query: Gmail search query
            max_results: Maximum number of results
            
        Returns:
            List of message dictionaries
        """
        if not self.service:
            logger.warning("Gmail service not initialized, returning empty list")
            return []
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} messages matching query: {query}")
            return messages
        
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return []
    
    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full message details
        
        Args:
            message_id: Message ID
            
        Returns:
            Message dictionary or None
        """
        if not self.service:
            logger.warning("Gmail service not initialized")
            return None
        
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            logger.debug(f"Retrieved message: {message_id}")
            return message
        
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return None
    
    def get_attachments(self, message_id: str) -> List[Dict[str, Any]]:
        """
        Get attachments from a message
        
        Args:
            message_id: Message ID
            
        Returns:
            List of attachment dictionaries
        """
        if not self.service:
            logger.warning("Gmail service not initialized")
            return []
        
        message = self.get_message(message_id)
        if not message:
            return []
        
        attachments = []
        
        if 'parts' in message.get('payload', {}):
            for part in message['payload']['parts']:
                if part.get('filename'):
                    attachment = {
                        'filename': part['filename'],
                        'mimeType': part.get('mimeType'),
                        'attachmentId': part['body'].get('attachmentId')
                    }
                    
                    # Download attachment data
                    if attachment['attachmentId']:
                        try:
                            att_data = self.service.users().messages().attachments().get(
                                userId='me',
                                messageId=message_id,
                                id=attachment['attachmentId']
                            ).execute()
                            
                            attachment['data'] = base64.urlsafe_b64decode(
                                att_data['data'].encode('UTF-8')
                            )
                            attachments.append(attachment)
                            logger.debug(f"Downloaded attachment: {attachment['filename']}")
                        
                        except HttpError as error:
                            logger.error(f"Failed to download attachment: {error}")
        
        logger.info(f"Found {len(attachments)} attachments in message {message_id}")
        return attachments
    
    def create_label(self, label_name: str) -> Optional[str]:
        """
        Create a label (folder)
        
        Args:
            label_name: Name of the label
            
        Returns:
            Label ID or None
        """
        if not self.service:
            logger.warning("Gmail service not initialized")
            return None
        
        try:
            label = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            
            created_label = self.service.users().labels().create(
                userId='me',
                body=label
            ).execute()
            
            logger.info(f"Created label: {label_name} (ID: {created_label['id']})")
            return created_label['id']
        
        except HttpError as error:
            logger.error(f"Failed to create label: {error}")
            return None
    
    def get_label_id(self, label_name: str) -> Optional[str]:
        """
        Get label ID by name, create if doesn't exist
        
        Args:
            label_name: Name of the label
            
        Returns:
            Label ID or None
        """
        if not self.service:
            logger.warning("Gmail service not initialized")
            return None
        
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            for label in labels:
                if label['name'] == label_name:
                    return label['id']
            
            # Label doesn't exist, create it
            return self.create_label(label_name)
        
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return None
    
    def move_to_label(self, message_id: str, label_name: str) -> bool:
        """
        Move message to label (folder)
        
        Args:
            message_id: Message ID
            label_name: Label name
            
        Returns:
            True if successful
        """
        if not self.service:
            logger.warning("Gmail service not initialized")
            return False
        
        label_id = self.get_label_id(label_name)
        if not label_id:
            logger.error(f"Could not get label ID for: {label_name}")
            return False
        
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={
                    'addLabelIds': [label_id],
                    'removeLabelIds': ['INBOX']
                }
            ).execute()
            
            logger.info(f"Moved message {message_id} to label: {label_name}")
            return True
        
        except HttpError as error:
            logger.error(f"Failed to move message: {error}")
            return False
