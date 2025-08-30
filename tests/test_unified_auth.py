"""
Test unified authentication system for Memo AI Coach
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services import (
    get_auth_service,
    authenticate,
    validate_session,
    logout,
    create_user
)
from backend.models.entities import User, Session

class TestUnifiedAuth(unittest.TestCase):
    """Test unified authentication system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Initialize auth service with test config
        test_config_path = os.path.join(os.path.dirname(__file__), 'test_config')
        cls.auth_service = get_auth_service(test_config_path)
        
        # Create test users
        cls.test_users = [
            ("testuser", "testPass123!", False),  # Regular user
            ("testadmin", "adminPass123!", True)  # Admin user
        ]
        
        for username, password, is_admin in cls.test_users:
            success, user_id, error = create_user(username, password, is_admin)
            if not success:
                logger.error(f"Failed to create test user {username}: {error}")
                raise Exception(f"Test setup failed: {error}")
            logger.info(f"Created test user {username} (admin: {is_admin})")
    
    def test_01_authenticate_regular_user(self):
        """Test regular user authentication"""
        # Test successful login
        success, token, error = authenticate("testuser", "testPass123!")
        self.assertTrue(success, f"Regular user login failed: {error}")
        self.assertIsNotNone(token, "No session token returned")
        
        # Verify session
        valid, session_data, error = validate_session(token)
        self.assertTrue(valid, f"Session validation failed: {error}")
        self.assertEqual(session_data['username'], "testuser")
        self.assertFalse(session_data['is_admin'])
        
        # Test invalid password
        success, token, error = authenticate("testuser", "wrongpass")
        self.assertFalse(success, "Login should fail with wrong password")
        self.assertIsNone(token)
        
        # Test non-existent user
        success, token, error = authenticate("nonexistent", "anypass")
        self.assertFalse(success, "Login should fail with non-existent user")
        self.assertIsNone(token)
    
    def test_02_authenticate_admin_user(self):
        """Test admin user authentication"""
        # Test successful login
        success, token, error = authenticate("testadmin", "adminPass123!")
        self.assertTrue(success, f"Admin user login failed: {error}")
        self.assertIsNotNone(token, "No session token returned")
        
        # Verify session
        valid, session_data, error = validate_session(token)
        self.assertTrue(valid, f"Session validation failed: {error}")
        self.assertEqual(session_data['username'], "testadmin")
        self.assertTrue(session_data['is_admin'])
        self.assertIn('permissions', session_data)
        self.assertIn('system_configuration', session_data['permissions'])
        
        # Test invalid password
        success, token, error = authenticate("testadmin", "wrongpass")
        self.assertFalse(success, "Login should fail with wrong password")
        self.assertIsNone(token)
    
    def test_03_session_management(self):
        """Test session management"""
        # Create session
        success, token, error = authenticate("testuser", "testPass123!")
        self.assertTrue(success, f"Session creation failed: {error}")
        
        # Validate session
        valid, session_data, error = validate_session(token)
        self.assertTrue(valid, f"Session validation failed: {error}")
        
        # Logout
        success = logout(token)
        self.assertTrue(success, "Logout failed")
        
        # Verify session is invalid after logout
        valid, session_data, error = validate_session(token)
        self.assertFalse(valid, "Session should be invalid after logout")
    
    def test_04_session_expiration(self):
        """Test session expiration"""
        # Create session
        success, token, error = authenticate("testuser", "testPass123!")
        self.assertTrue(success, f"Session creation failed: {error}")
        
        # Get session and modify expiration
        from backend.models.entities import Session
        session = Session.get_by_session_id(token)
        self.assertIsNotNone(session, "Session not found")
        
        # Set expiration to past
        session.expires_at = datetime.utcnow() - timedelta(hours=1)
        session.save()
        
        # Verify session is invalid
        valid, session_data, error = validate_session(token)
        self.assertFalse(valid, "Session should be invalid after expiration")
        self.assertIn("expired", error.lower())
    
    def test_05_brute_force_protection(self):
        """Test brute force protection"""
        # Attempt multiple failed logins
        for _ in range(5):
            success, token, error = authenticate("testuser", "wrongpass")
            self.assertFalse(success, "Login should fail with wrong password")
        
        # Verify account is locked
        success, token, error = authenticate("testuser", "testPass123!")
        self.assertFalse(success, "Account should be locked after multiple failures")
        self.assertIn("locked", error.lower())
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        # Delete test users
        from backend.models.entities import User
        for username, _, _ in cls.test_users:
            user = User.get_by_username(username)
            if user:
                user.deactivate()
                logger.info(f"Deactivated test user {username}")

if __name__ == '__main__':
    unittest.main(verbosity=2)
