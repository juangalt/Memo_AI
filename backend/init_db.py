"""
Database initialization script for Memo AI Coach
Creates the complete database schema as defined in 03_Data_Model.md
"""

import sqlite3
import os
import logging
from datetime import datetime, timedelta

# Get logger for this module
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database with schema from 03_Data_Model.md"""
    try:
        # Get database path from environment or use default
        db_path = os.getenv('DATABASE_URL', 'sqlite:///data/memoai.db').replace('sqlite:///', '')
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        logger.info(f"Initializing database at: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table
        logger.info("Creating users table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Create sessions table
        logger.info("Creating sessions table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                user_id INTEGER REFERENCES users(id),
                is_admin BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME NOT NULL,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Create submissions table
        logger.info("Creating submissions table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text_content TEXT NOT NULL,
                session_id TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
            )
        ''')
        
        # Create evaluations table
        logger.info("Creating evaluations table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id INTEGER NOT NULL,
                overall_score DECIMAL(5,2),
                strengths TEXT NOT NULL,
                opportunities TEXT NOT NULL,
                rubric_scores TEXT NOT NULL,
                segment_feedback TEXT NOT NULL,
                llm_provider TEXT NOT NULL DEFAULT 'claude',
                llm_model TEXT NOT NULL,
                raw_prompt TEXT,
                raw_response TEXT,
                debug_enabled BOOLEAN DEFAULT FALSE,
                processing_time DECIMAL(6,3),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE
            )
        ''')
        
        # Create schema migrations table
        logger.info("Creating schema migrations table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT UNIQUE NOT NULL,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        ''')
        
        # Create indexes for performance
        logger.info("Creating performance indexes...")
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username, is_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_admin ON users(is_admin, is_active)')  # Index for admin lookup
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_active ON sessions(user_id, is_active, expires_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_admin ON sessions(is_admin, is_active)')  # Index for admin sessions
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_submissions_session_date ON submissions(session_id, created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_evaluations_submission ON evaluations(submission_id, created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_active ON sessions(session_id, is_active, expires_at)')
        
        # Configure WAL mode for concurrent access
        logger.info("Configuring WAL mode...")
        cursor.execute('PRAGMA journal_mode = WAL')
        cursor.execute('PRAGMA synchronous = NORMAL')
        cursor.execute('PRAGMA cache_size = 10000')
        cursor.execute('PRAGMA temp_store = memory')
        
        # Insert initial migration record
        cursor.execute('''
            INSERT OR IGNORE INTO schema_migrations (version, description)
            VALUES (?, ?)
        ''', ('001_initial', 'Initial database schema for Memo AI Coach'))
        
        # Create default admin user if not exists
        logger.info("Creating default admin user...")
        admin_password = os.getenv('ADMIN_PASSWORD')
        if not admin_password:
            logger.warning("ADMIN_PASSWORD not set, using default password. THIS IS NOT SECURE!")
            admin_password = 'admin123'  # Default password with better complexity
        
        try:
            import bcrypt
            # Use higher salt rounds for better security
            salt_rounds = 12
            password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt(rounds=salt_rounds))
            
            # Check if admin user exists
            cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
            admin_exists = cursor.fetchone()
            
            if not admin_exists:
                logger.info("Creating new admin user...")
                cursor.execute('''
                    INSERT INTO users (username, password_hash, is_admin, is_active)
                    VALUES (?, ?, ?, ?)
                ''', ('admin', password_hash.decode('utf-8'), True, True))
            else:
                # Update admin password if ADMIN_PASSWORD is explicitly set
                if os.getenv('ADMIN_PASSWORD'):
                    logger.info("Updating admin password...")
                    cursor.execute('''
                        UPDATE users 
                        SET password_hash = ?, is_admin = TRUE, is_active = TRUE
                        WHERE username = ?
                    ''', (password_hash.decode('utf-8'), 'admin'))
        except Exception as e:
            logger.error(f"Failed to create/update admin user: {e}")
            raise
        
        # Add migration record for auth changes
        cursor.execute('''
            INSERT OR IGNORE INTO schema_migrations (version, description)
            VALUES (?, ?)
        ''', ('002_auth_unified', 'Unified authentication system with admin flag'))
        
        conn.commit()
        conn.close()
        
        logger.info("Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def verify_database():
    """Verify database schema and connectivity"""
    try:
        db_path = os.getenv('DATABASE_URL', 'sqlite:///data/memoai.db').replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if all tables exist
        tables = ['users', 'sessions', 'submissions', 'evaluations', 'schema_migrations']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                logger.error(f"Table {table} not found")
                return False
        
        # Check if required indexes exist
        required_indexes = [
            'idx_users_username',
            'idx_users_admin',
            'idx_sessions_user_active',
            'idx_sessions_admin',
            'idx_submissions_session_date',
            'idx_evaluations_submission',
            'idx_sessions_active'
        ]
        for idx in required_indexes:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND name='{idx}'")
            if not cursor.fetchone():
                logger.error(f"Required index {idx} not found")
                return False
        
        # Check WAL mode
        cursor.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0]
        if journal_mode != 'wal':
            logger.warning(f"WAL mode not enabled: {journal_mode}")
        
        # Check database integrity
        cursor.execute("PRAGMA integrity_check")
        integrity_check = cursor.fetchone()[0]
        if integrity_check != 'ok':
            logger.error(f"Database integrity check failed: {integrity_check}")
            return False
            
        # Check admin user exists and is properly configured
        cursor.execute('''
            SELECT username, is_admin, is_active 
            FROM users 
            WHERE username = 'admin'
        ''')
        admin_user = cursor.fetchone()
        if not admin_user:
            logger.error("Admin user not found")
            return False
        elif not admin_user[1]:  # is_admin flag
            logger.error("Admin user exists but is_admin flag is not set")
            return False
        elif not admin_user[2]:  # is_active flag
            logger.error("Admin user exists but is not active")
            return False
            
        # Check schema migration version
        cursor.execute('''
            SELECT version FROM schema_migrations 
            WHERE version = '002_auth_unified'
        ''')
        if not cursor.fetchone():
            logger.warning("Schema migration '002_auth_unified' not found")
        
        conn.close()
        logger.info("Database verification completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database verification failed: {e}")
        return False

if __name__ == "__main__":
    print("Initializing Memo AI Coach database...")
    
    if init_database():
        print("✓ Database initialized successfully")
        
        if verify_database():
            print("✓ Database verification completed")
        else:
            print("✗ Database verification failed")
            exit(1)
    else:
        print("✗ Database initialization failed")
        exit(1)
