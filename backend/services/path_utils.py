"""
Path Utilities for Memo AI Coach
Centralized configuration path resolution
"""

import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def resolve_config_dir() -> str:
    """
    Resolve the configuration directory path with consistent fallback logic.
    
    Returns:
        str: Path to configuration directory
        
    Logic:
        1. Check CONFIG_DIR environment variable
        2. If unset or path doesn't exist, return '/app/config' (container default)
        3. For development, services can check if '/app/config' exists and fallback to '../config'
    
    This centralizes the configuration path resolution logic used across all services.
    """
    config_dir = os.getenv('CONFIG_DIR')
    
    if config_dir and os.path.exists(config_dir):
        logger.debug(f"Using CONFIG_DIR environment variable: {config_dir}")
        return config_dir
    
    # Default container path
    default_path = '/app/config'
    logger.debug(f"CONFIG_DIR not set or invalid, using default: {default_path}")
    return default_path

def resolve_config_dir_with_fallback() -> str:
    """
    Resolve configuration directory with development fallback logic.
    
    Returns:
        str: Path to configuration directory with fallback for development
        
    Logic:
        1. Check CONFIG_DIR environment variable
        2. If unset or path doesn't exist, check if '/app/config' exists (container)
        3. If '/app/config' doesn't exist, check if './config' exists (root directory)
        4. If './config' doesn't exist, fallback to '../config' (backend directory)
    
    This is used by services that need to handle both container and development environments.
    """
    config_dir = os.getenv('CONFIG_DIR')
    
    if config_dir and os.path.exists(config_dir):
        logger.debug(f"Using CONFIG_DIR environment variable: {config_dir}")
        return config_dir
    
    # Check container path first
    if os.path.exists('/app/config'):
        logger.debug("Using container config path: /app/config")
        return '/app/config'
    
    # Check if we're in root directory
    if os.path.exists('./config'):
        logger.debug("Using root directory config path: ./config")
        return './config'
    
    # Fallback for development (backend directory)
    fallback_path = '../config'
    logger.debug(f"Using development fallback path: {fallback_path}")
    return fallback_path
