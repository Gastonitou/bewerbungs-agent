"""
Structured logging for the bewerbungs-agent.
"""

import logging
import logging.handlers
import os
from typing import Optional


def setup_logger(
    log_file: str = "bewerbungs_agent.log",
    level: str = "INFO",
    max_bytes: int = 5_242_880,
    backup_count: int = 3,
) -> logging.Logger:
    """
    Configure and return the root logger for the agent.

    Logs are written to both the console (stdout) and a rotating file.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    logger = logging.getLogger("bewerbungs_agent")
    logger.setLevel(numeric_level)

    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(fmt)
        logger.addHandler(console_handler)

        # Rotating file handler
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a child logger under the bewerbungs_agent namespace."""
    base = "bewerbungs_agent"
    return logging.getLogger(f"{base}.{name}" if name else base)
