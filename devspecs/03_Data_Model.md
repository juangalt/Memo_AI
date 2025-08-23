# Data Model Specification
## Memo AI Coach

**Document ID**: 03_Data_Model.md  
**Document Version**: 1.4  
**Last Updated**: Implementation Phase (Complete consistency fixes and standardization)  
**Next Review**: After initial deployment  
**Status**: Approved

---

## 1.0 Document Information

### 1.1 Purpose
Defines the data structures, database schema, and data relationships for the Memo AI Coach project, establishing the foundation for data persistence and management.

### 1.2 Scope
- Database technology decisions and rationale
- Core data entities and schema definitions
- Data relationships and integrity constraints
- Data access patterns and optimization strategies
- Security and privacy considerations

### 1.3 Dependencies
- **Prerequisites**: 00_ProjectOverview.md, 01_Requirements.md, 02_Architecture.md
- **Related Documents**: 04_API_Definitions.md, 05_UI_UX.md
- **Requirements**: Implements data requirements from 01_Requirements.md (Req 2.2-2.5, 3.4)

### 1.4 Document Structure
1. Document Information
2. Database Technology Decisions
3. Core Data Entities
4. Data Relationships
5. Data Access Patterns
6. Security and Privacy
7. Traceability Matrix

### 1.5 Traceability Summary
| Requirement ID | Requirement Description | Data Model Implementation | Status |
|---------------|------------------------|---------------------------|---------|
| 2.2.1-2.2.4 | Text Submission Requirements | Submissions Entity (3.3) | ✅ Implemented |
| 2.3.1-2.3.6 | Text Evaluation Requirements | Evaluations Entity (3.4) | ✅ Implemented |
| 2.4.1-2.4.3 | Admin Functions Requirements | Configuration Management | ✅ Implemented |
| 2.5.1-2.5.3 | Debug Mode Requirements | Debug Data Storage | ✅ Implemented |
| 3.4.1-3.4.5 | Security Requirements | Authentication Schema (3.1, 3.2) | ✅ Implemented |

### 1.6 Document Navigation
- **Previous Document**: 02_Architecture.md
- **Next Document**: 04_API_Definitions.md
- **Related Documents**: 05_UI_UX.md

---

## 2.0 Database Technology Decision

2.1 **Primary Database**
- **Decision**: SQLite for entire project lifecycle
- **Rationale**: Simple, file-based, no external dependencies, excellent performance with WAL mode
- **Scaling Strategy**: SQLite optimizations, connection pooling, and performance tuning for 100+ users

2.2 **ORM/Query Layer**

This section refers to the method used for interacting with the database from the application code. Instead of using a full-featured Object-Relational Mapper (ORM) like SQLAlchemy, the project uses the built-in `sqlite3` library and writes SQL queries directly ("Raw SQL"). This approach is chosen for its simplicity, transparency, and ease of maintenance. It allows developers to have direct control over database operations and schema evolution, and avoids the complexity and overhead of an ORM layer. See Section 10.1 for more details on this decision.
- **Decision**: SQLite3 + Raw SQL (see Section 10.1 for rationale)
- **Rationale**: Aligns with simplicity requirements and maintainability focus
- **Migration Strategy**: Version-based migration scripts (see Section 10.2)

---

## 3.0 Core Data Entities

### 3.1 Users and Authentication
**Based on Requirements**: Session-based authentication system (Req 3.4.1) with admin user support for system management.

**Users Schema**:
```sql
users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,    -- Admin username
    password_hash TEXT NOT NULL,      -- bcrypt hashed password
    is_admin BOOLEAN DEFAULT FALSE,   -- Admin flag for elevated access
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### 3.2 Sessions and Session Management
**Based on Requirements**: Session-based authentication system (Req 3.4.1). Session-based identification for users with admin support.

**Sessions Schema**:
```sql
sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,  -- Secure random token
    user_id INTEGER REFERENCES users(id),  -- Optional user reference (NULL for anonymous)
    is_admin BOOLEAN DEFAULT FALSE,   -- Admin flag for elevated access
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
```

### 3.3 User Submissions
**Based on Requirements**: Session-based identification for all users.

**Schema**:
```sql
submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text_content TEXT NOT NULL,
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.4 Evaluations
**Based on Requirements**: Store overall and segment-level evaluation results (Req 2.2.3a, 2.2.3b). Support debug mode with raw prompts/responses (Req 2.4).

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
    rubric_scores TEXT NOT NULL,  -- JSON string: {"category1": score, "category2": score}
    segment_feedback TEXT NOT NULL,  -- JSON string: [{"segment": "text", "comment": "feedback", "questions": ["q1", "q2"]}]
    llm_provider TEXT NOT NULL DEFAULT 'claude',
    llm_model TEXT NOT NULL,
    raw_prompt TEXT,  -- Stored when debug mode enabled
    raw_response TEXT,  -- Stored when debug mode enabled
    debug_enabled BOOLEAN DEFAULT FALSE,
    processing_time DECIMAL(6,3),  -- Processing time in seconds
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.5 Configuration Files
**Based on Architecture**: Source YAML files stored in filesystem as source of truth. Files are read directly from filesystem each time they're needed. No database tracking (Req 2.3).

**Configuration Files**:
- `rubric.yaml` - Grading criteria and scoring
- `prompt.yaml` - LLM prompt templates
- `llm.yaml` - LLM provider configuration
- `auth.yaml` - Authentication settings



---

## 4.0 Data Relationships

4.1 **Key Relationships**
```
users (1) ← (N) sessions
sessions (1) ← (N) submissions
submissions (1) ← (N) evaluations
```

4.2 **Foreign Key Constraints and Cascading Behaviors**
- `sessions.user_id` → `users.id` (optional, NULL for anonymous)
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
- **Initial Schema (001_initial.sql)**: Complete synchronous evaluation system designed for production
- **Synchronous-first design**: Simple schema focused on immediate evaluation processing
- **Future migrations**: Numbered SQL files for async features and schema enhancements (002_add_async.sql, 003_optimize_indexes.sql)
- **Migration tracking**: `schema_migrations` table to track applied migrations
- **Rollback capability**: Down migration scripts for each version
- **Development workflow**: Apply migrations on application startup

6.2 **Data Backup and Recovery**
- **SQLite backup**: Use SQLite backup API or file copy during quiet periods
- **WAL checkpoint**: Ensure WAL files are merged before backup
- **Automated backups**: Weekly backup script with rotation (keep 4 weeks)
- **Recovery procedure**: Replace database.db with backup file, restart application
- **Configuration backup**: Backup YAML files alongside database

---

## 7.0 Performance Considerations

7.1 **Indexing Strategy**
```sql
-- Performance indexes optimized for SQLite
CREATE INDEX idx_users_username ON users(username, is_active);
CREATE INDEX idx_sessions_user_active ON sessions(user_id, is_active, expires_at);
CREATE INDEX idx_submissions_session_date ON submissions(session_id, created_at);
CREATE INDEX idx_evaluations_submission ON evaluations(submission_id, created_at);
CREATE INDEX idx_sessions_active ON sessions(session_id, is_active, expires_at);

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
- **Authentication system**: Session-based authentication system implemented from project start
- **User isolation**: Data access controlled by user_id and session_id
- **Configuration security**: YAML files validated on startup and before each admin change
- **Version tracking**: All admin configuration changes logged in database
- **Password security**: bcrypt hashing for user passwords
- **Session security**: Configurable session tokens and expiration

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

**Decision**: **Synchronous-first schema with async migration path** (implemented in Section 6.1)

**Alternatives Considered**:
1. **Synchronous-first with async migration**: Start simple, add async fields later (CHOSEN)
2. **Dual-mode support**: Support both sync and async evaluation patterns
3. **Asynchronous-first design**: Design async from inception

**Rationale**: 
- **Pros**: Simpler implementation, clear migration path, maintains user experience
- **Cons**: Requires schema migration for async features
- **Decision Basis**: Synchronous-first design aligns with simplicity while providing clear upgrade path to async processing for scalability

### 9.3 JSON Field Strategy for SQLite ✅ **DECIDED**

**Decision**: **TEXT fields with JSON strings** (implemented in schema definitions)

**Alternatives Considered**:
1. **SQLite JSON1 extension**: Native JSON functions and operators
2. **TEXT fields with JSON strings**: Manual JSON parsing in application
3. **Separate normalized tables**: Traditional relational approach

**Rationale**: 
- **Pros**: Universal SQLite compatibility, simpler deployment
- **Cons**: No database-level JSON queries
- **Decision Basis**: Prioritizes deployment simplicity over query capabilities, aligns with simplicity requirements

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
- **Decision Basis**: Provides seamless user experience while supporting transition to authenticated sessions in production

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

## 10.0 Traceability Matrix

| Requirement ID | Requirement Description | Data Model Implementation | Status |
|---------------|------------------------|---------------------------|---------|
| 2.2.1 | Text input box available | Submissions table (3.3) - text_content field | ✅ Implemented |
| 2.2.2 | Submission processed by LLM | Submissions table (3.3) - session tracking | ✅ Implemented |
| 2.2.3a | Overall evaluation returned | Evaluations table (3.4) - overall_score, strengths, opportunities | ✅ Implemented |
| 2.2.3b | Segment evaluation returned | Evaluations table (3.4) - segment_feedback JSON field | ✅ Implemented |
| 2.2.4 | Evaluation processing straightforward | Evaluations table (3.4) - processing_time tracking | ✅ Implemented |
| 2.3.1 | System uses grading rubric | Evaluations table (3.4) - rubric_scores TEXT field | ✅ Implemented |
| 2.3.2 | System uses prompt templates | Configuration management (3.5) - prompt.yaml | ✅ Implemented |
| 2.3.3 | Overall strengths/opportunities | Evaluations table (3.4) - strengths, opportunities fields | ✅ Implemented |
| 2.3.4 | Detailed rubric grading | Evaluations table (3.4) - rubric_scores TEXT field | ✅ Implemented |
| 2.3.5 | Segment-level evaluation | Evaluations table (3.4) - segment_feedback TEXT field | ✅ Implemented |
| 2.3.6 | Immediate feedback processing | Evaluations table (3.4) - created_at timestamp | ✅ Implemented |
| 2.4.1 | Admin edits YAML | Configuration management (3.5) - YAML file storage | ✅ Implemented |
| 2.4.2 | Configuration changes validated | Configuration management (3.5) - Schema validation | ✅ Implemented |
| 2.4.3 | Simple configuration management | Configuration management (3.5) - Direct file access | ✅ Implemented |
| 2.5.1 | Debug output accessible | Evaluations table (3.4) - debug_enabled, raw_prompt, raw_response | ✅ Implemented |
| 2.5.2 | Raw prompts/responses shown | Evaluations table (3.4) - raw_prompt, raw_response fields | ✅ Implemented |
| 2.5.3 | Debug mode admin-only | Users table (3.1) - is_admin field | ✅ Implemented |
| 3.4.1 | Session-based authentication | Sessions table (3.2) - session management | ✅ Implemented |
| 3.4.2 | Secure session management | Sessions table (3.2) - expires_at, is_active fields | ✅ Implemented |
| 3.4.3 | CSRF protection and rate limiting | Sessions table (3.2) - session tracking for rate limiting | ✅ Implemented |
| 3.4.4 | Admin authentication | Users table (3.1) - is_admin field | ✅ Implemented |
| 3.4.5 | Optional JWT authentication | Sessions table (3.2) - Ready for JWT extension | ⏳ Planned |

---

**Document ID**: 03_Data_Model.md  
**Document Version**: 1.4  
**Last Updated**: Implementation Phase (Complete consistency fixes and standardization)  
**Next Review**: After initial deployment


