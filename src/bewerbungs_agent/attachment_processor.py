"""
Attachment processing for PDF and DOCX files
"""
import io
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None

from .logger import get_logger


logger = get_logger('attachment_processor')


class AttachmentProcessor:
    """Processor for email attachments"""
    
    @staticmethod
    def process_attachment(attachment: Dict[str, Any]) -> Optional[str]:
        """
        Process attachment and extract text
        
        Args:
            attachment: Attachment dictionary with 'filename', 'mimeType', and 'data'
            
        Returns:
            Extracted text or None
        """
        filename = attachment.get('filename', '').lower()
        mime_type = attachment.get('mimeType', '').lower()
        data = attachment.get('data')
        
        if not data:
            logger.warning(f"No data in attachment: {filename}")
            return None
        
        try:
            # Process PDF
            if filename.endswith('.pdf') or 'pdf' in mime_type:
                return AttachmentProcessor._process_pdf(data)
            
            # Process DOCX
            elif filename.endswith('.docx') or 'wordprocessingml' in mime_type:
                return AttachmentProcessor._process_docx(data)
            
            # Process DOC (limited support)
            elif filename.endswith('.doc') or 'msword' in mime_type:
                logger.info(f"DOC format has limited support: {filename}")
                return None
            
            else:
                logger.info(f"Unsupported attachment type: {filename} ({mime_type})")
                return None
        
        except Exception as e:
            logger.error(f"Error processing attachment {filename}: {e}")
            return None
    
    @staticmethod
    def _process_pdf(data: bytes) -> Optional[str]:
        """Extract text from PDF"""
        if not PdfReader:
            logger.error("PyPDF2 not installed, cannot process PDF")
            return None
        
        try:
            pdf_file = io.BytesIO(data)
            pdf_reader = PdfReader(pdf_file)
            
            text_parts = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            result = "\n".join(text_parts)
            logger.info(f"Extracted {len(result)} characters from PDF")
            return result
        
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return None
    
    @staticmethod
    def _process_docx(data: bytes) -> Optional[str]:
        """Extract text from DOCX"""
        if not Document:
            logger.error("python-docx not installed, cannot process DOCX")
            return None
        
        try:
            docx_file = io.BytesIO(data)
            doc = Document(docx_file)
            
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text:
                    text_parts.append(paragraph.text)
            
            result = "\n".join(text_parts)
            logger.info(f"Extracted {len(result)} characters from DOCX")
            return result
        
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            return None
