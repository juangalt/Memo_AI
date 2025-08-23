# 02_Architecture.md

## 1.0 How to Use This File

- Defines the high-level system architecture.
- Builds on `01_Requirements.md`.
- Review before proceeding to `03_Data_Model.md`.
- **Traceability Hook**: Each component and flow must map back to requirements in `01_Requirements.md`.

---

## 2.0 System Overview

The Memo AI Coach system consists of a modular architecture designed for clarity, maintainability, and scalability. It is composed of three major layers:

- **Frontend (GUI)**

  - Provides the main user interface as tabbed navigation (Req 2.1).
  - Framework: Streamlit
  - Pages: Text Input, Overall Feedback, Detailed Feedback, Debug, Help, Admin.
  - Supports fast load times (<1s main load, <15s submission response) and usability features (hover info bubbles, rubric/framework resources) (Req 3.1, 2.1).

- **Backend Services**

  - REST API layer providing synchronous evaluation endpoints, admin functions, and debug info (Req 2.2–2.4).
  - Handles orchestration between frontend requests and the LLM engine.
  - Provides error handling and logging.

- **LLM Engine Integration**

  - Connects with the chosen LLM provider for synchronous evaluation processing.
  - Uses rubric and prompt templates with user submissions to produce evaluations (Req 2.2).
  - Supports debug mode by exposing raw prompts, raw responses, and performance metrics (Req 2.4).
  - Simple synchronous processing for reliable evaluation results.

- **Data Layer**

  - Stores user submissions, evaluation history, and logs (Req 2.2, 2.4, 3.5).
  - YAML configuration files stored in filesystem, read directly each time.
  - Simple database schema focused on core evaluation functionality.

### Key Properties

- Modular, API-driven architecture (Req 3.5).
- Cloud-ready design that supports scaling from MVP single-user to 100+ users (Req 3.2).
- Emphasis on maintainability and error handling (Req 3.3, 3.5).

---

## 3.0 Architecture Diagram
(To be defined. Ensure diagram components map to requirement IDs.)

---

## 4.0 Components

### 4.1 Frontend (GUI)

- Framework/library: **Streamlit**
- Tabbed navigation
- **State persistence**: Use **Streamlit Session State** to maintain a centralized source of truth for all frontend components.
  - Ensures data (submitted text, evaluation results) is instantly available across tabs without re-fetching.
  - Leverages Streamlit's built-in session state capabilities.
  - Provides consistent user experience and scalability.

**Components:**
- `TextInputPage`
- `OverallFeedbackPage`
- `DetailedFeedbackPage`
- `DebugPage`
- `HelpPage`
- `AdminPage`

### 4.2 Backend Services

**Backend API Design:**
- **API Style**: REST (simple, maintainable, industry-standard).
- **Framework**: **FastAPI** (lightweight, automatic OpenAPI documentation).
- **Endpoint Organization**: Grouped by functional domain to align with requirements:
  - `/evaluations/submit` - Text submission for LLM evaluation [MVP]
  - `/evaluations/{id}` - Retrieve evaluation results with detailed feedback (Req 2.2.3a, 2.2.3b) [MVP]
  - `/admin/config/*` - YAML configuration file management [MVP]
  - `/debug` - Debug output, performance metrics, raw prompts/responses (admin-only, Req 2.4) [MVP]

**Suggested Components:**
- `EvaluationService` (synchronous LLM evaluation processing) [MVP]
- `AdminService` (simple configuration management) [MVP]
- `AuthenticationService` (session-based authentication with admin support) [MVP]
- `SessionService` (session lifecycle and validation) [MVP]
- `AuthorizationMiddleware` (session-based authorization) [MVP]
- `DebugService` [MVP]
- `ConfigurationService` (direct filesystem configuration management) [MVP]

### 4.3 LLM Engine Integration

- **Provider:** The system uses **Claude** as the default LLM provider, but the architecture allows for easy configuration to support alternative LLMs in the future.
- **Prompt Engineering:** Prompts are constructed using the grading rubric and prompt template with the user's submitted text for reliable evaluations.
- **Debugging:** The integration exposes debug data for troubleshooting and transparency, while ensuring that no sensitive information is leaked.

**Component Explanations:**

- `LLMConnector`: Handles all communication with the LLM provider (e.g., sending prompts to Claude and receiving responses). It abstracts the details of the LLM API, making it easy to swap providers if needed.
- `PromptBuilder`: Responsible for assembling the final prompt sent to the LLM. It combines the rubric, prompt template, and user input into a structured prompt that guides the LLM to produce the desired evaluation.
- `ResponseParser`: Processes and interprets the raw output from the LLM, extracting structured data such as overall feedback and segment-level evaluations for use by other backend services.
- `DebugAdapter`: Collects and formats debug information related to LLM interactions (such as prompt/response pairs and timing data), ensuring that this information is available for diagnostics without exposing sensitive user or system data.

### 4.4 Data Layer

- Database: SQLite (for entire project lifecycle)
- Schema: database tables to store user text submissions, LLM evaluation results, YAML configuration file copies (source files in filesystem), and system logs.
- Store history and evaluation data.
- Scalability: SQLite with WAL mode and optimizations for 100+ concurrent users

**Suggested Components:**
- `SubmissionRepository`
- `EvaluationRepository`
- `ConfigRepository` (direct filesystem YAML operations)
- `LogRepository`
- `UserRepository` (authentication credentials and profiles)
- `SessionRepository` (session management and validation)

---

## 5.0 Data Flow
**5.1 Primary Data Flow Overview**

A. The main input to the system is user-generated text submitted for evaluation.

B. The primary outputs are:
   - Overall and segment-level evaluation results.

C. Additional data flows include:
   - Admin configuration of YAML template files, validated and written to filesystem.

**5.2 Data Movement Between Front-End, Back-End API, LLM Engine, and Database**

A. **User Input (Front-End to Back-End API):**
   - The user enters text or interacts with the UI (e.g., submits text for evaluation or updates YAML configs).
   - The front-end sends an HTTP request (typically JSON payload) to the appropriate back-end API endpoint (e.g., `/evaluation`, `/admin`, `/debug`).

B. **Back-End API Processing:**
   - The back-end receives the request and validates it through AuthorizationMiddleware.
   - Authentication flow: validates session_id for user isolation and admin access.
   - For text evaluation, the back-end:
     - Stores the user submission in the database (`SubmissionRepository`).
     - Builds a prompt using the rubric, prompt template, and user text (`PromptBuilder`).
     - Sends the prompt to the LLM engine via the `LLMConnector`.

C. **LLM Engine Interaction:**
   - The LLM engine (e.g., Claude) processes the prompt and returns a response.
   - The back-end parses the LLM response (`ResponseParser`), extracting overall and segment-level evaluations.

D. **Database and Filesystem Operations:**
   - The back-end saves LLM results and evaluations to the database (`EvaluationRepository`, `LogRepository`).
   - Admin updates to YAML files are validated and written to filesystem.

5. **Response to Front-End:**
   - The back-end assembles the final response (evaluation results).
   - The response is sent back to the front-end as JSON.

6. **Front-End Display:**
   - The front-end updates the UI with the received data (e.g., displays overall and per segment feedback).

**Summary Table:**

| Step              | Source      | Destination   | Data Type                          |
|-------------------|-------------|---------------|-------------------------------------|
| User Action       | Front-End   | Back-End API  | Text input, commands, config files  |
| Evaluation        | Back-End    | LLM Engine    | Prompt (rubric + user text)         |
| LLM Response      | LLM Engine  | Back-End      | Evaluation results                  |
| Persistence       | Back-End    | Database      | Submissions, evaluations, logs      |
| Configuration     | Back-End    | Filesystem    | Configuration files                 |
| API Response      | Back-End    | Front-End     | JSON (evaluation results)           |

This flow ensures that all data is securely transmitted, processed, and stored, with clear boundaries between the front-end, back-end, LLM engine, and database at each step.

**5.3 Sequence of Operations for Core Requirements**

**Text Evaluation Flow (Req 2.2):**
1. User submits text via frontend → `TextInputPage`
2. Frontend validates input and sends to `/api/evaluations/submit`
3. Backend validates request and stores submission (`SubmissionRepository`)
4. Backend constructs prompt using rubric and prompt template (`PromptBuilder`)
5. Backend sends prompt to LLM engine (`LLMConnector`)
6. LLM processes and returns evaluation response
7. Backend parses response into structured data (`ResponseParser`)
8. Backend stores evaluation (`EvaluationRepository`)
9. Backend returns evaluation response to frontend
10. Frontend updates `OverallFeedbackPage` and `DetailedFeedbackPage`



**Admin Functions Flow (Req 2.3):**
1. Admin accesses `AdminPage` → `/api/admin/config/{config_type}`
2. Frontend reads and displays current YAML configuration from filesystem
3. Admin edits configuration and submits → `/api/admin/config/{config_type}`
4. Backend validates YAML syntax and structure
5. Backend writes validated configuration to filesystem
6. Configuration immediately available for new evaluations (read from filesystem)

**Debug Mode Flow (Req 2.4):**
1. Debug mode enabled via admin interface (admin-only access)
2. All LLM interactions include debug data collection
3. Raw prompts and responses stored (`LogRepository`)
4. Performance metrics captured during processing
5. Debug data accessible via `/api/debug/info` (admin authentication required)
6. Frontend displays debug information on `DebugPage` (admin-only)

**Authentication Flow (Req 3.4):**
1. **Session-Based Authentication:**
   - Frontend generates secure session_id on first visit
   - All requests include session_id in headers/cookies
   - Backend validates session existence and expiration
   - Session data isolated by session_id
   - Admin sessions validated for management functions

2. **Admin Authentication:**
   - Admin credentials validated via simple password check
   - Admin session provides elevated access to management functions
   - Admin sessions tracked in `SessionRepository`

3. **Future Enhancement:**
   - Advanced authentication features can be added if complex user management is needed
   - Current session-based approach provides sufficient isolation for MVP

**5.4 Intermediate Results Storage and Retrieval**

**LLM Response Storage:**
- Raw LLM responses stored in `evaluations` table (debug mode only)
- Parsed structured data stored in separate fields for efficient querying
- Simple evaluation responses stored in evaluations table
- All LLM interactions logged with timestamps and performance metrics

**Evaluation Results Storage:**
- Overall scores and feedback stored in `evaluations` table
- Segment-level feedback stored as JSON in `evaluations.segment_feedback`
- Rubric scores stored as JSON for flexible scoring schemes


**Configuration Storage:**
- YAML configurations stored in filesystem as source of truth
- Version control maintained in `configuration_versions` table for admin changes
- Configuration files read directly from filesystem each time
- Startup validation ensures all YAML files are present and valid

**Session Context Management:**
- User sessions identified by `session_id` across all tables
- Session data persists across tab switches via global state
- Historical data linked to sessions for evaluation history
- Session cleanup handled by scheduled maintenance

**5.5 Data Integrity, Privacy, and Session Context**

**Data Integrity:**
- Database transactions ensure atomic operations for evaluation storage
- Foreign key constraints maintain referential integrity
- Input validation at API layer prevents malformed data
- YAML configuration validation prevents system corruption
- Regular database integrity checks and backups

**Privacy Protection:**
- Session-based authentication system for user isolation
- User data isolated by session_id with admin sessions for management
- No personal information collected beyond submitted text and admin credentials
- Debug data sanitized to remove sensitive information
- Data retention policies for old submissions and expired sessions
- Secure session management with httpOnly cookies and CSRF protection

**Session Context Maintenance:**
- Global state manager maintains session data across tabs
- Session_id passed in all API requests for data isolation
- Evaluation context maintained within sessions
- Session timeout handling for inactive users

**5.6 Error Handling and Debug Data Propagation**

**Error Handling Strategy:**
- Input validation errors returned with specific field details
- LLM API failures handled with retry logic and fallback responses
- Database errors logged and user-friendly messages returned
- Configuration validation errors prevent system corruption
- Network timeouts handled with appropriate user feedback

**Debug Data Collection:**
- Performance metrics captured for all LLM interactions
- Raw prompts and responses stored when debug mode enabled
- System resource usage monitored during processing
- Error logs include stack traces and context information
- Debug data accessible via dedicated API endpoints

**Error Propagation:**
- Errors logged at each layer with appropriate detail level
- User-facing error messages sanitized for security
- Debug information available to administrators
- Error recovery mechanisms for critical system failures
- Monitoring and alerting for system health

**5.7 Application Startup and Validation**

**Startup Validation Process:**
- All 4 essential YAML configuration files validated for syntax and structure on application startup
- Required configuration files (4 total):
  - `rubric.yaml`: Grading criteria and scoring
  - `prompt.yaml`: LLM prompt templates
  - `llm.yaml`: LLM provider configuration
  - `auth.yaml`: Authentication settings
- Validation includes schema checking, required fields verification, and format consistency
- Application fails to start if any configuration file is missing or invalid
- Clear error messages provided for configuration issues
- Startup validation logs recorded for debugging

**Configuration File Requirements:**
- Files must be present in designated config directory
- Valid YAML syntax and structure
- Required fields present for each configuration type
- Schema validation against predefined rules
- UTF-8 encoding for all files

**Configuration File Details:**

**Essential Configuration Files:**
- `rubric.yaml`: Grading criteria, scoring categories, evaluation rubrics
- `prompt.yaml`: LLM prompt templates, instruction formats, response schemas
- `llm.yaml`: LLM provider settings, API configuration, timeout settings
- `auth.yaml`: Authentication settings, session management

**5.8 Extensibility and Future Enhancements**

**Modular Architecture Support:**
- Pluggable LLM providers via `LLMConnector` interface
- Configurable evaluation rubrics via YAML configuration

- Modular frontend components for new features
- API versioning support for backward compatibility

**Scalability Considerations:**
- SQLite with WAL mode for concurrent read/write operations
- Database connection pooling and query optimization
- Stateless API design supports load balancing
- Caching layer ready for performance optimization
- Containerization supports cloud deployment with persistent volumes

**Feature Extension Points:**
- Additional evaluation frameworks via configuration

- Enhanced evaluation capabilities
- Advanced admin analytics and reporting
- Integration with external learning management systems

**Performance Optimization:**
- Database indexing strategy for common queries
- Caching layer for frequently accessed data
- Synchronous processing for reliable evaluation results
- Resource pooling for LLM API connections
- Monitoring and profiling for optimization opportunities

---

## 6.0 Extensibility Points

**6.1 LLM Provider Extensibility**
- **Interface**: `LLMConnector` abstract class defines standard interface
- **Current**: Claude integration via Anthropic API
- **Future**: Support for OpenAI GPT, Google Gemini, local models
- **Configuration**: LLM selection via environment variables or admin interface
- **Fallback**: Automatic failover to alternative providers

**6.2 Evaluation Framework Extensibility**
- **Configuration**: New evaluation rubrics added via YAML configuration
- **Scoring**: Flexible scoring schemes supported through JSON storage
- **Segmentation**: Configurable text segmentation strategies
- **Validation**: Framework validation rules defined in configuration
- **Versioning**: Framework version control for backward compatibility

**6.3 System Extensibility**
- **Metrics**: New evaluation metrics through modular components
- **Storage**: Flexible data storage for additional features
- **Integration**: Extension points for future capabilities
- **Analysis**: Configurable analysis through frontend components
- **Reporting**: Extensible reporting capabilities
- **Export**: Additional export formats for future use

**6.4 Frontend Component Extensibility**
- **Modular Design**: Reusable components for new features
- **State Management**: Global state supports new data types
- **Routing**: Tab-based navigation easily extended
- **Theming**: CSS variables for consistent styling
- **Internationalization**: Ready for multi-language support

**6.5 API Extensibility**
- **Versioning**: API versioning strategy for backward compatibility
- **Endpoints**: New endpoints follow established patterns
- **Authentication**: Session-based authentication system ready for production deployment
- **Rate Limiting**: Configurable rate limiting per session/user
- **Documentation**: Auto-generated OpenAPI documentation with authentication schemas

**6.6 Database Extensibility**
- **Schema Evolution**: Migration scripts for schema changes
- **Data Types**: JSON fields support flexible data structures
- **Indexing**: Optimized for common query patterns
- **WAL Mode**: Write-Ahead Logging for concurrent access
- **Performance**: Connection pooling and query optimization for scale

**6.7 Integration Extensibility**
- **Webhooks**: Event-driven integrations with external systems
- **APIs**: RESTful API ready for third-party integrations
- **Export Formats**: Additional export formats (CSV, JSON, XML)
- **LMS Integration**: Ready for learning management system integration
- **Analytics**: Data export for external analytics platforms

---

## 7.0 Traceability Links

- **Source of Truth**: `01_Requirements.md`
- **Mapped Requirements**:
  - GUI (2.1)
  - Text Evaluation (2.2)
  - Admin Functions (2.3)
  - Debug Mode (2.4)
  - Performance (3.1)
  - Scalability (3.2)
  - Reliability (3.3)
  - Security (3.4)
  - Maintainability (3.5)

