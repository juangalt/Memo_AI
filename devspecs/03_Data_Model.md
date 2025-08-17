# 03_Data_Model.md

## 1.0 How to Use This File

1.1 **Audience**
- AI coding agents and human developers.

1.2 **Purpose**
- Defines the data structures, database schema, and data relationships for the Memo AI Coach project.
- Builds directly on the architecture defined in `02_Architecture.md`.

1.3 **Next Steps**
- Review this file before proceeding to `04_API_Definitions.md`.

---

## 2.0 Database Technology Decision

2.1 **Primary Database**
- **Decision**: SQLite for entire project lifecycle
- **Rationale**: Simple, file-based, no external dependencies, excellent performance with WAL mode
- **Scaling Strategy**: SQLite optimizations, connection pooling, and performance tuning for 100+ users

2.2 **ORM/Query Layer**

This section refers to the method used for interacting with the database from the application code. Instead of using a full-featured Object-Relational Mapper (ORM) like SQLAlchemy, the project uses the built-in `sqlite3` library and writes SQL queries directly ("Raw SQL"). This approach is chosen for its simplicity, transparency, and ease of maintenance, especially for an MVP (Minimum Viable Product). It allows developers to have direct control over database operations and schema evolution, and avoids the complexity and overhead of an ORM layer. See Section 10.1 for more details on this decision.
- **Decision**: SQLite3 + Raw SQL (see Section 10.1 for rationale)
- **Rationale**: Aligns with MVP simplicity requirements and maintainability focus
- **Migration Strategy**: Version-based migration scripts (see Section 10.2)

---

## 3.0 Core Data Entities

### 3.1 Users and Authentication
**Based on Requirements**: JWT + Session hybrid authentication system implemented but disabled for MVP (Req 3.4.1). Session-based identification used for MVP, user authentication ready for production.

**Schema**:
```sql
users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,  -- bcrypt hash
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,  -- Server-generated secure random token
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,  -- NULL for anonymous sessions in MVP
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    ip_address TEXT,
    user_agent TEXT
);

auth_configuration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    auth_enabled BOOLEAN DEFAULT FALSE,  -- Toggle for MVP vs Production
    jwt_secret_key TEXT NOT NULL,
    session_timeout INTEGER DEFAULT 3600,  -- seconds
    max_login_attempts INTEGER DEFAULT 5,
    lockout_duration INTEGER DEFAULT 900,  -- seconds
    require_email_verification BOOLEAN DEFAULT FALSE,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT DEFAULT 'system'
);
```

### 3.2 User Submissions
**Based on Requirements**: Authentication system implemented but disabled for MVP (Req 3.4.1). Session-based identification used.

**Schema**:
```sql
submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text_content TEXT NOT NULL,
    submission_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,  -- NULL for anonymous sessions in MVP
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    version INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.3 Evaluations
**Based on Requirements**: Store overall and segment-level evaluation results (Req 2.2.3). Support debug mode with raw prompts/responses (Req 2.5). Progress data integrated with evaluations (Req 2.6).

**Schema**:
```sql
evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    overall_score DECIMAL(5,2),
    strengths TEXT NOT NULL,
    opportunities TEXT NOT NULL,
    rubric_scores JSON NOT NULL,  -- Structure: {"category1": score, "category2": score}
    segment_feedback JSON NOT NULL,  -- Structure: [{"segment": "text", "comment": "feedback", "questions": ["q1", "q2"]}]
    evaluation_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    llm_provider TEXT NOT NULL DEFAULT 'claude',
    llm_model TEXT NOT NULL,
    raw_prompt TEXT,  -- Stored when debug mode enabled
    raw_response TEXT,  -- Stored when debug mode enabled
    debug_enabled BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.4 Configuration Files
**Based on Architecture**: Source YAML files stored in filesystem, database copies for version tracking and admin edits (Arch 5.2.D). Support admin YAML editing (Req 2.4.1).

**Schema**:
```sql
configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_type TEXT NOT NULL CHECK (config_type IN ('rubric', 'frameworks', 'context', 'prompt')),
    config_content TEXT NOT NULL,
    file_path TEXT NOT NULL,  -- Path to source YAML file
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    is_valid BOOLEAN DEFAULT TRUE,  -- Validation status
    validation_errors TEXT,  -- JSON array of validation errors
    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT DEFAULT 'system'  -- Track who made changes
);
```

### 3.5 Chat History
**Based on Requirements**: Chat available after feedback using submission context (Req 2.3). LLM uses submitted text, rubric, frameworks, and context template (Req 2.3.2).

**Schema**:
```sql
chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER NOT NULL REFERENCES evaluations(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES sessions(session_id),  -- Link to user session
    session_start DATETIME DEFAULT CURRENT_TIMESTAMP,
    session_end DATETIME,
    context_snapshot JSON,  -- Snapshot of evaluation context for chat
    is_active BOOLEAN DEFAULT TRUE
);

chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    message_type TEXT NOT NULL CHECK (message_type IN ('user', 'assistant')),
    message_content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    llm_provider TEXT,  -- Track which LLM generated response
    llm_model TEXT
);
```

### 3.6 Progress Tracking (Integrated with Evaluations)
**Based on Architecture**: Progress data automatically calculated during evaluation processing and displayed in separate tab (Arch 5.1.B). Progress tracking populated by evaluation data output (Arch 4.1).

**Note**: Progress metrics are computed from historical evaluations and rubric scores. No separate storage needed - calculated on-demand from evaluations table.

**Computed Metrics**:
- Overall score trends over time
- Rubric category improvements
- Submission frequency patterns
- Strength/opportunity evolution

**Schema** (Optional caching table for performance optimization):
```sql
progress_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    metric_type TEXT NOT NULL,  -- 'overall_trend', 'rubric_category', 'submission_frequency'
    metric_data JSON NOT NULL,  -- Computed chart data
    last_calculated DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME DEFAULT (datetime('now', '+1 hour')),  -- Cache TTL: 1 hour
    UNIQUE(session_id, metric_type)
);
```

---

## 4.0 Data Relationships

4.1 **Key Relationships**
```
users (1) ← (N) sessions (anonymous sessions have user_id = NULL)
sessions (1) ← (N) submissions
submissions (1) ← (N) evaluations
evaluations (1) ← (N) chat_sessions  
chat_sessions (1) ← (N) chat_messages
sessions (1) ← (N) progress_cache (optional performance caching)
configurations (independent - referenced by application logic)
auth_configuration (singleton - single row for system configuration)
```

4.2 **Foreign Key Constraints and Cascading Behaviors**
- `sessions.user_id` → `users.id` (CASCADE DELETE, NULL for anonymous sessions)
- `submissions.session_id` → `sessions.session_id` (CASCADE DELETE)
- `submissions.user_id` → `users.id` (SET NULL)
- `evaluations.submission_id` → `submissions.id` (CASCADE DELETE)
- `chat_sessions.evaluation_id` → `evaluations.id` (CASCADE DELETE)
- `chat_sessions.session_id` → `sessions.session_id` (CASCADE DELETE)
- `chat_messages.chat_session_id` → `chat_sessions.id` (CASCADE DELETE)
- `progress_cache.session_id` → `sessions.session_id` (CASCADE DELETE)

4.3 **Data Integrity Rules**
- User sessions identified by server-generated `session_id` across all tables
- Configuration types restricted to: 'rubric', 'frameworks', 'context', 'prompt' (authentication config stored separately)
- Chat message types restricted to: 'user', 'assistant'
- Only one active configuration per config_type at a time
- Progress cache expires after 1 hour to ensure fresh data
- Single row in auth_configuration table maintains system authentication settings

---

## 5.0 Data Access Patterns

5.1 **Read Patterns**
- **Evaluation History**: `SELECT * FROM evaluations WHERE submission_id IN (SELECT id FROM submissions WHERE session_id = ?) ORDER BY evaluation_timestamp DESC`
- **Progress Data**: Calculate from evaluations grouped by time periods, check cache first: `SELECT * FROM progress_cache WHERE session_id = ? AND metric_type = ? AND expires_at > datetime('now')`
- **Active Configurations**: `SELECT * FROM configurations WHERE is_active = TRUE AND is_valid = TRUE`
- **Chat History**: `SELECT * FROM chat_messages WHERE chat_session_id = ? ORDER BY timestamp`
- **Latest Evaluation**: `SELECT * FROM evaluations WHERE submission_id = ? ORDER BY evaluation_timestamp DESC LIMIT 1`
- **Session Validation**: `SELECT * FROM sessions WHERE session_id = ? AND is_active = TRUE AND expires_at > datetime('now')`

5.2 **Write Patterns**
- **Text Submission**: Single transaction (submissions → evaluations → progress_cache invalidation)
- **Chat Messages**: Single insert with session validation
- **Configuration Updates**: Transaction (validate → update is_active → insert new version)
- **Debug Data**: Conditional writes based on debug_enabled flag

5.3 **Performance Optimizations**
- Index on `(session_id, created_at)` for session-based queries
- Index on `(submission_id, evaluation_timestamp)` for evaluation history
- Progress cache to avoid recalculating expensive metrics (TTL: 1 hour)
- Server-generated session tokens for fast database lookups

---

## 6.0 Data Migration Strategy

6.1 **Schema Evolution**
- **Version-based migrations**: Numbered SQL files (001_initial.sql, 002_add_debug.sql)
- **Migration tracking**: `schema_migrations` table to track applied migrations
- **Rollback capability**: Down migration scripts for each version
- **Development workflow**: Apply migrations on application startup

6.2 **Data Backup and Recovery**
- **SQLite backup**: Use SQLite backup API or file copy during quiet periods
- **WAL checkpoint**: Ensure WAL files are merged before backup
- **Automated backups**: Daily backup script with rotation (keep 7 days)
- **Recovery procedure**: Replace database.db with backup file, restart application
- **Configuration backup**: Backup YAML files alongside database

---

## 7.0 Performance Considerations

7.1 **Indexing Strategy**
```sql
-- Performance indexes optimized for SQLite
CREATE INDEX idx_submissions_session_date ON submissions(session_id, created_at);
CREATE INDEX idx_submissions_user_session ON submissions(user_id, session_id, created_at);
CREATE INDEX idx_evaluations_submission ON evaluations(submission_id, evaluation_timestamp);
CREATE INDEX idx_chat_sessions_evaluation ON chat_sessions(evaluation_id);
CREATE INDEX idx_chat_sessions_session ON chat_sessions(session_id);
CREATE INDEX idx_chat_messages_session ON chat_messages(chat_session_id, timestamp);
CREATE INDEX idx_configurations_active ON configurations(config_type, is_active, is_valid);
CREATE INDEX idx_sessions_active ON sessions(session_id, is_active, expires_at);
CREATE INDEX idx_sessions_user_activity ON sessions(user_id, last_activity);
CREATE INDEX idx_users_login ON users(username, is_active);
CREATE INDEX idx_users_email ON users(email, is_active);
CREATE INDEX idx_progress_cache_lookup ON progress_cache(session_id, metric_type, expires_at);

-- SQLite-specific optimizations
PRAGMA journal_mode = WAL;  -- Enable Write-Ahead Logging for concurrency
PRAGMA synchronous = NORMAL;  -- Balance safety and performance
PRAGMA cache_size = 10000;  -- Increase cache for better performance
PRAGMA temp_store = memory;  -- Use memory for temporary tables
```

7.2 **Data Archiving and Retention**
- **Retention policy**: Keep last 100 submissions per session (configurable)
- **Cleanup frequency**: Weekly automated cleanup job
- **Archive before delete**: Export old data to JSON before deletion
- **Performance monitoring**: Log query execution times, optimize slow queries
- **Progress cache cleanup**: Automatic cleanup of expired cache entries
- **Session cleanup**: Remove expired sessions and associated data

---

## 8.0 Security and Privacy

8.1 **Data Protection**
- **No PII collection**: Only text submissions and system-generated IDs stored
- **Session isolation**: Data scoped by server-generated session_id, no cross-session access
- **Debug data sanitization**: Remove sensitive information from debug logs
- **Data anonymization**: Hash session IDs for analytics if needed
- **Secure session tokens**: Server-generated cryptographically secure session identifiers

8.2 **Access Control**
- **Database permissions**: Application has full access, no direct user access
- **Admin functions**: Configuration editing through application only
- **Session validation**: Verify session ownership before data access
- **Authentication system**: JWT + Session hybrid infrastructure implemented, configurable enable/disable
- **User isolation**: Data access controlled by user_id and session_id
- **Password security**: bcrypt hashing for user passwords
- **JWT security**: Configurable secret keys and token expiration

---

## 9.0 Traceability Links

- **Source of Truth**: `02_Architecture.md`
- **Mapped Requirements**: 
  - Progress Tracking (2.6)
  - Admin Functions (2.4)
  - Debug Mode (2.5)
  - Data Layer requirements from Architecture


