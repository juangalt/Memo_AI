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
**Hybrid JWT + Session System**:
- **MVP Mode**: Session-based authentication using secure session tokens
- **Production Mode**: JWT tokens with httpOnly cookies + session validation
- **Configuration Toggle**: Enable/disable without code changes
- **Seamless Transition**: Maintains session_id compatibility across modes

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
  description: Get debug information when debug mode enabled
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

## 9.0 Open Technical Decisions

### 9.1 LLM Response Handling Strategy
**Decision Required**: How to handle potentially long-running LLM evaluation requests?

**Context**: Given moderate traffic expectations (20 submissions/hour per session), small team size, and focus on simplicity.

**Options Analysis**:

1. **Synchronous with extended timeout** (60 seconds)
   - **Pros**:
     - Minimal implementation complexity
     - No additional infrastructure required
     - Straightforward error handling
     - Direct request-response pattern familiar to developers
     - No state management needed
   - **Cons**:
     - Poor user experience during long evaluations
     - Browser timeout risks
     - Server resources tied up during processing
     - No progress feedback to user
     - Difficulty handling connection drops
   - **Complexity**: Low
   - **Modularity**: High (self-contained)
   - **Extensibility**: Low (hard to add features like progress tracking)

2. **Asynchronous with polling**
   - **Pros**:
     - Better user experience with progress updates
     - Server resources freed during processing
     - Resilient to connection issues
     - Can add progress tracking later
     - Scalable to higher loads
   - **Cons**:
     - Requires additional endpoints (`/evaluations/{id}/status`)
     - Client-side polling logic needed
     - State management for in-progress evaluations
     - Complexity in error handling across requests
   - **Complexity**: Medium
   - **Modularity**: High (separate concerns)
   - **Extensibility**: High (easy to add features)

3. **WebSocket real-time updates**
   - **Pros**:
     - Excellent real-time user experience
     - Instant progress updates
     - Bidirectional communication
     - Future-proof for chat functionality
   - **Cons**:
     - High implementation complexity
     - Additional infrastructure (WebSocket support)
     - Connection management overhead
     - Not RESTful
     - Debugging complexity
     - Firewall/proxy complications
   - **Complexity**: High
   - **Modularity**: Medium (tightly coupled real-time communication)
   - **Extensibility**: High (supports future real-time features)

4. **Server-sent events for progress**
   - **Pros**:
     - Real-time progress updates
     - Simpler than WebSocket
     - One-way communication sufficient
     - HTTP-based (firewall friendly)
   - **Cons**:
     - Browser compatibility considerations
     - Still requires connection management
     - Not RESTful
     - Additional complexity over polling
   - **Complexity**: Medium-High
   - **Modularity**: Medium
   - **Extensibility**: Medium

**🎯 RECOMMENDATION: Asynchronous with polling**
- **Rationale**: Best balance of simplicity, user experience, and extensibility for a moderate-scale service
- **Implementation**: Start with basic polling, optimize interval based on usage patterns
- **Future Path**: Can enhance with SSE later if needed
- **Team Impact**: Manageable complexity for small development team

---

### 9.2 File Upload and Download Strategy
**Decision Required**: How to handle PDF exports and configuration file bulk operations?

**Context**: Small to moderate file sizes (PDFs <5MB, config files <1MB), limited concurrent users, focus on operational simplicity.

**Options Analysis**:

1. **Direct file serving from application**
   - **Pros**:
     - Zero external dependencies
     - Simple implementation and debugging
     - Full control over access permissions
     - No additional infrastructure costs
     - Immediate availability after generation
     - Works well with existing authentication
   - **Cons**:
     - Uses application server memory/bandwidth
     - Files stored on local filesystem
     - Cleanup management required
     - Not optimal for high-traffic scenarios
   - **Complexity**: Low
   - **Modularity**: High (self-contained)
   - **Extensibility**: Medium (can migrate to external storage later)

2. **Signed URLs with external storage (S3/MinIO)**
   - **Pros**:
     - Offloads bandwidth from application
     - Scalable storage solution
     - Built-in redundancy and backup
     - Professional production approach
   - **Cons**:
     - Additional infrastructure dependency
     - External service costs
     - More complex deployment
     - Additional failure points
     - Overkill for small file volumes
     - Configuration complexity
   - **Complexity**: High
   - **Modularity**: Medium (external dependency)
   - **Extensibility**: High (industry standard approach)

3. **Streaming responses**
   - **Pros**:
     - Memory efficient for large files
     - No temporary file storage needed
     - Good for real-time generation
   - **Cons**:
     - Complex error handling during stream
     - Difficult to implement proper caching
     - Connection drop handling complexity
     - Limited browser progress indication
   - **Complexity**: Medium-High
   - **Modularity**: Medium
   - **Extensibility**: Medium

**🎯 RECOMMENDATION: Direct file serving from application**
- **Rationale**: Optimal for small-scale service with simple operational requirements
- **Implementation**: Temporary file storage with automatic cleanup (24-hour retention)
- **Future Path**: Can migrate to external storage when scale demands it
- **Team Impact**: Minimal operational overhead, easier debugging and deployment

---

### 9.3 API Documentation and Maintenance Strategy
**Decision Required**: How to generate and maintain comprehensive API documentation?

**Context**: Small development team, moderate API complexity, need for developer onboarding and client integration.

**Options Analysis**:

1. **Auto-generated OpenAPI/Swagger from code**
   - **Pros**:
     - Always synchronized with implementation
     - Interactive testing interface
     - Industry-standard format
     - Automatic client SDK generation possible
     - Reduced maintenance overhead
   - **Cons**:
     - Code annotation overhead
     - Limited customization for complex examples
     - Generic descriptions without business context
     - Tool-dependent formatting
     - Learning curve for annotation syntax
   - **Complexity**: Medium
   - **Modularity**: High (separate documentation concerns)
   - **Extensibility**: High (standard tooling ecosystem)

2. **Manual documentation with examples**
   - **Pros**:
     - Complete control over content and format
     - Rich business context and examples
     - Custom formatting and organization
     - No tool dependencies
     - Easy to include implementation notes
   - **Cons**:
     - High maintenance burden
     - Risk of becoming outdated
     - No interactive testing
     - Manual effort for each change
     - Inconsistent formatting risk
   - **Complexity**: Low (to create), High (to maintain)
   - **Modularity**: Low (documentation separate from code)
   - **Extensibility**: Low (manual scaling)

3. **Hybrid approach with manual OpenAPI specs**
   - **Pros**:
     - Best of both worlds
     - Version-controlled specifications
     - Rich examples and descriptions
     - Interactive testing interface
     - Can validate implementation against spec
   - **Cons**:
     - Double maintenance (spec + code)
     - Risk of spec-implementation drift
     - Additional complexity in workflow
     - Requires OpenAPI expertise
   - **Complexity**: Medium-High
   - **Modularity**: Medium
   - **Extensibility**: High

**🎯 RECOMMENDATION: Auto-generated OpenAPI/Swagger from code**
- **Rationale**: Best long-term maintenance approach for small team with evolving API
- **Implementation**: FastAPI native OpenAPI support with rich docstring annotations
- **Future Path**: Can supplement with additional manual documentation for complex workflows
- **Team Impact**: Lower maintenance overhead, automatic updates, interactive testing for development

---

### 9.4 Rate Limiting Implementation Strategy
**Decision Required**: How to implement and store rate limiting data for abuse prevention?

**Context**: Moderate traffic (20 submissions/hour per session), single or few-instance deployment, simple operational requirements.

**Options Analysis**:

1. **In-memory rate limiting (per instance)**
   - **Pros**:
     - Extremely fast (no I/O overhead)
     - Simple implementation
     - No external dependencies
     - Zero additional infrastructure
     - Perfect for single-instance deployment
   - **Cons**:
     - Inaccurate in multi-instance deployments
     - Lost on application restart
     - No persistence across deployments
     - Memory usage grows with active sessions
   - **Complexity**: Low
   - **Modularity**: High (self-contained)
   - **Extensibility**: Low (doesn't scale to multiple instances)

2. **Database-backed rate limiting**
   - **Pros**:
     - Accurate across multiple instances
     - Persistent across restarts
     - Uses existing database infrastructure
     - Easy to query and monitor
     - Consistent with existing data storage
   - **Cons**:
     - Database I/O overhead on every request
     - Potential performance bottleneck
     - Requires cleanup of old rate limit records
     - Additional database schema complexity
   - **Complexity**: Medium
   - **Modularity**: Medium (couples rate limiting to database)
   - **Extensibility**: Medium (scales with database)

3. **Redis-based rate limiting**
   - **Pros**:
     - Very fast (in-memory)
     - Accurate across instances
     - Built-in expiration (TTL)
     - Industry standard for rate limiting
     - Excellent performance characteristics
   - **Cons**:
     - Additional infrastructure dependency
     - Another service to deploy and monitor
     - Overkill for simple use cases
     - Additional complexity in deployment
     - Cost of running Redis instance
   - **Complexity**: Medium-High
   - **Modularity**: High (dedicated service)
   - **Extensibility**: High (industry standard, very scalable)

4. **External service (reverse proxy/API gateway)**
   - **Pros**:
     - Offloaded from application logic
     - Proven, battle-tested solutions
     - Often includes additional features
     - No application code needed
   - **Cons**:
     - External dependency
     - Less control over logic
     - Additional deployment complexity
     - May require learning new tools
     - Overkill for simple requirements
   - **Complexity**: Medium (deployment), Low (application)
   - **Modularity**: High (completely external)
   - **Extensibility**: High (enterprise-grade solutions)

**🎯 RECOMMENDATION: In-memory rate limiting for MVP**
- **Rationale**: Optimal for single-instance MVP deployment with minimal complexity
- **Implementation**: Sliding window algorithm with in-memory storage, cleanup via background task
- **Future Path**: Database-backed rate limiting for multi-instance deployments
- **Team Impact**: Simple implementation, no external dependencies, perfect for MVP scale

---

### 9.5 Configuration Hot-Reload Strategy
**Decision Required**: Should configuration changes require application restart or support hot-reload?

**Context**: 13 configuration files, admin-driven changes, need for system stability vs. operational convenience.

**Options Analysis**:

1. **Restart required for all configuration changes**
   - **Pros**:
     - Simple implementation
     - Guaranteed consistency
     - No memory leaks from reloading
     - Clear change boundaries
     - Easier testing and debugging
   - **Cons**:
     - Service downtime for configuration changes
     - Poor admin user experience
     - Delays in configuration testing
   - **Complexity**: Low
   - **Modularity**: High
   - **Extensibility**: Medium

2. **Hot-reload for business logic configs only**
   - **Pros**:
     - No downtime for common changes (rubrics, prompts)
     - Better admin experience for content changes
     - System configs still require restart (safer)
     - Balanced approach
   - **Cons**:
     - Partial complexity increase
     - Need to categorize config types
     - Potential inconsistency risks
   - **Complexity**: Medium
   - **Modularity**: Medium
   - **Extensibility**: High

3. **Full hot-reload with validation**
   - **Pros**:
     - Best admin user experience
     - No downtime for any changes
     - Can validate before applying
   - **Cons**:
     - High implementation complexity
     - Risk of system instability
     - Difficult error recovery
     - Memory management complexity
   - **Complexity**: High
   - **Modularity**: Low
   - **Extensibility**: Medium

**🎯 RECOMMENDATION: Hot-reload for business logic configs only**
- **Rationale**: Balances operational convenience with system stability
- **Implementation**: Hot-reload for rubric, frameworks, context, prompt; restart for system configs
- **Future Path**: Can expand hot-reload scope based on operational experience
- **Team Impact**: Manageable complexity while improving most common admin operations

---

## 10.0 Implementation Priority

### 10.1 Phase 1: MVP Core (Weeks 1-6)
1. Authentication endpoints (session management)
2. Text evaluation endpoints
3. Basic configuration management
4. Debug endpoints
5. Error handling and validation

### 10.2 Phase 2: Enhanced Features (Weeks 7-12)
1. Complete configuration management system
2. User management endpoints
3. Chat functionality endpoints [Post-MVP]
4. Progress tracking endpoints [Post-MVP]
5. PDF export endpoints [Post-MVP]

### 10.3 Phase 3: Production Ready (Weeks 13-18)
1. JWT authentication implementation
2. Comprehensive rate limiting
3. Performance optimization
4. Security hardening
5. API documentation completion

---

## 11.0 Traceability Matrix

| **Requirement** | **API Endpoints** | **Status** |
|-----------------|-------------------|------------|
| Text Evaluation (2.2) | `/evaluations/submit`, `/evaluations/{id}` | MVP |
| Chat with LLM (2.3) | `/chat/sessions`, `/chat/sessions/{id}/messages` | Post-MVP |
| Admin Functions (2.4) | `/admin/config/*`, `/admin/auth/config` | MVP |
| Debug Mode (2.5) | `/debug/info`, `/admin/debug/toggle` | MVP |
| Progress Tracking (2.6) | `/progress/{session_id}` | Post-MVP |
| PDF Export (2.7) | `/export/pdf/{evaluation_id}` | Post-MVP |
| Authentication (3.4) | `/auth/*`, `/sessions/*`, `/users/*` | MVP/Production |

---

**Document Version**: 1.0  
**Last Updated**: Implementation Phase  
**Next Review**: After key technical decisions are resolved