"""
Database entity models for Memo AI Coach
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from .database import db_manager

logger = logging.getLogger(__name__)

class User:
    """User entity model"""
    
    def __init__(self, id: Optional[int] = None, username: str = "", password_hash: str = "", 
                 is_admin: bool = False, created_at: Optional[datetime] = None, is_active: bool = True):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.created_at = created_at or datetime.utcnow()
        self.is_active = is_active
    
    @classmethod
    def create(cls, username: str, password_hash: str, is_admin: bool = False) -> 'User':
        """Create a new user"""
        try:
            query = """
                INSERT INTO users (username, password_hash, is_admin, created_at, is_active)
                VALUES (?, ?, ?, ?, ?)
            """
            user_id = db_manager.execute_insert(query, (username, password_hash, is_admin, datetime.utcnow(), True))
            return cls.get_by_id(user_id)
        except sqlite3.IntegrityError as e:
            logger.error(f"User creation failed - duplicate username: {e}")
            raise ValueError(f"Username '{username}' already exists")
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            raise
    
    @classmethod
    def get_by_id(cls, user_id: int) -> Optional['User']:
        """Get user by ID"""
        try:
            query = "SELECT * FROM users WHERE id = ? AND is_active = TRUE"
            result = db_manager.execute_query(query, (user_id,))
            if result:
                row = result[0]
                return cls(
                    id=row['id'],
                    username=row['username'],
                    password_hash=row['password_hash'],
                    is_admin=bool(row['is_admin']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    is_active=bool(row['is_active'])
                )
            return None
        except Exception as e:
            logger.error(f"User retrieval failed: {e}")
            raise
    
    @classmethod
    def get_by_username(cls, username: str) -> Optional['User']:
        """Get user by username"""
        try:
            query = "SELECT * FROM users WHERE username = ?"
            result = db_manager.execute_query(query, (username,))
            if result:
                row = result[0]
                return cls(
                    id=row['id'],
                    username=row['username'],
                    password_hash=row['password_hash'],
                    is_admin=bool(row['is_admin']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    is_active=bool(row['is_active'])
                )
            return None
        except Exception as e:
            logger.error(f"User retrieval failed: {e}")
            raise

    @classmethod
    def get_all(cls) -> List['User']:
        """Get all users"""
        try:
            query = "SELECT * FROM users WHERE is_active = TRUE ORDER BY created_at DESC"
            result = db_manager.execute_query(query)
            users = []
            for row in result:
                users.append(cls(
                    id=row['id'],
                    username=row['username'],
                    password_hash=row['password_hash'],
                    is_admin=bool(row['is_admin']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    is_active=bool(row['is_active'])
                ))
            return users
        except Exception as e:
            logger.error(f"User retrieval failed: {e}")
            raise

    def deactivate(self) -> bool:
        """Deactivate user"""
        try:
            query = "DELETE FROM users WHERE id = ?"
            affected = db_manager.execute_update(query, (self.id,))
            if affected > 0:
                self.is_active = False
                return True
            return False
        except Exception as e:
            logger.error(f"User deactivation failed: {e}")
            raise

class Session:
    """Session entity model"""
    
    def __init__(self, id: Optional[int] = None, session_id: str = "", user_id: Optional[int] = None,
                 is_admin: bool = False, created_at: Optional[datetime] = None, 
                 expires_at: Optional[datetime] = None, is_active: bool = True):
        self.id = id
        self.session_id = session_id
        self.user_id = user_id
        self.is_admin = is_admin
        self.created_at = created_at or datetime.utcnow()
        self.expires_at = expires_at or (datetime.utcnow() + timedelta(seconds=3600))  # Default 1 hour
        self.is_active = is_active
    
    @classmethod
    def create(cls, session_id: str, user_id: Optional[int] = None, is_admin: bool = False) -> 'Session':
        """Create a new session"""
        try:
            # Get session timeout from configuration service
            from services.config_service import ConfigService
            config_service = ConfigService()
            auth_config = config_service.get_auth_config()
            
            # Default to 1 hour if configuration is not available
            session_timeout_seconds = 3600
            if auth_config and 'session_management' in auth_config:
                session_timeout_seconds = auth_config['session_management'].get('session_timeout', 3600)
            

            expires_at = datetime.utcnow() + timedelta(seconds=session_timeout_seconds)
            query = """
                INSERT INTO sessions (session_id, user_id, is_admin, created_at, expires_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            session_db_id = db_manager.execute_insert(query, (
                session_id, user_id, is_admin, datetime.utcnow(), expires_at, True
            ))
            return cls.get_by_session_id(session_id)
        except Exception as e:
            logger.error(f"Session creation failed: {e}")
            raise
    
    @classmethod
    def get_by_session_id(cls, session_id: str) -> Optional['Session']:
        """Get session by session ID"""
        try:
            query = """
                SELECT * FROM sessions 
                WHERE session_id = ? AND is_active = TRUE AND expires_at > ?
            """
            result = db_manager.execute_query(query, (session_id, datetime.utcnow()))
            if result:
                row = result[0]
                return cls(
                    id=row['id'],
                    session_id=row['session_id'],
                    user_id=row['user_id'],
                    is_admin=bool(row['is_admin']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    expires_at=datetime.fromisoformat(row['expires_at']),
                    is_active=bool(row['is_active'])
                )
            return None
        except Exception as e:
            logger.error(f"Session retrieval failed: {e}")
            raise
    
    def deactivate(self) -> bool:
        """Deactivate session"""
        try:
            query = "UPDATE sessions SET is_active = FALSE WHERE session_id = ?"
            affected = db_manager.execute_update(query, (self.session_id,))
            if affected > 0:
                self.is_active = False
                return True
            return False
        except Exception as e:
            logger.error(f"Session deactivation failed: {e}")
            raise

    @classmethod
    def get_by_user_id(cls, user_id: int) -> List['Session']:
        """Get all active sessions for a user by user ID"""
        try:
            query = """
                SELECT * FROM sessions 
                WHERE user_id = ? AND is_active = TRUE AND expires_at > ?
                ORDER BY created_at DESC
            """
            result = db_manager.execute_query(query, (user_id, datetime.utcnow()))
            sessions = []
            for row in result:
                sessions.append(cls(
                    id=row['id'],
                    session_id=row['session_id'],
                    user_id=row['user_id'],
                    is_admin=bool(row['is_admin']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    expires_at=datetime.fromisoformat(row['expires_at']),
                    is_active=bool(row['is_active'])
                ))
            return sessions
        except Exception as e:
            logger.error(f"Session retrieval failed: {e}")
            raise
            
    @classmethod
    def get_active_sessions(cls) -> List['Session']:
        """Get all active sessions"""
        try:
            query = """
                SELECT * FROM sessions 
                WHERE is_active = TRUE AND expires_at > ?
                ORDER BY created_at DESC
            """
            result = db_manager.execute_query(query, (datetime.utcnow(),))
            sessions = []
            for row in result:
                sessions.append(cls(
                    id=row['id'],
                    session_id=row['session_id'],
                    user_id=row['user_id'],
                    is_admin=bool(row['is_admin']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    expires_at=datetime.fromisoformat(row['expires_at']),
                    is_active=bool(row['is_active'])
                ))
            return sessions
        except Exception as e:
            logger.error(f"Session retrieval failed: {e}")
            raise

class Submission:
    """Submission entity model"""
    
    def __init__(self, id: Optional[int] = None, text_content: str = "", session_id: str = "",
                 created_at: Optional[datetime] = None):
        self.id = id
        self.text_content = text_content
        self.session_id = session_id
        self.created_at = created_at or datetime.utcnow()
    
    @classmethod
    def create(cls, text_content: str, session_id: str) -> 'Submission':
        """Create a new submission"""
        try:
            query = """
                INSERT INTO submissions (text_content, session_id, created_at)
                VALUES (?, ?, ?)
            """
            submission_id = db_manager.execute_insert(query, (text_content, session_id, datetime.utcnow()))
            return cls.get_by_id(submission_id)
        except Exception as e:
            logger.error(f"Submission creation failed: {e}")
            raise
    
    @classmethod
    def get_by_id(cls, submission_id: int) -> Optional['Submission']:
        """Get submission by ID"""
        try:
            query = "SELECT * FROM submissions WHERE id = ?"
            result = db_manager.execute_query(query, (submission_id,))
            if result:
                row = result[0]
                return cls(
                    id=row['id'],
                    text_content=row['text_content'],
                    session_id=row['session_id'],
                    created_at=datetime.fromisoformat(row['created_at'])
                )
            return None
        except Exception as e:
            logger.error(f"Submission retrieval failed: {e}")
            raise
    
    @classmethod
    def get_by_session(cls, session_id: str) -> List['Submission']:
        """Get all submissions for a session"""
        try:
            query = "SELECT * FROM submissions WHERE session_id = ? ORDER BY created_at DESC"
            results = db_manager.execute_query(query, (session_id,))
            submissions = []
            for row in results:
                submissions.append(cls(
                    id=row['id'],
                    text_content=row['text_content'],
                    session_id=row['session_id'],
                    created_at=datetime.fromisoformat(row['created_at'])
                ))
            return submissions
        except Exception as e:
            logger.error(f"Submissions retrieval failed: {e}")
            raise

class Evaluation:
    """Evaluation entity model"""
    
    def __init__(self, id: Optional[int] = None, submission_id: int = 0, overall_score: Optional[float] = None,
                 strengths: str = "", opportunities: str = "", rubric_scores: str = "",
                 segment_feedback: str = "", llm_provider: str = "claude", llm_model: str = "",
                 raw_prompt: Optional[str] = None, raw_response: Optional[str] = None,
                 debug_enabled: bool = False, processing_time: Optional[float] = None,
                 created_at: Optional[datetime] = None):
        self.id = id
        self.submission_id = submission_id
        self.overall_score = overall_score
        self.strengths = strengths
        self.opportunities = opportunities
        self.rubric_scores = rubric_scores
        self.segment_feedback = segment_feedback
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.raw_prompt = raw_prompt
        self.raw_response = raw_response
        self.debug_enabled = debug_enabled
        self.processing_time = processing_time
        self.created_at = created_at or datetime.utcnow()
    
    @classmethod
    def create(cls, submission_id: int, overall_score: float, strengths: str, opportunities: str,
               rubric_scores: str, segment_feedback: str, llm_provider: str = "claude",
               llm_model: str = "", raw_prompt: Optional[str] = None, raw_response: Optional[str] = None,
               debug_enabled: bool = False, processing_time: Optional[float] = None) -> 'Evaluation':
        """Create a new evaluation"""
        try:
            query = """
                INSERT INTO evaluations (
                    submission_id, overall_score, strengths, opportunities, rubric_scores,
                    segment_feedback, llm_provider, llm_model, raw_prompt, raw_response,
                    debug_enabled, processing_time, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            evaluation_id = db_manager.execute_insert(query, (
                submission_id, overall_score, strengths, opportunities, rubric_scores,
                segment_feedback, llm_provider, llm_model, raw_prompt, raw_response,
                debug_enabled, processing_time, datetime.utcnow()
            ))
            return cls.get_by_id(evaluation_id)
        except Exception as e:
            logger.error(f"Evaluation creation failed: {e}")
            raise
    
    @classmethod
    def get_by_id(cls, evaluation_id: int) -> Optional['Evaluation']:
        """Get evaluation by ID"""
        try:
            query = "SELECT * FROM evaluations WHERE id = ?"
            result = db_manager.execute_query(query, (evaluation_id,))
            if result:
                row = result[0]
                return cls(
                    id=row['id'],
                    submission_id=row['submission_id'],
                    overall_score=row['overall_score'],
                    strengths=row['strengths'],
                    opportunities=row['opportunities'],
                    rubric_scores=row['rubric_scores'],
                    segment_feedback=row['segment_feedback'],
                    llm_provider=row['llm_provider'],
                    llm_model=row['llm_model'],
                    raw_prompt=row['raw_prompt'],
                    raw_response=row['raw_response'],
                    debug_enabled=bool(row['debug_enabled']),
                    processing_time=row['processing_time'],
                    created_at=datetime.fromisoformat(row['created_at'])
                )
            return None
        except Exception as e:
            logger.error(f"Evaluation retrieval failed: {e}")
            raise
    
    @classmethod
    def get_by_submission(cls, submission_id: int) -> Optional['Evaluation']:
        """Get evaluation by submission ID"""
        try:
            query = "SELECT * FROM evaluations WHERE submission_id = ? ORDER BY created_at DESC LIMIT 1"
            result = db_manager.execute_query(query, (submission_id,))
            if result:
                row = result[0]
                return cls(
                    id=row['id'],
                    submission_id=row['submission_id'],
                    overall_score=row['overall_score'],
                    strengths=row['strengths'],
                    opportunities=row['opportunities'],
                    rubric_scores=row['rubric_scores'],
                    segment_feedback=row['segment_feedback'],
                    llm_provider=row['llm_provider'],
                    llm_model=row['llm_model'],
                    raw_prompt=row['raw_prompt'],
                    raw_response=row['raw_response'],
                    debug_enabled=bool(row['debug_enabled']),
                    processing_time=row['processing_time'],
                    created_at=datetime.fromisoformat(row['created_at'])
                )
            return None
        except Exception as e:
            logger.error(f"Evaluation retrieval failed: {e}")
            raise
