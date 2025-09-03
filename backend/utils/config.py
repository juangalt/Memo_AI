"""Utility functions for configuration path detection."""
from pathlib import Path
import os

def get_config_path() -> Path:
    """Return path to configuration directory.

    Preference order:
    1. Mounted container path ``/app/config``
    2. ``CONFIG_DIR`` environment variable
    3. ``../config`` relative path
    """
    if os.path.exists('/app/config'):
        return Path('/app/config')
    return Path(os.getenv('CONFIG_DIR', '../config'))
