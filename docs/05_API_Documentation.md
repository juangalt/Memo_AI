# API Documentation
## Memo AI Coach

**Document ID**: 05_API_Documentation.md
**Document Version**: 1.0
**Last Updated**: Phase 9
**Status**: Draft

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
| POST | `/api/v1/evaluations/submit` | Submit text for evaluation |
| GET | `/api/v1/evaluations/{evaluation_id}` | Retrieve evaluation result (placeholder) |
| GET | `/api/v1/evaluations/session/{session_id}` | List evaluations for a session |

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

### 2.4 Authentication
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

### 2.5 User Management (Admin)
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

### 2.6 Configuration Management (Admin)
| Method | Path | Description |
|-------|------|-------------|
| GET | `/api/v1/admin/config/{config_name}` | Read configuration file |
| PUT | `/api/v1/admin/config/{config_name}` | Update configuration file |

**Update Payload:**
```json
{"content": "<YAML string>"}
```
Success responses include updated YAML and path to the backup file created before modification.

### 2.7 Health Endpoints
All health endpoints respond with HTTP 200. The `status` field is `ok` or `error` with diagnostic details.

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
All API responses follow this structure:
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
- **Avoid Double Processing**: Do not re-process the `{data, meta, errors}` format
- **Error Handling**: Check `result.data.errors` array for detailed error information
- **Success Validation**: Verify `result.success` before accessing `result.data`

#### Example Implementation
```javascript
// Correct pattern
const result = await apiClient.post('/api/v1/evaluations/submit', data)
if (result.success) {
  // Access data directly - no double processing
  const evaluation = result.data.evaluation
  return evaluation
} else {
  // Handle errors from result.data.errors
  throw new Error(result.error)
}

// Incorrect pattern - causes double processing
const result = await apiClient.post('/api/v1/evaluations/submit', data)
if (result.success && result.data) {
  // Double processing - result.data already contains the response
  const processed = result.data.data.evaluation  // WRONG
  return processed
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
- **Single Instance**: Use Layout component only at App.vue level
- **No Duplication**: Avoid wrapping view components with additional Layout wrappers
- **Authentication State**: Layout should display authentication status and navigation

#### Component Hierarchy
```
App.vue (Layout wrapper)
├── RouterView
    ├── Home.vue (no Layout wrapper)
    ├── Login.vue (no Layout wrapper)
    ├── TextInput.vue (no Layout wrapper)
    └── OverallFeedback.vue (no Layout wrapper)
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
