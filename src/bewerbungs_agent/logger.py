"""
Logging setup for the Bewerbungs-Agent
"""
import logging
import os
from pathlib import Path
from typing import Optional


def setup_logging(config: dict) -> logging.Logger:
    """
    Set up logging for the agent
    
    Args:
        config: Logging configuration dictionary
        
    Returns:
        Configured logger
    """
    # Get configuration
    log_level = config.get('level', 'INFO')
    log_file = config.get('file', 'logs/agent.log')
    console = config.get('console', True)
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('bewerbungs_agent')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name (uses bewerbungs_agent if None)
        
    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f'bewerbungs_agent.{name}')
    return logging.getLogger('bewerbungs_agent')
