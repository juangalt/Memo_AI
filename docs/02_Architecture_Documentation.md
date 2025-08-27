# Architecture Documentation
## Memo AI Coach

**Document ID**: 02_Architecture_Documentation.md
**Document Version**: 1.0
**Last Updated**: Phase 9
**Status**: Draft

---

## 1.0 System Architecture

### 1.1 Component Overview
- **Frontend**: Streamlit application (`frontend/app.py`) presenting a tabbed interface.
- **Backend**: FastAPI service (`backend/main.py`) exposing REST endpoints.
- **Database**: SQLite accessed through `backend/models/database.py` using WAL mode.
- **LLM Service**: `backend/services/llm_service.py` for Claude API interaction.
- **Configuration Service**: `backend/services/config_service.py` and `config_manager.py` for loading and editing YAML configs.
- **Authentication Service**: `backend/services/auth_service.py` providing admin login and session validation.

Each component follows single-responsibility design so that updates to one area minimally impact others. Communication occurs through well defined interfaces and explicit data contracts.

### 1.2 Data Flow
1. User submits text via frontend.
2. Frontend calls backend evaluation endpoint.
3. Backend loads rubric, prompt and LLM configs then sends prompt to Claude.
4. LLM response is parsed and stored in SQLite.
5. Backend returns evaluation to frontend for display.
6. Admin endpoints allow configuration edits which are validated and written atomically before reloading in memory.

### 1.3 Data Model
| Table | Purpose | Key Fields |
|-------|---------|------------|
| `users` | future extension for named accounts; currently unused | `id`, `email`, `created_at` |
| `sessions` | track active evaluation sessions | `id`, `created_at`, `updated_at` |
| `submissions` | store original memo text | `id`, `session_id`, `content` |
| `evaluations` | store LLM generated feedback | `id`, `submission_id`, `overall`, `strengths`, `opportunities`, `rubric_scores`, `segments` |

Relationships:
- A `session` has many `submissions`.
- Each `submission` has one `evaluation`.

### 1.3 Deployment Topology
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
- `main.py` imports services and models to handle requests.
- Models (`entities.py`) encapsulate database tables: `User`, `Session`, `Submission`, `Evaluation`.
- Services provide single-responsibility utilities: auth, config, LLM.
- Frontend `api_client.py` communicates with backend endpoints and handles retries.
- `state_manager.py` maintains session state and validation.

Sequence example for evaluation submission:
1. `frontend/components/api_client.py` POSTs to `/api/v1/evaluations/submit`.
2. `backend/main.py` routes to evaluation handler which loads configs via `config_service`.
3. `llm_service` builds prompt from `prompt.yaml` and sends to Claude.
4. Parsed result is persisted using `models/entities.py` helpers.
5. Response object serialized and returned to frontend for display.

---

## 3.0 Security Architecture
- All admin actions require session tokens provided by `/api/v1/admin/login`.
- Rate limiting and brute force protection configured via `auth.yaml` and Traefik labels.
- Configuration files mounted read-only in containers.
- HTTPS termination handled by Traefik with Let's Encrypt certificates.
- Session tokens expire after a configurable timeout (`auth.yaml`) and are stored in memory to avoid persistent credentials.
- Brute force protection counts failed login attempts and throttles accordingly.

---

## 4.0 Scalability and Performance
- SQLite database uses WAL mode (`init_db.py` sets `PRAGMA journal_mode = WAL`).
- LLM service tracks processing time and enforces <15s response target (`config/llm.yaml`).
- Traefik rate limiting protects against excessive requests.
- Backend and frontend services are stateless allowing horizontal scaling by adding containers behind Traefik.
- Configuration reloads avoid service restarts, enabling runtime changes without downtime.

---

## 5.0 References
- `backend/main.py`
- `frontend/app.py`
- `docker-compose.yml`
