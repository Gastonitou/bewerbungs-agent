"""
Attachment text extraction for PDF, DOCX, and RTF files.

Supports:
- PDF (text-based via PyPDF2, OCR fallback via pytesseract)
- DOCX (python-docx)
- RTF (striprtf)
"""

import os
import tempfile
from typing import Optional

from agent.logger import get_logger

logger = get_logger("attachment_handler")

# Lazily imported so the agent can still run without optional OCR dependencies
_pypdf2_available = False
_docx_available = False
_rtf_available = False
_ocr_available = False

try:
    import PyPDF2  # noqa: F401
    _pypdf2_available = True
except ImportError:
    logger.warning("PyPDF2 not installed – PDF text extraction unavailable.")

try:
    import docx as _docx_mod  # noqa: F401
    _docx_available = True
except ImportError:
    logger.warning("python-docx not installed – DOCX extraction unavailable.")

try:
    from striprtf.striprtf import rtf_to_text  # noqa: F401
    _rtf_available = True
except ImportError:
    logger.warning("striprtf not installed – RTF extraction unavailable.")

try:
    import pytesseract  # noqa: F401
    from PIL import Image  # noqa: F401
    _ocr_available = True
except ImportError:
    logger.warning("pytesseract / Pillow not installed – OCR unavailable.")


def extract_text_from_pdf(path: str) -> str:
    """
    Extract text from a PDF file.

    Attempts direct text extraction first; if no text is found (scanned PDF),
    falls back to OCR via pytesseract (requires tesseract to be installed).
    """
    if not _pypdf2_available:
        logger.error("PyPDF2 is required for PDF extraction.")
        return ""

    import PyPDF2

    text_parts: list[str] = []
    try:
        with open(path, "rb") as fh:
            reader = PyPDF2.PdfReader(fh)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
    except Exception as exc:
        logger.error("Error reading PDF %s: %s", path, exc)
        return ""

    extracted = "\n".join(text_parts).strip()

    if extracted:
        logger.debug("Extracted %d chars from PDF %s via PyPDF2.", len(extracted), path)
        return extracted

    # Fallback: OCR
    if not _ocr_available:
        logger.warning(
            "PDF %s appears to be scanned, but OCR (pytesseract) is unavailable.", path
        )
        return ""

    logger.info("PDF %s appears scanned; attempting OCR.", path)
    return _ocr_pdf(path)


def _ocr_pdf(path: str) -> str:
    """Perform OCR on each page of a PDF using pytesseract."""
    import pytesseract
    from PIL import Image

    try:
        import pdf2image  # optional dependency
        images = pdf2image.convert_from_path(path)
    except ImportError:
        logger.warning(
            "pdf2image not installed; cannot OCR PDF %s. "
            "Install with: pip install pdf2image",
            path,
        )
        return ""
    except Exception as exc:
        logger.error("Error converting PDF %s to images: %s", path, exc)
        return ""

    text_parts: list[str] = []
    for i, img in enumerate(images):
        try:
            page_text = pytesseract.image_to_string(img, lang="deu+eng")
            text_parts.append(page_text)
            logger.debug("OCR page %d of %s: %d chars.", i + 1, path, len(page_text))
        except Exception as exc:
            logger.error("OCR failed on page %d of %s: %s", i + 1, path, exc)

    return "\n".join(text_parts).strip()


def extract_text_from_docx(path: str) -> str:
    """Extract all paragraph text from a DOCX file."""
    if not _docx_available:
        logger.error("python-docx is required for DOCX extraction.")
        return ""

    import docx

    try:
        doc = docx.Document(path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        extracted = "\n".join(paragraphs)
        logger.debug("Extracted %d chars from DOCX %s.", len(extracted), path)
        return extracted
    except Exception as exc:
        logger.error("Error reading DOCX %s: %s", path, exc)
        return ""


def extract_text_from_rtf(path: str) -> str:
    """Extract plain text from an RTF file."""
    if not _rtf_available:
        logger.error("striprtf is required for RTF extraction.")
        return ""

    from striprtf.striprtf import rtf_to_text

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            rtf_content = fh.read()
        extracted = rtf_to_text(rtf_content).strip()
        logger.debug("Extracted %d chars from RTF %s.", len(extracted), path)
        return extracted
    except Exception as exc:
        logger.error("Error reading RTF %s: %s", path, exc)
        return ""


MIME_EXTRACTORS = {
    "application/pdf": extract_text_from_pdf,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": extract_text_from_docx,
    "application/rtf": extract_text_from_rtf,
    "text/rtf": extract_text_from_rtf,
}


def extract_text(path: str, mime_type: str) -> Optional[str]:
    """
    Dispatch text extraction based on *mime_type*.

    Returns the extracted text string, or ``None`` if the type is unsupported.
    """
    extractor = MIME_EXTRACTORS.get(mime_type)
    if extractor is None:
        logger.warning("Unsupported attachment MIME type '%s' for file %s.", mime_type, path)
        return None
    return extractor(path)
