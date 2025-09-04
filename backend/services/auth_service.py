"""
Authentication Service for Memo AI Coach
Handles admin authentication and session management
"""

import os
import bcrypt
import secrets
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
import yaml
import hashlib
from .path_utils import resolve_config_dir_with_fallback

# Get logger for this module
logger = logging.getLogger(__name__)

class AuthService:
    """Service for unified user and admin authentication"""
    
    def __init__(self, config_path: str = None, config_service=None):
        """Initialize auth service with automatic path detection"""
        if config_path is None:
            config_path = resolve_config_dir_with_fallback()
        
        self.config_path = config_path
        self.config_service = config_service
        self.auth_config = None
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
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Unified authentication for both users and admins
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Tuple of (success, session_token, error_message)
        """
        try:
            # Check brute force protection
            if self._is_brute_force_attempt(username):
                logger.warning(f"Brute force attempt detected for user: {username}")
                return False, None, "Account temporarily locked due to too many failed attempts"
            
            # Import User model here to avoid circular imports
            from models.entities import User
            
            # Get user from database
            user = User.get_by_username(username)
            if not user:
                self._record_login_attempt(username, False)
                return False, None, "Invalid credentials"
            
            if not user.is_active:
                return False, None, "Account is deactivated"
            
            # Verify password
            if not self._verify_password(password, user.password_hash):
                self._record_login_attempt(username, False)
                return False, None, "Invalid credentials"
            
            # Generate session token
            session_token = self._generate_session_token()
            
            # Create session in database
            from models.entities import Session
            session = Session.create(
                session_id=session_token,
                user_id=user.id,
                is_admin=user.is_admin,
                config_service=self.config_service
            )
            
            # Record successful login
            self._record_login_attempt(username, True)
            
            logger.info(f"Authentication successful for user: {username} (admin: {user.is_admin})")
            return True, session_token, None
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False, None, f"Authentication error: {str(e)}"
    
    def validate_session(self, session_token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validate session for any user type
        
        Args:
            session_token: Session token to validate
            
        Returns:
            Tuple of (valid, session_data, error_message)
        """
        try:
            # Import Session model here to avoid circular imports
            from models.entities import Session
            
            # Get session from database
            session = Session.get_by_session_id(session_token)
            if not session:
                return False, None, "Invalid session token"
            
            if not session.is_active:
                return False, None, "Session is inactive"
            
            # Check if session has expired
            if datetime.utcnow() > session.expires_at:
                # Deactivate expired session
                session.deactivate()
                return False, None, "Session expired"
            
            # Get user information
            from models.entities import User
            user = User.get_by_id(session.user_id) if session.user_id else None
            if not user or not user.is_active:
                session.deactivate()
                return False, None, "User account is inactive"
            
            session_data = {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'username': user.username,
                'is_admin': session.is_admin,
                'created_at': session.created_at,
                'expires_at': session.expires_at,
                'is_active': session.is_active,
                'permissions': [
                    'system_configuration',
                    'user_management',
                    'debug_access',
                    'backup_management',
                    'log_access'
                ] if session.is_admin else []
            }
            
            return True, session_data, None
            
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            return False, None, f"Session validation error: {str(e)}"
    
    def logout(self, session_token: str) -> bool:
        """
        Logout any user type
        
        Args:
            session_token: Session token to invalidate
            
        Returns:
            True if logout successful
        """
        try:
            # Import Session model here to avoid circular imports
            from models.entities import Session
            
            # Get session from database
            session = Session.get_by_session_id(session_token)
            if session and session.is_active:
                session.deactivate()
                logger.info(f"Session terminated: {session_token[:8]}...")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False
    
    def get_active_sessions(self) -> Dict[str, Any]:
        """
        Get information about all active sessions
        
        Returns:
            Dictionary with session information
        """
        try:
            # Import Session model here to avoid circular imports
            from models.entities import Session, User
            
            # Get all active sessions
            active_sessions = {}
            now = datetime.utcnow()
            
            sessions = Session.get_active_sessions()
            for session in sessions:
                if session.expires_at > now:
                    user = User.get_by_id(session.user_id) if session.user_id else None
                    if user and user.is_active:
                        active_sessions[session.session_id[:8] + "..."] = {
                            'username': user.username,
                            'is_admin': session.is_admin,
                            'created_at': session.created_at.isoformat(),
                            'expires_at': session.expires_at.isoformat(),
                            'permissions': [
                                'system_configuration',
                                'user_management',
                                'debug_access',
                                'backup_management',
                                'log_access'
                            ] if session.is_admin else []
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
            # Check if auth config is loaded
            if not self.auth_config:
                return {
                    "status": "unhealthy",
                    "error": "Authentication configuration not loaded"
                }
            
            # Check if required config sections exist
            required_sections = ["session_management", "authentication_methods"]
            missing_sections = [section for section in required_sections if section not in self.auth_config]
            if missing_sections:
                return {
                    "status": "unhealthy",
                    "error": f"Missing required configuration sections: {missing_sections}"
                }
            
            # Get active sessions count
            from models.entities import Session
            active_sessions = len(Session.get_active_sessions())
            
            return {
                "status": "healthy",
                "service": "authentication",
                "config_loaded": True,
                "active_sessions": active_sessions,
                "brute_force_protection": True,
                "session_expiry_hours": self.auth_config["session_management"].get("session_expiry_hours", 24),
                "session_token_length": self.auth_config["session_management"].get("session_token_length", 32),
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Auth health check failed: {e}")
            return {
                "status": "unhealthy",
                "service": "authentication",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }

    def create_user(self, username: str, password: str, is_admin: bool = False) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Create new user account (admin-only function)
        
        Args:
            username: Username for new user
            password: Password for new user
            
        Returns:
            Tuple of (success, user_id, error_message)
        """
        try:
            # Import User model here to avoid circular imports
            from models.entities import User
            
            # Validate input
            if not username or len(username.strip()) < 3:
                return False, None, "Username must be at least 3 characters long"
            
            # Password length validation temporarily disabled
            # if not password or len(password) < 8:
            #     return False, None, "Password must be at least 8 characters long"
            
            # Check if user already exists
            existing_user = User.get_by_username(username)
            if existing_user:
                return False, None, f"Username '{username}' already exists"
            
            # Hash password
            password_hash = self._hash_password(password)
            
            # Create user
            user = User.create(username=username, password_hash=password_hash, is_admin=is_admin)
            
            logger.info(f"User created successfully: {username} (admin: {is_admin})")
            return True, str(user.id), None
            
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            return False, None, f"User creation error: {str(e)}"

    def list_users(self) -> List[Dict[str, Any]]:
        """
        List all users (admin-only function)
        
        Returns:
            List of user information (without passwords)
        """
        try:
            # Import User model here to avoid circular imports
            from models.entities import User
            
            # Get all users from database
            users = User.get_all()
            
            user_list = []
            for user in users:
                user_list.append({
                    'id': user.id,
                    'username': user.username,
                    'is_admin': user.is_admin,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat()
                })
            
            return user_list
            
        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            return []

    def delete_user(self, username: str) -> bool:
        """
        Delete user account (admin-only function)
        
        Args:
            username: Username to delete
            
        Returns:
            True if deletion successful
        """
        try:
            # Import User model here to avoid circular imports
            from models.entities import User, Session
            
            # Get user
            user = User.get_by_username(username)
            if not user:
                logger.warning(f"Attempted to delete non-existent user: {username}")
                return False
            
            # Deactivate all user sessions
            sessions = Session.get_by_user_id(user.id)
            for session in sessions:
                session.deactivate()
            
            # Deactivate user
            user.deactivate()
            
            logger.info(f"User deleted successfully: {username}")
            return True
            
        except Exception as e:
            logger.error(f"User deletion failed: {e}")
            return False

# Global auth service instance
auth_service = None

def get_auth_service(config_path: str = None, config_service=None) -> AuthService:
    """
    Get the global authentication service instance
    
    Args:
        config_path: Optional path to config directory
        config_service: Optional ConfigService instance to inject
    """
    global auth_service
    if auth_service is None:
        auth_service = AuthService(config_path, config_service)
    elif config_path is not None or config_service is not None:
        # Create new instance with custom config or service
        return AuthService(config_path, config_service)
    return auth_service


