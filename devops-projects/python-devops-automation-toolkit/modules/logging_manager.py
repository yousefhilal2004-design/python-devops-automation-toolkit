"""
Professional Logging Manager

Python DevOps Automation Toolkit
Stage 10

Features:
- Console logging
- File logging
- UTC timestamps
- Configurable logging levels
- Automatic log rotation
- Duplicate handler prevention
- Module execution tracking
"""

import logging
import sys
import time

from pathlib import Path
from logging.handlers import RotatingFileHandler


LOGGER_NAME = "devops_toolkit"

DEFAULT_LOG_FILE = "logs/toolkit.log"

DEFAULT_MAX_BYTES = 1_000_000

DEFAULT_BACKUP_COUNT = 3

VALID_LOG_LEVELS = (
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
)


# ==========================================
# 1. UTC Formatter
# ==========================================

class UTCFormatter(logging.Formatter):
    """
    Format log timestamps in UTC.
    """

    converter = time.gmtime


# ==========================================
# 2. Create Formatter
# ==========================================

def create_formatter():
    """
    Create a consistent log format.
    """

    return UTCFormatter(
        fmt=(
            "%(asctime)s UTC | "
            "%(levelname)-8s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# ==========================================
# 3. Validate Settings
# ==========================================

def validate_logging_settings(
    level,
    max_bytes,
    backup_count,
):
    """
    Validate logging configuration.
    """

    if not isinstance(level, str):
        raise ValueError(
            "Logging level must be a string"
        )

    level = level.upper()

    if level not in VALID_LOG_LEVELS:
        raise ValueError(
            "Invalid logging level. "
            f"Choose from: {', '.join(VALID_LOG_LEVELS)}"
        )

    if (
        isinstance(max_bytes, bool)
        or not isinstance(max_bytes, int)
        or max_bytes <= 0
    ):
        raise ValueError(
            "max_bytes must be a positive integer"
        )

    if (
        isinstance(backup_count, bool)
        or not isinstance(backup_count, int)
        or backup_count < 0
    ):
        raise ValueError(
            "backup_count must be a non-negative integer"
        )

    return level


# ==========================================
# 4. Configure Logging
# ==========================================

def setup_logging(
    log_file=DEFAULT_LOG_FILE,
    level="INFO",
    max_bytes=DEFAULT_MAX_BYTES,
    backup_count=DEFAULT_BACKUP_COUNT,
    console=True,
):
    """
    Configure application logging.

    Parameters:
        log_file:
            Destination log file.

        level:
            DEBUG, INFO, WARNING, ERROR,
            or CRITICAL.

        max_bytes:
            Maximum log file size before rotation.

        backup_count:
            Number of rotated files to retain.

        console:
            Whether to log to stderr.

    Returns:
        Configured application logger.
    """

    level = validate_logging_settings(
        level,
        max_bytes,
        backup_count,
    )

    if not isinstance(console, bool):
        raise ValueError(
            "console must be a boolean"
        )

    if not isinstance(log_file, (str, Path)):
        raise ValueError(
            "log_file must be a path"
        )

    if not str(log_file).strip():
        raise ValueError(
            "log_file cannot be empty"
        )

    log_path = Path(log_file).expanduser()

    logger = logging.getLogger(
        LOGGER_NAME
    )

    formatter = create_formatter()

    # Prepare the new handlers before replacing
    # any existing handlers.
    #
    # This prevents a failed reconfiguration
    # from removing the working configuration.

    new_handlers = []

    try:
        log_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_handler = RotatingFileHandler(
            filename=log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )

        file_handler.setFormatter(
            formatter
        )

        new_handlers.append(
            file_handler
        )

        if console:
            console_handler = logging.StreamHandler(
                sys.stderr
            )

            console_handler.setFormatter(
                formatter
            )

            new_handlers.append(
                console_handler
            )

    except Exception:
        for handler in new_handlers:
            handler.close()

        raise

    # Replace existing handlers.
    # This avoids duplicate log messages when
    # setup_logging() is called repeatedly.

    for handler in logger.handlers[:]:
        logger.removeHandler(
            handler
        )

        handler.close()

    logger.setLevel(
        getattr(logging, level)
    )

    logger.propagate = False

    for handler in new_handlers:
        logger.addHandler(
            handler
        )

    return logger


# ==========================================
# 5. Get Logger
# ==========================================

def get_logger(name=None):
    """
    Return the application logger or
    a named child logger.
    """

    if name is None:
        return logging.getLogger(
            LOGGER_NAME
        )

    return logging.getLogger(
        f"{LOGGER_NAME}.{name}"
    )


# ==========================================
# 6. Log Module Start
# ==========================================

def log_module_start(
    logger,
    module_name,
):
    """
    Record module execution start.
    """

    logger.info(
        "Starting module: %s",
        module_name,
    )


# ==========================================
# 7. Log Module Result
# ==========================================

def log_module_result(
    logger,
    module_name,
    success,
    duration_ms,
):
    """
    Record the result of a module execution.
    """

    if success:
        logger.info(
            "Module %s completed: PASS (%.2f ms)",
            module_name,
            duration_ms,
        )

    else:
        logger.warning(
            "Module %s completed: FAIL (%.2f ms)",
            module_name,
            duration_ms,
        )


# ==========================================
# 8. Log Module Exception
# ==========================================

def log_module_exception(
    logger,
    module_name,
    error,
):
    """
    Record exception type without logging
    potentially sensitive exception text.
    """

    logger.error(
        "Module %s raised %s",
        module_name,
        type(error).__name__,
    )