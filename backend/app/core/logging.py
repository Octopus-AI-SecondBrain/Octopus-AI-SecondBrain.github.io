"""
Octopus AI Second Brain - Structured Logging
Provides comprehensive logging with JSON support for production environments.
"""
import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from logging.handlers import RotatingFileHandler


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data, default=str)


class StructuredLogger(logging.LoggerAdapter):
    """Logger adapter that adds structured context to log records"""

    def process(
        self, msg: str, kwargs: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """Add extra fields to log record"""
        extra = kwargs.get("extra", {})
        if self.extra:
            extra.update(self.extra)
        kwargs["extra"] = {"extra_fields": extra}
        return msg, kwargs


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_json: bool = False,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Set up application logging with console and optional file output.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        enable_json: Enable JSON structured logging
        max_bytes: Max size of log file before rotation
        backup_count: Number of backup log files to keep
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    if enable_json:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_format = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(logging.Formatter(console_format))

    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))

        if enable_json:
            file_handler.setFormatter(JSONFormatter())
        else:
            file_format = (
                "%(asctime)s - %(name)s - %(levelname)s - "
                "%(module)s:%(funcName)s:%(lineno)d - %(message)s"
            )
            file_handler.setFormatter(logging.Formatter(file_format))

        root_logger.addHandler(file_handler)

    # Set lower log levels for noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str, **context: Any) -> StructuredLogger:
    """
    Get a structured logger with optional context.

    Args:
        name: Logger name (typically __name__)
        **context: Additional context to add to all log messages

    Returns:
        StructuredLogger instance

    Example:
        logger = get_logger(__name__, service="rag", component="embedder")
        logger.info("Processing documents", extra={"count": 10})
    """
    base_logger = logging.getLogger(name)
    return StructuredLogger(base_logger, context)
