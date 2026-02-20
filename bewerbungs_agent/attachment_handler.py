"""Attachment handler: extract text from PDF and DOCX files."""
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text_from_attachment(filename: str, mime_type: str, data: bytes) -> Optional[str]:
    """Return plain text extracted from *data* based on *mime_type* / *filename*.

    Supports:
    - PDF  (via PyPDF2; falls back to pytesseract OCR for scanned PDFs)
    - DOCX (via python-docx)
    - RTF  (plain-text strip of RTF control words)
    """
    lower_name = filename.lower()

    if mime_type == "application/pdf" or lower_name.endswith(".pdf"):
        return _extract_pdf(data)

    if mime_type in (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ) or lower_name.endswith((".docx", ".doc")):
        return _extract_docx(data)

    if lower_name.endswith(".rtf"):
        return _extract_rtf(data)

    logger.debug("Unsupported attachment type: %s / %s", filename, mime_type)
    return None


def _extract_pdf(data: bytes) -> str:
    try:
        import pypdf  # noqa: PLC0415

        reader = pypdf.PdfReader(io.BytesIO(data))
        texts = []
        for page in reader.pages:
            text = page.extract_text() or ""
            texts.append(text)
        combined = "\n".join(texts).strip()
        if combined:
            return combined
        # Scanned PDF – fall through to OCR
    except Exception as exc:  # noqa: BLE001
        logger.warning("PyPDF2 failed: %s", exc)

    # OCR fallback
    try:
        import pytesseract  # noqa: PLC0415
        from PIL import Image  # noqa: PLC0415
        import fitz  # PyMuPDF  # noqa: PLC0415

        doc = fitz.open(stream=data, filetype="pdf")
        texts = []
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            texts.append(pytesseract.image_to_string(img))
        return "\n".join(texts).strip()
    except Exception as exc:  # noqa: BLE001
        logger.warning("OCR fallback failed: %s", exc)
        return ""


def _extract_docx(data: bytes) -> str:
    try:
        from docx import Document  # noqa: PLC0415

        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception as exc:  # noqa: BLE001
        logger.warning("python-docx failed: %s", exc)
        return ""


def _extract_rtf(data: bytes) -> str:
    import re

    text = data.decode("utf-8", errors="replace")
    # Strip RTF control words and groups
    text = re.sub(r"\\[a-z]+\d*\s?", " ", text)
    text = re.sub(r"[{}\\]", "", text)
    return text.strip()
