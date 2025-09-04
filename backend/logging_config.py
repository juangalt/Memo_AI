"""
Centralized logging configuration for Memo AI Coach application.

This module provides a unified logging configuration that ensures consistent
formatting and log levels across all application modules.
"""

import logging
import os
import sys
from typing import Optional, List, Dict, Any
from collections import deque
from datetime import datetime
import traceback


def configure_logging(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Configure logging for the entire application.
    
    This function sets up logging with consistent formatting and levels
    across all modules. It should be called once during application startup.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                  Defaults to INFO, or DEBUG if DEBUG environment variable is set
        log_format: Custom log format string. If None, uses default format
        log_file: Optional log file path. If None, logs only to console
    
    Environment Variables:
        APP_ENV: Environment name (development, staging, production) - affects default log level
        DEBUG: If set to any value, enables DEBUG logging level
        LOG_LEVEL: Override default log level
        LOG_FILE: Override default log file path
        LOG_FORMAT: Override default log format
    """
    
    # Determine log level from parameters or environment
    if log_level is None:
        if os.getenv('DEBUG'):
            log_level = 'DEBUG'
        elif os.getenv('LOG_LEVEL'):
            log_level = os.getenv('LOG_LEVEL')
        else:
            # Check APP_ENV for default log level
            app_env = os.getenv('APP_ENV', 'production')
            if app_env == 'development':
                log_level = 'DEBUG'
            elif app_env == 'staging':
                log_level = 'INFO'
            else:  # production
                log_level = 'INFO'
    
    # Convert string to logging level constant
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    numeric_level = level_map.get(log_level.upper(), logging.INFO)
    
    # Determine log format
    if log_format is None:
        log_format = os.getenv('LOG_FORMAT', 
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Determine log file
    if log_file is None:
        log_file = os.getenv('LOG_FILE')
    
    # Clear any existing handlers to avoid duplicates
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)
    
    # Add console handler to root logger
    root_logger.addHandler(console_handler)
    
    # Create file handler if log file is specified
    if log_file:
        try:
            # Ensure log directory exists
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(numeric_level)
            root_logger.addHandler(file_handler)
            
            # Log that file logging is enabled
            root_logger.info(f"File logging enabled: {log_file}")
            
        except Exception as e:
            # If file logging fails, log error but continue with console logging
            root_logger.warning(f"Failed to enable file logging to {log_file}: {e}")
    
    # Set root logger level
    root_logger.setLevel(numeric_level)

    # Attach in-memory recent logs handler for admin inspection
    try:
        _attach_recent_logs_handler(root_logger)
    except Exception as e:
        # Do not fail app startup if recent logs handler fails
        root_logger.warning(f"Failed to attach recent logs handler: {e}")
    
    # Disable propagation for third-party loggers to avoid duplicate messages
    logging.getLogger('uvicorn').propagate = False
    logging.getLogger('fastapi').propagate = False
    
    # Log configuration completion
    app_env = os.getenv('APP_ENV', 'production')
    root_logger.info(f"Logging configured - Environment: {app_env}, Level: {log_level}, Format: {log_format}")
    if log_file:
        root_logger.info(f"Log file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    This is a convenience function that ensures consistent logger naming
    and configuration. Use this instead of logging.getLogger() directly.
    
    Args:
        name: Logger name (typically __name__ from the calling module)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def set_log_level(level: str) -> None:
    """
    Dynamically change the log level for all handlers.
    
    Args:
        level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    numeric_level = level_map.get(level.upper(), logging.INFO)
    
    # Update root logger level
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Update all handler levels
    for handler in root_logger.handlers:
        handler.setLevel(numeric_level)
    
    root_logger.info(f"Log level changed to: {level.upper()}")


# Default configuration for quick setup
def configure_default_logging() -> None:
    """
    Configure logging with default settings.
    
    This is a convenience function for simple applications that don't
    need custom logging configuration.
    """
    configure_logging()


# --- In-memory recent logs support (admin-only endpoint uses this) ---

class _RecentLogsHandler(logging.Handler):
    """Logging handler that keeps a bounded in-memory buffer of recent logs.

    Stores minimal structured fields for safe exposure via the admin API.
    """

    def __init__(self, max_entries: int = 1000) -> None:
        super().__init__()
        self.max_entries = max_entries
        self.buffer: deque = deque(maxlen=max_entries)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            entry: Dict[str, Any] = {
                'timestamp': datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
            }
            # Include exception info if present
            if record.exc_info:
                entry['details'] = ''.join(traceback.format_exception(*record.exc_info))
            # Include module/function context for troubleshooting
            entry['context'] = f"{record.module}.{record.funcName}:{record.lineno}"
            self.buffer.append(entry)
        except Exception:
            # Never raise from logging
            self.handleError(record)


_recent_handler: Optional[_RecentLogsHandler] = None


def _attach_recent_logs_handler(root_logger: logging.Logger, max_entries: int = 1000) -> None:
    global _recent_handler
    if _recent_handler is None:
        _recent_handler = _RecentLogsHandler(max_entries=max_entries)
        _recent_handler.setLevel(root_logger.level)
        root_logger.addHandler(_recent_handler)


def get_recent_logs(limit: int = 200, level: Optional[str] = None, since: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return recent logs as structured dicts.

    Args:
        limit: Max number of entries to return (most recent first)
        level: Optional level filter (e.g., 'INFO', 'ERROR')
        since: Optional ISO timestamp (UTC) to include entries at/after time
    """
    global _recent_handler
    if _recent_handler is None:
        return []

    entries: List[Dict[str, Any]] = list(_recent_handler.buffer)

    # Filter by level
    if level:
        level = level.upper()
        entries = [e for e in entries if e.get('level') == level]

    # Filter by time
    if since:
        try:
            # Accept with or without trailing Z
            s = since[:-1] if since.endswith('Z') else since
            since_dt = datetime.fromisoformat(s)
            entries = [e for e in entries if _parse_iso(e.get('timestamp')) >= since_dt]
        except Exception:
            # Ignore invalid since parameter
            pass

    # Return most recent first
    entries = list(reversed(entries))
    return entries[: max(1, min(limit, 1000))]


def _parse_iso(ts: str) -> datetime:
    s = ts[:-1] if ts.endswith('Z') else ts
    return datetime.fromisoformat(s)
