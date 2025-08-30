# Architecture Documentation
## Memo AI Coach

**Document ID**: 02_Architecture_Documentation.md
**Document Version**: 1.2
**Last Updated**: Phase 9
**Status**: Draft

---

## 1.0 System Architecture

### 1.1 Component Overview
- **Frontend**: Vue.js application (`vue-frontend/`) providing a modern reactive interface with authentication-gated access.
- **Backend**: FastAPI service (`backend/main.py`) exposing REST endpoints with authentication middleware.
- **Database**: SQLite accessed through `backend/models/database.py` using WAL mode.
- **LLM Service**: `backend/services/llm_service.py` for Claude API interaction.
- **Configuration Service**: `backend/services/config_service.py` and `config_manager.py` for loading and editing YAML configs.
- **Authentication Service**: `backend/services/auth_service.py` providing user and admin login, session validation, and role-based access control.

Each component follows single-responsibility design so that updates to one area minimally impact others. Communication occurs through well defined interfaces and explicit data contracts.

### 1.2 Authentication Architecture
The system implements session-based authentication with role-based access control. See `docs/02b_Authentication_Specifications.md` for complete authentication details.

### 1.3 Data Flow
1. User authenticates and receives session token.
2. User submits text via authenticated interface.
3. Frontend calls backend evaluation endpoint.
4. Backend validates authentication and processes request.
5. Backend loads configurations and sends prompt to LLM service.
6. Response is parsed, stored, and returned to frontend.
7. Admin functions allow configuration and user management.

### 1.4 Data Model
| Table | Purpose | Key Fields |
|-------|---------|------------|
| `users` | user accounts with role-based access | `id`, `email`, `password_hash`, `role`, `created_at` |
| `sessions` | track active evaluation sessions | `id`, `user_id`, `created_at`, `updated_at` |
| `submissions` | store original memo text | `id`, `session_id`, `content` |
| `evaluations` | store LLM generated feedback | `id`, `submission_id`, `overall`, `strengths`, `opportunities`, `rubric_scores`, `segments` |

Relationships:
- A `user` has many `sessions`.
- A `session` has many `submissions`.
- Each `submission` has one `evaluation`.

### 1.5 Frontend Interface Structure
The Vue.js frontend provides a single-page application with router-based navigation and role-based access control:

1. **Login** (`/login`) - Authentication interface
2. **Text Input** (`/text-input`) – Content submission for evaluation
3. **Overall Feedback** (`/overall-feedback`) – Evaluation results display
4. **Detailed Feedback** (`/detailed-feedback`) – Detailed scoring and comments
5. **Debug** (`/debug`) – System diagnostics and tools (admin only)
6. **Admin** (`/admin`) – System management and configuration (admin only)

Vue Router controls navigation and enforces authentication requirements on protected routes.

### 1.6 Deployment Topology
- Containers orchestrated by `docker-compose.yml` with Traefik reverse proxy.
- Volumes map host `./config`, `./data`, and `./logs` to `/app/*` in containers.
- Non-root container user UID/GID `1000:1000` to avoid permission issues.

Service diagram:
```
Client -> Traefik -> Backend (FastAPI) -> SQLite
                              ↘
                               LLM Service (Claude API)
Frontend (Vue.js) <- Traefik
```

---

## 2.0 Module Relationships
- `main.py` imports services and models to handle requests with authentication middleware.
- Models (`entities.py`) encapsulate database tables: `User`, `Session`, `Submission`, `Evaluation`.
- Services provide single-responsibility utilities: auth, config, LLM.
- Vue.js `services/api.js` provides HTTP client with automatic authentication headers.
- Vue.js `stores/auth.js` manages authentication state and session validation.
- Vue.js `router/index.js` enforces route-based access control.

Sequence example for evaluation submission:
1. User authenticates via Vue.js login interface.
2. `vue-frontend/services/evaluation.js` POSTs to `/api/v1/evaluations/submit` with authentication headers.
3. `backend/main.py` routes to evaluation handler after validating user session and permissions.
4. Handler loads configs via `config_service`.
5. `llm_service` builds prompt from `prompt.yaml` and sends to Claude.
6. Parsed result is persisted using `models/entities.py` helpers.
7. Response object serialized and returned to Vue.js frontend for display.

---

## 3.0 Security Architecture
- **Authentication**: Session-based authentication with role-based access control
- **Authorization**: Permission validation on all endpoints and UI components
- **Session Security**: Configurable token expiration and validation
- **Network Security**: HTTPS termination via Traefik with Let's Encrypt certificates
- **Container Security**: Read-only configuration files and non-root user execution
- **Rate Limiting**: Request throttling via Traefik and application-level controls

See `docs/02b_Authentication_Specifications.md` for detailed authentication security measures.

---

## 4.0 Scalability and Performance
- SQLite database uses WAL mode (`init_db.py` sets `PRAGMA journal_mode = WAL`).
- LLM service tracks processing time and enforces <15s response target (`config/llm.yaml`).
- Traefik rate limiting protects against excessive requests.
- Backend and frontend services are stateless allowing horizontal scaling by adding containers behind Traefik.
- Configuration reloads avoid service restarts, enabling runtime changes without downtime.
- Authentication overhead minimized through efficient session validation.

---

## 5.0 References
- `docs/02b_Authentication_Specifications.md` - Complete authentication specifications
- `devlog/vue_frontend_implementation_plan.md` - Vue.js frontend implementation plan
- `backend/main.py`
- `vue-frontend/` - Vue.js frontend application
- `docker-compose.yml`
