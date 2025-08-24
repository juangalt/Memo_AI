"""
Authentication Service for Memo AI Coach
Handles admin authentication and session management
"""

import os
import bcrypt
import secrets
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import yaml
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthService:
    """Service for admin authentication and session management"""
    
    def __init__(self, config_path: str = "../config"):
        """
        Initialize authentication service
        
        Args:
            config_path: Path to configuration directory
        """
        self.config_path = config_path
        self.auth_config = None
        self.admin_sessions = {}  # In-memory session storage for development
        self.login_attempts = {}  # Track login attempts for brute force protection
        
        # Load authentication configuration
        self._load_auth_config()
    
    def _load_auth_config(self):
        """Load authentication configuration from YAML"""
        try:
            with open(f"{self.config_path}/auth.yaml", 'r') as f:
                self.auth_config = yaml.safe_load(f)
            logger.info("Authentication configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load authentication configuration: {e}")
            raise
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def _generate_session_token(self) -> str:
        """Generate secure session token"""
        try:
            token_length = self.auth_config.get('session_management', {}).get('session_token_length', 32)
            alphabet = self.auth_config.get('session_management', {}).get('session_token_alphabet', 
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
            return ''.join(secrets.choice(alphabet) for _ in range(token_length))
        except Exception as e:
            logger.error(f"Session token generation failed: {e}")
            return secrets.token_urlsafe(32)
    
    def _is_brute_force_attempt(self, username: str) -> bool:
        """Check if login attempt is part of brute force attack"""
        try:
            brute_force_config = self.auth_config.get('authentication_methods', {}).get('admin_authentication', {})
            threshold = brute_force_config.get('brute_force_threshold', 3)
            window = brute_force_config.get('brute_force_window', 300)
            
            if username not in self.login_attempts:
                return False
            
            attempts = self.login_attempts[username]
            now = datetime.utcnow()
            
            # Remove old attempts outside the window
            attempts = [attempt for attempt in attempts if (now - attempt).total_seconds() < window]
            self.login_attempts[username] = attempts
            
            return len(attempts) >= threshold
            
        except Exception as e:
            logger.error(f"Brute force check failed: {e}")
            return False
    
    def _record_login_attempt(self, username: str, success: bool):
        """Record login attempt for brute force detection"""
        try:
            if username not in self.login_attempts:
                self.login_attempts[username] = []
            
            if not success:
                self.login_attempts[username].append(datetime.utcnow())
            else:
                # Clear attempts on successful login
                self.login_attempts[username] = []
                
        except Exception as e:
            logger.error(f"Failed to record login attempt: {e}")
    
    def authenticate_admin(self, username: str, password: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Authenticate admin user
        
        Args:
            username: Admin username
            password: Admin password
            
        Returns:
            Tuple of (success, session_token, error_message)
        """
        try:
            # Check brute force protection
            if self._is_brute_force_attempt(username):
                logger.warning(f"Brute force attempt detected for user: {username}")
                return False, None, "Account temporarily locked due to too many failed attempts"
            
            # Get admin credentials from environment or config
            expected_username = "admin"
            expected_password = os.getenv("ADMIN_PASSWORD", "admin123")
            
            # Verify credentials
            if username == expected_username and password == expected_password:
                # Generate session token
                session_token = self._generate_session_token()
                
                # Create session
                session_data = {
                    'username': username,
                    'is_admin': True,
                    'created_at': datetime.utcnow(),
                    'expires_at': datetime.utcnow() + timedelta(hours=1),
                    'permissions': ['system_configuration', 'user_management', 'debug_access', 'backup_management', 'log_access']
                }
                
                self.admin_sessions[session_token] = session_data
                
                # Record successful login
                self._record_login_attempt(username, True)
                
                logger.info(f"Admin authentication successful for user: {username}")
                return True, session_token, None
            else:
                # Record failed login
                self._record_login_attempt(username, False)
                
                logger.warning(f"Admin authentication failed for user: {username}")
                return False, None, "Invalid credentials"
                
        except Exception as e:
            logger.error(f"Admin authentication failed: {e}")
            return False, None, f"Authentication error: {str(e)}"
    
    def validate_session(self, session_token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validate admin session
        
        Args:
            session_token: Session token to validate
            
        Returns:
            Tuple of (valid, session_data, error_message)
        """
        try:
            if session_token not in self.admin_sessions:
                return False, None, "Invalid session token"
            
            session_data = self.admin_sessions[session_token]
            
            # Check if session has expired
            if datetime.utcnow() > session_data['expires_at']:
                # Remove expired session
                del self.admin_sessions[session_token]
                return False, None, "Session expired"
            
            # Extend session if needed
            if (session_data['expires_at'] - datetime.utcnow()).total_seconds() < 300:  # 5 minutes
                session_data['expires_at'] = datetime.utcnow() + timedelta(hours=1)
                self.admin_sessions[session_token] = session_data
            
            return True, session_data, None
            
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            return False, None, f"Session validation error: {str(e)}"
    
    def logout_admin(self, session_token: str) -> bool:
        """
        Logout admin user
        
        Args:
            session_token: Session token to invalidate
            
        Returns:
            True if logout successful
        """
        try:
            if session_token in self.admin_sessions:
                del self.admin_sessions[session_token]
                logger.info("Admin session terminated")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Admin logout failed: {e}")
            return False
    
    def get_active_sessions(self) -> Dict[str, Any]:
        """
        Get information about active admin sessions
        
        Returns:
            Dictionary with session information
        """
        try:
            active_sessions = {}
            now = datetime.utcnow()
            
            for token, session_data in self.admin_sessions.items():
                if session_data['expires_at'] > now:
                    active_sessions[token[:8] + "..."] = {
                        'username': session_data['username'],
                        'created_at': session_data['created_at'].isoformat(),
                        'expires_at': session_data['expires_at'].isoformat(),
                        'permissions': session_data['permissions']
                    }
            
            return {
                'total_sessions': len(active_sessions),
                'sessions': active_sessions
            }
            
        except Exception as e:
            logger.error(f"Failed to get active sessions: {e}")
            return {'total_sessions': 0, 'sessions': {}}
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check authentication service health
        
        Returns:
            Health status information
        """
        try:
            return {
                "status": "healthy",
                "service": "authentication",
                "config_loaded": self.auth_config is not None,
                "active_sessions": len(self.admin_sessions),
                "brute_force_protection": True,
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Authentication health check failed: {e}")
            return {
                "status": "unhealthy",
                "service": "authentication",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }

# Global auth service instance
auth_service = None

def get_auth_service() -> AuthService:
    """Get the global authentication service instance"""
    global auth_service
    if auth_service is None:
        auth_service = AuthService()
    return auth_service

def authenticate_admin_user(username: str, password: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Authenticate admin user
    
    Args:
        username: Admin username
        password: Admin password
        
    Returns:
        Tuple of (success, session_token, error_message)
    """
    service = get_auth_service()
    return service.authenticate_admin(username, password)

def validate_admin_session(session_token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Validate admin session
    
    Args:
        session_token: Session token to validate
        
    Returns:
        Tuple of (valid, session_data, error_message)
    """
    service = get_auth_service()
    return service.validate_session(session_token)
