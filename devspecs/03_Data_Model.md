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
- **Decision**: SQLite for MVP (as specified in Architecture)
- **Rationale**: Simple, file-based, no external dependencies
- **Migration Path**: PostgreSQL for production scaling

2.2 **ORM/Query Layer**
- **Decision**: SQLite3 + Raw SQL (see Section 10.1 for rationale)
- **Rationale**: Aligns with MVP simplicity requirements and maintainability focus
- **Migration Strategy**: Version-based migration scripts (see Section 10.2)

---

## 3.0 Core Data Entities

### 3.1 User Submissions
**Based on Requirements**: Authentication system implemented but disabled for MVP (Req 3.4.1). Session-based identification used.

**Schema**:
```sql
submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text_content TEXT NOT NULL,
    submission_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_session_id TEXT NOT NULL,  -- Session-based identification
    version INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 Evaluations
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

### 3.3 Configuration Files
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

### 3.4 Chat History
**Based on Requirements**: Chat available after feedback using submission context (Req 2.3). LLM uses submitted text, rubric, frameworks, and context template (Req 2.3.2).

**Schema**:
```sql
chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER NOT NULL REFERENCES evaluations(id) ON DELETE CASCADE,
    user_session_id TEXT NOT NULL,  -- Link to user session
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

### 3.5 Progress Tracking (Integrated with Evaluations)
**Based on Architecture**: Progress data automatically calculated during evaluation processing and displayed in separate tab (Arch 5.1.B). Progress tracking populated by evaluation data output (Arch 4.1).

**Note**: Progress metrics are computed from historical evaluations and rubric scores. No separate storage needed - calculated on-demand from evaluations table.

**Computed Metrics**:
- Overall score trends over time
- Rubric category improvements
- Submission frequency patterns
- Strength/opportunity evolution

**Schema** (Optional caching table for performance):
```sql
progress_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_session_id TEXT NOT NULL,
    metric_type TEXT NOT NULL,  -- 'overall_trend', 'rubric_category', 'submission_frequency'
    metric_data JSON NOT NULL,  -- Computed chart data
    last_calculated DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,  -- Cache expiration
    UNIQUE(user_session_id, metric_type)
);
```

---

## 4.0 Data Relationships

4.1 **Key Relationships**
```
submissions (1) ← (N) evaluations
evaluations (1) ← (N) chat_sessions  
chat_sessions (1) ← (N) chat_messages
configurations (independent - referenced by application logic)
progress_cache (computed from evaluations by user_session_id)
```

4.2 **Foreign Key Constraints and Cascading Behaviors**
- `evaluations.submission_id` → `submissions.id` (CASCADE DELETE)
- `chat_sessions.evaluation_id` → `evaluations.id` (CASCADE DELETE)  
- `chat_messages.chat_session_id` → `chat_sessions.id` (CASCADE DELETE)

4.3 **Data Integrity Rules**
- User sessions identified by `user_session_id` across all tables
- Configuration types restricted to: 'rubric', 'frameworks', 'context', 'prompt'
- Chat message types restricted to: 'user', 'assistant'
- Only one active configuration per config_type at a time
- Progress cache expires after 1 hour to ensure fresh data

---

## 5.0 Data Access Patterns

5.1 **Read Patterns**
- **Evaluation History**: `SELECT * FROM evaluations WHERE submission_id IN (SELECT id FROM submissions WHERE user_session_id = ?) ORDER BY evaluation_timestamp DESC`
- **Progress Data**: Calculate from evaluations grouped by time periods for charts
- **Active Configurations**: `SELECT * FROM configurations WHERE is_active = TRUE AND is_valid = TRUE`
- **Chat History**: `SELECT * FROM chat_messages WHERE chat_session_id = ? ORDER BY timestamp`
- **Latest Evaluation**: `SELECT * FROM evaluations WHERE submission_id = ? ORDER BY evaluation_timestamp DESC LIMIT 1`

5.2 **Write Patterns**
- **Text Submission**: Single transaction (submissions → evaluations → progress_cache invalidation)
- **Chat Messages**: Single insert with session validation
- **Configuration Updates**: Transaction (validate → update is_active → insert new version)
- **Debug Data**: Conditional writes based on debug_enabled flag

5.3 **Performance Optimizations**
- Index on `(user_session_id, created_at)` for session-based queries
- Index on `(submission_id, evaluation_timestamp)` for evaluation history
- Progress cache to avoid recalculating metrics on every request

---

## 6.0 Data Migration Strategy

6.1 **Schema Evolution**
- **Version-based migrations**: Numbered SQL files (001_initial.sql, 002_add_debug.sql)
- **Migration tracking**: `schema_migrations` table to track applied migrations
- **Rollback capability**: Down migration scripts for each version
- **Development workflow**: Apply migrations on application startup

6.2 **Data Backup and Recovery**
- **SQLite backup**: Simple file copy of database.db to backup location
- **Automated backups**: Daily backup script with rotation (keep 7 days)
- **Recovery procedure**: Replace database.db with backup file, restart application
- **Configuration backup**: Backup YAML files alongside database

---

## 7.0 Performance Considerations

7.1 **Indexing Strategy**
```sql
-- Performance indexes
CREATE INDEX idx_submissions_session_date ON submissions(user_session_id, created_at);
CREATE INDEX idx_evaluations_submission ON evaluations(submission_id, evaluation_timestamp);
CREATE INDEX idx_chat_sessions_evaluation ON chat_sessions(evaluation_id);
CREATE INDEX idx_chat_messages_session ON chat_messages(chat_session_id, timestamp);
CREATE INDEX idx_configurations_active ON configurations(config_type, is_active, is_valid);
```

7.2 **Data Archiving and Retention**
- **Retention policy**: Keep last 100 submissions per user session (configurable)
- **Cleanup frequency**: Weekly automated cleanup job
- **Archive before delete**: Export old data to JSON before deletion
- **Performance monitoring**: Log query execution times, optimize slow queries

---

## 8.0 Security and Privacy

8.1 **Data Protection**
- **No PII collection**: Only text submissions and system-generated IDs stored
- **Session isolation**: Data scoped by user_session_id, no cross-session access
- **Debug data sanitization**: Remove sensitive information from debug logs
- **Data anonymization**: Hash session IDs for analytics if needed

8.2 **Access Control**
- **Database permissions**: Application has full access, no direct user access
- **Admin functions**: Configuration editing through application only
- **Session validation**: Verify session ownership before data access
- **Authentication ready**: Infrastructure in place but disabled for MVP

---

## 9.0 Traceability Links

- **Source of Truth**: `02_Architecture.md`
- **Mapped Requirements**: 
  - Progress Tracking (2.6)
  - Admin Functions (2.4)
  - Debug Mode (2.5)
  - Data Layer requirements from Architecture

---

## 10.0 Pending Design Decisions

### 10.1 ORM vs Raw SQL Choice

**Alternatives**:
1. **SQLAlchemy ORM**: Full-featured ORM with automatic migrations, relationships, validation
2. **SQLite3 + Raw SQL**: Direct database access, minimal dependencies
3. **Tortoise ORM**: Async-native ORM, lighter than SQLAlchemy

**Recommendation**: **SQLite3 + Raw SQL**
- **Pros**: Maximum simplicity (Req 3.5.2), no external dependencies, explicit control
- **Cons**: More boilerplate code, manual migration scripts
- **Rationale**: Given MVP focus on simplicity and maintainability, raw SQL aligns with "no duplicate functions" principle

### 10.2 Database Migration Strategy

**Alternatives**:
1. **Version-based migrations**: Numbered migration files (001_initial.sql, 002_add_debug.sql)
2. **Schema comparison**: Compare current vs target schema and generate migrations
3. **Recreate on schema changes**: Drop and recreate database (development only)

**Recommendation**: **Version-based migrations**
- **Pros**: Explicit control, rollback capability, version tracking
- **Cons**: Requires migration discipline
- **Implementation**: Simple Python script to execute numbered SQL files

### 10.3 JSON Field Strategy for SQLite

**Alternatives**:
1. **SQLite JSON1 extension**: Native JSON functions and operators
2. **TEXT fields with JSON strings**: Manual JSON parsing in application
3. **Separate normalized tables**: Traditional relational approach

**Recommendation**: **TEXT fields with JSON strings**
- **Pros**: Universal SQLite compatibility, simpler deployment
- **Cons**: No database-level JSON queries
- **Rationale**: Prioritizes deployment simplicity over query capabilities

### 10.4 Data Retention and Cleanup

**Alternatives**:
1. **Time-based retention**: Delete data older than X months
2. **Count-based retention**: Keep last N submissions per user
3. **No automatic cleanup**: Manual admin cleanup only
4. **Archival system**: Move old data to separate archive database

**Recommendation**: **Count-based retention (keep last 100 submissions per user)**
- **Pros**: Predictable storage usage, maintains useful history
- **Cons**: May lose valuable long-term trends
- **Implementation**: Scheduled cleanup task, configurable limit

### 10.5 Session Management Strategy

**Alternatives**:
1. **UUID-based sessions**: Generate UUID on first visit, store in browser
2. **Browser fingerprinting**: Use browser characteristics as session ID
3. **Temporary cookies**: Server-generated session cookies
4. **localStorage persistence**: Client-side session storage

**Recommendation**: **UUID-based sessions with localStorage**
- **Pros**: Simple, stateless, persistent across browser sessions
- **Cons**: No cross-device continuity
- **Implementation**: Generate UUID client-side, persist in localStorage, send with each request

### 10.6 Configuration Validation Strategy

**Alternatives**:
1. **Schema-based validation**: YAML schema files with jsonschema validation
2. **Code-based validation**: Python validation functions
3. **Template validation**: Ensure required template variables exist
4. **Runtime validation**: Validate during LLM prompt generation

**Recommendation**: **Schema-based validation with runtime fallback**
- **Pros**: Comprehensive validation, prevents system corruption
- **Cons**: Additional schema maintenance overhead
- **Implementation**: YAML schema files, validation before database storage
