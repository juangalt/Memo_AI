# API Documentation
## Memo AI Coach

**Document ID**: 05_API_Documentation.md
**Document Version**: 2.0
**Last Updated**: Phase 10 - Prompt Refactor Implementation
**Status**: Active

---

## 1.0 Base URL
`http://<domain>/api`
All endpoints return JSON objects with `data`, `meta`, and `errors` keys.

## 2.0 Endpoints

### 2.1 Public Endpoints
| Method | Path | Description |
|-------|------|-------------|
| GET | `/` | Root information |
| GET | `/health` | Aggregate health status |
| GET | `/health/database` | Database health |
| GET | `/health/config` | Configuration health |
| GET | `/health/llm` | LLM service health |
| GET | `/health/auth` | Authentication service health |
| GET | `/health/language_detection` | Language detection service health |
| GET | `/docs` | Swagger UI with OpenAPI schema |

### 2.2 Session Management
| Method | Path | Description |
|-------|------|-------------|
| POST | `/api/v1/sessions/create` | Create authenticated session (requires login first) |
| GET | `/api/v1/sessions/{session_id}` | Retrieve session details |
| DELETE | `/api/v1/sessions/{session_id}` | End a session and remove related data |

### 2.3 Evaluation
| Method | Path | Description |
|-------|------|-------------|
| POST | `/api/v1/evaluations/submit` | Submit text for evaluation with automatic language detection |
| GET | `/api/v1/evaluations/{evaluation_id}` | Retrieve evaluation result (placeholder) |
| GET | `/api/v1/evaluations/session/{session_id}` | List evaluations for a session |

**Dynamic Language Detection and Prompt Generation**: The evaluation system automatically detects text language using multiple detection methods and generates language-appropriate prompts using Jinja2 templates. The system supports English and Spanish with automatic fallback to default language when detection confidence is low.

**Language Detection Process**:
1. **Primary Detection**: Uses Polyglot, Langdetect, and Pycld2 methods
2. **Confidence Scoring**: Calculates reliability of detection results
3. **Fallback Strategy**: Falls back to default language if confidence is below threshold
4. **Prompt Generation**: Creates language-specific prompts using Jinja2 templates
5. **Dynamic Rubric**: Automatically adapts prompts to any rubric structure

**Request Body for `/api/v1/evaluations/submit`:**
```json
{
  "text_content": "<string>",
  "session_id": "<string>"
}
```

**Success Response:**
```json
{
  "data": {
    "evaluation": {
      "overall_score": 4.2,
      "strengths": ["..."],
      "opportunities": ["..."],
      "rubric_scores": {"criterion": {"score": 4, "justification": "..."}},
      "segment_feedback": [
        {"segment": "text", "comment": "...", "questions": [], "suggestions": []}
      ],
      "language_detection": {
        "detected_language": "en",
        "confidence": 0.95,
        "detection_method": "polyglot",
        "fallback_used": false
      },
      "processing_time": 3.1,
      "created_at": "2024-01-01T00:00:00Z"
    }
  },
  "meta": {"timestamp": "...", "request_id": "..."},
  "errors": []
}
```

**Failure Response:**
```json
{
  "data": null,
  "meta": {"timestamp": "...", "request_id": "..."},
  "errors": [{"code": "EVAL_TIMEOUT", "message": "LLM did not respond within limit"}]
}
```

### 2.4 Language Detection
| Method | Path | Description |
|-------|------|-------------|
| POST | `/api/v1/language/detect` | Detect language of provided text |
| GET | `/api/v1/language/supported` | List supported languages and detection methods |

**Language Detection Request Body:**
```json
{
  "text_content": "<string>",
  "session_id": "<string>"
}
```

**Language Detection Response:**
```json
{
  "data": {
    "language_detection": {
      "detected_language": "en",
      "confidence": 0.95,
      "detection_method": "polyglot",
      "alternative_methods": [
        {"method": "langdetect", "language": "en", "confidence": 0.92},
        {"method": "pycld2", "language": "en", "confidence": 0.89}
      ],
      "fallback_used": false,
      "processing_time": 0.15
    }
  },
  "meta": {"timestamp": "...", "request_id": "..."},
  "errors": []
}
```

**Supported Languages Response:**
```json
{
  "data": {
    "supported_languages": [
      {
        "code": "en",
        "name": "English",
        "description": "English language support",
        "enabled": true
      },
      {
        "code": "es",
        "name": "Spanish",
        "description": "Spanish language support",
        "enabled": true
      }
    ],
    "detection_methods": [
      {
        "name": "polyglot",
        "description": "Polyglot language detection library",
        "enabled": true,
        "priority": 1
      },
      {
        "name": "langdetect",
        "description": "Google's language detection library",
        "enabled": true,
        "priority": 2
      },
      {
        "name": "pycld2",
        "description": "Compact Language Detector 2",
        "enabled": true,
        "priority": 3
      }
    ],
    "default_language": "en",
    "confidence_threshold": 0.7
  },
  "meta": {"timestamp": "...", "request_id": "..."},
  "errors": []
}
```

### 2.5 Authentication
| Method | Path | Description |
|-------|------|-------------|
| POST | `/api/v1/auth/login` | Unified login for all users (admins and regular users) |
| POST | `/api/v1/auth/logout` | Unified logout for all users |
| GET | `/api/v1/auth/validate` | Validate session token and get user info |

**Login Request Body:**
```json
{
  "username": "admin",
  "password": "secret"
}
```

**Login Success Response:**
```json
{
  "data": {
    "session_token": "aB3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW3xY5zA2bC4dE6fG8hI0jK2lM4nO6pQ8rS0tU2vW4xY6z",
    "username": "admin",
    "is_admin": true,
    "user_id": 1
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "placeholder"
  },
  "errors": []
}
```

All authentication endpoints require proper credentials and return session tokens. See `docs/02b_Authentication_Specifications.md` for complete authentication details.

### 2.6 User Management (Admin)
| Method | Path | Description |
|-------|------|-------------|
| POST | `/api/v1/admin/users/create` | Create new user account |
| GET | `/api/v1/admin/users` | List all users |
| DELETE | `/api/v1/admin/users/{username}` | Delete user account |

**Create User Request Body:**
```json
{
  "username": "newuser",
  "password": "securepassword123"
}
```

### 2.7 Debug and Development Endpoints

#### Debug Environment Variables
**GET `/api/v1/debug/env`**

Returns environment variable information for debugging purposes.

**Response:**
```json
{
  "data": {
    "DOMAIN": "memo.myisland.dev",
    "APP_ENV": "production",
    "all_env": {
      "DOMAIN": "memo.myisland.dev",
      "APP_ENV": "production"
    }
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "debug"
  },
  "errors": []
}
```

#### Frontend Configuration
**GET `/api/v1/config/frontend`**

Returns frontend-specific configuration settings.

**Response:**
```json
{
  "data": {
    "backend_url": "https://memo.myisland.dev",
    "session_warning_threshold": 10,
    "session_refresh_interval": 60,
    "debug_console_log_limit": 50,
    "llm_timeout_expectation": 15,
    "default_response_time": 1000
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "placeholder"
  },
  "errors": []
}
```

### 2.8 Admin Evaluation Data (Admin Only)

#### Last Evaluations List
**GET `/api/v1/admin/last-evaluations`**

Returns the last evaluation for each user in the system.

**Headers Required:**
- `X-Session-Token`: Valid admin session token

**Response:**
```json
{
  "data": {
    "evaluations": [
      {
        "id": 123,
        "submission_id": 456,
        "overall_score": 4.2,
        "processing_time": 3.1,
        "created_at": "2024-01-01T00:00:00Z",
        "llm_provider": "anthropic",
        "llm_model": "claude-3-haiku-20240307",
        "debug_enabled": true,
        "has_raw_data": true,
        "submission_preview": "This is a sample memo for testing purposes...",
        "username": "admin",
        "is_admin": true
      }
    ],
    "total": 1
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "abc123"
  },
  "errors": []
}
```

#### Evaluation Raw Data
**GET `/api/v1/admin/evaluation/{evaluation_id}/raw`**

Returns raw LLM prompt and response data for a specific evaluation.

**Headers Required:**
- `X-Session-Token`: Valid admin session token

**Path Parameters:**
- `evaluation_id`: Integer ID of the evaluation

**Response:**
```json
{
  "data": {
    "evaluation": {
      "id": 123,
      "submission_id": 456,
      "overall_score": 4.2,
      "processing_time": 3.1,
      "created_at": "2024-01-01T00:00:00Z",
      "llm_provider": "anthropic",
      "llm_model": "claude-3-haiku-20240307",
      "debug_enabled": true,
      "raw_prompt": "You are an expert evaluator...",
      "raw_response": "Based on the provided memo...",
      "submission": {
        "id": 456,
        "content": "This is the original memo text...",
        "created_at": "2024-01-01T00:00:00Z"
      }
    }
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "abc123"
  },
  "errors": []
}
```

**Error Responses:**
- **401 Unauthorized**: Invalid or missing session token
- **403 Forbidden**: Non-admin user attempting to access admin endpoint
- **404 Not Found**: Evaluation with specified ID does not exist
- **500 Internal Server Error**: Server error during data retrieval

### 2.9 Health Endpoints
All health endpoints return standardized `{data, meta, errors}` format and respond with HTTP 200 for healthy status or HTTP 503 for unhealthy status.

**Main Health Endpoint (`GET /health`):**
```json
{
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0",
    "services": {
      "api": "healthy",
      "database": "healthy", 
      "configuration": "healthy",
      "llm": "healthy",
      "auth": "healthy"
    },
    "database_details": {
      "tables": ["users", "sessions", "submissions", "evaluations"],
      "journal_mode": "wal",
      "user_count": 5
    }
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "placeholder"
  },
  "errors": []
}
```

**Database Health Endpoint (`GET /health/database`):**
```json
{
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z",
    "database": {
      "connection": "connected",
      "tables": ["users", "sessions", "submissions", "evaluations"],
      "journal_mode": "wal",
      "integrity_check": "ok",
      "user_count": 5
    }
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "placeholder"
  },
  "errors": []
}
```

**Configuration Health Endpoint (`GET /health/config`):**
```json
{
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z",
    "configuration": {
      "configs_loaded": ["rubric.yaml", "prompt.yaml", "llm.yaml", "auth.yaml"],
      "last_loaded": "2024-01-01T00:00:00Z",
      "config_dir": "/app/config",
      "validation_status": "valid"
    }
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "placeholder"
  },
  "errors": []
}
```

**LLM Health Endpoint (`GET /health/llm`):**
```json
{
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z",
    "llm": {
      "provider": "anthropic",
      "model": "claude-3-haiku-20240307",
      "api_accessible": true,
      "config_loaded": true,
      "response_time": 2.5
    }
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "placeholder"
  },
  "errors": []
}
```

**Authentication Health Endpoint (`GET /health/auth`):**
```json
{
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z",
    "auth": {
      "config_loaded": true,
      "active_sessions": 3,
      "brute_force_protection": true,
      "session_timeout": 3600
    }
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "placeholder"
  },
  "errors": []
}
```

**Health Endpoint Error Response (HTTP 503):**
```json
{
  "data": {
    "status": "unhealthy",
    "timestamp": "2024-01-01T00:00:00Z",
    "services": {
      "api": "healthy",
      "database": "unhealthy",
      "configuration": "healthy",
      "llm": "healthy", 
      "auth": "healthy"
    },
    "database_details": {
      "error": "Connection failed",
      "tables": [],
      "journal_mode": "unknown"
    }
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "placeholder"
  },
  "errors": []
}
```

## 3.0 Error Format
All errors share the structure:
```json
{
  "data": null,
  "meta": {"timestamp": "...", "request_id": "..."},
  "errors": [
    {"code": "ERROR_CODE", "message": "Description", "field": "optional", "details": "optional"}
  ]
}
```

## 4.0 Authentication
All protected endpoints require authentication via `X-Session-Token` header. See `docs/02b_Authentication_Specifications.md` for complete authentication requirements and token management.

## 5.0 Frontend Integration Guidelines

### 5.1 Response Processing
Frontend services must handle the standardized API response format correctly to avoid processing errors.

#### Standard Response Format
All API responses (including health endpoints) follow this structure:
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

#### Frontend Processing Guidelines
- **Direct Data Access**: Use `result.data` directly from API client responses
- **Consistent Format**: All endpoints (including health endpoints) return standardized format
- **Error Handling**: Check `result.errors` array for detailed error information
- **Success Validation**: Verify `result.success` before accessing `result.data`
- **Type Safety**: Use proper TypeScript interfaces for all response types

#### Example Implementation
```javascript
// Correct pattern for all endpoints
const result = await apiClient.get('/health')
if (result.success) {
  // Access data directly - health status is in result.data
  const healthStatus = result.data.status
  const services = result.data.services
  return healthStatus
} else {
  // Handle errors from result.errors
  throw new Error(result.error)
}

// Correct pattern for evaluation endpoints
const result = await apiClient.post('/api/v1/evaluations/submit', data)
if (result.success) {
  // Access data directly - evaluation is in result.data
  const evaluation = result.data.evaluation
  return evaluation
} else {
  // Handle errors from result.errors
  throw new Error(result.error)
}
```

#### Health Endpoint Processing
```javascript
// Health endpoint returns standardized format
const result = await apiClient.get('/health')
if (result.success) {
  const health = result.data
  // Access health data directly
  const overallStatus = health.status
  const databaseStatus = health.services.database
  const version = health.version
}
```

### 5.2 Authentication Integration
Frontend authentication must integrate properly with Vue Router and global state management.

#### Global Auth Store Access
- **Router Guards**: Use `window.authStoreInstance` for router guard authentication
- **Session Validation**: Implement automatic session validation on protected route access
- **Token Management**: Clear tokens from memory on 401 responses
- **State Persistence**: Store authentication state in memory only (never localStorage)

#### Vue Router Integration
```javascript
// Router guard implementation
router.beforeEach(async (to, from, next) => {
  const authStore = window.authStoreInstance
  
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      const valid = await authStore.validateSession()
      if (!valid) {
        next('/login')
        return
      }
    }
  }
  next()
})
```

### 5.3 Component Architecture Patterns
Frontend components must follow specific patterns to avoid UI duplication and ensure proper authentication state management.

#### Layout Component Usage
- **Layout Usage**: Use Layout component in view components when navigation is needed
- **No Duplication**: App.vue uses RouterView only, Layout is used in individual view components
- **Authentication State**: Layout should display authentication status and navigation

#### Component Hierarchy
```
App.vue (RouterView only)
├── RouterView
    ├── Home.vue (no Layout wrapper)
    ├── Login.vue (no Layout wrapper)
    ├── TextInput.vue (with Layout wrapper)
    ├── OverallFeedback.vue (with Layout wrapper)
    ├── DetailedFeedback.vue (with Layout wrapper)
    ├── Help.vue (with Layout wrapper)
    ├── Admin.vue (with Layout wrapper)
    └── Debug.vue (with Layout wrapper)
```

#### Authentication State Management
- **Global Store**: Use Pinia store for authentication state
- **Memory Storage**: Store tokens in memory only per security requirements
- **Session Validation**: Implement automatic session validation on app startup
- **Error Handling**: Handle authentication errors gracefully with user feedback

## 6.0 References
- `docs/02b_Authentication_Specifications.md` - Complete authentication details
- `devlog/vue_frontend_implementation_plan.md` - Vue.js frontend implementation plan
- `backend/main.py`
- `vue-frontend/services/api.js` - Vue.js API client implementation
