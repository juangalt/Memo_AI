# AI Agent Guidelines
## Memo AI Coach Project

**Version**: 2.0
**Last Updated**: Implementation Phase
**Purpose**: Comprehensive guidance for AI agents working on the Memo AI Coach project

---

## 🚨 CRITICAL: Project Specifications

### **MANDATORY: Read All Documentation in `docs/` Directory**

**BEFORE STARTING ANY WORK**, AI agents **MUST** read and understand the complete project specifications:

#### **📋 Required Reading Order:**
1. **`docs/01_Project_Overview.md`** - Project goals, technology stack, and requirements
2. **`docs/02_Architecture_Documentation.md`** - System architecture and component relationships
3. **`docs/04_Configuration_Guide.md`** - Configuration management and YAML files
4. **`docs/05_API_Documentation.md`** - Complete API reference and endpoints
5. **`docs/08_Development_Guide.md`** - Development procedures and coding standards
6. **`docs/09_Testing_Guide.md`** - Testing procedures and frameworks
7. **`docs/AGENTS.md`** (in docs/) - Documentation guidelines and quality standards

#### **📚 Additional Reference Documents:**
- `docs/03_Installation_Guide.md` - Installation and setup procedures
- `docs/06_User_Guide.md` - End-user documentation
- `docs/07_Administration_Guide.md` - System administration
- `docs/10_Deployment_Guide.md` - Production deployment
- `docs/11_Maintenance_Guide.md` - System maintenance
- `docs/12_Troubleshooting_Guide.md` - Problem resolution
- `docs/13_Reference_Manual.md` - Technical reference

### **🚫 CRITICAL RULE: DO NOT EDIT `docs/` DIRECTORY**
- **NEVER** modify, update, or edit any files in the `docs/` directory
- **NEVER** add, remove, or change content in documentation files
- The `docs/` directory contains the **authoritative project specifications**
- Only modify `docs/` files when the **user explicitly requests** it
- All other directories (backend/, frontend/, config/, etc.) can be modified as needed

---

## 🎯 Project Overview Summary

### **What is Memo AI Coach?**
Memo AI Coach is an **instructional text evaluation system** that provides AI-generated feedback for business memos. The application helps writers improve by:

- Evaluating text against a detailed rubric
- Returning strengths, opportunities, and rubric scores
- Providing segment-level suggestions
- Maintaining simplicity for novice developers while remaining extensible

### **Key Features:**
- **FastAPI backend** with RESTful API
- **Streamlit frontend** with tabbed interface
- **SQLite database** with WAL mode for 100+ concurrent users
- **YAML-based configuration** for rubric, prompts, LLM, and authentication
- **Claude LLM integration** with mock mode for development
- **Admin authentication** and configuration editor
- **Comprehensive testing** and deployment scripts

### **Technology Stack:**
| Component | Technology |
|-----------|------------|
| Backend | Python, FastAPI |
| Frontend | Python, Streamlit |
| Database | SQLite with WAL mode |
| LLM | Anthropic Claude API |
| Deployment | Docker, docker-compose, Traefik |
| Configuration | YAML files |

### **Performance Requirements:**
- **<15 seconds** for LLM evaluation responses
- **<1 second** for UI loads
- **100+ concurrent users** support via SQLite WAL mode

---

## 🏗️ System Architecture Summary

### **Component Overview:**
- **Frontend**: Streamlit application (`frontend/app.py`) with tabbed interface
- **Backend**: FastAPI service (`backend/main.py`) exposing REST endpoints
- **Database**: SQLite accessed through `backend/models/database.py` with WAL mode
- **LLM Service**: `backend/services/llm_service.py` for Claude API interaction
- **Configuration Service**: `backend/services/config_service.py` and `config_manager.py`
- **Authentication Service**: `backend/services/auth_service.py` for admin login

### **Data Flow:**
1. User submits text via Streamlit UI
2. Frontend calls backend evaluation endpoint (`/api/v1/evaluations/submit`)
3. Backend loads YAML configs and sends prompt to Claude API
4. LLM response is parsed and stored in SQLite database
5. Backend returns evaluation to frontend for display

### **Data Model:**
| Table | Purpose | Key Fields |
|-------|---------|------------|
| `users` | Future extension | `id`, `email`, `created_at` |
| `sessions` | Active evaluation sessions | `id`, `created_at`, `updated_at` |
| `submissions` | Original memo text | `id`, `session_id`, `content` |
| `evaluations` | LLM feedback | `id`, `submission_id`, `overall`, `strengths`, `opportunities`, `rubric_scores`, `segments` |

### **Security Architecture:**
- Admin operations require session tokens via `X-Session-Token` header
- Rate limiting and brute force protection
- Configuration files mounted read-only in containers
- HTTPS termination handled by Traefik

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

### **Session Management:**
- `POST /api/v1/sessions/create` - Generate anonymous session
- `GET /api/v1/sessions/{session_id}` - Retrieve session details
- `DELETE /api/v1/sessions/{session_id}` - End session

### **Evaluation Endpoints:**
- `POST /api/v1/evaluations/submit` - Submit text for evaluation
- `GET /api/v1/evaluations/{evaluation_id}` - Retrieve evaluation result
- `GET /api/v1/evaluations/session/{session_id}` - List evaluations for session

### **Admin Endpoints:**
- `POST /api/v1/admin/login` - Admin login
- `POST /api/v1/admin/logout` - Logout
- `GET /api/v1/admin/config/{config_name}` - Read configuration
- `PUT /api/v1/admin/config/{config_name}` - Update configuration

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
- Session creation is anonymous
- Admin endpoints require `X-Session-Token` header
- Tokens expire according to `auth.yaml` configuration

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
backend/     # FastAPI service
frontend/    # Streamlit interface
config/      # YAML configuration files
tests/       # Test suites
docs/        # Comprehensive project documentation
```

### **Backend Development:**
- Entry point: `backend/main.py`
- Data models in `backend/models/entities.py`
- Services in `backend/services/` (config, auth, LLM)
- Error responses use standard `{data: null, meta, errors}` schema
- Add new endpoints by extending `backend/main.py`

### **Frontend Development:**
- Entry point: `frontend/app.py`
- `components/api_client.py` wraps REST calls with retry logic
- `components/state_manager.py` manages Streamlit session state
- Follow existing tab structure for new UI features
- Components added under `frontend/components/` with clear functions

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

## 📋 Implementation Checklist

### **Before Starting Any Work:**
- [ ] **MANDATORY**: Read all relevant `docs/` files completely
- [ ] Understand the specific requirement being implemented
- [ ] Review related architecture components
- [ ] Check data model requirements
- [ ] Verify API specifications
- [ ] Consider UI/UX implications
- [ ] Review testing requirements

### **During Implementation:**
- [ ] Follow coding principles (simplicity, readability, single responsibility)
- [ ] Add comprehensive docstrings and inline comments
- [ ] Use established patterns and naming conventions
- [ ] Include error handling with educational messages
- [ ] Ensure backward compatibility
- [ ] Test all procedures and examples
- [ ] Validate against documented acceptance criteria

### **Code Quality Standards:**
- [ ] Code is self-documenting and easy to understand
- [ ] All functions have clear docstrings
- [ ] Error messages are helpful and educational
- [ ] Code follows established patterns
- [ ] No complex abstractions unless absolutely necessary
- [ ] Maintains consistency with existing codebase

### **Quality Assurance:**
- [ ] Run appropriate test suites
- [ ] Verify technical accuracy against specifications
- [ ] Ensure consistency with existing codebase
- [ ] Test all code changes thoroughly
- [ ] Validate that changes meet acceptance criteria

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
- `frontend/app.py` - Streamlit application entry point
- `config/*.yaml` - Configuration files (4 essential files)
- `docker-compose.yml` - Container orchestration
- `docs/` - **Authoritative project specifications**

### **Key Requirements:**
- **Performance**: <15 seconds for LLM evaluation responses
- **Scalability**: Support 100+ concurrent users with SQLite WAL mode
- **Simplicity**: Maximum simplicity, no duplicate functions
- **Documentation**: Comprehensive comments required
- **Security**: All admin operations require authentication

### **Development Workflow:**
1. **Read the Specs**: Start with `docs/01_Project_Overview.md`
2. **Understand Requirements**: Review relevant specification documents
3. **Plan Implementation**: Study architecture and data model
4. **Implement**: Follow coding standards and patterns
5. **Test**: Run appropriate test suites
6. **Validate**: Ensure compliance with specifications

---

## 🚨 FINAL REMINDER

**DO NOT EDIT ANY FILES IN THE `docs/` DIRECTORY UNLESS EXPLICITLY REQUESTED BY THE USER**

This rule is critical to maintain the integrity of the project specifications. The `docs/` directory contains the authoritative documentation that guides all development work.

**Remember**: This project is about learning and collaboration. Every line of code should be educational, maintainable, and extensible.

---

**Document ID**: AGENTS.md (Project Root)
**Version**: 2.0
**Last Updated**: Implementation Phase
**Status**: Active