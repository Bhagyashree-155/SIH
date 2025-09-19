import logging
import sys
from typing import Dict, Any
from src.core.config import settings


class ColorFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    COLORS = {
        logging.DEBUG: '\033[36m',    # Cyan
        logging.INFO: '\033[32m',     # Green
        logging.WARNING: '\033[33m',  # Yellow
        logging.ERROR: '\033[31m',    # Red
        logging.CRITICAL: '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelno, '')
        reset = self.RESET
        record.levelname = f"{color}{record.levelname}{reset}"
        return super().format(record)


def setup_logging() -> logging.Logger:
    """Setup application logging"""
    
    # Get root logger
    logger = logging.getLogger("powergrid_ticketing")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Formatter
    if settings.DEBUG:
        formatter = ColorFormatter(settings.LOG_FORMAT)
    else:
        formatter = logging.Formatter(settings.LOG_FORMAT)
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler for production
    if settings.ENVIRONMENT == "production":
        file_handler = logging.FileHandler("app.log")
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(settings.LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    
    return logger


# Audit logging function
def log_audit_event(event_type: str, user_id: str, details: Dict[str, Any]):
    """Log audit events for security and compliance"""
    audit_logger = logging.getLogger("powergrid_ticketing.audit")
    audit_logger.info(f"AUDIT: {event_type} | User: {user_id} | Details: {details}")


# Get logger instance
logger = setup_logging()
