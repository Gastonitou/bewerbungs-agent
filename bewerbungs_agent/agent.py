"""Main agent orchestrator."""
import logging
import os
from dataclasses import dataclass, field
from typing import List

from .attachment_handler import extract_text_from_attachment
from .classifier import classify_email
from .gmail_service import (
    extract_body,
    fetch_unread_emails,
    get_attachments,
    get_gmail_service,
    get_or_create_label,
    move_message_to_label,
)

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    message_id: str
    subject: str
    category: str
    action_taken: str
    attachment_filenames: List[str] = field(default_factory=list)


def run(
    inbox_label: str = "INBOX",
    zusage_label: str = "Zusagen",
    absage_label: str = "Absagen",
    max_emails: int = 50,
) -> List[ProcessingResult]:
    """Fetch unread emails, classify each one and sort it into the right label.

    Returns a list of :class:`ProcessingResult` objects for logging / reporting.
    """
    service = get_gmail_service()

    zusage_id = get_or_create_label(service, zusage_label)
    absage_id = get_or_create_label(service, absage_label)

    messages = fetch_unread_emails(service, label=inbox_label, max_results=max_emails)
    results: List[ProcessingResult] = []

    for msg in messages:
        subject = _get_header(msg, "Subject")
        logger.info("Processing: %s", subject)

        body = extract_body(msg)
        attachments = get_attachments(service, msg)
        attachment_texts = []
        attachment_filenames = []
        for att in attachments:
            text = extract_text_from_attachment(att["filename"], att["mime_type"], att["data"])
            if text:
                attachment_texts.append(text)
            attachment_filenames.append(att["filename"])

        combined_attachment_text = "\n\n".join(attachment_texts)
        category = classify_email(body, combined_attachment_text)

        action = "keine Aktion (sonstiges)"
        if category == "zusage":
            move_message_to_label(service, msg["id"], zusage_id)
            action = f"verschoben nach '{zusage_label}'"
        elif category == "absage":
            move_message_to_label(service, msg["id"], absage_id)
            action = f"verschoben nach '{absage_label}'"

        result = ProcessingResult(
            message_id=msg["id"],
            subject=subject,
            category=category,
            action_taken=action,
            attachment_filenames=attachment_filenames,
        )
        results.append(result)
        logger.info(
            "  ➜ Kategorie: %-10s | Aktion: %s | Anhänge: %s",
            category,
            action,
            attachment_filenames or "–",
        )

    logger.info("Fertig. %d E-Mail(s) verarbeitet.", len(results))
    return results


def _get_header(message: dict, name: str) -> str:
    headers = message.get("payload", {}).get("headers", [])
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return "(kein Betreff)"
