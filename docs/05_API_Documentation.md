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
| POST | `/api/v1/sessions/create` | Generate anonymous session |
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

### 2.4 Admin Authentication
| Method | Path | Description |
|-------|------|-------------|
| POST | `/api/v1/admin/login` | Admin login with username/password |
| POST | `/api/v1/admin/logout` | Logout current admin session |

Authentication endpoints require proper credentials and return session tokens. See `docs/02b_Authentication_Specifications.md` for complete authentication details.

### 2.5 Configuration Management (Admin)
| Method | Path | Description |
|-------|------|-------------|
| GET | `/api/v1/admin/config/{config_name}` | Read configuration file |
| PUT | `/api/v1/admin/config/{config_name}` | Update configuration file |

**Update Payload:**
```json
{"content": "<YAML string>"}
```
Success responses include updated YAML and path to the backup file created before modification.

### 2.6 Health Endpoints
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

## 5.0 References
- `docs/02b_Authentication_Specifications.md` - Complete authentication details
- `devlog/vue_frontend_implementation_plan.md` - Vue.js frontend implementation plan
- `backend/main.py`
- `vue-frontend/services/api.js` - Vue.js API client implementation
