"""
Tests for email parser
"""
import pytest

from src.bewerbungs_agent.email_parser import EmailParser


class TestEmailParser:
    """Test email parsing functionality"""
    
    def test_parse_message_basic(self):
        """Test basic message parsing"""
        message = {
            'id': 'msg123',
            'threadId': 'thread456',
            'snippet': 'Test email content',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'From', 'value': 'sender@example.com'},
                    {'name': 'To', 'value': 'receiver@example.com'},
                    {'name': 'Date', 'value': 'Mon, 19 Feb 2024 10:00:00 +0000'}
                ],
                'body': {
                    'data': 'VGVzdCBib2R5IGNvbnRlbnQ='  # Base64 for "Test body content"
                }
            }
        }
        
        parsed = EmailParser.parse_message(message)
        
        assert parsed['id'] == 'msg123'
        assert parsed['threadId'] == 'thread456'
        assert parsed['subject'] == 'Test Subject'
        assert parsed['from'] == 'sender@example.com'
        assert parsed['to'] == 'receiver@example.com'
        assert 'body' in parsed
    
    def test_extract_sender_email(self):
        """Test extracting email from From header"""
        # Test with name and email
        email = EmailParser.extract_sender_email('John Doe <john@example.com>')
        assert email == 'john@example.com'
        
        # Test with just email
        email = EmailParser.extract_sender_email('jane@example.com')
        assert email == 'jane@example.com'
        
        # Test with empty
        email = EmailParser.extract_sender_email('')
        assert email == ''
    
    def test_get_header(self):
        """Test getting header values"""
        headers = [
            {'name': 'Subject', 'value': 'Test'},
            {'name': 'From', 'value': 'test@example.com'}
        ]
        
        subject = EmailParser._get_header(headers, 'Subject')
        assert subject == 'Test'
        
        from_header = EmailParser._get_header(headers, 'From')
        assert from_header == 'test@example.com'
        
        missing = EmailParser._get_header(headers, 'Missing')
        assert missing is None
    
    def test_parse_message_with_parts(self):
        """Test parsing message with multiple parts"""
        message = {
            'id': 'msg789',
            'threadId': 'thread101',
            'snippet': 'Multipart email',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Multipart Test'}
                ],
                'parts': [
                    {
                        'mimeType': 'text/plain',
                        'body': {
                            'data': 'UGxhaW4gdGV4dCBjb250ZW50'  # Base64 for "Plain text content"
                        }
                    },
                    {
                        'mimeType': 'text/html',
                        'body': {
                            'data': 'PGh0bWw+SFRNTCBjb250ZW50PC9odG1sPg=='  # Base64 for "<html>HTML content</html>"
                        }
                    }
                ]
            }
        }
        
        parsed = EmailParser.parse_message(message)
        
        assert parsed['id'] == 'msg789'
        assert parsed['subject'] == 'Multipart Test'
        assert len(parsed['body']) > 0
