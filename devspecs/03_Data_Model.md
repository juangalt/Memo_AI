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
**Based on Requirements**: Session-based authentication system (Req 3.4.1). Session-based identification for users with admin support.

**Schema**:
```sql
users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,  -- simple hash for MVP
    is_admin BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,  -- Secure random token
    user_id INTEGER REFERENCES users(id),  -- NULL for anonymous sessions
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
```

### 3.2 User Submissions
**Based on Requirements**: Authentication system implemented from project start (Req 3.4.1). Session-based identification for all users.

**Schema**:
```sql
submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text_content TEXT NOT NULL,
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.3 Evaluations [MVP]
**Based on Requirements**: Store overall and segment-level evaluation results (Req 2.2.3a, 2.2.3b) [MVP]. Support debug mode with raw prompts/responses (Req 2.4) [MVP].

**Design Philosophy**: Simple synchronous evaluation system for reliable performance.

**Schema Design Rationale**:
- Simple structure focused on core evaluation functionality
- JSON fields for flexible rubric and segment feedback storage
- Debug fields for troubleshooting when enabled

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
    llm_provider TEXT NOT NULL DEFAULT 'claude',
    llm_model TEXT NOT NULL,
    raw_prompt TEXT,  -- Stored when debug mode enabled
    raw_response TEXT,  -- Stored when debug mode enabled
    debug_enabled BOOLEAN DEFAULT FALSE,
    processing_time DECIMAL(6,3),  -- Processing time in seconds
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.4 Configuration Files [MVP]
**Based on Architecture**: Source YAML files stored in filesystem as source of truth. Files are read directly from filesystem each time they're needed. No database tracking for MVP (Req 2.3).

**Configuration Files**:
- `rubric.yaml` - Grading criteria and scoring
- `prompt.yaml` - LLM prompt templates
- `llm.yaml` - LLM provider configuration
- `auth.yaml` - Authentication settings



---

## 4.0 Data Relationships

4.1 **Key Relationships**
```
sessions (1) ← (N) submissions
submissions (1) ← (N) evaluations
```

4.2 **Foreign Key Constraints and Cascading Behaviors**
- `evaluations.submission_id` → `submissions.id` (CASCADE DELETE)
- `submissions.session_id` → `sessions.session_id` (CASCADE DELETE)

4.3 **Data Integrity Rules**
- User sessions identified by `session_id` across tables
- Configuration files stored in filesystem, read directly each time
- Debug mode affects evaluation storage when enabled
- Simple foreign key relationships ensure data consistency

---

## 5.0 Data Access Patterns

5.1 **Read Patterns**
- **Evaluation History**: `SELECT * FROM evaluations WHERE submission_id IN (SELECT id FROM submissions WHERE session_id = ?) ORDER BY created_at DESC`
- **User Evaluations**: `SELECT * FROM evaluations e JOIN submissions s ON e.submission_id = s.id WHERE s.session_id = ? ORDER BY e.created_at DESC`
- **YAML Configuration Files**: Read directly from filesystem each time
- **Latest Evaluation**: `SELECT * FROM evaluations WHERE submission_id = ? ORDER BY created_at DESC LIMIT 1`

5.2 **Write Patterns**
- **Text Submission**: Single transaction (submissions → evaluations)
- **Configuration Updates**: Validate YAML → write to filesystem
- **Debug Data**: Conditional writes based on debug_enabled flag

5.3 **Performance Optimizations**
- Index on `(session_id, created_at)` for session-based queries
- Index on `(submission_id, created_at)` for evaluation history
- YAML files read directly from filesystem (simple and reliable)

**Configuration File Access Patterns:**
- **Business Logic Configs** (`rubric`, `prompt`): Read on evaluation request
- **System Configs** (`auth`, `llm`): Read on startup and admin changes

---

## 6.0 Data Migration Strategy

6.1 **Schema Evolution**
- **Initial Schema (001_initial.sql)**: Complete async-ready evaluation system designed from inception
- **Asynchronous-first design**: No migration from synchronous version required - async fields included in initial deployment
- **Future migrations**: Numbered SQL files for schema enhancements (002_add_feature.sql, 003_optimize_indexes.sql)
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

CREATE INDEX idx_config_versions_type_date ON configuration_versions(config_type, changed_at);
CREATE INDEX idx_sessions_active ON sessions(session_id, is_active, expires_at);
CREATE INDEX idx_sessions_user_activity ON sessions(user_id, last_activity);
CREATE INDEX idx_users_login ON users(username, is_active);
CREATE INDEX idx_users_email ON users(email, is_active);

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


---

## 8.0 Security and Privacy

8.1 **Data Protection**
- **No PII collection**: Only text submissions and system-generated IDs stored
- **Session isolation**: Data scoped by session_id, no cross-session access
- **Debug data sanitization**: Remove sensitive information from debug logs
- **Data anonymization**: Hash session IDs for analytics if needed
- **Global debug mode**: When enabled, stores debug data for all new evaluations

8.2 **Access Control**
- **Database permissions**: Application has full access, no direct user access
- **Admin functions**: Configuration editing through application only
- **Session validation**: Verify session ownership before data access
- **Authentication system**: JWT + Session hybrid infrastructure implemented from project start
- **User isolation**: Data access controlled by user_id and session_id
- **Configuration security**: YAML files validated on startup and before each admin change
- **Version tracking**: All admin configuration changes logged in database
- **Password security**: bcrypt hashing for user passwords
- **JWT security**: Configurable secret keys and token expiration

---

## 9.0 Design Decisions

### 9.1 ORM vs Raw SQL Choice ✅ **DECIDED**

**Decision**: **SQLite3 + Raw SQL** (implemented in Section 2.2)

**Alternatives Considered**:
1. **SQLAlchemy ORM**: Full-featured ORM with automatic migrations, relationships, validation
2. **SQLite3 + Raw SQL**: Direct database access, minimal dependencies
3. **Tortoise ORM**: Async-native ORM, lighter than SQLAlchemy

**Rationale**: 
- **Pros**: Maximum simplicity (Req 3.5.2), no external dependencies, explicit control
- **Cons**: More boilerplate code, manual migration scripts
- **Decision Basis**: Given MVP focus on simplicity and maintainability, raw SQL aligns with "no duplicate functions" principle

### 9.2 Database Migration Strategy ✅ **DECIDED**

**Decision**: **Asynchronous-first schema with version-based migrations** (implemented in Section 6.1)

**Alternatives Considered**:
1. **Synchronous-first with async migration**: Start simple, add async fields later
2. **Dual-mode support**: Support both sync and async evaluation patterns
3. **Asynchronous-first design**: Design async from inception (CHOSEN)

**Rationale**: 
- **Pros**: Consistent async patterns, modern web app design, no migration complexity, scalable from day 1
- **Cons**: Slightly more complex initial implementation than basic CRUD
- **Decision Basis**: Async-first design eliminates schema migration complexity while providing superior user experience and scalability

### 9.3 JSON Field Strategy for SQLite ✅ **DECIDED**

**Decision**: **TEXT fields with JSON strings** (implemented in schema definitions)

**Alternatives Considered**:
1. **SQLite JSON1 extension**: Native JSON functions and operators
2. **TEXT fields with JSON strings**: Manual JSON parsing in application
3. **Separate normalized tables**: Traditional relational approach

**Rationale**: 
- **Pros**: Universal SQLite compatibility, simpler deployment
- **Cons**: No database-level JSON queries
- **Decision Basis**: Prioritizes deployment simplicity over query capabilities, aligns with MVP simplicity requirements

### 9.4 Data Retention and Cleanup ✅ **DECIDED**

**Decision**: **Count-based retention (keep last 100 submissions per user)** (implemented in Section 7.2)

**Alternatives Considered**:
1. **Time-based retention**: Delete data older than X months
2. **Count-based retention**: Keep last N submissions per user
3. **No automatic cleanup**: Manual admin cleanup only
4. **Archival system**: Move old data to separate archive database

**Rationale**: 
- **Pros**: Predictable storage usage, maintains useful history
- **Cons**: May lose valuable long-term trends
- **Decision Basis**: Provides predictable storage management while preserving recent user activity

### 9.5 Session Management Strategy ✅ **DECIDED**

**Decision**: **Server-generated session tokens with database tracking** (implemented in authentication schema)

**Alternatives Considered**:
1. **UUID-based sessions**: Generate UUID on first visit, store in browser
2. **Browser fingerprinting**: Use browser characteristics as session ID
3. **Temporary cookies**: Server-generated session cookies
4. **localStorage persistence**: Client-side session storage

**Rationale**: 
- **Pros**: Simple, stateless, persistent across browser sessions, secure server control
- **Cons**: No cross-device continuity
- **Decision Basis**: Provides seamless user experience in MVP mode while supporting transition to authenticated sessions in production

### 9.6 Configuration Validation Strategy ✅ **DECIDED**

**Decision**: **Schema-based validation with runtime fallback** (implemented in configurations table)

**Alternatives Considered**:
1. **Schema-based validation**: YAML schema files with jsonschema validation
2. **Code-based validation**: Python validation functions
3. **Template validation**: Ensure required template variables exist
4. **Runtime validation**: Validate during LLM prompt generation

**Rationale**: 
- **Pros**: Comprehensive validation, prevents system corruption
- **Cons**: Additional schema maintenance overhead
- **Decision Basis**: Ensures data integrity and prevents configuration errors that could break the evaluation system

---

## 10.0 Traceability Links

- **Source of Truth**: `02_Architecture.md`
- **Mapped Requirements**: 
  
  - Admin Functions (2.4)
  - Debug Mode (2.5)
  - Data Layer requirements from Architecture


