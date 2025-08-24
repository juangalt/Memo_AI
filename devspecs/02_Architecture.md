# System Architecture
## Memo AI Coach

**Document ID**: 02_Architecture.md  
**Document Version**: 1.4  
**Last Updated**: Implementation Phase (Complete consistency fixes and standardization)  
**Next Review**: After initial deployment

---

## 1.0 Document Information

### 1.1 Purpose
Defines the high-level system architecture, component design, and data flow patterns for the Memo AI Coach application.

### 1.2 Scope
- System architecture overview and design principles
- Component specifications and relationships
- Data flow patterns and integration points
- Technology stack and framework decisions

### 1.3 Dependencies
- **Prerequisites**: 00_Devspecs_Overview.md, 01_Requirements.md
- **Related Documents**: 03_Data_Model.md, 04_API_Definitions.md, 05_UI_UX.md
- **Requirements**: Implements requirements from 01_Requirements.md (Req 2.1-2.5, 3.1-3.5)

### 1.4 Document Structure
1. Document Information
2. System Overview
3. Architecture Components
4. Data Flow Patterns
5. Technology Decisions
6. Traceability Matrix

### 1.5 Traceability Summary
| Requirement ID | Requirement Description | Architecture Implementation | Status |
|---------------|------------------------|----------------------------|---------|
| 2.1.1-2.1.5 | User Interface Requirements | Frontend Components (4.1) | ✅ Implemented |
| 2.2.1-2.2.4 | Text Submission Requirements | Backend Services (4.2) | ✅ Implemented |
| 2.3.1-2.3.6 | Text Evaluation Requirements | LLM Engine Integration (4.3) | ✅ Implemented |
| 2.4.1-2.4.3 | Admin Functions Requirements | Admin Services (4.2) | ✅ Implemented |
| 2.5.1-2.5.3 | Debug Mode Requirements | Debug Services (4.2) | ✅ Implemented |
| 3.1.1-3.1.2 | Performance Requirements | Performance Optimizations | ✅ Implemented |
| 3.2.1-3.2.2 | Scalability Requirements | Scalable Architecture | ✅ Implemented |
| 3.3.1-3.3.2 | Reliability Requirements | Error Handling & Logging | ✅ Implemented |
| 3.4.1-3.4.5 | Security Requirements | Authentication & Authorization | ✅ Implemented |
| 3.5.1-3.5.4 | Maintainability Requirements | Modular Architecture | ✅ Implemented |

### 1.6 Document Navigation
- **Previous Document**: 01_Requirements.md
- **Next Document**: 03_Data_Model.md
- **Related Documents**: 04_API_Definitions.md, 05_UI_UX.md

---

## 2.0 System Overview

The Memo AI Coach system consists of a modular architecture designed for clarity, maintainability, and scalability. It is composed of three major layers:

- **Frontend (GUI)**

  - Provides the main user interface as tabbed navigation (Req 2.1).
  - Framework: Streamlit
  - Pages: Text Input, Overall Feedback, Detailed Feedback, Debug, Help, Admin.
  - Supports fast load times (<1s main load, <15s text submission response) and usability features (hover info bubbles, rubric/framework resources) (Req 3.1, 2.1).

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
  - Admin user accounts for system management (Req 3.4.4).
  - Session management for user isolation and authentication (Req 3.4.1).
  - YAML configuration files stored in filesystem, read directly each time.
  - Simple database schema focused on core evaluation functionality.

### Key Properties

- Modular, API-driven architecture (Req 3.5).
- Cloud-ready design that supports scaling from single-user to 100+ users (Req 3.2).
- Emphasis on maintainability and error handling (Req 3.3, 3.5).

---

## 3.0 Architecture Diagram

The Memo AI Coach system follows a three-layer architecture designed for clarity, maintainability, and scalability:

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                          │
│                    (Streamlit - Req 2.1)                       │
├─────────────────────────────────────────────────────────────────┤
│  Text Input  │ Overall Feedback │ Detailed Feedback │ Help     │
│  (Req 2.1.1) │   (Req 2.2.3a)   │   (Req 2.2.3b)    │(Req 2.1.4)│
│              │                  │                   │          │
│  Debug       │ Admin            │ Session State     │          │
│(Req 2.5.1-3) │(Req 2.4.1-3)     │ Management       │          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼ HTTP/JSON
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND LAYER                             │
│                    (FastAPI - Req 2.2)                         │
├─────────────────────────────────────────────────────────────────┤
│  EvaluationService  │  AdminService  │  AuthenticationService   │
│   (Req 2.2.1-4)     │  (Req 2.4.1-3) │     (Req 3.4.1-5)        │
│                     │                │                          │
│  LLMConnector       │  DebugService  │  SessionService          │
│   (Req 2.3.1-6)     │  (Req 2.5.1-3) │     (Req 3.4.2-3)        │
│                     │                │                          │
│  PromptBuilder      │  ConfigService │  AuthorizationMiddleware │
│   (Req 2.3.1-2)     │  (Req 2.4.2-3) │     (Req 3.4.3-4)        │
│                     │                │                          │
│  ResponseParser     │  Rate Limiting │  Error Handling          │
│   (Req 2.3.3-6)     │  (Req 3.4.3)   │     (Req 3.3.2)          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼ SQL/File I/O
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                              │
│                    (SQLite + YAML)                             │
├─────────────────────────────────────────────────────────────────┤
│  Database Tables    │  Configuration Files │  Session Storage   │
│  (Req 2.2.1-4)      │     (Req 2.4.1-3)    │   (Req 3.4.1-3)    │
│                     │                      │                    │
│  • users            │  • rubric.yaml       │  • Session tokens  │
│  • sessions         │  • prompt.yaml       │  • User sessions   │
│  • submissions      │  • llm.yaml          │  • Admin sessions  │
│  • evaluations      │  • auth.yaml         │  • Rate limits     │
│                     │                      │                    │
│  WAL Mode           │  Direct File Access  │  Secure Storage    │
│  (Req 3.2.2)        │  (Req 2.4.3)         │  (Req 3.4.1-5)     │
└─────────────────────────────────────────────────────────────────┘
```

**Key Architecture Principles:**
- **Modular Design**: Clear separation between frontend, backend, and data layers
- **API-Driven**: RESTful API communication between frontend and backend
- **Session-Based**: Secure session management for user isolation (anonymous users with admin user accounts)
- **Synchronous Processing**: Immediate feedback for evaluation requests
- **Scalable**: SQLite with WAL mode supports 100+ concurrent users
- **Maintainable**: Simple, focused components with clear responsibilities

**Component Mapping to Requirements:**
- **Frontend Components**: Implement Req 2.1 (User Interface)
- **Backend Services**: Implement Req 2.2-2.5 (Text Submission, Evaluation, Admin, Debug)
- **Data Layer**: Implement Req 3.4 (Security) and support Req 3.2 (Scalability)
- **Performance**: Optimized for Req 3.1 (Performance targets)
- **Maintainability**: Designed for Req 3.5 (Maintainability requirements)

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
  - `/evaluations/submit` - Text submission for LLM evaluation
  - `/evaluations/{id}` - Retrieve evaluation results with detailed feedback (Req 2.2.3a, 2.2.3b)
  - `/admin/config/*` - YAML configuration file management
  - `/debug` - Debug output, performance metrics, raw prompts/responses (admin-only, Req 2.4)

**Suggested Components:**
- `EvaluationService` (synchronous LLM evaluation processing)
- `AdminService` (simple configuration management)
- `AuthenticationService` (session-based authentication with admin support)
- `SessionService` (session lifecycle and validation)
- `AuthorizationMiddleware` (session-based authorization)
- `DebugService`
- `ConfigurationService` (direct filesystem configuration management)

### 4.3 LLM Engine Integration

- **Provider:** The system uses **Claude** as the default LLM provider, but the architecture allows for easy configuration to support alternative LLMs in the future.
- **Backend Prompt Generation:** The backend dynamically generates prompts by combining content from rubric.yaml and prompt.yaml. The PromptBuilder component reads framework definitions from rubric.yaml and populates template variables in prompt.yaml to create customized prompts.
- **JSON Response Format:** The LLM is configured to respond in structured JSON format as defined in prompt.yaml response schemas, ensuring reliable parsing and consistent data structure.
- **Debugging:** The integration exposes debug data for troubleshooting and transparency, while ensuring that no sensitive information is leaked.

**Component Explanations:**

- `LLMConnector`: Handles all communication with the LLM provider (e.g., sending prompts to Claude and receiving responses). It abstracts the details of the LLM API, making it easy to swap providers if needed.
- `PromptBuilder`: Responsible for dynamically assembling the final prompt sent to the LLM. It reads framework definitions from rubric.yaml and populates template variables in prompt.yaml to create customized prompts. It combines the rubric content, framework definitions, prompt templates, and user input into a structured prompt that guides the LLM to produce the desired evaluation in JSON format.
- `ResponseParser`: Processes and interprets the JSON response from the LLM, extracting structured data such as overall feedback and segment-level evaluations for use by other backend services. It validates the JSON structure against the defined response schemas in prompt.yaml.
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
- `UserRepository` (admin user credentials and profiles)
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
4. Backend dynamically constructs prompt using rubric.yaml framework definitions and prompt.yaml templates (`PromptBuilder`)
5. Backend sends prompt to LLM engine (`LLMConnector`)
6. LLM processes and returns JSON evaluation response
7. Backend parses JSON response into structured data (`ResponseParser`)
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
   - Backend generates secure session_id on first request
   - All requests include session_id in headers/cookies
   - Backend validates session existence and expiration
   - Session data isolated by session_id
   - Admin sessions validated for management functions

2. **Admin Authentication:**
   - Admin credentials validated via simple password check
   - Admin session provides elevated access to management functions
   - Admin sessions tracked in `SessionRepository`

3. **Future Enhancement:**
   - JWT authentication can be implemented for production deployment
   - Current session-based approach provides sufficient isolation
   - Enhanced user management features can be added as needed

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
- Configuration files read directly from filesystem each time
- Startup validation ensures all YAML files are present and valid
- Simple filesystem-based configuration management

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

**Rate Limiting Implementation:**
- In-memory rate limiting suitable for single-instance deployment
- Per-session rate limiting for text submissions and admin operations
- Rate limit data lost on server restart (acceptable for development)
- Database-backed rate limiting recommended for production multi-instance deployment

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
- Option to display spanish site
- Have the AI make questions to prepare the human for presentation of the memo

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

## 7.0 Development Team Considerations

### 7.1 Novice Programmer Support Architecture
**7.1.1 Simplified Component Design**
- **Clear Boundaries**: Each component has a single, well-defined responsibility
- **Minimal Dependencies**: Components are loosely coupled with clear interfaces
- **Straightforward Data Flow**: Linear, easy-to-follow data movement between components
- **Predictable Behavior**: Components behave consistently and predictably

**7.1.2 Learning-Friendly Patterns**
- **Explicit Interfaces**: All component interactions are clearly defined
- **Simple State Management**: Centralized state with clear update patterns
- **Error Handling**: Comprehensive error handling with educational messages
- **Debugging Support**: Built-in debugging capabilities for understanding system behavior

**7.1.3 Educational Architecture**
- **Modular Structure**: Easy to understand and modify individual components
- **Configuration-Driven**: Behavior controlled through simple configuration files
- **Documentation Integration**: Architecture supports comprehensive documentation
- **Progressive Enhancement**: Simple base functionality with optional advanced features

### 7.2 AI Coding Agent Collaboration Support
**7.2.1 Code Generation-Friendly Design**
- **Consistent Patterns**: Standardized patterns across all components
- **Clear Contracts**: Well-defined interfaces and data structures
- **Predictable Structure**: Consistent file and component organization
- **Template-Based**: Reusable patterns for common functionality

**7.2.2 Maintainability Focus**
- **Single Responsibility**: Each component has one clear purpose
- **Low Coupling**: Minimal dependencies between components
- **High Cohesion**: Related functionality grouped together
- **Clear Naming**: Descriptive names that explain purpose and function

**7.2.3 Extensibility for Learning**
- **Plugin Architecture**: Easy to add new features without modifying existing code
- **Configuration Extensions**: New capabilities added through configuration
- **API Extensions**: Clear patterns for adding new API endpoints
- **UI Extensions**: Modular UI components for new features

### 7.3 Implementation Guidelines for Development Team
**7.3.1 Code Organization**
- **Logical Grouping**: Related functionality organized in clear directory structures
- **Consistent Naming**: Standard naming conventions throughout the codebase
- **Documentation Integration**: Code and documentation co-located where possible
- **Version Control**: Clear commit messages and change documentation

**7.3.2 Quality Standards**
- **Comprehensive Comments**: Every function and class thoroughly documented
- **Error Handling**: Clear, educational error messages and handling
- **Testing Support**: Architecture supports comprehensive testing
- **Debugging Tools**: Built-in debugging and monitoring capabilities

**7.3.3 Collaboration Support**
- **Clear Interfaces**: Well-defined boundaries between components
- **Documentation Standards**: Consistent documentation format and style
- **Code Review Process**: Architecture supports effective code reviews
- **Knowledge Transfer**: Design facilitates learning and understanding

---

## 8.0 Traceability Matrix

| Requirement ID | Requirement Description | Architecture Implementation | Status |
|---------------|------------------------|----------------------------|---------|
| 2.1.1 | Main page shows text input | Frontend Components (4.1) - TextInputPage | ✅ Implemented |
| 2.1.2 | Tab navigation fast | Frontend Components (4.1) - Tabbed navigation | ✅ Implemented |
| 2.1.3 | Info bubbles | Frontend Components (4.1) - Information tooltips | ✅ Implemented |
| 2.1.4 | Help tab resources | Frontend Components (4.1) - HelpPage | ✅ Implemented |
| 2.1.5 | Clean visuals | Frontend Components (4.1) - Visual design system | ✅ Implemented |
| 2.2.1 | Text input box available | Backend Services (4.2) - EvaluationService | ✅ Implemented |
| 2.2.2 | Submission processed by LLM | LLM Engine Integration (4.3) - LLMConnector | ✅ Implemented |
| 2.2.3a | Overall evaluation returned | Backend Services (4.2) - EvaluationService | ✅ Implemented |
| 2.2.3b | Segment evaluation returned | Backend Services (4.2) - EvaluationService | ✅ Implemented |
| 2.2.4 | Evaluation processing straightforward | Backend Services (4.2) - Synchronous processing | ✅ Implemented |
| 2.3.1 | System uses grading rubric | LLM Engine Integration (4.3) - PromptBuilder | ✅ Implemented |
| 2.3.2 | System uses prompt templates | LLM Engine Integration (4.3) - PromptBuilder | ✅ Implemented |
| 2.3.3 | Overall strengths/opportunities | LLM Engine Integration (4.3) - ResponseParser | ✅ Implemented |
| 2.3.4 | Detailed rubric grading | LLM Engine Integration (4.3) - ResponseParser | ✅ Implemented |
| 2.3.5 | Segment-level evaluation | LLM Engine Integration (4.3) - ResponseParser | ✅ Implemented |
| 2.3.6 | Immediate feedback processing | Backend Services (4.2) - Real-time response | ✅ Implemented |
| 2.4.1 | Admin edits YAML | Backend Services (4.2) - AdminService | ✅ Implemented |
| 2.4.2 | Configuration changes validated | Backend Services (4.2) - ConfigurationService | ✅ Implemented |
| 2.4.3 | Simple configuration management | Backend Services (4.2) - AdminService | ✅ Implemented |
| 2.5.1 | Debug output accessible | Backend Services (4.2) - DebugService | ✅ Implemented |
| 2.5.2 | Raw prompts/responses shown | Backend Services (4.2) - DebugService | ✅ Implemented |
| 2.5.3 | Debug mode admin-only | Backend Services (4.2) - AuthorizationMiddleware | ✅ Implemented |
| 3.1.1 | Responsive system | Performance optimizations throughout | ✅ Implemented |
| 3.1.2 | Text submission response: < 15 seconds (LLM processing) | LLM Engine Integration (4.3) - Optimized processing | ✅ Implemented |
| 3.2.1 | System handles 10-20 users | Scalable architecture design | ✅ Implemented |
| 3.2.2 | Scales to 100+ users | SQLite WAL mode and optimizations | ✅ Implemented |
| 3.3.1 | High uptime | Error handling and logging | ✅ Implemented |
| 3.3.2 | Robust error handling | Comprehensive error handling | ✅ Implemented |
| 3.4.1 | Session-based authentication | AuthenticationService (4.2) with admin user accounts | ✅ Implemented |
| 3.4.2 | Secure session management | SessionService (4.2) with user isolation | ✅ Implemented |
| 3.4.3 | CSRF protection and rate limiting | AuthorizationMiddleware (4.2) | ✅ Implemented |
| 3.4.4 | Admin authentication | AuthenticationService (4.2) with users table | ✅ Implemented |
| 3.4.5 | Optional JWT authentication | Future enhancement ready | ⏳ Planned |
| 3.5.1 | Maintainability priority | Modular architecture design | ✅ Implemented |
| 3.5.2 | Maximum simplicity | Simple, focused component design | ✅ Implemented |
| 3.5.3 | Comprehensive comments | Documentation requirements | ✅ Implemented |
| 3.5.4 | Modular architecture | Modular component design | ✅ Implemented |

---

**Document ID**: 02_Architecture.md  
**Document Version**: 1.4  
**Last Updated**: Implementation Phase (Complete consistency fixes and standardization)  
**Next Review**: After initial deployment
