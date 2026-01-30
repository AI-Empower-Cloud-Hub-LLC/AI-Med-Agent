"""Logging configuration for AI-Med-Agent"""

import logging
import logging.handlers
import sys
from pathlib import Path


def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: str = "logs/ai-med-agent.log"
) -> logging.Logger:
    """
    Configure and return a logger instance with both file and console handlers
    
    Args:
        name: Logger name (typically __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_file).parent
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler (rotating)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, level))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
