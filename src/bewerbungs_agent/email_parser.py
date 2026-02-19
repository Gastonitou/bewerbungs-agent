"""
Email parsing utilities for the Bewerbungs-Agent
"""
import re
import base64
from typing import Dict, Any, Optional
from email.mime.text import MIMEText

from .logger import get_logger


logger = get_logger('email_parser')


class EmailParser:
    """Parser for email messages"""
    
    @staticmethod
    def parse_message(message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Gmail message into structured format
        
        Args:
            message: Gmail message dictionary
            
        Returns:
            Parsed message dictionary
        """
        headers = message.get('payload', {}).get('headers', [])
        
        parsed = {
            'id': message.get('id'),
            'threadId': message.get('threadId'),
            'subject': EmailParser._get_header(headers, 'Subject'),
            'from': EmailParser._get_header(headers, 'From'),
            'to': EmailParser._get_header(headers, 'To'),
            'date': EmailParser._get_header(headers, 'Date'),
            'body': EmailParser._get_body(message.get('payload', {})),
            'snippet': message.get('snippet', '')
        }
        
        logger.debug(f"Parsed message: {parsed['subject']}")
        return parsed
    
    @staticmethod
    def _get_header(headers: list, name: str) -> Optional[str]:
        """Get header value by name"""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return None
    
    @staticmethod
    def _get_body(payload: Dict[str, Any]) -> str:
        """Extract email body from payload"""
        body = ""
        
        if 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(
                payload['body']['data'].encode('ASCII')
            ).decode('utf-8')
        
        elif 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data'].encode('ASCII')
                        ).decode('utf-8')
                        break
                elif part.get('mimeType') == 'text/html':
                    if 'data' in part['body']:
                        html_body = base64.urlsafe_b64decode(
                            part['body']['data'].encode('ASCII')
                        ).decode('utf-8')
                        # Simple HTML to text conversion
                        body = re.sub('<[^<]+?>', '', html_body)
        
        return body.strip()
    
    @staticmethod
    def extract_sender_email(from_header: str) -> str:
        """
        Extract email address from From header
        
        Args:
            from_header: From header value
            
        Returns:
            Email address
        """
        if not from_header:
            return ""
        
        # Extract email from format: "Name <email@example.com>"
        match = re.search(r'<(.+?)>', from_header)
        if match:
            return match.group(1)
        
        # Or just return the whole thing if it's already an email
        return from_header.strip()
