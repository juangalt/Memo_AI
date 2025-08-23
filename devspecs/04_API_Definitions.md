# 04_API_Definitions.md

## 1.0 Document Overview

### 1.1 Purpose
This document defines the REST API specifications for the Memo AI Coach project, including endpoint definitions, request/response schemas, authentication patterns, and data validation rules.

### 1.2 Scope
- REST API endpoint specifications
- Authentication and authorization patterns
- Request/response formats and validation
- Error handling and status codes
- Performance requirements and rate limiting

### 1.3 Dependencies
- **Architecture**: `02_Architecture.md` - System components and data flow
- **Data Model**: `03_Data_Model.md` - Database schema and relationships
- **Requirements**: `01_Requirements.md` - Functional requirements mapping

---

## 2.0 API Design Principles

### 2.1 REST API Standards
- **Resource-based URLs**: Clear resource identification in endpoints
- **HTTP Methods**: Standard GET, POST, PUT, DELETE usage
- **Stateless Design**: No server-side session state in API calls
- **Consistent Naming**: Plural nouns for resources, clear hierarchies

### 2.2 Response Format Standardization
All API responses follow a consistent structure:

```json
{
  "data": {},           // Actual response data
  "meta": {            // Metadata (pagination, timestamps, etc.)
    "timestamp": "ISO8601",
    "request_id": "uuid"
  },
  "errors": []         // Error array (empty on success)
}
```

### 2.3 HTTP Status Codes
- **200**: Success
- **201**: Created
- **400**: Bad Request (validation errors)
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **429**: Rate Limited
- **500**: Internal Server Error

### 2.4 API Versioning
- **URL-based versioning**: `/api/v1/` prefix for all endpoints
- **Backward compatibility**: Maintained within major versions
- **Version migration**: Clear upgrade paths documented

---

## 3.0 Authentication and Authorization

### 3.1 Authentication Strategy
**Session-Based Authentication System**:
- **Session Management**: Secure session tokens for user isolation
- **Admin Access**: Admin authentication for system management functions
- **Future Enhancement**: JWT authentication can be added if complex user management is needed
- **Simple Design**: Focuses on security without unnecessary complexity

### 3.2 Authentication Endpoints

#### 3.2.1 Session Management (Anonymous Mode)
```yaml
GET /api/v1/sessions/create
  description: Create anonymous session for MVP mode
  authentication: None required
  response:
    data:
      session_id: string (secure token)
      expires_at: datetime
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
    
POST /api/v1/sessions/validate
  description: Validate session token
  authentication: None required
  request:
    session_id: string
  response:
    data:
      valid: boolean
      expires_at: datetime
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
```

#### 3.2.2 User Authentication (Production Mode)
```yaml
POST /api/v1/auth/login
  description: User login with credentials
  authentication: None required
  request:
    username: string
    password: string
  response:
    data:
    user: {id, username, is_admin}
    session_id: string
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
  cookies:
    jwt_token: httpOnly, secure
    csrf_token: string

POST /api/v1/auth/logout
  description: User logout and session cleanup
  authentication: Valid session required
  response:
    data:
    success: boolean
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []

GET /api/v1/auth/verify
  description: Verify JWT token and session
  authentication: Valid session required
  response:
    data:
    user: {id, username, is_admin}
    session_valid: boolean
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []

POST /api/v1/auth/refresh
  description: Refresh JWT token
  authentication: Valid JWT required
  response:
    data:
    user: {id, username, is_admin}
    expires_at: datetime
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
```

#### 3.2.3 User Management (Admin Only)
```yaml
POST /api/v1/users
  description: Create new user account
  authentication: Admin required
  request:
    username: string
    email: string (optional)
    password: string
    is_admin: boolean (default: false)
  response:
    data:
      user: {id, username, email, is_admin, created_at}
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []

GET /api/v1/users
  description: List all users
  authentication: Admin required
  response:
    data:
    users: [{id, username, email, is_active, created_at}]
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []

PUT /api/v1/users/{user_id}
  description: Update user account
  authentication: Admin or self
  request:
    username: string (optional)
    email: string (optional)
    is_active: boolean (optional)
  response:
    data:
      user: {id, username, email, is_active, updated_at}
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
```

---

## 4.0 Core Application Endpoints

### 4.1 Text Evaluation Endpoints [MVP]
**Design Philosophy**: All evaluation endpoints follow asynchronous-first design patterns. The system was designed from inception to handle LLM processing asynchronously for optimal user experience and scalability.

#### 4.1.1 Submit Text for Evaluation (Asynchronous by Design)
```yaml
POST /api/v1/evaluations/submit
  description: Submit text for LLM evaluation with detailed feedback (asynchronous-first design)
  authentication: Session required (any mode)
  design_note: System designed async from inception for consistent UX and scalability
  request:
    text_content: string (max 10,000 chars)
    session_id: string (Anonymous) | derived from JWT (Authenticated)
  response:
    data:
      evaluation_id: string
      status: "queued"
      estimated_completion: datetime (current_time + 60 seconds)
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
```

#### 4.1.2 Check Evaluation Status
```yaml
GET /api/v1/evaluations/{evaluation_id}/status
  description: Check the status of an evaluation in progress
  authentication: Session owner or admin
  response:
    data:
      evaluation_id: string
      status: "queued" | "processing" | "completed" | "failed"
      progress_percentage: integer (0-100)
      estimated_completion: datetime (if processing)
      completed_at: datetime (if completed)
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
```

#### 4.1.3 Retrieve Evaluation Results
```yaml
GET /api/v1/evaluations/{evaluation_id}
  description: Retrieve completed evaluation details and results
  authentication: Session owner or admin
  response:
    data:
      evaluation:
        overall_score: decimal
        strengths: string
        opportunities: string
        rubric_scores: object
        segment_feedback: array
        evaluation_timestamp: datetime
        processing_time: decimal (seconds)
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
  error_responses:
    404: Evaluation not found or not accessible
    425: Evaluation still processing (use status endpoint)
```

### 4.2 Configuration Management Endpoints [MVP]

#### 4.2.1 Individual Configuration Management
```yaml
GET /api/v1/admin/config/{config_type}
  description: Get current configuration file content
  authentication: Admin required
  parameters:
    config_type: enum [rubric, frameworks, context, prompt, auth, security, frontend, backend, database, llm, logging, monitoring, performance]
  response:
    data:
      config_content: string (YAML)
      file_path: string
      last_modified: datetime
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []

POST /api/v1/admin/config/{config_type}
  description: Update configuration file with validation and versioning
  authentication: Admin required
  request:
    config_content: string (YAML)
    change_reason: string (optional)
  response:
    data:
      validation_result: {is_valid, errors}
      file_updated: boolean
      version_logged: boolean
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []

GET /api/v1/admin/config/{config_type}/history
  description: Get configuration change history
  authentication: Admin required
  response:
    data:
      versions: [{id, old_content, new_content, changed_by, changed_at, change_reason}]
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
```

#### 4.2.2 Bulk Configuration Management
```yaml
GET /api/v1/admin/config/categories
  description: Get all configuration categories and their purposes
  authentication: Admin required
  response:
    data:
      categories:
        business_logic: ["rubric", "frameworks", "context", "prompt"]
        system_security: ["auth", "security"]
        component_config: ["frontend", "backend"]
        infrastructure: ["database", "llm"]
        operations: ["logging", "monitoring", "performance"]
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []

POST /api/v1/admin/config/validate-all
  description: Validate all configuration files
  authentication: Admin required
  response:
    data:
      validation_results: {config_type: {is_valid, errors}}
      overall_status: "valid" | "invalid"
      failed_configs: array
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []

GET /api/v1/admin/config/bulk-export
  description: Export all configuration files as ZIP (direct file serving)
  authentication: Admin required
  response:
    Content-Type: application/zip
    Content-Disposition: attachment; filename="memoai-config-export-{timestamp}.zip"
    File: Direct file serving from temporary storage (24-hour retention)
    
POST /api/v1/admin/config/bulk-import
  description: Import and validate multiple configuration files (direct file handling)
  authentication: Admin required
  request:
    Content-Type: multipart/form-data
    files: configuration files (max 10MB total)
    validate_only: boolean (default: false)
  response:
    data:
      imported_configs: array
      validation_results: object
      applied: boolean
      hot_reloaded: boolean (true for business logic configs)
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
```

### 4.3 Debug and System Management Endpoints [MVP]

#### 4.3.1 Debug Information
```yaml
GET /api/v1/debug/info
  description: Get debug information when debug mode enabled (admin-only for security)
  authentication: Admin required
  response:
    data:
      debug_enabled: boolean
      performance_metrics: object
      raw_prompts: array (if debug mode enabled)
      raw_responses: array (if debug mode enabled)
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
    
POST /api/v1/admin/debug/toggle
  description: Enable/disable global debug mode
  authentication: Admin required
  request:
    debug_enabled: boolean
  response:
    data:
      debug_mode: boolean
      affected_evaluations: "all_new"
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
```

#### 4.3.2 Authentication Configuration
```yaml
GET /api/v1/admin/auth/config
  description: Get authentication configuration status
  authentication: Admin required
  response:
    data:
      auth_enabled: boolean
      session_timeout: integer
      max_login_attempts: integer
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []

PUT /api/v1/admin/auth/config
  description: Update authentication configuration
  authentication: Admin required
  request:
    auth_enabled: boolean
    session_timeout: integer
    max_login_attempts: integer
  response:
    data:
      updated: boolean
      config_applied: boolean
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
```

---

## 5.0 Post-MVP Endpoints

### 5.1 Chat Functionality [Post-MVP]
```yaml
POST /api/v1/chat/sessions
  description: Start chat session after evaluation
  authentication: Session required
  request:
    evaluation_id: integer
  response:
    data:
      chat_session_id: string
      context_loaded: boolean
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []

POST /api/v1/chat/sessions/{session_id}/messages
  description: Send message in chat session
  authentication: Session required
  request:
    message_content: string
  response:
    data:
      message_id: string
      assistant_response: string
      context_used: boolean
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
```

### 5.2 Progress Tracking [Post-MVP]
```yaml
GET /api/v1/progress/{session_id}
  description: Get progress data for session
  authentication: Session owner or admin
  response:
    data:
      overall_trends: array
      rubric_improvements: object
      submission_frequency: object
      cached: boolean
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
```

### 5.3 PDF Export [Post-MVP]
```yaml
GET /api/v1/export/pdf/{evaluation_id}
  description: Download PDF export of evaluation (direct file serving)
  authentication: Session owner or admin
  response:
    Content-Type: application/pdf
    Content-Disposition: attachment; filename="evaluation-{evaluation_id}-{timestamp}.pdf"
    File: Direct file serving from temporary storage (24-hour retention)
```

---

## 6.0 Data Validation and Security

### 6.1 Input Validation Rules
- **Text Content**: Max 10,000 characters, XSS sanitization, UTF-8 encoding
- **Session ID**: Format validation (UUID v4), expiration checks
- **YAML Configuration**: Schema validation, syntax checking, required field validation, UTF-8 encoding
- **Configuration Types**: Must be one of: 'rubric', 'frameworks', 'context', 'prompt', 'auth', 'security', 'frontend', 'backend', 'database', 'llm', 'logging', 'monitoring', 'performance'
- **Authentication**: Username/password length limits, character restrictions

### 6.2 Output Sanitization
- **User Content**: HTML entity encoding, script tag removal
- **Error Messages**: No sensitive information exposure, generic error codes
- **Debug Data**: Authentication token removal, PII scrubbing

### 6.3 Security Implementation
- **JWT Configuration**: HS256 algorithm, configurable secret key rotation
- **Session Security**: Secure random tokens (32 bytes), httpOnly cookies
- **Password Policy**: bcrypt hashing with cost factor 12
- **CSRF Protection**: Double-submit cookie pattern for state-changing operations
- **Authorization Middleware**: `AuthorizationMiddleware` validates all protected endpoints
- **Role-based Access**: Admin vs regular user permissions
- **Session Isolation**: Data access restricted by session_id/user_id

### 6.4 Error Response Format
```json
{
  "data": null,
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "uuid"
  },
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "message": "Invalid input provided",
      "field": "text_content",
      "details": "Text content exceeds maximum length"
    }
  ]
}
```

---

## 7.0 Performance and Rate Limiting

### 7.1 Response Time Targets
- **Page Load**: < 1 second
- **Text Submission**: < 60 seconds (LLM processing)
- **Chat Messages**: < 5 seconds
- **Admin Operations**: < 3 seconds
- **Progress Data**: < 2 seconds (cached)
- **Configuration Operations**: < 3 seconds

### 7.2 Rate Limiting Policies (In-Memory Implementation)
- **Text Submissions**: 20 per hour per session (in-memory tracking)
- **Chat Messages**: 50 per hour per session (in-memory tracking)
- **Admin Operations**: 100 per hour per admin user (in-memory tracking)
- **Configuration Changes**: 20 per hour per admin user (in-memory tracking)
- **Global API**: 1000 requests per hour per IP (in-memory tracking)
- **Headers**: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
- **Implementation**: Sliding window algorithm with in-memory storage
- **Scope**: Per-instance rate limiting (suitable for single-instance MVP deployment)
- **Future Enhancement**: Database-backed rate limiting for multi-instance deployments

### 7.3 Caching Strategies
- **Progress Data**: 1-hour cache with invalidation on new evaluations
- **Configuration Files**: Direct filesystem reads (no caching)
- **Static Content**: Browser caching with ETags
- **API Responses**: No caching for dynamic content

---

## 8.0 Key Architectural Decisions

### 8.1 Resolved Design Decisions

#### 8.1.1 Authentication Strategy ✅ **RESOLVED**
- **Decision**: Hybrid JWT + Session system with configuration toggle
- **Rationale**: Supports MVP (session-only) and production (JWT + session) modes
- **Implementation**: Seamless transition maintaining session_id compatibility

#### 8.1.2 Response Format ✅ **RESOLVED**
- **Decision**: Standardized JSON response structure with data/meta/errors
- **Rationale**: Consistent client-side handling, extensible metadata support
- **Implementation**: All endpoints follow same response pattern

#### 8.1.3 Configuration Management ✅ **RESOLVED**
- **Decision**: Comprehensive 13-file YAML configuration system
- **Rationale**: Separation of concerns, version tracking, admin control
- **Implementation**: Category-based organization with validation and versioning

---

## 9.0 Implementation Decisions

- **File handling**: Direct file serving with temporary storage and automatic cleanup
- **Configuration**: Hot-reload for business logic configs, restart for system configs
- **Rate limiting**: In-memory implementation for MVP deployment
- **Documentation**: Auto-generated OpenAPI/Swagger from FastAPI code

## 10.0 Implementation Priority

### 10.1 Phase 1: MVP Core
1. Authentication endpoints (session management)
2. Text evaluation endpoints (submit, status, results)
3. Basic configuration management
4. Debug endpoints (admin-only)
5. Error handling and validation

### 10.2 Phase 2: Enhanced Features
1. Complete configuration management system
2. User management endpoints
3. Chat functionality endpoints
4. Progress tracking endpoints
5. PDF export endpoints

---

## 11.0 Traceability Matrix

|| **Requirement** | **API Endpoints** | **Status** |
||-----------------|-------------------|------------|
|| Text Evaluation (2.2) | `/evaluations/submit`, `/evaluations/{id}` | MVP |
|| Chat with LLM (2.3) | `/chat/sessions`, `/chat/sessions/{id}/messages` | Post-MVP |
|| Admin Functions (2.4) | `/admin/config/*`, `/admin/auth/config` | MVP |
|| Debug Mode (2.5) | `/debug/info`, `/admin/debug/toggle` | MVP |
|| Progress Tracking (2.6) | `/progress/{session_id}` | Post-MVP |
|| PDF Export (2.7) | `/export/pdf/{evaluation_id}` | Post-MVP |
|| Authentication (3.4) | `/auth/*`, `/sessions/*`, `/users/*` | MVP |

---

**Document Version**: 2.0
**Last Updated**: Implementation Phase
**Next Review**: After MVP deployment
