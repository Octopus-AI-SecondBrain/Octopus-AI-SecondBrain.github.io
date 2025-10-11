"""
Professional logging configuration for SecondBrain application.
Provides structured logging with different levels and formatters.
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = getattr(record, 'user_id')
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = getattr(record, 'request_id')
        if hasattr(record, 'endpoint'):
            log_entry["endpoint"] = getattr(record, 'endpoint')
            
        return json.dumps(log_entry, default=str)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_json: bool = False
) -> None:
    """
    Configure application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, logs only to console
        enable_json: Whether to use JSON formatting
    """
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)
    
    # Create formatters
    if enable_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(numeric_level)
        root_logger.addHandler(file_handler)
    
    # Set levels for third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)


# Application-specific loggers
api_logger = get_logger("secondbrain.api")
db_logger = get_logger("secondbrain.database")
vector_logger = get_logger("secondbrain.vector")
auth_logger = get_logger("secondbrain.auth")
security_logger = get_logger("secondbrain.security")