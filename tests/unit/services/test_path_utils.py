"""
Unit tests for path utilities
"""

import os
import pytest
from unittest.mock import patch, mock_open
from backend.services.path_utils import resolve_config_dir, resolve_config_dir_with_fallback

class TestPathUtils:
    """Test cases for path utility functions"""
    
    def test_resolve_config_dir_env_set_and_exists(self):
        """Test resolve_config_dir when CONFIG_DIR is set and path exists"""
        with patch.dict(os.environ, {'CONFIG_DIR': '/custom/config'}):
            with patch('os.path.exists', return_value=True):
                result = resolve_config_dir()
                assert result == '/custom/config'
    
    def test_resolve_config_dir_env_set_but_not_exists(self):
        """Test resolve_config_dir when CONFIG_DIR is set but path doesn't exist"""
        with patch.dict(os.environ, {'CONFIG_DIR': '/custom/config'}):
            with patch('os.path.exists', return_value=False):
                result = resolve_config_dir()
                assert result == '/app/config'
    
    def test_resolve_config_dir_env_not_set(self):
        """Test resolve_config_dir when CONFIG_DIR is not set"""
        with patch.dict(os.environ, {}, clear=True):
            result = resolve_config_dir()
            assert result == '/app/config'
    
    def test_resolve_config_dir_with_fallback_env_set_and_exists(self):
        """Test resolve_config_dir_with_fallback when CONFIG_DIR is set and path exists"""
        with patch.dict(os.environ, {'CONFIG_DIR': '/custom/config'}):
            with patch('os.path.exists', return_value=True):
                result = resolve_config_dir_with_fallback()
                assert result == '/custom/config'
    
    def test_resolve_config_dir_with_fallback_env_set_but_not_exists(self):
        """Test resolve_config_dir_with_fallback when CONFIG_DIR is set but path doesn't exist"""
        with patch.dict(os.environ, {'CONFIG_DIR': '/custom/config'}):
            with patch('os.path.exists') as mock_exists:
                # First call for CONFIG_DIR check, second for /app/config check
                mock_exists.side_effect = [False, True]
                result = resolve_config_dir_with_fallback()
                assert result == '/app/config'
    
    def test_resolve_config_dir_with_fallback_container_path_exists(self):
        """Test resolve_config_dir_with_fallback when /app/config exists (container)"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('os.path.exists') as mock_exists:
                def mock_exists_side_effect(path):
                    if path == '/app/config':
                        return True
                    return False
                mock_exists.side_effect = mock_exists_side_effect
                result = resolve_config_dir_with_fallback()
                assert result == '/app/config'
    
    def test_resolve_config_dir_with_fallback_development_fallback(self):
        """Test resolve_config_dir_with_fallback when falling back to development path"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('os.path.exists') as mock_exists:
                def mock_exists_side_effect(path):
                    if path == '/app/config':
                        return False
                    elif path == './config':
                        return False
                    return False
                mock_exists.side_effect = mock_exists_side_effect
                result = resolve_config_dir_with_fallback()
                assert result == '../config'
    
    def test_resolve_config_dir_with_fallback_env_unset(self):
        """Test resolve_config_dir_with_fallback when CONFIG_DIR is not set"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('os.path.exists') as mock_exists:
                def mock_exists_side_effect(path):
                    if path == '/app/config':
                        return True
                    return False
                mock_exists.side_effect = mock_exists_side_effect
                result = resolve_config_dir_with_fallback()
                assert result == '/app/config'
    
    def test_resolve_config_dir_with_fallback_root_directory(self):
        """Test resolve_config_dir_with_fallback when ./config exists (root directory)"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('os.path.exists') as mock_exists:
                def mock_exists_side_effect(path):
                    if path == '/app/config':
                        return False
                    elif path == './config':
                        return True
                    return False
                mock_exists.side_effect = mock_exists_side_effect
                result = resolve_config_dir_with_fallback()
                assert result == './config'
