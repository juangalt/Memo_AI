# 04_API_Definitions.md

## 1.0 How to Use This File

1.1 **Audience**
- AI coding agents and human developers.

1.2 **Purpose**
- Defines the REST API endpoints, request/response schemas, and authentication patterns for the Memo AI Coach project.
- Builds directly on the architecture defined in `02_Architecture.md` and data model in `03_Data_Model.md`.

1.3 **Next Steps**
- Review this file before proceeding to `05_UI_UX.md`.

---

## 2.0 Key High-Level Decisions Needed

### 2.1 API Authentication Strategy
**DECISION**: JWT + Session hybrid authentication system implemented
- **MVP Mode**: Session-based authentication using secure session tokens
- **Production Mode**: JWT tokens with httpOnly cookies + session validation
- **Toggle**: Configuration-based enable/disable without code changes
- **Transition**: Seamless transition maintaining existing session_id compatibility

### 2.2 Request/Response Format Standardization ✅ **RESOLVED**
**DECISION**: Standardized response format across all endpoints
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
**HTTP Status Codes**:
- 200: Success
- 400: Bad Request (validation errors)
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Rate Limited
- 500: Internal Server Error

### 2.3 API Versioning Strategy
**Question**: How should we prepare for future API changes?
- Should we implement versioning from the start (v1 prefix) or defer until needed?
- URL-based versioning (/api/v1/) vs header-based vs parameter-based?
- How do we handle backward compatibility?

### 2.4 File Upload and Download Handling
**Question**: How should we handle PDF exports and potential file uploads?
- Direct file serving vs signed URLs vs streaming responses?
- Where should generated PDFs be stored temporarily?
- What's the cleanup strategy for temporary files?

### 2.5 Real-time vs Polling for LLM Responses
**Question**: How should we handle potentially long-running LLM evaluation requests?
- Synchronous requests with longer timeouts?
- Asynchronous with polling endpoints?
- WebSocket connections for real-time updates?
- Server-sent events for progress updates?

### 2.6 Rate Limiting and Performance
**Question**: What rate limiting should we implement to prevent abuse?
- Per-session rate limits for text submissions?
- Per-IP rate limits for the overall API?
- Different limits for different endpoint types?
- How do we handle rate limit responses?

### 2.7 API Documentation Strategy
**Question**: How should we document and maintain API specifications?
- Auto-generated OpenAPI/Swagger documentation?
- Manual documentation with examples?
- Interactive API explorer for development?
- How do we keep documentation in sync with implementation?

### 2.8 Error Handling and Validation
**Question**: How should we handle input validation and error responses?
- Client-side validation vs server-side validation vs both?
- Detailed validation error messages vs simple error codes?
- How do we handle LLM provider errors gracefully?
- What's the fallback strategy for service failures?

---

## 3.0 Placeholder Sections

### 3.1 Authentication Endpoints

#### 3.1.1 Session Management (Anonymous Mode)
```yaml
GET /api/v1/sessions/create
  description: Create anonymous session for anonymous mode
  response:
    session_id: string (secure token)
    expires_at: datetime
    
POST /api/v1/sessions/validate
  description: Validate session token
  request:
    session_id: string
  response:
    valid: boolean
    expires_at: datetime
```

#### 3.1.2 User Authentication (Authenticated Mode)
```yaml
POST /api/v1/auth/login
  description: User login with credentials
  request:
    username: string
    password: string
  response:
    user: {id, username, is_admin}
    session_id: string
  cookies:
    jwt_token: httpOnly, secure
    csrf_token: string

POST /api/v1/auth/logout
  description: User logout and session cleanup
  response:
    success: boolean

GET /api/v1/auth/verify
  description: Verify JWT token and session
  response:
    user: {id, username, is_admin}
    session_valid: boolean

POST /api/v1/auth/refresh
  description: Refresh JWT token
  response:
    user: {id, username, is_admin}
    expires_at: datetime
```

#### 3.1.3 User Management (Admin Only)
```yaml
POST /api/v1/users
  description: Create new user account
  authentication: Admin required
  request:
    username: string
    email: string (optional)
    password: string
    is_admin: boolean (default: false)

GET /api/v1/users
  description: List all users
  authentication: Admin required
  response:
    users: [{id, username, email, is_active, created_at}]

PUT /api/v1/users/{user_id}
  description: Update user account
  authentication: Admin or self
  request:
    username: string (optional)
    email: string (optional)
    is_active: boolean (optional)
```

### 3.2 Core Application Endpoints
```yaml
POST /api/v1/evaluations/submit
  description: Submit text for evaluation
  authentication: Session required (any mode)
  request:
    text_content: string
    session_id: string (Anonymous) | derived from JWT (Authenticated)
  response:
    data:
      evaluation: {overall_score, strengths, opportunities, rubric_scores}
      progress_data: {trends, metrics, charts}
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []

GET /api/v1/evaluations/{evaluation_id}
  description: Retrieve evaluation details
  authentication: Session owner or admin
  response:
    data:
      evaluation: full evaluation object
      progress_data: integrated progress information
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []

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

POST /api/v1/admin/config/{config_type}
  description: Update configuration files
  authentication: Admin required
  request:
    config_content: string (YAML)
  response:
    data:
      validation_result: {is_valid, errors}
      file_updated: boolean
      cache_synchronized: boolean
    meta:
      timestamp: ISO8601
      request_id: uuid
    errors: []
    
GET /api/v1/admin/auth/config
  description: Get authentication configuration
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

# Additional Core Endpoints

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

GET /api/v1/export/pdf/{evaluation_id}
  description: Download PDF export of evaluation
  authentication: Session owner or admin
  response:
    Content-Type: application/pdf
    Content-Disposition: attachment
    File: evaluation_report.pdf

GET /api/v1/debug/info
  description: Get debug information (when debug mode enabled)
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

### 3.3 Data Validation Rules

#### 3.3.1 Input Validation Patterns
- **Text Content**: Max 10,000 characters, XSS sanitization, UTF-8 encoding
- **Session ID**: Format validation (UUID v4), expiration checks
- **YAML Configuration**: Schema validation, syntax checking, required field validation
- **Authentication**: Username/password length limits, character restrictions

#### 3.3.2 Output Sanitization Requirements
- **User Content**: HTML entity encoding, script tag removal
- **Error Messages**: No sensitive information exposure, generic error codes
- **Debug Data**: Authentication token removal, PII scrubbing

#### 3.3.3 Error Response Format
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

### 3.4 Performance Requirements

#### 3.4.1 Response Time Targets
- **Page Load**: < 1 second
- **Text Submission**: < 60 seconds (LLM processing)
- **Chat Messages**: < 5 seconds
- **Admin Operations**: < 3 seconds
- **Progress Data**: < 2 seconds (cached)

#### 3.4.2 Rate Limiting Policies
- **Text Submissions**: 10 per hour per session
- **Chat Messages**: 50 per hour per session
- **Admin Operations**: 100 per hour per admin user
- **Global**: 1000 requests per hour per IP
- **Headers**: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset

#### 3.4.3 Caching Strategies
- **Progress Data**: 1-hour cache with invalidation on new evaluations
- **Configuration**: Database cache synchronized with filesystem
- **Static Content**: Browser caching with ETags
- **API Responses**: No caching for dynamic content

### 3.5 Security Considerations

#### 3.5.1 Authentication Implementation
- **JWT Configuration**: HS256 algorithm, configurable secret key rotation
- **Session Security**: Secure random tokens (32 bytes), httpOnly cookies
- **Password Policy**: bcrypt hashing with cost factor 12
- **CSRF Protection**: Double-submit cookie pattern for state-changing operations

#### 3.5.2 Authorization Patterns
- **Middleware**: `AuthorizationMiddleware` validates all protected endpoints
- **Role-based Access**: Admin vs regular user permissions
- **Session Isolation**: Data access restricted by session_id/user_id
- **Rate Limiting**: Per-session/user rate limits to prevent abuse

#### 3.5.3 Input Sanitization Requirements
- **Text Content**: XSS prevention, length limits (10,000 chars), UTF-8 validation
- **Configuration**: YAML validation, schema enforcement, injection prevention
- **Authentication**: Username/password input validation and sanitization
- **Session Tokens**: Format validation, expiration checks, secure generation
- **Debug Mode**: Global debug setting affects all new evaluations when enabled

---

## 4.0 Traceability Links

- **Source of Truth**: `02_Architecture.md`, `03_Data_Model.md`
- **Mapped Requirements**: 
  - Text Evaluation (2.2)
  - Chat with LLM (2.3)
  - Admin Functions (2.4)
  - Debug Mode (2.5)
  - Progress Tracking (2.6)
  - PDF Export (2.7)
