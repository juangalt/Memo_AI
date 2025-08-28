"""
Database connection and management for Memo AI Coach
"""

import sqlite3
import os
import logging
from contextlib import contextmanager
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection manager with connection pooling and error handling"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager"""
        if db_path is None:
            # Default to data directory
            db_path = os.getenv('DATABASE_URL', 'sqlite:///data/memoai.db').replace('sqlite:///', '')
            # Ensure we're using absolute path from project root
            if not os.path.isabs(db_path):
                db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), db_path)
        
        self.db_path = db_path
        self._connection = None
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        logger.info(f"Database manager initialized with path: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context management"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable row factory for named access
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def health_check(self) -> dict:
        """Check database health and connectivity"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if database file exists and is accessible
                if not os.path.exists(self.db_path):
                    return {"status": "unhealthy", "error": "Database file not found"}
                
                # Check if tables exist
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                required_tables = ['users', 'sessions', 'submissions', 'evaluations', 'schema_migrations']
                
                missing_tables = [table for table in required_tables if table not in tables]
                if missing_tables:
                    return {"status": "unhealthy", "error": f"Missing tables: {missing_tables}"}
                
                # Check WAL mode
                cursor.execute("PRAGMA journal_mode")
                journal_mode = cursor.fetchone()[0]
                
                # Check database integrity
                cursor.execute("PRAGMA integrity_check")
                integrity_check = cursor.fetchone()[0]
                
                if integrity_check != 'ok':
                    return {"status": "unhealthy", "error": f"Integrity check failed: {integrity_check}"}
                
                # Test write operation
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                
                return {
                    "status": "healthy",
                    "tables": tables,
                    "journal_mode": journal_mode,
                    "integrity": integrity_check,
                    "user_count": user_count,
                    "db_path": self.db_path
                }
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """Execute a query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an update query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an insert query and return the last row ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

# Global database manager instance
db_manager = DatabaseManager()
