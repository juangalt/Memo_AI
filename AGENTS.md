# AI Agent Guidelines
## Memo AI Coach Project

**Version**: 3.0
**Last Updated**: Phase 9 - Documentation Update
**Purpose**: Comprehensive guidance for AI agents working on the Memo AI Coach project

---

## 🚨 CRITICAL: Project Specifications

### **MANDATORY: Read All Documentation in `docs/` Directory**

**BEFORE STARTING ANY WORK**, AI agents **MUST** read and understand the complete project specifications:

#### **📋 Required Reading Order:**
1. **`docs/01_Project_Overview.md`** - Project goals, technology stack, and requirements
2. **`docs/02_Architecture_Documentation.md`** - System architecture and component relationships
3. **`docs/02b_Authentication_Specifications.md`** - Complete authentication system specifications
4. **`docs/04_Configuration_Guide.md`** - Configuration management and YAML files
5. **`docs/05_API_Documentation.md`** - Complete API reference and endpoints
6. **`docs/08_Development_Guide.md`** - Development procedures and coding standards
7. **`docs/09_Testing_Guide.md`** - Testing procedures and frameworks
8. **`docs/AGENTS.md`** (in docs/) - Documentation guidelines and quality standards

#### **📚 Additional Reference Documents:**
- `docs/03_Installation_Guide.md` - Installation and setup procedures
- `docs/06_User_Guide.md` - End-user documentation
- `docs/07_Administration_Guide.md` - System administration
- `docs/10_Deployment_Guide.md` - Production deployment
- `docs/11_Maintenance_Guide.md` - System maintenance
- `docs/12_Troubleshooting_Guide.md` - Problem resolution
- `docs/13_Reference_Manual.md` - Technical reference
- `docs/14_Tailwind_CSS_Troubleshooting.md` - Vue.js frontend styling issues

### **🚫 CRITICAL RULE: DO NOT EDIT `docs/` DIRECTORY**
- **NEVER** modify, update, or edit any files in the `docs/` directory
- **NEVER** add, remove, or change content in documentation files
- The `docs/` directory contains the **authoritative project specifications**
- Only modify `docs/` files when the **user explicitly requests** it
- All other directories (backend/, vue-frontend/, config/, etc.) can be modified as needed

---

## 🎯 Project Overview Summary

### **What is Memo AI Coach?**
Memo AI Coach is an **instructional text evaluation system** that provides AI-generated feedback for business memos. The application helps writers improve by:

- Evaluating text against a detailed rubric
- Returning strengths, opportunities, and rubric scores
- Providing segment-level suggestions
- Maintaining simplicity for novice developers while remaining extensible
- Providing secure, role-based access control for all users

### **Key Features:**
- **FastAPI backend** with RESTful API and authentication middleware
- **Vue.js 3 frontend** with TypeScript and modern reactive interface
- **SQLite database** with WAL mode for 100+ concurrent users
- **YAML-based configuration** for rubric, prompts, LLM, and authentication
- **Claude LLM integration** with mock mode for development
- **Secure Authentication** – session-based authentication with role-based access control
- **Beautiful Welcome Page** – Professional landing page with application overview
- **Help Documentation** – Comprehensive user guide and rubric explanation
- **Conditional Admin Access** – Admin features only visible to admin users
- **Responsive Design** – Mobile and desktop compatible interface
- **Tailwind CSS** – Modern styling with v3.4.17 (stable) configuration
- Admin interface for configuration and system management
- Comprehensive testing and deployment scripts
- Detailed documentation replacing legacy `devspecs/` files as the primary source of truth

### **Technology Stack:**
| Component | Technology |
|-----------|------------|
| Backend | Python, FastAPI |
| Frontend | JavaScript, Vue.js 3, TypeScript |
| Database | SQLite with WAL mode |
| LLM | Anthropic Claude API |
| Deployment | Docker, docker-compose, Traefik |
| Configuration | YAML files |
| Authentication | Session-based with role management |
| Styling | Tailwind CSS v3.4.17 |

### **Performance Requirements:**
- **<15 seconds** for LLM evaluation responses
- **<1 second** for UI loads
- **100+ concurrent users** support via SQLite WAL mode
- **<500ms** for authentication responses
- **<100ms** for session validation

---

## 🏗️ System Architecture Summary

### **Component Overview:**
- **Frontend**: Vue.js 3 application (`vue-frontend/`) providing a modern reactive interface with authentication-gated access
- **Backend**: FastAPI service (`backend/main.py`) exposing REST endpoints with authentication middleware
- **Database**: SQLite accessed through `backend/models/database.py` using WAL mode
- **LLM Service**: `backend/services/llm_service.py` for Claude API interaction
- **Configuration Service**: `backend/services/config_service.py` and `config_manager.py` for loading and editing YAML configs
- **Authentication Service**: `backend/services/auth_service.py` providing user and admin login, session validation, and role-based access control

### **Data Flow:**
1. User authenticates and receives session token
2. User submits text via authenticated Vue.js interface
3. Frontend calls backend evaluation endpoint with authentication headers
4. Backend validates authentication and processes request
5. Backend loads configurations and sends prompt to LLM service
6. Response is parsed, stored, and returned to frontend
7. Admin functions allow configuration and user management

### **Data Model:**
| Table | Purpose | Key Fields |
|-------|---------|------------|
| `users` | user accounts with role-based access | `id`, `username`, `password_hash`, `is_admin`, `is_active`, `created_at` |
| `sessions` | track active evaluation sessions | `id`, `session_id`, `user_id`, `is_admin`, `is_active`, `created_at`, `expires_at` |
| `submissions` | store original memo text | `id`, `session_id`, `content` |
| `evaluations` | store LLM generated feedback | `id`, `submission_id`, `overall`, `strengths`, `opportunities`, `rubric_scores`, `segments` |

### **Frontend Interface Structure:**
The Vue.js frontend provides a single-page application with router-based navigation and role-based access control:

1. **Home** (`/`) - Beautiful welcome page with application overview
2. **Login** (`/login`) - Authentication interface with "Back to Home" link
3. **Text Input** (`/text-input`) – Content submission for evaluation (authenticated)
4. **Overall Feedback** (`/overall-feedback`) – Evaluation results display (authenticated)
5. **Detailed Feedback** (`/detailed-feedback`) – Detailed scoring and comments (authenticated)
6. **Help** (`/help`) – Comprehensive documentation and rubric explanation (authenticated)
7. **Admin** (`/admin`) – System management and configuration (admin only)
8. **Debug** (`/debug`) – System diagnostics and tools (admin only)

### **Security Architecture:**
- **Universal Authentication**: All users must authenticate before accessing any application functions
- **Role-Based Access**: Clear distinction between regular users and administrators
- **Session-Based**: Stateless session tokens for scalable authentication
- **Defense in Depth**: Multiple security layers with prioritized protection levels
- **Brute Force Protection**: Attempt tracking + temporary lockout
- **Rate Limiting**: Request throttling via Traefik and application-level controls
- **Configuration Security**: Read-only configuration files and non-root user execution

---

## 🔐 Authentication System

### **Authentication Flow:**
1. User enters credentials (username/password)
2. System validates against brute force protection
3. Session token generated and stored in database
4. Token included in `X-Session-Token` header for all requests
5. Backend validates token on each protected request
6. Session expires according to configuration (default: 1 hour)

### **User Types:**
| User Type | Description | Permissions |
|-----------|-------------|-------------|
| **Regular User** | Writers seeking memo feedback | Submit evaluations, view results |
| **Administrator** | System managers | All user permissions + configuration, user management, debug access |

### **Security Priority Levels:**
- **🔴 Critical**: Session token validation, password hashing, secure token generation
- **🟡 Important**: Brute force protection, rate limiting, input validation
- **🟢 Recommended**: Audit logging, CSRF protection, secure cookie settings
- **🔵 Optional**: Advanced threat detection, session hijacking prevention

### **Configuration Presets:**
- **Development**: 2-hour sessions, basic security
- **Production**: 1-hour sessions, comprehensive security
- **Enterprise**: 30-minute sessions, advanced security features

---

## ⚙️ Configuration Management

### **YAML Configuration Files:**
All runtime behavior controlled by **4 YAML files** in `config/`:

#### **`config/rubric.yaml`**
- Defines evaluation rubric and scoring categories
- Contains criteria with weights and scoring guidance
- Includes evaluation framework for strengths and opportunities

#### **`config/prompt.yaml`**
- Holds prompt templates and instruction lists for LLM
- Contains system messages and user templates
- Defines prompt variables for dynamic field injection

#### **`config/llm.yaml`**
- Configures LLM provider and runtime limits
- Sets API configuration, timeouts, retries, token limits
- Defines performance optimization (<15s requirement)

#### **`config/auth.yaml`**
- Defines authentication and security parameters
- Configures session management, timeouts, cookie settings
- Sets security settings, rate limiting, input validation

### **Environment Variables:**
- `.env` provides base values: `DOMAIN`, `LLM_API_KEY`, `SECRET_KEY`, `ADMIN_PASSWORD`
- Can override YAML fields for flexibility
- Used for performance settings and sensitive data

### **Frontend Configuration:**
- **Tailwind CSS**: Use v3.4.17 (stable) for production. Avoid v4.x (beta) versions
- **PostCSS**: Configure with `tailwindcss` plugin (not `@tailwindcss/postcss`)
- **Build Process**: Use `npm install` instead of `npm ci` for better dependency management
- **CSS Classes**: All components use Tailwind classes for consistent styling

### **Configuration Validation:**
- Run `python3 backend/validate_config.py` to ensure configs are valid
- Admin UI creates timestamped backups before changes
- Configuration reloads happen without service restarts

---

## 🔌 API Reference Summary

### **Base URL:** `http://<domain>/api`
All endpoints return JSON with `data`, `meta`, and `errors` keys.

### **Public Endpoints:**
- `GET /` - Root information
- `GET /health` - Aggregate health status
- `GET /docs` - Swagger UI with OpenAPI schema

### **Authentication Endpoints:**
- `POST /api/v1/auth/login` - Unified login for all users (admins and regular users)
- `POST /api/v1/auth/logout` - Unified logout for all users
- `GET /api/v1/auth/validate` - Validate session token and get user info

### **Session Management:**
- `POST /api/v1/sessions/create` - Create authenticated session (requires login first)
- `GET /api/v1/sessions/{session_id}` - Retrieve session details
- `DELETE /api/v1/sessions/{session_id}` - End session

### **Evaluation Endpoints:**
- `POST /api/v1/evaluations/submit` - Submit text for evaluation
- `GET /api/v1/evaluations/{evaluation_id}` - Retrieve evaluation result
- `GET /api/v1/evaluations/session/{session_id}` - List evaluations for session

### **Admin Endpoints (Require `is_admin: true`):**
- `GET /api/v1/admin/config/{config_name}` - Read configuration
- `PUT /api/v1/admin/config/{config_name}` - Update configuration
- `POST /api/v1/admin/users/create` - Create new user account
- `GET /api/v1/admin/users` - List all users
- `DELETE /api/v1/admin/users/{username}` - Delete user account

### **Request/Response Format:**
```json
{
  "data": {
    "evaluation": {
      "overall_score": 4.2,
      "strengths": ["..."],
      "opportunities": ["..."],
      "rubric_scores": {"criterion": {"score": 4, "justification": "..."}},
      "segment_feedback": [...]
    }
  },
  "meta": {"timestamp": "...", "request_id": "..."},
  "errors": []
}
```

### **Authentication:**
- All protected endpoints require `X-Session-Token` header
- Session creation requires prior authentication
- Tokens expire according to `auth.yaml` configuration
- Role-based access control enforced on all endpoints

---

## 💻 Development Standards

### **Coding Principles:**
- **Favor simplicity and readability** over abstraction
- Each module serves a **single responsibility**
- Provide **docstrings and inline comments** for educational clarity
- **Follow PEP 8** style with descriptive variable names
- **Use `evaluate_text_with_llm`** for all evaluations (handles prompt generation and error management)

### **Repository Structure:**
```
backend/       # FastAPI service
vue-frontend/  # Vue.js reactive interface
config/        # YAML configuration files
tests/         # Test suites
docs/          # Comprehensive project documentation
```

### **Backend Development:**
- Entry point: `backend/main.py`
- Data models in `backend/models/entities.py`
- Services in `backend/services/` (config, auth, LLM)
- Error responses use standard `{data: null, meta, errors}` schema
- Add new endpoints by extending `backend/main.py`

### **Frontend Development (Vue.js):**
- Entry point: `vue-frontend/src/main.js`
- `vue-frontend/src/services/api.js` provides HTTP client with automatic authentication headers
- `vue-frontend/src/stores/auth.js` manages authentication state using Pinia
- `vue-frontend/src/router/index.js` handles route-based navigation and access control
- Follow Vue 3 Composition API patterns for reactive components
- Views should be added under `vue-frontend/src/views/` with corresponding routes
- Components should be added under `vue-frontend/src/components/` with clear, commented functions
- **Layout Component**: Use Layout wrapper in view components when navigation is needed
- **Tailwind CSS**: Use v3.4.17 (stable) with proper PostCSS configuration
- **Authentication Flow**: Login redirects to `/text-input`, logout redirects to `/`
- **Admin Access**: Conditional menu items based on `isAdmin` status

### **Vue Router Integration:**
- **Global Auth Store Access**: Router guards must access global auth store via `window.authStoreInstance`
- **Session Validation**: Implement automatic session validation before protected route access
- **Authentication Redirects**: Handle authentication redirects gracefully with proper error messages
- **Route Protection**: Use `meta: { requiresAuth: true, requiresAdmin: true }` for protected routes

### **Component Architecture Guidelines:**
- **Layout Usage**: Use Layout component in view components when navigation is needed
- **Component Hierarchy**: Implement proper component hierarchy to avoid UI duplication
- **Authentication State Display**: Layout should display authentication status and user information
- **Navigation Structure**: Implement tab-based navigation with proper authentication state integration
- **Error Handling**: Display authentication errors gracefully with user-friendly messages

### **Configuration & Secrets:**
- Never commit API keys or passwords
- Use environment variables or `.env` for sensitive data
- Configuration editing through admin API or `config_manager.py`
- Update documentation when adding new config keys

---

## 🧪 Testing Standards

### **Test Categories:**
- **Configuration Tests** - Environment and config file validation
- **Integration Tests** - API endpoints, session management, LLM responses
- **Performance Tests** - Load testing against <15s requirement
- **Security Tests** - Basic security validation
- **End-to-End Tests** - Production deployment verification

### **Running Tests:**
```bash
# Quick suite (non-performance tests)
python3 tests/run_quick_tests.py

# Full production suite (includes performance)
python3 tests/run_production_tests.py
```

### **Test Outputs:**
- Results stored in `logs/` directory
- JSON files with summary statistics and assertion outcomes
- Category-specific results for each test type

### **Test Data:**
- Tests interact with running containers
- Use mock LLM responses for local development (unset `LLM_API_KEY`)
- Performance tests adjustable via environment variables

---

## 🎨 Frontend Styling Guidelines

### **Tailwind CSS Configuration:**
- **Version**: Use Tailwind CSS v3.4.17 (stable) for production
- **PostCSS**: Configure with `tailwindcss` plugin (not `@tailwindcss/postcss`)
- **Build Process**: Use `npm install` instead of `npm ci` for better dependency management
- **CSS Classes**: All components use Tailwind classes for consistent styling

### **Critical Tailwind Issues:**
- **Avoid v4.x**: Beta versions cause build failures and styling issues
- **CSS File Size**: Correct builds produce 25-30 kB CSS files (not 4-5 kB)
- **PostCSS Plugin**: Use `tailwindcss: {}` not `@tailwindcss/postcss: {}`
- **Package Dependencies**: Ensure correct version in package.json

### **Component Styling Patterns:**
- Use Tailwind utility classes for all styling
- Maintain consistent spacing and typography
- Implement responsive design for mobile and desktop
- Follow established color schemes and design patterns

---

## 📋 Implementation Checklist

### **Before Starting Any Work:**
- [ ] **MANDATORY**: Read all relevant `docs/` files completely
- [ ] Understand the specific requirement being implemented
- [ ] Review related architecture components
- [ ] Check data model requirements
- [ ] Verify API specifications
- [ ] Consider UI/UX implications
- [ ] Review testing requirements
- [ ] Check authentication requirements

### **During Implementation:**
- [ ] Follow coding principles (simplicity, readability, single responsibility)
- [ ] Add comprehensive docstrings and inline comments
- [ ] Use established patterns and naming conventions
- [ ] Include error handling with educational messages
- [ ] Ensure backward compatibility
- [ ] Test all procedures and examples
- [ ] Validate against documented acceptance criteria
- [ ] Implement proper authentication and authorization

### **Code Quality Standards:**
- [ ] Code is self-documenting and easy to understand
- [ ] All functions have clear docstrings
- [ ] Error messages are helpful and educational
- [ ] Code follows established patterns
- [ ] No complex abstractions unless absolutely necessary
- [ ] Maintains consistency with existing codebase
- [ ] Proper authentication and security measures implemented

### **Quality Assurance:**
- [ ] Run appropriate test suites
- [ ] Verify technical accuracy against specifications
- [ ] Ensure consistency with existing codebase
- [ ] Test all code changes thoroughly
- [ ] Validate that changes meet acceptance criteria
- [ ] Test authentication and authorization flows

---

## 🔍 Best Practices for AI Agents

### **Documentation Generation:**
- Use provided templates and structures consistently
- Maintain consistent formatting and style
- Ensure all required sections are included
- Verify all technical information is accurate and current

### **Code Development:**
- Write clear, understandable code with comprehensive comments
- Include practical examples in documentation
- Link to related documentation and resources
- Verify procedures and examples work correctly

### **Quality Standards:**
- Review content for completeness and accuracy
- Test all procedures and examples before finalizing
- Ensure consistency with existing documentation
- Update related documentation when system changes occur

### **Learning-Focused Development:**
- Structure code to help understanding
- Explain design decisions and trade-offs
- Provide context for technical choices
- Use progressive complexity (simple first, advanced later)
- Include debugging support and helpful error messages

---

## ⚡ Quick Reference

### **Essential Files:**
- `backend/main.py` - FastAPI application entry point
- `vue-frontend/src/main.js` - Vue.js application entry point
- `config/*.yaml` - Configuration files (4 essential files)
- `docker-compose.yml` - Container orchestration
- `docs/` - **Authoritative project specifications**

### **Key Requirements:**
- **Performance**: <15 seconds for LLM evaluation responses
- **Scalability**: Support 100+ concurrent users with SQLite WAL mode
- **Simplicity**: Maximum simplicity, no duplicate functions
- **Documentation**: Comprehensive comments required
- **Security**: All application functions require user authentication with role-based access control
- **Authentication**: Session-based authentication with comprehensive security measures

### **Development Workflow:**
1. **Read the Specs**: Start with `docs/01_Project_Overview.md`
2. **Understand Requirements**: Review relevant specification documents
3. **Plan Implementation**: Study architecture and data model
4. **Implement**: Follow coding standards and patterns
5. **Test**: Run appropriate test suites
6. **Validate**: Ensure compliance with specifications

### **Critical Frontend Notes:**
- **Vue.js 3**: Use Composition API and TypeScript
- **Tailwind CSS**: Use v3.4.17 (stable) only
- **Authentication**: Implement proper session management
- **Router Guards**: Use global auth store for route protection
- **Component Structure**: Follow established hierarchy patterns

---

## 🚨 FINAL REMINDER

**DO NOT EDIT ANY FILES IN THE `docs/` DIRECTORY UNLESS EXPLICITLY REQUESTED BY THE USER**

This rule is critical to maintain the integrity of the project specifications. The `docs/` directory contains the authoritative documentation that guides all development work.

**Remember**: This project is about learning and collaboration. Every line of code should be educational, maintainable, and extensible.

---

**Document ID**: AGENTS.md (Project Root)
**Version**: 3.0
**Last Updated**: Phase 9 - Documentation Update
**Status**: Active