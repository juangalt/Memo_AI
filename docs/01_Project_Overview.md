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
- **Administrators** – managing configuration validation, monitoring, user management, and system administration with elevated privileges.
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
- Vue.js frontend with modern reactive interface requiring user authentication.
- SQLite database with WAL mode for 100+ concurrent users.
- YAML-based configuration for rubric, prompts, LLM and authentication.
- Claude LLM integration with mock mode for development.
- **Secure Authentication** – session-based authentication with role-based access control.
- **Beautiful Welcome Page** – Professional landing page with application overview.
- **Help Documentation** – Comprehensive user guide and rubric explanation.
- **Conditional Admin Access** – Admin features only visible to admin users.
- **Responsive Design** – Mobile and desktop compatible interface.
- Admin interface for system monitoring and user management.
- Debug interface for system diagnostics and development tools.
- Comprehensive testing and deployment scripts.
- Detailed documentation replacing legacy `devspecs/` files and `devlog/changelog.md` as the primary source of truth.

---

## 3.0 Technology Stack
| Layer | Technology |
|------|------------|
| Backend | Python, FastAPI |
| Frontend | JavaScript, Vue.js 3, TypeScript |
| Database | SQLite |
| LLM | Anthropic Claude API |
| Deployment | Docker, docker-compose, Traefik |
| Configuration | YAML |
| Authentication | Session-based with role management |

The stack was selected to align with project principles of simplicity, transparency and rapid iteration. All components are fully containerized to ensure consistent environments across development and production.

---

## 4.0 System Overview
1. **Welcome Page**: Users land on a beautiful, professional welcome page explaining the application.
2. **Authentication**: Users authenticate through secure login with role-based access control.
3. **Text Submission**: Users submit text through the authenticated Vue.js interface.
4. **API Communication**: Frontend communicates with backend APIs using session tokens.
5. **Evaluation Processing**: Backend processes evaluations and returns structured feedback.
6. **Help Documentation**: Users can access comprehensive help and rubric documentation.
7. **Admin Functions**: Administrators manage system monitoring, configuration validation, and user accounts.
8. **System Monitoring**: Health endpoints provide system monitoring capabilities.
9. **Debug Tools**: Administrators can access system diagnostics and development tools.

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
- `docs/02b_Authentication_Specifications.md` - Complete authentication specifications
- `docs/05_API_Documentation.md`
- `devlog/vue_frontend_implementation_plan.md` - Vue.js frontend implementation plan
- `devlog/changelog.md`
