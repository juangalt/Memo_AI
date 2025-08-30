# Reference Manual
## Memo AI Coach

**Document ID**: 13_Reference_Manual.md
**Document Version**: 1.0
**Last Updated**: Phase 9
**Status**: Draft

---

## 1.0 Module Index
### Backend
- `backend/main.py` – FastAPI application with routes for health, admin authentication, configuration, sessions and evaluations.
- `backend/models/database.py` – Database connection manager (SQLite).
- `backend/models/entities.py` – ORM-like classes `User`, `Session`, `Submission`, `Evaluation`.
- `backend/services/auth_service.py` – password hashing, session tokens, brute force protection.
- `backend/services/config_service.py` – load and validate YAML configs with environment overrides.
- `backend/services/config_manager.py` – read/write configuration files with backups and validation.
- `backend/services/llm_service.py` – Claude API integration, prompt generation, response parsing.
- `backend/init_db.py` – initialize database schema.
- `backend/validate_config.py` – configuration validation utility.
- `backend/utils/logger.py` – shared logging setup for consistent format.

### Frontend (Vue.js)
- `vue-frontend/src/main.js` – Vue.js application entry point with router and store setup.
- `vue-frontend/src/services/api.js` – Axios HTTP client with automatic authentication headers.
- `vue-frontend/src/stores/auth.js` – Pinia store for authentication state management.
- `vue-frontend/src/stores/evaluation.js` – Pinia store for evaluation state management.
- `vue-frontend/src/router/index.js` – Vue Router configuration with route guards.
- `vue-frontend/src/views/` – Vue components for each application view (Login, TextInput, etc.).
- `vue-frontend/src/components/` – Reusable Vue components (Layout, ProgressBar, etc.).

## 2.0 Data Models
| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `users` | Admin accounts | username, password_hash, is_admin |
| `sessions` | User sessions | session_id, user_id, expires_at |
| `submissions` | Text submissions | text_content, session_id |
| `evaluations` | LLM evaluations | overall_score, strengths, opportunities, rubric_scores, segment_feedback |
| `schema_migrations` | Migration history | version, description |

## 3.0 Configuration Keys
See detailed descriptions in `docs/04_Configuration_Guide.md`. Important keys include:
- `LLM_API_KEY` – environment variable for Anthropic access.
- `session_management.session_timeout` – auth.yaml.
- `provider.model` – llm.yaml.
- `rubric.criteria[*].weight` – rubric.yaml weights for scoring.
- `prompt.templates.evaluation_prompt.user_template` – base template for LLM evaluation.

## 4.0 Constants and Defaults
- Maximum text length: 10,000 characters (`llm.yaml` and backend validation).
- Session token length: 32 characters (`auth.yaml`).
- Default admin user: `admin` created by `init_db.py` with password from `ADMIN_PASSWORD` env variable.
- Configuration backups: `config/backups/<timestamp>_<name>.yaml`.
- Health endpoint path: `/health` returning component statuses.

## 5.0 File Paths
- Config directory: `config/` (mounted to `/app/config/`).
- Database file: `data/memoai.db`.
- Log directory: `logs/`.
- Deployment script: `deploy-production.sh`.
- Test runners: `tests/run_quick_tests.py`, `tests/run_production_tests.py`.

## 6.0 Reference Links
- `docs/05_API_Documentation.md` for endpoint details.
- `docs/04_Configuration_Guide.md` for configuration fields.
- `devlog/changelog.md` for development history.
- `docs/10_Deployment_Guide.md` for container orchestration and SSL setup.
