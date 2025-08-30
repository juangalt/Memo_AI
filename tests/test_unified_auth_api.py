"""
Test unified authentication API endpoints for Memo AI Coach
"""

import os
import sys
import unittest
import json
from datetime import datetime
import logging
from fastapi.testclient import TestClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main import app
from backend.services import get_auth_service
from backend.services.auth_service import create_user
from backend.models.entities import User, Session

class TestUnifiedAuthAPI(unittest.TestCase):
    """Test unified authentication API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Initialize test client
        cls.client = TestClient(app)
        
        # Set database path
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'memoai.db')
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
        logger.info(f"Using database path: {db_path}")
        
        # Initialize auth service with test config
        test_config_path = os.path.join(os.path.dirname(__file__), 'test_config')
        logger.info(f"Using test config path: {test_config_path}")
        cls.auth_service = get_auth_service(test_config_path)
        
        # Clean up any existing test users
        cls.test_users = [
            ("testuser", "testPass123!", False),  # Regular user
            ("testadmin", "adminPass123!", True)  # Admin user
        ]
        for username, _, _ in cls.test_users:
            user = User.get_by_username(username)
            if user:
                user.deactivate()
                logger.info(f"Cleaned up existing test user {username}")
        
        # Create test users
        
        for username, password, is_admin in cls.test_users:
            success, user_id, error = create_user(username, password, is_admin)
            if not success:
                logger.error(f"Failed to create test user {username}: {error}")
                raise Exception(f"Test setup failed: {error}")
            logger.info(f"Created test user {username} (admin: {is_admin})")
    
    def test_01_unified_login(self):
        """Test unified login endpoint"""
        # Test regular user login
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testPass123!"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertIn("session_token", data["data"])
        self.assertEqual(data["data"]["username"], "testuser")
        self.assertFalse(data["data"]["is_admin"])
        
        # Test admin user login
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testadmin",
            "password": "adminPass123!"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertIn("session_token", data["data"])
        self.assertEqual(data["data"]["username"], "testadmin")
        self.assertTrue(data["data"]["is_admin"])
        
        # Test invalid credentials
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "wrongpass"
        })
        self.assertEqual(response.status_code, 401)
    
    def test_02_admin_endpoint_access(self):
        """Test admin endpoint access control"""
        # Login as admin
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testadmin",
            "password": "adminPass123!"
        })
        admin_token = response.json()["data"]["session_token"]
        
        # Test admin endpoint with admin token
        response = self.client.get("/api/v1/admin/users", headers={
            "X-Session-Token": admin_token
        })
        self.assertEqual(response.status_code, 200)
        
        # Login as regular user
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testPass123!"
        })
        user_token = response.json()["data"]["session_token"]
        
        # Test admin endpoint with user token
        response = self.client.get("/api/v1/admin/users", headers={
            "X-Session-Token": user_token
        })
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_03_unified_logout(self):
        """Test unified logout endpoint"""
        # Login as user
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testPass123!"
        })
        token = response.json()["data"]["session_token"]
        
        # Test successful logout
        response = self.client.post("/api/v1/auth/logout", headers={
            "X-Session-Token": token
        })
        self.assertEqual(response.status_code, 200)
        
        # Test accessing endpoint with logged out token
        response = self.client.get("/api/v1/admin/users", headers={
            "X-Session-Token": token
        })
        self.assertEqual(response.status_code, 401)  # Unauthorized
    
    def test_04_session_management(self):
        """Test session management endpoints"""
        # Login as user
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testPass123!"
        })
        token = response.json()["data"]["session_token"]
        
        # Validate session
        response = self.client.get("/api/v1/auth/validate", headers={
            "X-Session-Token": token
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["username"], "testuser")
        self.assertFalse(data["is_admin"])
        self.assertIn("permissions", data)
        self.assertEqual(data["permissions"], [])
    
    def test_05_legacy_admin_login(self):
        """Test legacy admin login endpoint redirects to unified auth"""
        # Test admin login through legacy endpoint
        response = self.client.post("/api/v1/admin/login", json={
            "username": "testadmin",
            "password": "adminPass123!"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertIn("session_token", data["data"])
        self.assertEqual(data["data"]["username"], "testadmin")
        self.assertTrue(data["data"]["is_admin"])
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        # Delete test users
        for username, _, _ in cls.test_users:
            user = User.get_by_username(username)
            if user:
                user.deactivate()
                logger.info(f"Deactivated test user {username}")

if __name__ == '__main__':
    unittest.main(verbosity=2)
