# API Definitions Specification
## Memo AI Coach

**Document ID**: 04_API_Definitions.md  
**Document Version**: 1.2  
**Last Updated**: Implementation Phase (Updated with critical and high impact fixes)  
**Next Review**: After initial deployment  
**Status**: Approved

---

## 1.0 Document Information

### 1.1 Purpose
Defines the REST API specifications for the Memo AI Coach project, including endpoint definitions, request/response schemas, authentication patterns, and data validation rules.

### 1.2 Scope
- REST API endpoint specifications and design principles
- Authentication and authorization patterns
- Request/response formats and validation rules
- Error handling and status codes
- Performance requirements and rate limiting

### 1.3 Dependencies
- **Prerequisites**: 00_ProjectOverview.md, 01_Requirements.md, 02_Architecture.md, 03_Data_Model.md
- **Related Documents**: 05_UI_UX.md
- **Requirements**: Implements API requirements from 01_Requirements.md (Req 2.2-2.5, 3.4)

### 1.4 Document Structure
1. Document Information
2. API Design Principles
3. Authentication and Authorization
4. Core Application Endpoints
5. Error Handling and Validation
6. Performance and Rate Limiting
7. Traceability Matrix

### 1.5 Traceability Summary
| Requirement ID | Requirement Description | API Implementation | Status |
|---------------|------------------------|-------------------|---------|
| 2.2.1-2.2.4 | Text Submission Requirements | /evaluations/submit | ✅ Implemented |
| 2.3.1-2.3.6 | Text Evaluation Requirements | /evaluations/{id} | ✅ Implemented |
| 2.4.1-2.4.3 | Admin Functions Requirements | /admin/config/* | ✅ Implemented |
| 2.5.1-2.5.3 | Debug Mode Requirements | /debug/* | ✅ Implemented |
| 3.4.1-3.4.5 | Security Requirements | Authentication Endpoints | ✅ Implemented |

### 1.6 Document Navigation
- **Previous Document**: 03_Data_Model.md
- **Next Document**: 05_UI_UX.md
- **Related Documents**: 06_Testing.md

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
- **Scope**: Session-only authentication system

### 3.2 Authentication Endpoints

#### 3.2.1 Session Management
```yaml
GET /api/v1/sessions/create
  description: Create new session for user
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

#### 3.2.2 User Authentication
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
    session_token: httpOnly, secure
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
  description: Verify session token and session
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
  description: Refresh session token
  authentication: Valid session required
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

### 4.1 Text Evaluation Endpoints
**Design Philosophy**: Simple synchronous evaluation system for reliable performance.

#### 4.1.1 Submit Text for Evaluation
```yaml
POST /api/v1/evaluations/submit
  description: Submit text for synchronous LLM evaluation with immediate feedback
  authentication: Session required
  request:
    text_content: string (max 10,000 chars)
    session_id: string
  response:
    data:
      evaluation:
        overall_score: decimal
        strengths: string
        opportunities: string
        rubric_scores: object
        segment_feedback: array
        processing_time: decimal (seconds)
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
```

#### 4.1.2 Retrieve Evaluation Results
```yaml
GET /api/v1/evaluations/{evaluation_id}
  description: Retrieve evaluation details and results
  authentication: Session owner or admin
  response:
    data:
      evaluation:
        overall_score: decimal
        strengths: string
        opportunities: string
        rubric_scores: object
        segment_feedback: array
        processing_time: decimal (seconds)
        created_at: datetime
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
  error_responses:
    404: Evaluation not found or not accessible
```

### 4.2 Configuration Management Endpoints

#### 4.2.1 Configuration Management
```yaml
GET /api/v1/admin/config/{config_type}
  description: Get current configuration file content
  authentication: Admin required
  parameters:
    config_type: enum [rubric, prompt, llm, auth]
  response:
    data:
      config_content: string (YAML)
      file_path: string
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []

POST /api/v1/admin/config/{config_type}
  description: Update configuration file with validation
  authentication: Admin required
  request:
    config_content: string (YAML)
  response:
    data:
      validation_result: {is_valid, errors}
      file_updated: boolean
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
```



### 4.3 Debug and System Management Endpoints

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
GET /api/v1/admin/auth/status
  description: Get authentication system status
  authentication: Admin required
  response:
    data:
      auth_system: "session-based"
      active_sessions: integer
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
```

---

## 6.0 Data Validation and Security

### 6.1 Input Validation Rules
- **Text Content**: Max 10,000 characters, XSS sanitization, UTF-8 encoding
- **Session ID**: Format validation (UUID v4), expiration checks
- **YAML Configuration**: Schema validation, syntax checking, required field validation, UTF-8 encoding
- **Configuration Types**: Must be one of: 'rubric', 'prompt', 'llm', 'auth'
- **Authentication**: Username/password length limits, character restrictions

### 6.2 Output Sanitization
- **User Content**: HTML entity encoding, script tag removal
- **Error Messages**: No sensitive information exposure, generic error codes
- **Debug Data**: Authentication token removal, PII scrubbing

### 6.3 Security Implementation
- **Session Security**: Secure random tokens, httpOnly cookies
- **Password Policy**: Simple password validation for admin access
- **CSRF Protection**: Basic CSRF protection for state-changing operations
- **Authorization Middleware**: `AuthorizationMiddleware` validates all protected endpoints
- **Role-based Access**: Admin vs regular user permissions
- **Session Isolation**: Data access restricted by session_id

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

### 6.5 Error Codes and Messages

#### 6.5.1 Validation Errors
- **VALIDATION_ERROR**: Input validation failures
  - `text_content`: Text content validation (empty, too long, invalid characters)
  - `session_id`: Session ID format or expiration validation
  - `config_content`: YAML configuration validation (syntax, schema, required fields)
  - `username`: Username validation (length, characters, uniqueness)
  - `password`: Password validation (length, complexity)

#### 6.5.2 Authentication Errors
- **UNAUTHORIZED**: Authentication required but not provided
- **INVALID_SESSION**: Session token invalid or expired
- **ADMIN_REQUIRED**: Admin privileges required for operation
- **INVALID_CREDENTIALS**: Username/password combination invalid

#### 6.5.3 Authorization Errors
- **FORBIDDEN**: User lacks permission for requested operation
- **SESSION_OWNERSHIP**: User attempting to access another session's data
- **RATE_LIMITED**: User has exceeded rate limits

#### 6.5.4 System Errors
- **LLM_ERROR**: LLM provider communication failure
- **CONFIGURATION_ERROR**: Configuration file access or validation failure
- **DATABASE_ERROR**: Database operation failure
- **INTERNAL_ERROR**: Unexpected system error

#### 6.5.5 Resource Errors
- **NOT_FOUND**: Requested resource not found
- **EVALUATION_NOT_FOUND**: Evaluation ID not found or not accessible
- **CONFIG_NOT_FOUND**: Configuration file not found
- **USER_NOT_FOUND**: User account not found

### 6.6 Error Response Examples

#### 6.6.1 Text Submission Validation Error
```json
{
  "data": null,
  "meta": {
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req-12345"
  },
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "message": "Text content validation failed",
      "field": "text_content",
      "details": "Text content exceeds maximum length of 10,000 characters"
    }
  ]
}
```

#### 6.6.2 Authentication Error
```json
{
  "data": null,
  "meta": {
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req-12346"
  },
  "errors": [
    {
      "code": "INVALID_SESSION",
      "message": "Session token is invalid or expired",
      "field": "session_id",
      "details": "Please create a new session"
    }
  ]
}
```

#### 6.6.3 LLM Processing Error
```json
{
  "data": null,
  "meta": {
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req-12347"
  },
  "errors": [
    {
      "code": "LLM_ERROR",
      "message": "LLM processing failed",
      "field": null,
      "details": "Unable to process evaluation request. Please try again."
    }
  ]
}
```

---

## 7.0 Performance and Rate Limiting

### 7.1 Response Time Targets
- **Page Load**: < 1 second
- **Text Submission**: < 15 seconds (LLM processing)
- **Admin Operations**: < 3 seconds
- **Configuration Operations**: < 3 seconds

### 7.2 Rate Limiting Policies (In-Memory Implementation)
- **Text Submissions**: 20 per hour per session (in-memory tracking)
- **Admin Operations**: 100 per hour per admin user (in-memory tracking)
- **Configuration Changes**: 20 per hour per admin user (in-memory tracking)
- **Global API**: 1000 requests per hour per IP (in-memory tracking)
- **Headers**: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
- **Implementation**: Sliding window algorithm with in-memory storage
- **Scope**: Per-instance rate limiting (suitable for single-instance deployment)
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
- **Decision**: Session-based authentication with JWT enhancement path
- **Rationale**: Supports simplicity while providing clear upgrade path to production features
- **Implementation**: Session-only system with documented JWT migration path
- **Future Enhancement**: JWT authentication can be added for production deployment with token-based authentication

#### 8.1.2 Response Format ✅ **RESOLVED**
- **Decision**: Standardized JSON response structure with data/meta/errors
- **Rationale**: Consistent client-side handling, extensible metadata support
- **Implementation**: All endpoints follow same response pattern

#### 8.1.3 Configuration Management ✅ **RESOLVED**
- **Decision**: 4 essential YAML configuration files for complete system management
- **Rationale**: Separation of concerns, admin control, simple maintenance
- **Implementation**: Essential files organization with validation and direct filesystem access

---

## 9.0 Implementation Decisions

- **File handling**: Direct file serving with temporary storage and automatic cleanup
- **Configuration**: Hot-reload for business logic configs, restart for system configs
- **Rate limiting**: In-memory implementation for development deployment
- **Documentation**: Auto-generated OpenAPI/Swagger from FastAPI code
- **Future Enhancements**: Chat functionality and advanced features can be added in future phases

## 10.0 Implementation Priority

### 10.1 Phase 1: Core Development
1. Authentication endpoints (session management)
2. Text evaluation endpoints (submit, status, results)
3. Basic configuration management
4. Debug endpoints (admin-only)
5. Error handling and validation

### 10.2 Phase 2: Enhanced Features
1. User management endpoints
2. Progress tracking endpoints
3. PDF export endpoints
4. Advanced configuration features

---

## 11.0 Traceability Matrix

| Requirement ID | Requirement Description | API Implementation | Status |
|---------------|------------------------|-------------------|---------|
| 2.2.1 | Text input box available | POST /api/v1/evaluations/submit | ✅ Implemented |
| 2.2.2 | Submission processed by LLM | POST /api/v1/evaluations/submit (synchronous) | ✅ Implemented |
| 2.2.3a | Overall evaluation returned | GET /api/v1/evaluations/{id} | ✅ Implemented |
| 2.2.3b | Segment evaluation returned | GET /api/v1/evaluations/{id} | ✅ Implemented |
| 2.2.4 | Evaluation processing straightforward | POST /api/v1/evaluations/submit (immediate response) | ✅ Implemented |
| 2.3.1 | System uses grading rubric | Configuration via /api/v1/admin/config/rubric | ✅ Implemented |
| 2.3.2 | System uses prompt templates | Configuration via /api/v1/admin/config/prompt | ✅ Implemented |
| 2.3.3 | Overall strengths/opportunities | Response format in /api/v1/evaluations/{id} | ✅ Implemented |
| 2.3.4 | Detailed rubric grading | Response format in /api/v1/evaluations/{id} | ✅ Implemented |
| 2.3.5 | Segment-level evaluation | Response format in /api/v1/evaluations/{id} | ✅ Implemented |
| 2.3.6 | Immediate feedback processing | Real-time response in /api/v1/evaluations/submit | ✅ Implemented |
| 2.4.1 | Admin edits YAML | POST /api/v1/admin/config/{config_type} | ✅ Implemented |
| 2.4.2 | Configuration changes validated | Validation in /api/v1/admin/config/{config_type} | ✅ Implemented |
| 2.4.3 | Simple configuration management | GET/POST /api/v1/admin/config/* | ✅ Implemented |
| 2.5.1 | Debug output accessible | GET /api/v1/debug/info | ✅ Implemented |
| 2.5.2 | Raw prompts/responses shown | GET /api/v1/debug/info | ✅ Implemented |
| 2.5.3 | Debug mode admin-only | Authorization middleware on /api/v1/debug/* | ✅ Implemented |
| 3.4.1 | Session-based authentication | POST /api/v1/sessions/create | ✅ Implemented |
| 3.4.2 | Secure session management | POST /api/v1/sessions/validate | ✅ Implemented |
| 3.4.3 | CSRF protection and rate limiting | Rate limiting middleware | ✅ Implemented |
| 3.4.4 | Admin authentication | POST /api/v1/auth/login | ✅ Implemented |
| 3.4.5 | Optional JWT authentication | Future enhancement ready | ⏳ Planned |

---

**Document ID**: 04_API_Definitions.md  
**Document Version**: 1.2  
**Last Updated**: Implementation Phase (Updated with critical and high impact fixes)  
**Next Review**: After initial deployment
