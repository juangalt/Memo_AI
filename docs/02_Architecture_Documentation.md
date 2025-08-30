# Architecture Documentation
## Memo AI Coach

**Document ID**: 02_Architecture_Documentation.md
**Document Version**: 1.2
**Last Updated**: Phase 9
**Status**: Draft

---

## 1.0 System Architecture

### 1.1 Component Overview
- **Frontend**: Streamlit application (`frontend/app.py`) presenting a tabbed interface with authentication-gated access.
- **Backend**: FastAPI service (`backend/main.py`) exposing REST endpoints with authentication middleware.
- **Database**: SQLite accessed through `backend/models/database.py` using WAL mode.
- **LLM Service**: `backend/services/llm_service.py` for Claude API interaction.
- **Configuration Service**: `backend/services/config_service.py` and `config_manager.py` for loading and editing YAML configs.
- **Authentication Service**: `backend/services/auth_service.py` providing user and admin login, session validation, and role-based access control.

Each component follows single-responsibility design so that updates to one area minimally impact others. Communication occurs through well defined interfaces and explicit data contracts.

### 1.2 Authentication Architecture
The system implements a comprehensive authentication system with two user categories:

#### 1.2.1 User Categories
- **Regular Users**: Can submit memos for evaluation, view feedback, and access basic application functions.
- **Administrators**: Have all regular user privileges plus access to configuration management, system monitoring, debug tools, user management, and administrative functions.

#### 1.2.2 Authentication Flow
1. **Homepage Login**: All users must authenticate through a centralized login page before accessing any application functions.
2. **Session Management**: Upon successful authentication, users receive session tokens used for subsequent API calls.
3. **Role-Based Access**: Backend middleware validates session tokens and enforces role-based permissions for all endpoints.
4. **Session Expiration**: Tokens expire according to `auth.yaml` configuration with automatic logout and re-authentication prompts.

### 1.3 Data Flow
1. User authenticates via homepage login interface.
2. Frontend validates credentials and receives session token.
3. User submits text via authenticated frontend session.
4. Frontend calls backend evaluation endpoint with authentication headers.
5. Backend validates session and user permissions before processing.
6. Backend loads rubric, prompt and LLM configs then sends prompt to Claude.
7. LLM response is parsed and stored in SQLite.
8. Backend returns evaluation to frontend for display.
9. Admin endpoints allow configuration edits and user management which are validated and written atomically before reloading in memory.

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
The Streamlit frontend provides six tabs, all requiring authentication:

1. **Login** - Centralized authentication interface for all users
2. **Text Input** – submit content for evaluation (regular users and admins)
3. **Overall Feedback** – displays overall score, strengths and opportunities (regular users and admins)
4. **Detailed Feedback** – shows rubric scores and segment-level comments (regular users and admins)
5. **Debug** – system diagnostics, API testing, and development tools (admins only)
6. **Admin** – configuration management, user management, and system monitoring (admins only)

The Admin tab includes:
- **Health Monitoring**: System status and service health checks
- **Configuration Management**: Edit YAML configuration files
- **User Management**: Add, edit, delete, and manage user accounts and roles
- **Session Management**: View and manage active sessions
- **Logout**: End administrative session

### 1.6 Deployment Topology
- Containers orchestrated by `docker-compose.yml` with Traefik reverse proxy.
- Volumes map host `./config`, `./data`, and `./logs` to `/app/*` in containers.
- Non-root container user UID/GID `1000:1000` to avoid permission issues.

Service diagram:
```
Client -> Traefik -> Backend (FastAPI) -> SQLite
                              ↘
                               LLM Service (Claude API)
Frontend (Streamlit) <- Traefik
```

---

## 2.0 Module Relationships
- `main.py` imports services and models to handle requests with authentication middleware.
- Models (`entities.py`) encapsulate database tables: `User`, `Session`, `Submission`, `Evaluation`.
- Services provide single-responsibility utilities: auth, config, LLM.
- Frontend `api_client.py` communicates with backend endpoints and handles retries with authentication headers.
- `state_manager.py` maintains session state, authentication status, and validation.

Sequence example for evaluation submission:
1. User authenticates via homepage login interface.
2. `frontend/components/api_client.py` POSTs to `/api/v1/evaluations/submit` with authentication headers.
3. `backend/main.py` routes to evaluation handler after validating user session and permissions.
4. Handler loads configs via `config_service`.
5. `llm_service` builds prompt from `prompt.yaml` and sends to Claude.
6. Parsed result is persisted using `models/entities.py` helpers.
7. Response object serialized and returned to frontend for display.

---

## 3.0 Security Architecture
- **Universal Authentication**: All application functions require user authentication via homepage login.
- **Role-Based Access Control**: Regular users and administrators have different permission sets.
- **Session Management**: All user actions require valid session tokens provided by authentication endpoints.
- **User Management**: Administrators can create, edit, delete, and manage user accounts and roles.
- **Rate limiting and brute force protection** configured via `auth.yaml` and Traefik labels.
- **Configuration files mounted read-only** in containers.
- **HTTPS termination handled by Traefik** with Let's Encrypt certificates.
- **Session tokens expire** after a configurable timeout (`auth.yaml`) and are stored in memory to avoid persistent credentials.
- **Brute force protection** counts failed login attempts and throttles accordingly.
- **Debug tab access** restricted to administrators only for security.

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
- `backend/main.py`
- `frontend/app.py`
- `docker-compose.yml`
