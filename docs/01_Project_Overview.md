# Project Overview
## Memo AI Coach

**Document ID**: 01_Project_Overview.md
**Document Version**: 1.2
**Last Updated**: Phase 9
**Status**: Draft

---

## 1.0 Introduction

### 1.1 Purpose
Memo AI Coach is an instructional text evaluation system that provides AI-generated feedback for business memos. The application helps writers improve by scoring submissions against a detailed rubric and offering segment-level suggestions.

### 1.2 Goals
- Evaluate text against a healthcare investment memo rubric.
- Return strengths, opportunities, rubric scores and detailed segment feedback.
- Maintain simplicity for novice developers while remaining extensible.
- Provide secure, role-based access control for all users.

### 1.3 Target Users
- **Regular Users** – writers seeking automated memo feedback with authenticated access.
- **Administrators** – managing configuration, monitoring, user management, and system administration with elevated privileges.
- **Developers/AI agents** extending the system.

### 1.4 Stakeholders
- **Learners** – individuals submitting memos for structured feedback through authenticated sessions.
- **Business Coaches** – review aggregate scores and suggestions to guide instruction.
- **Operations Team** – deploy and maintain production instances with administrative access.
- **Future Contributors** – extend functionality through well documented interfaces.

### 1.5 Key Terms
- **Evaluation** – a structured response containing overall scores, strengths, opportunities and segment level feedback.
- **Session** – server side context linking multiple submissions from the same authenticated user for configured duration.
- **Mock Mode** – development setting that simulates LLM responses without contacting the external API.
- **Role-Based Access** – system of user permissions distinguishing regular users from administrators.

---

## 2.0 Key Features
- FastAPI backend with RESTful API and authentication middleware.
- Streamlit frontend with tabbed interface requiring user authentication.
- SQLite database with WAL mode for 100+ concurrent users.
- YAML-based configuration for rubric, prompts, LLM and authentication.
- Claude LLM integration with mock mode for development.
- **Universal Authentication** – all users must authenticate through homepage login.
- **Role-Based Access Control** – regular users and administrators with different permission sets.
- **User Management** – administrators can create, edit, delete, and manage user accounts and roles.
- **Debug Tab** – system diagnostics and development tools for administrators.
- Admin authentication and configuration editor.
- Comprehensive testing and deployment scripts.
- Detailed documentation replacing legacy `devspecs/` files and `devlog/changelog.md` as the primary source of truth.

---

## 3.0 Technology Stack
| Layer | Technology |
|------|------------|
| Backend | Python, FastAPI |
| Frontend | Python, Streamlit |
| Database | SQLite |
| LLM | Anthropic Claude API |
| Deployment | Docker, docker-compose, Traefik |
| Configuration | YAML |
| Authentication | Session-based with role management |

The stack was selected to align with project principles of simplicity, transparency and rapid iteration. All components are fully containerized to ensure consistent environments across development and production.

---

## 4.0 System Overview
1. **Authentication**: Users authenticate through centralized homepage login interface.
2. **Role Assignment**: System assigns appropriate permissions based on user credentials.
3. Users submit text through the Streamlit UI with authenticated session.
4. Frontend sends text to backend `/api/v1/evaluations/submit` with authentication headers.
5. Backend validates user session and permissions before processing.
6. Backend loads YAML configs and sends prompt to Claude API.
7. Evaluation results are stored and returned to frontend.
8. Admins manage configs, users, and sessions via dedicated endpoints and UI with elevated privileges.
9. Configuration edits are validated, backed up and immediately applied.
10. Health endpoints provide operational status for monitoring tools.
11. Debug tab provides system diagnostics and development tools for administrators.
12. User management allows administrators to create, edit, delete, and manage user accounts and roles.

---

## 5.0 Project Timeline
- Phases 1-8: Completed (environment, backend, frontend, core evaluation, admin functions, integration, deployment, testing).
- **Phase 9**: Comprehensive documentation (current phase).

## 6.0 Non-Functional Requirements
- **Performance**: LLM evaluations must return within 15 seconds; UI loads in under one second.
- **Scalability**: SQLite operates in WAL mode to support 100+ concurrent users.
- **Reliability**: Configuration changes are atomic with automatic backups.
- **Security**: All application functions require user authentication with role-based access control.
- **Maintainability**: Code and docs favor readability with minimal abstraction.
- **Portability**: Entire stack runs via Docker with minimal host dependencies.

## 7.0 Out of Scope
- Rich text editing beyond basic text area input.
- Advanced user account management beyond basic authentication.
- Advanced analytics or reporting dashboards.
- Automated rubric editing beyond YAML configuration files.

## 8.0 Document History
- Derived from development phases recorded in `devlog/changelog.md`.
- Phase 1–8 entries capture environment setup through production validation.
- This document supersedes previous devspec overviews as the canonical reference.

## 9.0 References
- `docs/02_Architecture_Documentation.md`
- `docs/05_API_Documentation.md`
- `devlog/changelog.md`
