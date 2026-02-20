"""
Bewerbungs-Agent – main entry point.

Orchestrates the full pipeline:
1. Authenticate with Gmail via OAuth2
2. Fetch unprocessed application emails
3. Download and extract attachment text
4. Classify each email with OpenAI
5. Move emails to the correct Gmail label (Zusagen / Absagen)
6. Dispatch tasks to the virtual agent team
7. Log all actions for traceability

Usage
-----
    OPENAI_API_KEY=<key> python -m agent.main [--config config.yaml] [--dry-run]

Arguments
---------
--config   Path to YAML configuration file (default: config.yaml)
--dry-run  Run the full pipeline but skip moving emails and writing tokens
"""

import argparse
import os
import shutil
import sys
import tempfile
from typing import Dict, List, Optional

import yaml

from agent.attachment_handler import MIME_EXTRACTORS, extract_text
from agent.classifier import Classifier, ClassificationResult
from agent.gmail_client import GmailClient
from agent.logger import get_logger, setup_logger
from agent.task_manager import TaskManager


def load_config(path: str) -> Dict:
    """Load YAML configuration from *path*."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def process_email(
    gmail: GmailClient,
    classifier: Classifier,
    task_manager: TaskManager,
    message_meta: Dict,
    config: Dict,
    dry_run: bool,
) -> Optional[ClassificationResult]:
    """
    Run the full pipeline for a single email message.

    Returns the ClassificationResult or None if the message is skipped.
    """
    logger = get_logger("main")
    message_id = message_meta["id"]

    # Fetch full message
    message = gmail.get_message(message_id)
    headers = GmailClient.extract_headers(message)
    subject = headers.get("subject", "(no subject)")
    sender = headers.get("from", "unknown")

    logger.info("Processing message %s | from: %s | subject: %s", message_id, sender, subject)

    # Extract body
    body = GmailClient.extract_body(message)

    # Download and extract attachment text
    att_config = config.get("attachments", {})
    max_size = att_config.get("max_size_bytes", 10_485_760)
    supported_types = set(att_config.get("supported_types", list(MIME_EXTRACTORS.keys())))
    tmp_dir = att_config.get("temp_dir", tempfile.gettempdir())
    os.makedirs(tmp_dir, exist_ok=True)

    attachment_texts: List[str] = []
    attachments = gmail.list_attachments(message)
    for att in attachments:
        mime = att.get("mime_type", "")
        size = att.get("size", 0)
        filename = att.get("filename", "unknown")

        if mime not in supported_types:
            logger.debug("Skipping attachment '%s' (unsupported type '%s').", filename, mime)
            continue
        if size > max_size:
            logger.warning(
                "Skipping attachment '%s' (size %d bytes exceeds limit %d).",
                filename,
                size,
                max_size,
            )
            continue

        # Use a secure temp file scoped to this run
        suffix = os.path.splitext(filename)[1] or ".bin"
        fd, tmp_path = tempfile.mkstemp(dir=tmp_dir, suffix=suffix)
        os.close(fd)
        try:
            if not dry_run:
                gmail.download_attachment(message_id, att["attachment_id"], tmp_path)
                text = extract_text(tmp_path, mime)
                if text:
                    attachment_texts.append(text)
                    logger.info(
                        "Extracted %d chars from attachment '%s'.", len(text), filename
                    )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    # Classify email
    result = classifier.classify(
        message_id=message_id,
        subject=subject,
        body=body,
        attachment_texts=attachment_texts,
    )

    logger.info(
        "Classification: message=%s category=%s summary=%s",
        message_id,
        result.category,
        result.summary,
    )

    # Move to appropriate Gmail label
    if not dry_run:
        gmail_cfg = config.get("gmail", {})
        if result.is_rejection:
            gmail.move_to_label(message_id, gmail_cfg.get("rejection_label", "Absagen"))
        elif result.is_acceptance:
            gmail.move_to_label(message_id, gmail_cfg.get("acceptance_label", "Zusagen"))
        gmail.mark_as_read(message_id)
    else:
        logger.info("[DRY RUN] Would move message %s (category: %s).", message_id, result.category)

    # Dispatch tasks to agent team
    completed_tasks = task_manager.dispatch(result)
    logger.info(
        "Dispatched %d task(s) for message %s.", len(completed_tasks), message_id
    )

    return result


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bewerbungs-Agent: AI-powered job application email manager"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to YAML configuration file (default: config.yaml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pipeline without moving emails or persisting OAuth tokens",
    )
    args = parser.parse_args(argv)

    # Load configuration
    config = load_config(args.config)

    # Initialise logging
    log_cfg = config.get("logging", {})
    setup_logger(
        log_file=log_cfg.get("log_file", "bewerbungs_agent.log"),
        level=log_cfg.get("level", "INFO"),
        max_bytes=log_cfg.get("max_bytes", 5_242_880),
        backup_count=log_cfg.get("backup_count", 3),
    )
    logger = get_logger("main")
    logger.info("=== Bewerbungs-Agent starting (dry_run=%s) ===", args.dry_run)

    # Validate OpenAI key early
    if not os.environ.get("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is not set. Exiting.")
        return 1

    gmail_cfg = config.get("gmail", {})
    openai_cfg = config.get("openai", {})
    agents_cfg = config.get("agents", {})

    # Initialise components
    gmail = GmailClient(
        credentials_file=gmail_cfg.get("credentials_file", "credentials.json"),
        token_file=gmail_cfg.get("token_file", "token.json"),
        email_address=gmail_cfg.get("email_address", ""),
    )

    classifier = Classifier(
        model=openai_cfg.get("model", "gpt-4o"),
        max_tokens=openai_cfg.get("max_tokens", 1024),
        temperature=openai_cfg.get("temperature", 0.2),
    )

    task_manager = TaskManager(team_config=agents_cfg.get("team", []))

    # Authenticate
    if not args.dry_run:
        gmail.authenticate()
    else:
        logger.info("[DRY RUN] Skipping Gmail authentication.")

    # Fetch emails
    inbox_label = gmail_cfg.get("inbox_label", "INBOX")
    max_results = gmail_cfg.get("max_results", 50)
    messages = []
    if not args.dry_run:
        messages = gmail.list_messages(label=inbox_label, max_results=max_results)
    else:
        logger.info("[DRY RUN] Skipping email fetch.")

    logger.info("Processing %d message(s).", len(messages))

    results: List[ClassificationResult] = []
    for msg_meta in messages:
        result = process_email(
            gmail=gmail,
            classifier=classifier,
            task_manager=task_manager,
            message_meta=msg_meta,
            config=config,
            dry_run=args.dry_run,
        )
        if result:
            results.append(result)

    # Summary
    rejections = sum(1 for r in results if r.is_rejection)
    acceptances = sum(1 for r in results if r.is_acceptance)
    others = len(results) - rejections - acceptances
    logger.info(
        "=== Run complete: %d processed | %d Zusagen | %d Absagen | %d Sonstige ===",
        len(results),
        acceptances,
        rejections,
        others,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
