"""Centralized logging configuration utilities."""
import logging

def setup_logging() -> None:
    """Configure root logger for the application."""
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')

def get_logger(name: str) -> logging.Logger:
    """Return a logger with the given name."""
    return logging.getLogger(name)
