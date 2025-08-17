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

### 2.2 Request/Response Format Standardization
**Question**: What should be the standard API response format across all endpoints?
- Should we use a consistent wrapper format (e.g., `{data: {}, meta: {}, errors: []})?
- How do we handle error responses consistently?
- What HTTP status codes should we use for different scenarios?

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

#### 3.1.1 Session Management (MVP Mode)
```yaml
GET /api/sessions/create
  description: Create anonymous session for MVP mode
  response:
    session_id: string (secure token)
    expires_at: datetime
    
POST /api/sessions/validate
  description: Validate session token
  request:
    session_id: string
  response:
    valid: boolean
    expires_at: datetime
```

#### 3.1.2 User Authentication (Production Mode)
```yaml
POST /api/auth/login
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

POST /api/auth/logout
  description: User logout and session cleanup
  response:
    success: boolean

GET /api/auth/verify
  description: Verify JWT token and session
  response:
    user: {id, username, is_admin}
    session_valid: boolean

POST /api/auth/refresh
  description: Refresh JWT token
  response:
    user: {id, username, is_admin}
    expires_at: datetime
```

#### 3.1.3 User Management (Admin Only)
```yaml
POST /api/users
  description: Create new user account
  authentication: Admin required
  request:
    username: string
    email: string (optional)
    password: string
    is_admin: boolean (default: false)

GET /api/users
  description: List all users
  authentication: Admin required
  response:
    users: [{id, username, email, is_active, created_at}]

PUT /api/users/{user_id}
  description: Update user account
  authentication: Admin or self
  request:
    username: string (optional)
    email: string (optional)
    is_active: boolean (optional)
```

### 3.2 Core Application Endpoints
```yaml
POST /api/evaluations/submit
  description: Submit text for evaluation
  authentication: Session required (any mode)
  request:
    text_content: string
    session_id: string (MVP) | derived from JWT (Production)
  response:
    evaluation: {overall_score, strengths, opportunities, rubric_scores}
    progress_data: {trends, metrics, charts}

GET /api/evaluations/{evaluation_id}
  description: Retrieve evaluation details
  authentication: Session owner or admin
  response:
    evaluation: full evaluation object
    progress_data: integrated progress information

POST /api/chat/sessions
  description: Start chat session after evaluation
  authentication: Session required
  request:
    evaluation_id: integer
  response:
    chat_session_id: string
    context_loaded: boolean

POST /api/admin/config/{config_type}
  description: Update configuration files
  authentication: Admin required
  request:
    config_content: string (YAML)
  response:
    validation_result: {is_valid, errors}
    
GET /api/admin/auth/config
  description: Get authentication configuration
  authentication: Admin required
  response:
    auth_enabled: boolean
    session_timeout: integer
    max_login_attempts: integer

PUT /api/admin/auth/config
  description: Update authentication configuration
  authentication: Admin required
  request:
    auth_enabled: boolean
    session_timeout: integer
    max_login_attempts: integer
```

### 3.3 Data Validation Rules
- (Pending) Input validation patterns
- (Pending) Output sanitization requirements
- (Pending) Error response formats

### 3.4 Performance Requirements
- (Pending) Response time targets
- (Pending) Rate limiting policies
- (Pending) Caching strategies

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
- **Text Content**: XSS prevention, length limits (10,000 chars)
- **Configuration**: YAML validation, schema enforcement
- **Authentication**: Username/password input validation and sanitization
- **Session Tokens**: Format validation, expiration checks

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
