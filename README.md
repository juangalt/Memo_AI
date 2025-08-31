# Memo AI Coach

An instructional text evaluation system that provides AI-generated feedback for business memos

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com/)

## 📋 Overview

Memo AI Coach is an **instructional text evaluation system** designed to help writers improve their business memo writing skills through AI-powered feedback and structured evaluation.

### Key Features
- **🎯 Intelligent Evaluation**: AI-powered analysis using Claude LLM
- **📊 Rubric-Based Scoring**: Structured evaluation with customizable criteria
- **🔍 Segment-Level Feedback**: Detailed feedback on specific text segments
- **⚙️ Admin Management**: Comprehensive configuration management
- **🔐 Secure Authentication**: Session-based authentication with admin controls
- **📈 Performance Optimized**: <15 second response times, supports 100+ concurrent users

### Core Capabilities
- **Text Submission**: Submit business memos for evaluation
- **AI Feedback**: Receive comprehensive AI-generated feedback
- **Scoring System**: Structured evaluation using detailed rubrics
- **Segment Analysis**: Get specific feedback on individual text segments
- **Strengths & Opportunities**: Identify areas of excellence and improvement
- **Admin Configuration**: Full YAML-based configuration management

## 🏗️ System Architecture

### Technology Stack
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Python, FastAPI | REST API, LLM integration, business logic |
| **Frontend** | Python, Streamlit | User interface, tabbed navigation |
| **Database** | SQLite with WAL mode | Data persistence, supports 100+ concurrent users |
| **LLM** | Anthropic Claude API | AI-powered text evaluation and feedback |
| **Deployment** | Docker, Docker Compose, Traefik | Containerization, orchestration, reverse proxy |
| **Configuration** | YAML files | Runtime behavior control |

### Component Overview
- **Frontend (`frontend/app.py`)**: Streamlit application with tabbed interface
- **Backend (`backend/main.py`)**: FastAPI service exposing REST endpoints
- **Database (`backend/models/database.py`)**: SQLite with WAL mode for high concurrency
- **LLM Service (`backend/services/llm_service.py`)**: Claude API integration
- **Configuration Service**: YAML-based configuration management
- **Authentication Service**: Admin login and session validation

### Data Flow
1. **User Submission** → Text submitted via Streamlit UI
2. **API Request** → Frontend calls backend `/api/v1/evaluations/submit`
3. **Configuration Load** → Backend loads YAML configs (rubric, prompt, LLM, auth)
4. **LLM Processing** → Sends prompt to Claude API with <15s timeout
5. **Response Parsing** → Parses and validates LLM response
6. **Data Persistence** → Stores evaluation results in SQLite database
7. **Frontend Display** → Returns evaluation to user for display

### Deployment Topology
```
Client → Traefik (SSL/TLS) → Backend (FastAPI) → SQLite
                              ↘
                               LLM Service (Claude API)
Frontend (Streamlit) ← Traefik
```

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose**: Container runtime and orchestration
- **LLM API Key**: Anthropic Claude API key (or set `LLM_API_KEY=unset` for mock mode)
- **Domain Name**: For production deployment with SSL

### 🚨 Critical: Tailwind CSS Configuration
**⚠️ IMPORTANT**: If you're working with the Vue.js frontend, use Tailwind CSS v3.4.17 (stable) for production. Avoid v4.x (beta) versions which cause build failures.

✅ **Correct Configuration**:
```json
// package.json
{
  "dependencies": {
    "tailwindcss": "^3.4.17"
  }
}
```
```javascript
// postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

❌ **Wrong Configuration** (causes build failures):
```json
// package.json - WRONG
{
  "dependencies": {
    "tailwindcss": "^4.1.12"  // Beta version
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4.1.12"  // Wrong plugin
  }
}
```

**CSS File Size Indicators**:
- ✅ **Correct**: 25-30 kB (Tailwind processing)
- ❌ **Wrong**: 4-5 kB (Tailwind not processing)

### Installation

1. **Clone and enter the repository**:
   ```bash
   git clone <repository-url>
   cd memo_AI
   ```

2. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your values
   ```

3. **Required environment variables**:
   ```bash
   # Essential
   DOMAIN=your-domain.com
   LLM_API_KEY=your-claude-api-key  # or 'unset' for mock mode
   SECRET_KEY=your-random-secret-key
   ADMIN_PASSWORD=your-admin-password

   # Optional
   MAX_CONCURRENT_USERS=100
   SESSION_TIMEOUT=3600
   ```

4. **Deploy the application**:
   ```bash
   docker compose up -d --build
   ```

5. **Access the application**:
   - **Frontend**: `https://your-domain.com`
   - **Backend API**: `https://your-domain.com/api/docs`
   - **Admin Panel**: `https://your-domain.com/admin`

## ⚙️ Configuration

The system uses **4 essential YAML configuration files** for complete runtime behavior control:

### Core Configuration Files
- **`config/rubric.yaml`**: Evaluation rubric, criteria, weights, and scoring guidance
- **`config/prompt.yaml`**: LLM prompt templates, system messages, and user instructions
- **`config/llm.yaml`**: Claude API configuration, timeouts, retries, and performance limits
- **`config/auth.yaml`**: Authentication, session management, and security settings

### Configuration Features
- **Runtime Editing**: Admin interface for live configuration updates
- **Atomic Changes**: Backup creation before modifications
- **Validation**: `python3 backend/validate_config.py` ensures configuration integrity
- **Environment Override**: Environment variables can override YAML settings

### Admin Access
- **Username**: `admin`
- **Password**: Set via `ADMIN_PASSWORD` environment variable
- **Access**: Navigate to `/admin` for configuration management
- **Session Tokens**: Admin operations require `X-Session-Token` header

## 🎯 Core Features

### Text Evaluation System
- **📝 Text Submission**: Submit business memos for comprehensive evaluation
- **🧠 AI Analysis**: Claude LLM provides intelligent, context-aware feedback
- **📊 Structured Scoring**: Rubric-based evaluation with weighted criteria
- **🔍 Segment-Level Feedback**: Detailed analysis of specific text segments
- **💪 Strengths & Opportunities**: Clear identification of excellence and improvement areas
- **⚡ Fast Response**: Guaranteed <15 second evaluation response times

### Administration & Management
- **⚙️ Configuration Management**: Live editing of YAML configuration files
- **🔐 Admin Authentication**: Secure admin panel with session-based access
- **📋 System Monitoring**: Health checks, performance metrics, and logs
- **🔄 Runtime Updates**: Configuration changes without service restarts
- **💾 Automatic Backups**: Timestamped backups before configuration changes

### Security & Performance
- **🔒 Session-Based Security**: Secure user sessions with configurable timeouts
- **🚀 High Performance**: SQLite WAL mode supports 100+ concurrent users
- **🛡️ Rate Limiting**: Protection against abuse and excessive API usage
- **🔐 CSRF Protection**: Cross-site request forgery prevention
- **🔒 Input Validation**: Comprehensive input sanitization and validation

## 📁 Project Structure

```
memo_AI/
├── backend/                 # FastAPI backend services
│   ├── main.py             # FastAPI application entry point
│   ├── models/             # Database models and entities
│   ├── services/           # Business logic services
│   ├── Dockerfile          # Backend container definition
│   ├── requirements.txt    # Python dependencies
│   └── validate_config.py  # Configuration validation
├── frontend/                # Streamlit frontend application
│   ├── app.py              # Streamlit application entry point
│   ├── components/         # UI components and utilities
│   ├── Dockerfile          # Frontend container definition
│   └── requirements.txt    # Python dependencies
├── config/                  # YAML configuration files
│   ├── rubric.yaml         # Evaluation rubric and criteria
│   ├── prompt.yaml         # LLM prompt templates
│   ├── llm.yaml           # LLM provider configuration
│   ├── auth.yaml           # Authentication settings
│   └── backups/            # Configuration backups
├── data/                    # SQLite database and persistent data
├── tests/                   # Comprehensive test suite
│   ├── config/             # Configuration tests
│   ├── integration/        # System integration tests
│   ├── performance/        # Performance and load tests
│   ├── run_quick_tests.py  # Quick test runner
│   ├── run_production_tests.py # Full production test suite
│   └── README.md           # Testing documentation
├── docs/                    # 📚 Authoritative project documentation
│   ├── 01_Project_Overview.md      # Project goals and overview
│   ├── 02_Architecture_Documentation.md # System architecture
│   ├── 03_Installation_Guide.md    # Installation procedures
│   ├── 04_Configuration_Guide.md   # Configuration management
│   ├── 05_API_Documentation.md     # Complete API reference
│   ├── 06_User_Guide.md           # End-user documentation
│   ├── 07_Administration_Guide.md  # System administration
│   ├── 08_Development_Guide.md     # Development standards
│   ├── 09_Testing_Guide.md         # Testing procedures
│   ├── 10_Deployment_Guide.md      # Production deployment
│   ├── 11_Maintenance_Guide.md     # System maintenance
│   ├── 12_Troubleshooting_Guide.md # Problem resolution
│   ├── 13_Reference_Manual.md      # Technical reference
│   └── AGENTS.md                   # AI agent guidelines
├── deprecated/              # Legacy documentation (devspecs/)
│   └── devspecs/           # Original development specifications
├── devlog/                  # Development changelog and history
├── logs/                    # Application logs and test results
├── letsencrypt/             # SSL certificates (auto-managed)
├── secrets/                 # Secret files and certificates
├── AGENTS.md               # 🤖 AI Agent Guidelines (Project Root)
├── docker-compose.yml      # Container orchestration and deployment
├── env.example             # Environment variables template
└── README.md              # This file
```

### Development Setup

#### Prerequisites for Development
- **Python 3.9+**: Backend and frontend development
- **Docker & Docker Compose**: Container development environment
- **Git**: Version control and collaboration

#### Local Development Environment

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd memo_AI
   cp env.example .env
   # Edit .env with development settings
   ```

2. **Development configuration**:
   ```bash
   # For local development
   LLM_API_KEY=unset  # Use mock mode for development
   DEBUG_MODE=true
   ```

3. **Start development environment**:
   ```bash
   docker compose up -d --build
   ```

4. **Access development URLs**:
   - **Frontend**: `http://localhost:8501`
   - **Backend API**: `http://localhost:8000/docs`
   - **Traefik Dashboard**: `http://localhost:8080`

#### Code Quality Standards
- **PEP 8**: Python style guide compliance
- **Single Responsibility**: Each module serves one purpose
- **Comprehensive Documentation**: Every function has docstrings
- **Simple Patterns**: Favor readability over complex abstractions
- **Error Handling**: Educational error messages for debugging

### 🤖 AI Agent Guidelines

**⚠️ CRITICAL**: All AI agents working on this project **MUST** read the following **BEFORE** starting any work:

1. **`AGENTS.md`** (Project Root) - **MANDATORY FIRST READ**
2. **`docs/01_Project_Overview.md`** - Project goals and requirements
3. **`docs/02_Architecture_Documentation.md`** - System architecture
4. **`docs/08_Development_Guide.md`** - Development standards
5. **`docs/04_Configuration_Guide.md`** - Configuration management

**🚫 CRITICAL RULE**: AI agents **MUST NOT** modify any files in the `docs/` directory unless explicitly requested by the user. The `docs/` directory contains the authoritative project specifications.

## 🚀 Deployment

### Production Deployment

#### Production Prerequisites
- **Domain Name**: Configured DNS pointing to your server
- **SSL Certificate**: Let's Encrypt (auto-managed by Traefik)
- **Production Environment**: Properly configured `.env` file

#### Deployment Steps

1. **Configure production environment**:
   ```bash
   cp env.example .env
   # Edit .env with production values
   ```

2. **Required production settings**:
   ```bash
   APP_ENV=production
   DEBUG_MODE=false
   DOMAIN=your-production-domain.com
   LLM_API_KEY=your-actual-claude-api-key
   SECRET_KEY=your-secure-random-key
   ADMIN_PASSWORD=your-secure-admin-password
   ```

3. **Deploy to production**:
   ```bash
   docker compose up -d --build
   ```

4. **Verify deployment**:
   - **Application**: `https://your-domain.com`
   - **API Docs**: `https://your-domain.com/api/docs`
   - **Health Check**: `https://your-domain.com/health`

#### Automated Deployment
Use Docker Compose for production deployment:
```bash
docker compose up -d --build
```

### Scaling and Performance

#### Horizontal Scaling
Scale backend services for higher load:
```bash
docker compose up -d --scale backend=3
```

#### Performance Optimization
- **SQLite WAL Mode**: Supports 100+ concurrent users
- **Response Time**: <15 seconds guaranteed for LLM evaluations
- **Caching**: Configuration cached in memory
- **Rate Limiting**: Configurable via Traefik and application settings

## 🧪 Testing

### Test Categories
The project includes a comprehensive testing suite with **4 main categories**:

#### Configuration Tests (`tests/config/`)
- **Environment validation**: Domain, SSL, database connectivity
- **Configuration file validation**: YAML syntax and required fields
- **API key validation**: LLM service and external service connectivity

#### Integration Tests (`tests/integration/`)
- **System integration**: Container status, API health, session management
- **Critical workflow**: Complete evaluation workflow end-to-end
- **Production readiness**: System accessibility, security, functionality

#### Performance Tests (`tests/performance/`)
- **Response time benchmarks**: <15 second requirement validation
- **Concurrent user simulation**: 100+ user load testing
- **Resource utilization**: Memory, CPU, and database performance

#### Security Tests (`tests/test_security_dev.py`)
- **Authentication validation**: Session management and admin access
- **Input validation**: Sanitization and injection prevention
- **Rate limiting**: Abuse prevention and DoS protection

### Running Tests

#### Quick Test Suite
Runs all non-performance tests for rapid validation:
```bash
python3 tests/run_quick_tests.py
```

#### Full Production Test Suite
Includes performance tests and comprehensive validation:
```bash
python3 tests/run_production_tests.py
```

#### Individual Test Execution
Run specific test modules directly:
```bash
python3 tests/config/test_environment.py
python3 tests/integration/test_critical_system_local.py
python3 tests/performance/test_load.py
```

### Test Results and Reporting
- **Results Location**: `logs/` and `tests/logs/` directories
- **Quick Test Results**: `logs/quick_production_test_results.json`
- **Full Test Results**: `logs/production_test_suite_results.json`
- **Format**: JSON reports with detailed assertion outcomes and metrics
- **Coverage**: Environment, integration, performance, security, and production readiness
- **Historical Data**: Test results retained for trend analysis and debugging

## 📊 Monitoring & Observability

### Health Check Endpoints
- **`GET /health`** - Aggregate system health status
- **`GET /health/database`** - Database connectivity and WAL mode validation
- **`GET /health/config`** - Configuration file validation and syntax checking
- **`GET /health/llm`** - Claude API service availability and response times
- **`GET /health/auth`** - Authentication service status and session validation

### Application Logs
- **Location**: `logs/` directory with automatic rotation
- **Types**: Application, error, debug, and access logs
- **Format**: Structured JSON for programmatic analysis and monitoring
- **Retention**: Configurable log retention with archival

### Performance Metrics
- **Response Times**: End-to-end LLM evaluation latency (<15s guaranteed)
- **Throughput**: Requests per second and concurrent user capacity
- **Resource Usage**: CPU, memory, and database performance metrics
- **Error Rates**: System availability and reliability tracking
- **API Usage**: Claude LLM token consumption and cost monitoring

### Traefik Dashboard
Access the reverse proxy dashboard for real-time monitoring:
- **Development**: `http://localhost:8080`
- **Production**: `https://traefik.your-domain.com` (if configured)
- **Metrics**: Request routing, SSL certificates, service health, and performance

### System Monitoring Scripts
- **Health validation**: `python3 backend/validate_config.py`
- **Log analysis**: Structured logging with correlation IDs
- **Performance testing**: Built-in load testing capabilities

## 🔒 Security

### Authentication & Authorization
- **Session-Based**: Secure user sessions with configurable timeouts
- **Admin Access**: Dedicated admin authentication with role-based permissions
- **Token Security**: Cryptographically secure session tokens with expiration
- **Rate Limiting**: Configurable abuse prevention and DoS protection

### Data Protection
- **No PII Collection**: System designed without personal information storage
- **Session Isolation**: User data isolation through session-based access
- **Configuration Security**: Encrypted configuration file handling
- **Input Validation**: Comprehensive sanitization and injection prevention

### Network Security
- **HTTPS Encryption**: End-to-end SSL/TLS with Let's Encrypt certificates
- **CSRF Protection**: Cross-site request forgery prevention
- **Secure Headers**: Security headers and content type validation
- **Container Security**: Non-root user execution and minimal attack surface

## 📚 Documentation System

### 📖 Complete Documentation Suite
The project maintains a comprehensive documentation system in the `docs/` directory:

#### **Core Documentation Files**
| Document | Purpose | Critical Reading |
|----------|---------|------------------|
| **`docs/01_Project_Overview.md`** | Project goals, features, technology stack | **MANDATORY** |
| **`docs/02_Architecture_Documentation.md`** | System architecture and data flow | **MANDATORY** |
| **`docs/04_Configuration_Guide.md`** | YAML configuration management | **MANDATORY** |
| **`docs/05_API_Documentation.md`** | Complete API reference and endpoints | **MANDATORY** |
| **`docs/08_Development_Guide.md`** | Development standards and procedures | **MANDATORY** |
| **`docs/09_Testing_Guide.md`** | Testing procedures and frameworks | **MANDATORY** |
| **`docs/14_Tailwind_CSS_Troubleshooting.md`** | Vue frontend Tailwind CSS issues | **FOR VUE DEVELOPERS** |

#### **Specialized Documentation**
- **`docs/03_Installation_Guide.md`** - Installation and setup procedures
- **`docs/06_User_Guide.md`** - End-user documentation
- **`docs/07_Administration_Guide.md`** - System administration
- **`docs/10_Deployment_Guide.md`** - Production deployment
- **`docs/11_Maintenance_Guide.md`** - System maintenance
- **`docs/12_Troubleshooting_Guide.md`** - Problem resolution
- **`docs/13_Reference_Manual.md`** - Technical reference
- **`docs/14_Tailwind_CSS_Troubleshooting.md`** - Vue frontend Tailwind CSS issues
- **`docs/AGENTS.md`** - AI agent guidelines and quality standards

### 🤖 AI Agent Guidelines (CRITICAL)

**⚠️ ALL AI agents working on this project MUST:**

1. **Read `AGENTS.md` FIRST** - Located in project root, contains mandatory guidelines
2. **Read `docs/AGENTS.md`** - Documentation guidelines and quality standards
3. **Study the complete `docs/` directory** - Authoritative project specifications (14 files)
4. **Follow established patterns** - Coding standards, API design, configuration management
5. **Maintain documentation integrity** - NEVER modify `docs/` files unless explicitly requested

#### **🚫 CRITICAL RULE**
AI agents **MUST NOT** modify any files in the `docs/` directory. This directory contains the authoritative project specifications that guide all development work.

### 📋 Development Workflow

1. **Read Specifications** - Start with `AGENTS.md` and relevant `docs/` files
2. **Understand Requirements** - Review project overview and architecture
3. **Follow Standards** - Adhere to development guide and coding principles
4. **Implement Changes** - Use established patterns and comprehensive documentation
5. **Test Thoroughly** - Run appropriate test suites before completion
6. **Validate Compliance** - Ensure implementation meets documented requirements

## 🆘 Troubleshooting

### Common Issues

#### 🎨 Tailwind CSS Issues (Vue Frontend)
**Symptoms**:
- Components display without styling
- CSS file size < 10 kB
- Build succeeds but styles don't work
- Console shows PostCSS plugin errors

**Solution**:
1. **Check package.json**: Ensure `tailwindcss: "^3.4.17"` (not v4.x)
2. **Verify postcss.config.js**: Use `tailwindcss: {}` (not `@tailwindcss/postcss`)
3. **Remove beta dependencies**: Delete any `@tailwindcss/postcss` packages
4. **Rebuild**: Use `npm install` (not `npm ci`) for better dependency management
5. **Check CSS file size**: Should be 25-30 kB if Tailwind is processing correctly

**Quick Fix**:
```bash
# Option 1: Use the automated fix script
./fix_tailwind_css.sh

# Option 2: Manual fix
npm uninstall @tailwindcss/postcss
npm install tailwindcss@^3.4.17
npm run build
```

#### Configuration Problems
- **Validate config**: `python3 backend/validate_config.py`
- **Check YAML syntax**: Ensure proper indentation and required fields
- **Review logs**: Check `logs/config.log` for validation errors

#### Database Issues
- **Health check**: `GET /health/database`
- **Permissions**: Ensure container user has database access
- **WAL mode**: Verify `PRAGMA journal_mode = WAL` is set

#### LLM Service Problems
- **API key**: Verify `LLM_API_KEY` is set and valid
- **Mock mode**: Set `LLM_API_KEY=unset` for development
- **Rate limits**: Check Claude API usage and limits

#### Container Issues
- **Logs**: `docker compose logs [service-name]`
- **Health**: `docker compose ps` to check container status
- **Restart**: `docker compose restart [service-name]`

### Support Resources
- **API Documentation**: `https://your-domain.com/api/docs`
- **Logs Directory**: `logs/` for application and error logs
- **Test Results**: `tests/logs/` for test execution reports
- **Configuration Backups**: `config/backups/` for recovery

## 📄 License

This project is developed for educational and demonstration purposes. Please refer to the specific license terms if applicable.

## 🤝 Contributing

### For Human Developers
1. **Read the Documentation**: Start with `AGENTS.md` and the complete `docs/` directory
2. **Follow Standards**: Adhere to the development guide and coding principles
3. **Test Changes**: Run appropriate test suites before submitting
4. **Document Updates**: Update relevant documentation for any system changes

### For AI Agents
**⚠️ CRITICAL**: AI agents must follow the guidelines in `AGENTS.md` and **NEVER** modify files in the `docs/` directory unless explicitly requested.

### Development Process
1. Fork the repository
2. Create a feature branch
3. Implement changes following project standards
4. Add comprehensive tests
5. Submit a pull request with detailed description

### Code Standards
- **PEP 8** compliance for Python code
- **Comprehensive documentation** for all functions and classes
- **Single responsibility principle** for modules and functions
- **Simple, readable patterns** over complex abstractions
- **Educational error messages** for debugging and learning

---

## 🎯 Project Status

### Current Phase: **Phase 9 - Production Ready & Fully Documented**
- ✅ **Complete system implementation** (Phases 1-8 merged from master-codex1)
- ✅ **Comprehensive documentation suite** - 14 files in `docs/` directory
- ✅ **Production deployment scripts** and configuration
- ✅ **Full testing infrastructure** with performance validation
- ✅ **Docker containerization** with orchestration and SSL/TLS
- ✅ **Security hardening** with session-based authentication
- ✅ **Legacy documentation** preserved in `deprecated/` directory

### Key Achievements
- **FastAPI backend** with comprehensive REST API
- **Streamlit frontend** with tabbed user interface
- **SQLite database** optimized for 100+ concurrent users
- **Claude LLM integration** with <15 second response times
- **YAML-based configuration** for complete runtime control
- **Automated testing** with production validation
- **Production deployment** with SSL/TLS and monitoring

### Quality Standards
- **Performance**: Guaranteed <15 second LLM evaluation responses
- **Scalability**: Supports 100+ concurrent users via SQLite WAL mode
- **Security**: Session-based authentication with admin controls
- **Documentation**: Comprehensive specifications in `docs/` directory
- **Testing**: Full test coverage with production validation
- **Simplicity**: Maximum simplicity for novice developers while remaining extensible

---

## 📞 Contact & Support

### Resources
- **📚 Documentation**: Complete specifications in `docs/` directory (14 comprehensive guides)
- **🔧 API Reference**: Interactive API documentation at `/api/docs`
- **📊 Health Checks**: System status at `/health` endpoints (5 health check types)
- **📝 Logs**: Application logs in `logs/` directory with structured JSON format
- **🧪 Test Results**: Validation reports in `logs/` and `tests/logs/` directories
- **⚙️ Configuration**: Live configuration editing at `/admin` (admin access required)

### Getting Help
1. **Check Documentation**: Review relevant `docs/` files first
2. **Run Diagnostics**: Use health check endpoints for system status
3. **Review Logs**: Check `logs/` directory for error details
4. **Validate Configuration**: Run `python3 backend/validate_config.py`

---

**🎓 Remember**: This project is designed for learning and collaboration. Every line of code should be educational, maintainable, and extensible.

**📖 For AI agents**: Always start by reading `AGENTS.md` (project root) and `docs/AGENTS.md`, then study the complete `docs/` directory (14 files) before beginning any work on this project.

**🚫 CRITICAL**: AI agents **MUST NOT** modify any files in the `docs/` directory. This contains the authoritative project specifications.
