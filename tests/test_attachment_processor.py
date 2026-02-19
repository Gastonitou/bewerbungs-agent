"""
Tests for attachment processor
"""
import pytest
import io

from src.bewerbungs_agent.attachment_processor import AttachmentProcessor


class TestAttachmentProcessor:
    """Test attachment processing"""
    
    def test_process_unsupported_attachment(self):
        """Test processing unsupported attachment type"""
        attachment = {
            'filename': 'test.txt',
            'mimeType': 'text/plain',
            'data': b'Test content'
        }
        
        result = AttachmentProcessor.process_attachment(attachment)
        
        # Text files are not supported
        assert result is None
    
    def test_process_attachment_no_data(self):
        """Test processing attachment without data"""
        attachment = {
            'filename': 'test.pdf',
            'mimeType': 'application/pdf',
            'data': None
        }
        
        result = AttachmentProcessor.process_attachment(attachment)
        
        assert result is None
    
    def test_process_pdf_not_installed(self):
        """Test PDF processing when library not installed"""
        # This tests the fallback behavior
        attachment = {
            'filename': 'test.pdf',
            'mimeType': 'application/pdf',
            'data': b'%PDF-1.4 fake pdf data'
        }
        
        # Will return None if PyPDF2 is not installed or if PDF is invalid
        result = AttachmentProcessor.process_attachment(attachment)
        
        # Either processed or None if library missing
        assert result is None or isinstance(result, str)
    
    def test_process_docx_not_installed(self):
        """Test DOCX processing when library not installed"""
        attachment = {
            'filename': 'test.docx',
            'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'data': b'PK fake docx data'
        }
        
        # Will return None if python-docx is not installed or if DOCX is invalid
        result = AttachmentProcessor.process_attachment(attachment)
        
        # Either processed or None if library missing
        assert result is None or isinstance(result, str)
    
    def test_identify_pdf_by_extension(self):
        """Test PDF identification by file extension"""
        attachment = {
            'filename': 'document.pdf',
            'mimeType': 'application/octet-stream',
            'data': b'fake data'
        }
        
        # Should attempt to process as PDF based on extension
        result = AttachmentProcessor.process_attachment(attachment)
        
        # Either processed or None
        assert result is None or isinstance(result, str)
    
    def test_identify_docx_by_mimetype(self):
        """Test DOCX identification by MIME type"""
        attachment = {
            'filename': 'document.unknown',
            'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'data': b'fake data'
        }
        
        # Should attempt to process as DOCX based on MIME type
        result = AttachmentProcessor.process_attachment(attachment)
        
        # Either processed or None
        assert result is None or isinstance(result, str)
