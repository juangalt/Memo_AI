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
  - Framework: Reflex
  - Pages: Text Input, Overall Feedback, Detailed Feedback, Progress Tracking, Debug, Help, Admin.
  - Progress Tracking tab is populated by evaluation data output.
  - Supports fast load times (<1s main load, <15s submission response) and usability features (hover info bubbles, rubric/framework resources) (Req 3.1, 2.1).

- **Backend Services**

  - REST API layer providing endpoints for evaluation (with integrated progress data), chat, admin functions, debugging info and exports (Req 2.2–2.7).
  - Handles orchestration between frontend requests and the LLM engine.
  - Provides error handling, logging, and PDF generation (Req 2.7, 3.3).

- **LLM Engine Integration**

  - Connects with the chosen LLM provider.
  - Uses context template, rubric, frameworks, and user submissions to produce evaluations with integrated progress data (Req 2.2, 2.6).
  - Supports debug mode by exposing raw prompts, raw responses, and performance metrics (Req 2.5).

- **Data Layer**

  - Stores user submissions, evaluation history, YAML configuration files, and logs (Req 2.6, 2.4, 3.5).
  - Enables charting for progress tracking integrated with evaluations (Req 2.6).

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

- Framework/library: **Reflex**
- Tabbed navigation
- **State persistence**: Use a **Global State Manager** to maintain a centralized source of truth for all frontend components.
  - Ensures data (submitted text, evaluation results with progress data, chat history) is instantly available across tabs without re-fetching.
  - Leverages Reflex’s built-in global state capabilities.
  - Provides consistent user experience and scalability.

**Components:**
- `TextInputPage`
- `OverallFeedbackPage`
- `DetailedFeedbackPage`
- `ProgressTrackingPage` (populated by evaluation data output)
- `DebugPage`
- `HelpPage`
- `AdminPage`

### 4.2 Backend Services

**Backend API Design:**
- **API Style**: REST (simple, maintainable, industry-standard).
- **Framework**: **FastAPI** (lightweight, async-friendly, automatic OpenAPI documentation).
- **Endpoint Organization**: Grouped by functional domain to align with requirements:
  - `/evaluation` - Text submission and LLM evaluation processing (Req 2.2)
  - `/chat` - LLM chat interactions with context (Req 2.3)
  - `/progress` - User submission history and progress tracking (Req 2.6)
  - `/admin` - YAML configuration file management (Req 2.4)
  - `/export` - PDF generation and download (Req 2.7)
  - `/debug` - Debug output, performance metrics, raw prompts/responses (Req 2.5)

**Suggested Components:**
- `EvaluationService` (includes progress calculation)
- `ChatService`
- `AdminService`
- `ExportService`
- `DebugService`

### 4.3 LLM Engine Integration

- Provider: **Claude** (default), configurable for future alternatives.
- Prompt engineering: combine context template, rubric, frameworks, and user text.
- Future enhancement: Use RAG
- Expose debug data without leaking sensitive info.

**Suggested Components:**
- `LLMConnector`
- `PromptBuilder`
- `ResponseParser`
- `DebugAdapter`

### 4.4 Data Layer

- Database: SQLite
- Schema: database tables to store user text submissions, LLM evaluation results, YAML configuration file copies (source files in filesystem), and system logs.
- Store history and generate progress data integrated with evaluations.

**Suggested Components:**
- `SubmissionRepository`
- `EvaluationRepository`
- `ConfigRepository`
- `LogRepository`
- `ProgressDataAdapter` (integrated with evaluation processing)

---

## 5.0 Data Flow
**5.1 Primary Data Flow Overview**

A. The main input to the system is user-generated text submitted for evaluation.

B. The primary outputs are:
   - Overall and segment-level evaluation results with integrated progress data.
   - Progress tracking data automatically calculated with each evaluation and displayed in separate tab.

C. Additional data flows include:
   - User-initiated chat interactions with the LLM, generating further input and output.
   - Admin submissions of YAML template files, which must be validated for correct format before being applied.

**5.2 Data Movement Between Front-End, Back-End API, LLM Engine, and Database**

A. **User Input (Front-End to Back-End API):**
   - The user enters text or interacts with the UI (e.g., submits text for evaluation, requests chat, downloads PDF, or updates YAML configs).
   - The front-end sends an HTTP request (typically JSON payload) to the appropriate back-end API endpoint (e.g., `/evaluation`, `/chat`, `/admin`, `/export`, `/debug`).

B. **Back-End API Processing:**
   - The back-end receives the request and validates it (authentication system implemented but disabled for MVP).
   - For text evaluation or chat, the back-end:
     - Stores the user submission and context in the database (`SubmissionRepository`).
     - Builds a prompt using the context template, rubric, frameworks, and user text (`PromptBuilder`).
     - Sends the prompt to the LLM engine via the `LLMConnector`.

C. **LLM Engine Interaction:**
   - The LLM engine (e.g., Claude) processes the prompt and returns a response.
   - The back-end parses the LLM response (`ResponseParser`), extracting overall and segment-level evaluations, chat replies, or debug data.

D. **Database Operations:**
   - The back-end saves LLM results, evaluations, and any relevant metadata to the database (`EvaluationRepository`, `LogRepository`).
   - Progress data is automatically calculated during evaluation processing using historical submissions and evaluations (`ProgressDataAdapter`).
   - Admin updates to YAML files are validated and stored (source files in filesystem, database copies for version tracking).

5. **Response to Front-End:**
   - The back-end assembles the final response (evaluation results with integrated progress data, chat reply, PDF link with progress information, debug info, etc.).
   - The response is sent back to the front-end as JSON or file download.

6. **Front-End Display:**
   - The front-end updates the UI with the received data (e.g., displays overall and per segment feedback, progress data, chat, or error/debug info).
   - For PDF export, the user is prompted to download the generated file.

**Summary Table:**

| Step              | Source      | Destination   | Data Type                          |
|-------------------|-------------|---------------|-------------------------------------|
| User Action       | Front-End   | Back-End API  | Text input, commands, config files  |
| Evaluation/Chat   | Back-End    | LLM Engine    | Prompt (constructed from context)   |
| LLM Response      | LLM Engine  | Back-End      | Evaluation results, chat reply      |
| Persistence       | Back-End    | Database      | Submissions, evaluations, logs      |
| Progress/Config   | Back-End    | Database      | Progress data, configuration files  |
| API Response      | Back-End    | Front-End     | JSON (results, progress), files     |

This flow ensures that all data is securely transmitted, processed, and stored, with clear boundaries between the front-end, back-end, LLM engine, and database at each step.

**5.3 Sequence of Operations for Core Requirements**

**Text Evaluation Flow (Req 2.2):**
1. User submits text via frontend → `TextInputPage`
2. Frontend validates input and sends to `/api/evaluations/submit`
3. Backend validates request and stores submission (`SubmissionRepository`)
4. Backend constructs prompt using context, rubric, frameworks (`PromptBuilder`)
5. Backend sends prompt to LLM engine (`LLMConnector`)
6. LLM processes and returns evaluation response
7. Backend parses response into structured data (`ResponseParser`)
8. Backend calculates progress data from historical evaluations (`ProgressDataAdapter`)
9. Backend stores evaluation and progress data (`EvaluationRepository`)
10. Backend returns complete response (evaluation + progress) to frontend
11. Frontend updates `OverallFeedbackPage` and `DetailedFeedbackPage`

**Chat Flow (Req 2.3):**
1. User initiates chat after evaluation → `OverallFeedbackPage`
2. Frontend sends chat request to `/api/chat/sessions`
3. Backend creates chat session with evaluation context
4. User sends message → `/api/chat/sessions/{session_id}/messages`
5. Backend constructs chat prompt with context (`PromptBuilder`)
6. LLM processes chat and returns response
7. Backend stores chat message and response (`ChatRepository`)
8. Frontend updates chat interface with response

**Progress Tracking Flow (Req 2.6):**
1. Progress data automatically calculated during evaluation processing
2. Historical metrics queried from database (`ProgressDataAdapter`)
3. Chart data generated from evaluation history
4. Trends computed from previous submissions
5. Progress data included in evaluation response
6. Frontend displays progress charts on feedback pages

**Admin Functions Flow (Req 2.4):**
1. Admin accesses `AdminPage` → `/api/admin/configurations/{config_type}`
2. Frontend displays current YAML configuration
3. Admin edits configuration and submits → `/api/admin/configurations/{config_type}`
4. Backend validates YAML syntax and structure
5. Backend stores validated configuration (`ConfigRepository`)
6. Configuration immediately available for new evaluations

**Debug Mode Flow (Req 2.5):**
1. Debug mode enabled via admin interface
2. All LLM interactions include debug data collection
3. Raw prompts and responses stored (`LogRepository`)
4. Performance metrics captured during processing
5. Debug data accessible via `/api/debug/info`
6. Frontend displays debug information on `DebugPage`

**PDF Export Flow (Req 2.7):**
1. User requests PDF export → `/api/export/pdf`
2. Backend retrieves evaluation data and progress information
3. PDF generated with user text, evaluation, and segment feedback
4. PDF stored temporarily and URL returned to frontend
5. User downloads PDF file

**5.4 Intermediate Results Storage and Retrieval**

**LLM Response Storage:**
- Raw LLM responses stored in `evaluations` table (debug mode only)
- Parsed structured data stored in separate fields for efficient querying
- Chat responses stored in `chat_messages` table with session context
- All LLM interactions logged with timestamps and performance metrics

**Evaluation Results Storage:**
- Overall scores and feedback stored in `evaluations` table
- Segment-level feedback stored as JSON in `evaluations.segment_feedback`
- Rubric scores stored as JSON for flexible scoring schemes
- Progress metrics calculated and stored in `progress_metrics` table

**Configuration Storage:**
- YAML configurations stored as text in `configurations` table
- Version control maintained for configuration rollback
- Active configuration marked with `is_active` flag
- Configuration validation results stored for audit trail

**Session Context Management:**
- User sessions identified by `session_id` across all tables
- Session data persists across tab switches via global state
- Historical data linked to sessions for progress tracking
- Session cleanup handled by scheduled maintenance

**5.5 Data Integrity, Privacy, and Session Context**

**Data Integrity:**
- Database transactions ensure atomic operations for evaluation storage
- Foreign key constraints maintain referential integrity
- Input validation at API layer prevents malformed data
- YAML configuration validation prevents system corruption
- Regular database integrity checks and backups

**Privacy Protection:**
- No user authentication required for MVP (session-based)
- User data isolated by session_id
- No personal information collected beyond submitted text
- Debug data sanitized to remove sensitive information
- Data retention policies for old submissions

**Session Context Maintenance:**
- Global state manager maintains session data across tabs
- Session_id passed in all API requests for data isolation
- Progress tracking scoped to individual sessions
- Chat context maintained within evaluation sessions
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

**5.7 Extensibility and Future Enhancements**

**Modular Architecture Support:**
- Pluggable LLM providers via `LLMConnector` interface
- Configurable evaluation rubrics via YAML configuration
- Extensible progress metrics through `ProgressDataAdapter`
- Modular frontend components for new features
- API versioning support for backward compatibility

**Scalability Considerations:**
- Database schema designed for horizontal scaling
- Stateless API design supports load balancing
- Caching layer ready for performance optimization
- Microservice architecture possible for future phases
- Containerization supports cloud deployment

**Feature Extension Points:**
- Additional evaluation frameworks via configuration
- New progress visualization types
- Enhanced chat capabilities with memory
- Advanced admin analytics and reporting
- Integration with external learning management systems

**Performance Optimization:**
- Database indexing strategy for common queries
- Caching layer for frequently accessed data
- Asynchronous processing for long-running operations
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

**6.3 Progress Tracking Extensibility**
- **Metrics**: New progress metrics added through `ProgressDataAdapter`
- **Visualizations**: Chart types configurable via frontend components
- **Time Periods**: Customizable time ranges for progress analysis
- **Trends**: Extensible trend calculation algorithms
- **Export**: Additional export formats beyond PDF

**6.4 Frontend Component Extensibility**
- **Modular Design**: Reusable components for new features
- **State Management**: Global state supports new data types
- **Routing**: Tab-based navigation easily extended
- **Theming**: CSS variables for consistent styling
- **Internationalization**: Ready for multi-language support

**6.5 API Extensibility**
- **Versioning**: API versioning strategy for backward compatibility
- **Endpoints**: New endpoints follow established patterns
- **Authentication**: Ready for future authentication systems
- **Rate Limiting**: Configurable rate limiting per endpoint
- **Documentation**: Auto-generated OpenAPI documentation

**6.6 Database Extensibility**
- **Schema Evolution**: Migration scripts for schema changes
- **Data Types**: JSON fields support flexible data structures
- **Indexing**: Optimized for common query patterns
- **Partitioning**: Ready for data partitioning strategies
- **Replication**: Support for read replicas in future

**6.7 Integration Extensibility**
- **Webhooks**: Event-driven integrations with external systems
- **APIs**: RESTful API ready for third-party integrations
- **Export Formats**: Additional export formats (CSV, JSON, XML)
- **LMS Integration**: Ready for learning management system integration
- **Analytics**: Data export for external analytics platforms

---

## 7.0 Traceability Links

- **Source of Truth**: `01_Requirements.md`
- **Mapped Requirements (placeholders)**:
  - GUI (2.1)
  - Text Evaluation (2.2)
  - Chat with LLM (2.3)
  - Admin Functions (2.4)
  - Debug Mode (2.5)
  - Progress Tracking (2.6)
  - PDF Export (2.7)
  - Performance (3.1)
  - Scalability (3.2)
  - Reliability (3.3)
  - Maintainability (3.5)

