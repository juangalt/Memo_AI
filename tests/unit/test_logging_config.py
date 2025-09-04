"""
Unit tests for logging configuration module.
"""

import logging
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import sys

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from logging_config import configure_logging, get_logger, set_log_level, configure_default_logging


class TestLoggingConfig(unittest.TestCase):
    """Test cases for logging configuration functions."""
    
    def setUp(self):
        """Set up test environment."""
        # Clear any existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Reset root logger level
        root_logger.setLevel(logging.WARNING)
    
    def tearDown(self):
        """Clean up after tests."""
        # Clear any existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Reset root logger level
        root_logger.setLevel(logging.WARNING)
    
    def test_configure_logging_defaults(self):
        """Test logging configuration with default parameters."""
        configure_logging()
        
        root_logger = logging.getLogger()
        
        # Check that handlers were added
        self.assertGreater(len(root_logger.handlers), 0)
        
        # Check console handler exists
        console_handlers = [h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)]
        self.assertGreater(len(console_handlers), 0)
        
        # Check log level is INFO (default)
        self.assertEqual(root_logger.level, logging.INFO)
        
        # Check that formatter is set
        for handler in root_logger.handlers:
            self.assertIsNotNone(handler.formatter)
    
    def test_configure_logging_custom_level(self):
        """Test logging configuration with custom log level."""
        configure_logging(log_level='DEBUG')
        
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.DEBUG)
        
        # Check that all handlers have the same level
        for handler in root_logger.handlers:
            self.assertEqual(handler.level, logging.DEBUG)
    
    def test_configure_logging_custom_format(self):
        """Test logging configuration with custom format."""
        custom_format = '%(levelname)s - %(message)s'
        configure_logging(log_format=custom_format)
        
        root_logger = logging.getLogger()
        
        # Check that formatter uses custom format
        for handler in root_logger.handlers:
            self.assertEqual(handler.formatter._fmt, custom_format)
    
    def test_configure_logging_with_file(self):
        """Test logging configuration with file handler."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            configure_logging(log_file=temp_file_path)
            
            root_logger = logging.getLogger()
            
            # Check that file handler was added
            file_handlers = [h for h in root_logger.handlers if isinstance(h, logging.FileHandler)]
            self.assertGreater(len(file_handlers), 0)
            
            # Check that file handler points to correct file
            self.assertEqual(file_handlers[0].baseFilename, temp_file_path)
            
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def test_configure_logging_environment_variables(self):
        """Test logging configuration using environment variables."""
        with patch.dict(os.environ, {'DEBUG': '1', 'LOG_LEVEL': 'ERROR'}):
            configure_logging()
            
            root_logger = logging.getLogger()
            # DEBUG environment variable should override LOG_LEVEL
            self.assertEqual(root_logger.level, logging.DEBUG)
    
    def test_configure_logging_clears_existing_handlers(self):
        """Test that configure_logging clears existing handlers."""
        # Add a dummy handler first
        root_logger = logging.getLogger()
        dummy_handler = logging.StreamHandler()
        root_logger.addHandler(dummy_handler)
        
        initial_handler_count = len(root_logger.handlers)
        
        # Configure logging
        configure_logging()
        
        # Check that old handlers were removed
        self.assertNotIn(dummy_handler, root_logger.handlers)
        
        # Check that new handlers were added
        self.assertGreater(len(root_logger.handlers), 0)
    
    def test_get_logger(self):
        """Test get_logger convenience function."""
        logger = get_logger('test_module')
        
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, 'test_module')
    
    def test_set_log_level(self):
        """Test set_log_level function."""
        # Configure logging first
        configure_logging(log_level='INFO')
        
        # Change log level
        set_log_level('DEBUG')
        
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.DEBUG)
        
        # Check that all handlers have the new level
        for handler in root_logger.handlers:
            self.assertEqual(handler.level, logging.DEBUG)
    
    def test_set_log_level_invalid(self):
        """Test set_log_level with invalid level."""
        configure_logging()
        
        # Set invalid level (should default to INFO)
        set_log_level('INVALID_LEVEL')
        
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.INFO)
    
    def test_configure_default_logging(self):
        """Test configure_default_logging convenience function."""
        configure_default_logging()
        
        root_logger = logging.getLogger()
        
        # Check that logging was configured
        self.assertGreater(len(root_logger.handlers), 0)
        self.assertEqual(root_logger.level, logging.INFO)
    
    def test_configure_logging_file_creation_failure(self):
        """Test logging configuration when file creation fails."""
        # Try to log to a directory that doesn't exist and can't be created
        with patch('os.makedirs', side_effect=PermissionError("Permission denied")):
            configure_logging(log_file='/root/invalid/path/test.log')
            
            root_logger = logging.getLogger()
            
            # Should still have console handler
            console_handlers = [h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)]
            self.assertGreater(len(console_handlers), 0)
            
            # Should not have file handler
            file_handlers = [h for h in root_logger.handlers if isinstance(h, logging.FileHandler)]
            self.assertEqual(len(file_handlers), 0)
    
    def test_configure_logging_third_party_loggers(self):
        """Test that third-party loggers have propagation disabled."""
        configure_logging()
        
        # Check that uvicorn and fastapi loggers don't propagate
        uvicorn_logger = logging.getLogger('uvicorn')
        fastapi_logger = logging.getLogger('fastapi')
        
        self.assertFalse(uvicorn_logger.propagate)
        self.assertFalse(fastapi_logger.propagate)


if __name__ == '__main__':
    unittest.main()
