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
- **Decision**: (Pending)
- **Options**: SQLAlchemy, Tortoise ORM, raw SQL
- **Questions**:
  - Should we use an ORM or raw SQL for simplicity?
  - What level of database abstraction is needed for MVP?

---

## 3.0 Core Data Entities

### 3.1 User Submissions
**Questions to Answer**:
- Should we support user accounts/authentication in MVP?
- How do we handle anonymous submissions vs. user sessions?
- What metadata should be stored with each submission?

**Proposed Schema**:
```sql
-- (Pending) Define exact fields and constraints
submissions (
    id INTEGER PRIMARY KEY,
    text_content TEXT NOT NULL,
    submission_timestamp DATETIME,
    user_session_id TEXT,  -- (Pending) How to handle user identification
    version INTEGER DEFAULT 1
)
```

### 3.2 Evaluations
**Questions to Answer**:
- How do we structure the evaluation results?
- Should we store raw LLM responses or parsed structured data?
- How do we handle evaluation versions and history?

**Proposed Schema**:
```sql
-- (Pending) Define exact fields and constraints
evaluations (
    id INTEGER PRIMARY KEY,
    submission_id INTEGER REFERENCES submissions(id),
    overall_score DECIMAL,
    strengths TEXT,
    opportunities TEXT,
    rubric_scores JSON,  -- (Pending) Structure for rubric breakdown
    segment_feedback JSON,  -- (Pending) Structure for segment-level feedback
    evaluation_timestamp DATETIME,
    llm_provider TEXT,
    llm_model TEXT,
    raw_prompt TEXT,  -- (Pending) Store for debug mode?
    raw_response TEXT   -- (Pending) Store for debug mode?
)
```

### 3.3 Configuration Files
**Questions to Answer**:
- How do we store and version YAML configurations?
- Should configurations be stored in database or file system?
- How do we handle configuration validation and rollbacks?

**Proposed Schema**:
```sql
-- (Pending) Define exact fields and constraints
configurations (
    id INTEGER PRIMARY KEY,
    config_type TEXT NOT NULL,  -- 'rubric', 'frameworks', 'context', 'prompt'
    config_content TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_timestamp DATETIME,
    updated_timestamp DATETIME
)
```

### 3.4 Chat History
**Questions to Answer**:
- How do we structure chat conversations?
- Should we store chat context or regenerate it?
- How do we link chats to specific evaluations?

**Proposed Schema**:
```sql
-- (Pending) Define exact fields and constraints
chat_sessions (
    id INTEGER PRIMARY KEY,
    evaluation_id INTEGER REFERENCES evaluations(id),
    session_start DATETIME,
    session_end DATETIME
)

chat_messages (
    id INTEGER PRIMARY KEY,
    chat_session_id INTEGER REFERENCES chat_sessions(id),
    message_type TEXT,  -- 'user' or 'assistant'
    message_content TEXT,
    timestamp DATETIME
)
```

### 3.5 Progress Tracking
**Questions to Answer**:
- What metrics should we track for progress?
- How do we aggregate data for charts?
- Should we track trends over time periods?

**Proposed Schema**:
```sql
-- (Pending) Define exact fields and constraints
progress_metrics (
    id INTEGER PRIMARY KEY,
    user_session_id TEXT,
    metric_type TEXT,  -- 'overall_score', 'rubric_category', etc.
    metric_value DECIMAL,
    evaluation_id INTEGER REFERENCES evaluations(id),
    timestamp DATETIME
)
```

---

## 4.0 Data Relationships

4.1 **Entity Relationship Diagram**
- (Pending) Create visual ERD showing relationships between entities

4.2 **Key Relationships**
- (Pending) Define foreign key constraints and cascading behaviors
- (Pending) Define data integrity rules

---

## 5.0 Data Access Patterns

5.1 **Read Patterns**
- (Pending) Define common query patterns for:
  - Retrieving evaluation history
  - Generating progress charts
  - Loading configuration files
  - Fetching chat history

5.2 **Write Patterns**
- (Pending) Define transaction boundaries
- (Pending) Define data validation rules
- (Pending) Define error handling for data operations

---

## 6.0 Data Migration Strategy

6.1 **Schema Evolution**
- (Pending) How to handle schema changes during development
- (Pending) Migration scripts and versioning strategy

6.2 **Data Backup and Recovery**
- (Pending) Backup strategy for SQLite files
- (Pending) Recovery procedures

---

## 7.0 Performance Considerations

7.1 **Indexing Strategy**
- (Pending) Define indexes for common query patterns
- (Pending) Performance monitoring for database operations

7.2 **Data Archiving**
- (Pending) Strategy for old data cleanup
- (Pending) Data retention policies

---

## 8.0 Security and Privacy

8.1 **Data Protection**
- (Pending) How to handle sensitive user data
- (Pending) Data anonymization for analytics

8.2 **Access Control**
- (Pending) Database access permissions
- (Pending) Admin vs. user data access

---

## 9.0 Traceability Links

- **Source of Truth**: `02_Architecture.md`
- **Mapped Requirements**: 
  - Progress Tracking (2.6)
  - Admin Functions (2.4)
  - Debug Mode (2.5)
  - Data Layer requirements from Architecture

---

## 10.0 Open Questions and Decisions

10.1 **Critical Decisions Needed**:
- User identification strategy (sessions vs. accounts)
- Evaluation data structure (raw vs. parsed)
- Configuration storage approach (DB vs. files)
- Chat context storage strategy
- Data retention and archiving policies

10.2 **Technical Decisions**:
- ORM vs. raw SQL choice
- Database migration strategy
- Performance optimization approach
- Security implementation details
