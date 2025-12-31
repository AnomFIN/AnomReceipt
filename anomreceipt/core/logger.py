"""
Logging configuration for AnomReceipt.
Professional logging system with file rotation and proper formatting.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logging(log_dir: str = "logs", log_level: int = logging.INFO):
    """
    Set up comprehensive logging system.
    
    Args:
        log_dir: Directory for log files
        log_level: Logging level (default: INFO)
    """
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Log file path
    log_file = log_path / f"anomreceipt_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Format for log messages
    log_format = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with rotation (10 MB max, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)
    
    # Console handler (only for warnings and errors)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
    
    # Log startup
    root_logger.info("=" * 80)
    root_logger.info("AnomReceipt Application Starting")
    root_logger.info(f"Log file: {log_file}")
    root_logger.info(f"Python version: {sys.version}")
    root_logger.info("=" * 80)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
