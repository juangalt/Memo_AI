# Architecture Documentation
## Memo AI Coach

**Document ID**: 02_Architecture_Documentation.md
**Document Version**: 3.0
**Last Updated**: Phase 11 - LLM Refactor & Health Security Implementation
**Status**: Active

---

## 1.0 System Architecture

### 1.1 Component Overview
- **Frontend**: Vue.js application (`vue-frontend/`) providing a modern reactive interface with authentication-gated access and dynamic rubric display.
- **Backend**: FastAPI service (`backend/main.py`) exposing REST endpoints with authentication middleware and enhanced LLM processing.
- **Database**: SQLite accessed through `backend/models/database.py` using WAL mode.
- **LLM Service**: `backend/services/llm_service.py` for Claude API interaction with Jinja2 templating, language detection, and Pydantic validation.
- **Configuration Service**: `backend/services/config_service.py` and `config_manager.py` for loading and editing YAML configs with Pydantic validation.
- **Authentication Service**: `backend/services/auth_service.py` providing user and admin login, session validation, and role-based access control.
- **Language Detection Service**: `backend/services/language_detection.py` for robust multi-language text identification.
- **Configuration Models**: `backend/models/config_models.py` with Pydantic models for type-safe configuration validation.
- **Authentication Decorators**: `backend/decorators.py` with `@require_auth` decorator for endpoint protection.

Each component follows single-responsibility design so that updates to one area minimally impact others. Communication occurs through well defined interfaces and explicit data contracts. The new architecture adds robust language detection, dynamic prompt generation, and comprehensive configuration validation.

### 1.2 Authentication Architecture
The system implements session-based authentication with role-based access control. See `docs/02b_Authentication_Specifications.md` for complete authentication details.

### 1.3 Data Flow
1. User authenticates and receives session token.
2. User submits text via authenticated interface.
3. **Language Detection**: System automatically detects text language using multiple detection methods.
4. **Dynamic Prompt Generation**: Backend generates language-appropriate prompts using Jinja2 templates.
5. Frontend calls backend evaluation endpoint with authentication headers.
6. Backend validates authentication and processes request.
7. Backend loads configurations (validated by Pydantic) and sends generated prompt to LLM service.
8. Response is parsed, stored, and returned to frontend with language detection metadata.
9. Admin functions allow system monitoring, user management, and configuration editing.

### 1.4 Data Model
| Table | Purpose | Key Fields |
|-------|---------|------------|
| `users` | user accounts with role-based access | `id`, `email`, `password_hash`, `role`, `created_at` |
| `sessions` | track active evaluation sessions | `id`, `user_id`, `created_at`, `updated_at` |
| `submissions` | store original memo text | `id`, `session_id`, `content` |
| `evaluations` | store LLM generated feedback | `id`, `submission_id`, `overall`, `strengths`, `opportunities`, `rubric_scores`, `segments`, `language_detected`, `detection_confidence` |

Relationships:
- A `user` has many `sessions`.
- A `session` has many `submissions`.
- Each `submission` has one `evaluation`.

### 1.5 Frontend Interface Structure
The Vue.js frontend provides a single-page application with router-based navigation and role-based access control:

1. **Home** (`/`) - Beautiful welcome page with application overview and copyright footer
2. **Login** (`/login`) - Authentication interface with "Back to Home" link and copyright footer
3. **Text Input** (`/text-input`) – Content submission for evaluation (authenticated) with copyright footer
4. **Overall Feedback** (`/overall-feedback`) – Evaluation results display with dynamic rubric scores and language detection (authenticated) with copyright footer
5. **Detailed Feedback** (`/detailed-feedback`) – Detailed scoring and comments with language-specific content (authenticated) with copyright footer
6. **Help** (`/help`) – Comprehensive documentation and rubric explanation (authenticated) with copyright footer
7. **Admin** (`/admin`) – System monitoring, configuration validation, user management, and prompt template editing (admin only) with copyright footer
8. **Last Evaluation** (`/last-evaluation`) – Raw LLM evaluation data viewer with language detection metadata (admin only) with copyright footer
9. **Debug** (`/debug`) – System diagnostics, API testing, and development tools (admin only) with copyright footer

Vue Router controls navigation and enforces authentication requirements on protected routes. The Layout component provides consistent navigation and is used in individual view components when needed. All pages include a consistent copyright footer with "© Copyright FGS" for brand protection and professional appearance.

**New Components**:
- `DynamicRubricScores.vue` - Automatically adapts to any rubric structure
- `LanguageDetectionDisplay.vue` - Shows detected language with confidence indicators

### 1.6 Deployment Topology
- Containers orchestrated by `docker-compose.yml` with Traefik reverse proxy.
- Volumes map host `./config`, `./data`, and `./logs` to `/app/*` in containers.
- Non-root container user UID/GID `1000:1000` to avoid permission issues.

Service diagram:
```
Client -> Traefik -> Backend (FastAPI) -> SQLite
                              ↘
                               LLM Service (Claude API + Jinja2)
                               Language Detection Service
Frontend (Vue.js) <- Traefik
```

---

## 2.0 Module Relationships
- `main.py` imports services and models to handle requests with authentication middleware.
- Models (`entities.py`) encapsulate database tables: `User`, `Session`, `Submission`, `Evaluation`.
- Services provide single-responsibility utilities: auth, config, LLM, language detection.
- Configuration models (`config_models.py`) provide Pydantic validation for all YAML configurations.
- Vue.js `services/api.js` provides HTTP client with automatic authentication headers.
- Vue.js `stores/auth.js` manages authentication state and session validation.
- Vue.js `router/index.js` enforces route-based access control.

Sequence example for evaluation submission:
1. User authenticates via Vue.js login interface.
2. `vue-frontend/services/evaluation.js` POSTs to `/api/v1/evaluations/submit` with authentication headers.
3. `backend/main.py` routes to evaluation handler after validating user session and permissions.
4. **Language Detection**: `language_detection.py` identifies text language using multiple methods.
5. **Dynamic Prompt Generation**: `llm_service.py` uses Jinja2 templates to generate language-appropriate prompts.
6. Handler loads configs via `config_service` with Pydantic validation.
7. `llm_service` builds prompt from Jinja2 templates and sends to Claude.
8. Parsed result is persisted using `models/entities.py` helpers with language metadata.
9. Response object serialized and returned to Vue.js frontend for display with dynamic rubric rendering.

---

## 3.0 Security Architecture
- **Authentication**: Session-based authentication with role-based access control
- **Authorization**: Permission validation on all endpoints and UI components
- **Session Security**: Configurable token expiration and validation
- **Network Security**: HTTPS termination via Traefik with Let's Encrypt certificates
- **Container Security**: Read-only configuration files and non-root user execution
- **Rate Limiting**: Request throttling via Traefik and application-level controls
- **Input Validation**: Pydantic models ensure all configuration data is validated and sanitized

See `docs/02b_Authentication_Specifications.md` for detailed authentication security measures.

---

## 4.0 Scalability and Performance
- SQLite database uses WAL mode (`init_db.py` sets `PRAGMA journal_mode = WAL`).
- LLM service tracks processing time and enforces <15s response target (`config/llm.yaml`).
- **Language Detection**: Multiple detection methods with fallback strategies for robust performance.
- **Template Caching**: Jinja2 templates are compiled and cached for improved performance.
- **Configuration Validation**: Pydantic validation ensures configuration integrity without performance impact.
- Traefik rate limiting protects against excessive requests.
- Backend and frontend services are stateless allowing horizontal scaling by adding containers behind Traefik.
- Configuration reloads avoid service restarts, enabling runtime changes without downtime.
- Authentication overhead minimized through efficient session validation.

---

## 5.0 New Architecture Features

### 5.1 Language Detection System
- **Multiple Detection Methods**: Polyglot, Langdetect, and Pycld2 for robust identification
- **Fallback Strategies**: Heuristic detection when primary methods fail
- **Confidence Scoring**: Reliability indicators for detection accuracy
- **Performance Optimization**: Cached detection results for improved response times

### 5.2 Dynamic Prompt Generation
- **Jinja2 Templating**: Flexible template system for prompt generation
- **Language-Specific Prompts**: Automatic adaptation to detected language
- **Rubric Flexibility**: Templates automatically adapt to any rubric structure
- **Configuration Validation**: Pydantic models ensure template variables are valid

### 5.3 Configuration Management
- **Pydantic Validation**: Type-safe configuration validation with clear error messages
- **Dynamic Reloading**: Configuration changes take effect without service restarts
- **Backup Management**: Automatic timestamped backups before configuration changes
- **Validation Rules**: Comprehensive validation for all configuration parameters

---

## 6.0 References
- `docs/02b_Authentication_Specifications.md` - Complete authentication specifications
- `devlog/prompt_refactor.md` - Prompt refactor implementation plan
- `backend/main.py`
- `vue-frontend/` - Vue.js frontend application
- `docker-compose.yml`
- `backend/models/config_models.py` - Pydantic configuration models
- `backend/services/language_detection.py` - Language detection service
