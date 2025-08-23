# Development Roadmap
## Memo AI Coach

**Document ID**: 09_Dev_Roadmap.md  
**Document Version**: 1.0  
**Last Updated**: Implementation Phase  
**Next Review**: After each phase completion  
**Status**: Ready for Implementation

---

## 1.0 Document Information

### 1.1 Purpose
Provides a comprehensive, phase-based development roadmap for implementing the Memo AI Coach project, specifically designed for novice human developers working with AI coding agents. Each phase includes explicit milestones, detailed development steps, testing procedures, and documentation requirements.

### 1.2 Scope
- Complete project implementation from setup to deployment
- Phase-based approach with testable milestones
- Detailed step-by-step instructions for each development task
- Testing and validation procedures for each step
- Documentation and error tracking requirements
- Design decision capture and devspec inconsistency identification

### 1.3 Target Audience
**Primary**: Novice human developer + AI coding agent collaboration
- Human developer provides requirements understanding, testing, validation
- AI coding agent provides code generation, implementation assistance
- Collaborative approach to learning and problem-solving

### 1.4 Implementation Approach
**Based on 00_ProjectOverview.md Section 6.2**:
- **Maximum Simplicity**: Straightforward implementations, no complex patterns
- **Comprehensive Documentation**: Extensive comments and explanations
- **Modular Design**: Clear separation of concerns, single responsibility
- **Extensibility**: Design for future enhancements
- **Learning Focus**: Code structure helps novice programmer understand

---

## 2.0 Development Approach and Principles

### 2.1 Human-AI Collaboration Model
**Roles and Responsibilities**:
- **Human Developer**: Requirements analysis, testing execution, design decisions, validation
- **AI Coding Agent**: Code generation, implementation, debugging assistance, documentation
- **Joint Activities**: Planning, design reviews, problem-solving, progress tracking

### 2.2 Progress Tracking Requirements
**For each completed step, document in `/devlog/changelog.md`**:
- **Progress Summary**: What was accomplished
- **Design Decisions**: Technical choices made and rationale
- **Error Fixes**: Issues encountered and resolutions
- **Devspec Inconsistencies**: Any inconsistencies found in foundational documents
- **Code Quality Notes**: Comments on maintainability and clarity
- **Learning Insights**: Key concepts learned during implementation

### 2.3 Testing Strategy
**Every step must include**:
- **Explicit Goal**: Clear objective and success criteria
- **Implementation Instructions**: Step-by-step guidance for AI agent
- **Testing Procedures**: How human developer can verify functionality
- **Debugging Instructions**: Common issues and solutions
- **Browser/Console Validation**: Visible proof that step works

---

## 3.0 Phase Overview

### 3.1 Phase Structure
Each phase follows a consistent structure:
- **Phase Overview**: Goals, duration, key skills developed
- **Milestones**: Testable checkpoints with browser/console verification
- **Development Steps**: Small, focused tasks with explicit instructions
- **Phase Testing**: Comprehensive validation procedures
- **Documentation Requirements**: What must be recorded in changelog

### 3.2 Phase Dependencies
```
Phase 1: Environment Setup & Validation
    ↓
Phase 2: Backend Foundation
    ↓
Phase 3: Frontend Foundation
    ↓
Phase 4: Core Evaluation System
    ↓
Phase 5: Administrative Functions
    ↓
Phase 6: Integration Testing & Polish
    ↓
Phase 7: Production Deployment
```

### 3.3 Milestone Validation Requirements
Each milestone must be **demonstrable to human developer**:
- **Browser Testing**: UI functionality visible and interactive
- **Console Testing**: API endpoints testable via curl/Postman
- **Database Testing**: Data persistence verifiable via SQL queries
- **Configuration Testing**: Settings changeable and effective

---

## 4.0 Phase 1: Environment Setup and Validation

### 4.1 Phase Overview
**Goal**: Establish development environment and validate all required dependencies  
**Duration**: 1-2 days  
**Key Skills**: Environment setup, dependency management, basic validation  
**Success Criteria**: All tools working, project structure created, dependencies validated

### 4.2 Phase 1 Milestones

#### Milestone 1.1: Development Environment Ready
**Human Validation**: All commands run without errors
- Python 3.9+ installed and accessible
- Virtual environment created and activated
- Docker and Docker Compose operational
- Git repository initialized

#### Milestone 1.2: Project Structure Complete
**Human Validation**: Directory structure matches 07_Deployment.md
- All required directories created
- Essential files initialized
- Configuration files in place
- README.md created with setup instructions

#### Milestone 1.3: Database Foundation Working
**Human Validation**: Database operations successful
- SQLite database created with correct schema
- All tables present with proper structure
- WAL mode enabled and verified
- Basic CRUD operations working

#### Milestone 1.4: Configuration System Validated
**Human Validation**: All YAML files load and validate
- All 4 essential YAML files present and valid
- Configuration validation script passes
- Environment variable override system functional
- Startup validation working

### 4.3 Development Steps

#### Step 1.1: Install and Validate Core Dependencies
**Goal**: Ensure all required tools are available and working

**AI Agent Instructions**:
Help the human developer install required dependencies. Provide platform-specific commands and troubleshoot any installation issues.

**Implementation Steps**:
1. **Verify Python Installation**:
   ```bash
   python3 --version  # Should show 3.9 or higher
   pip3 --version     # Should show pip version
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   cd /home/felipe/memoai
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # For Windows: venv\Scripts\activate
   ```

3. **Install Docker**:
   ```bash
   docker --version        # Should show Docker version
   docker compose version  # Should show Compose version
   ```

4. **Test Docker Installation**:
   ```bash
   docker run hello-world  # Should complete successfully
   ```

**Human Testing Procedures**:
- Run each command and verify expected output
- If any command fails, work with AI agent to resolve issues
- Document any platform-specific installation steps needed

**Common Issues & Solutions**:
- **Python not found**: Install from python.org or use package manager
- **Docker not working**: Install Docker Desktop or Docker Engine
- **Permission errors**: Add user to docker group or use sudo
- **Virtual environment issues**: Check Python installation and permissions

---

#### Step 1.2: Create Project Structure
**Goal**: Establish complete directory structure as defined in 07_Deployment.md

**AI Agent Instructions**:
Create the exact directory structure specified in the deployment document. Ensure all paths match the requirements.

**Implementation Steps**:
1. **Create Directory Structure**:
   ```bash
   mkdir -p backend/{services,models,utils}
   mkdir -p frontend/components
   mkdir -p config
   mkdir -p data/backups
   mkdir -p logs
   mkdir -p letsencrypt
   mkdir -p devlog
   ```

2. **Create Essential Files**:
   ```bash
   touch backend/main.py
   touch backend/requirements.txt
   touch backend/Dockerfile
   touch backend/init_db.py
   touch backend/validate_config.py
   touch frontend/app.py
   touch frontend/requirements.txt
   touch frontend/Dockerfile
   touch docker-compose.yml
   touch .env.example
   touch devlog/changelog.md
   ```

3. **Initialize Git Repository**:
   ```bash
   git init
   git add .
   git commit -m "Initial project structure"
   ```

**Human Testing Procedures**:
- Run `find . -type d | sort` and verify all directories exist
- Run `find . -name "*.py" -o -name "*.yml" -o -name "*.yaml" | sort`
- Compare structure with 07_Deployment.md Section 3.1
- Verify git repository initialized with `git status`

**Success Criteria**:
- [ ] All directories from deployment spec created
- [ ] Essential files exist (can be empty for now)
- [ ] Git repository initialized
- [ ] No permission or path errors

---

#### Step 1.3: Initialize Configuration Files
**Goal**: Create all 4 essential YAML configuration files with valid structure

**AI Agent Instructions**:
Create configuration files that match the validation rules in 03_Data_Model.md Section 9.7. Ensure all required fields are present and properly structured.

**Implementation**: (Due to length constraints, I'll provide the structure and note that each configuration file needs to be created with healthcare-focused content as shown in the full specification)

**Configuration Files to Create**:
1. `config/rubric.yaml` - Healthcare communication rubric with 4 criteria (clarity, accuracy, empathy, professionalism)
2. `config/prompt.yaml` - LLM prompt templates with JSON response schemas
3. `config/llm.yaml` - Claude provider configuration with performance settings
4. `config/auth.yaml` - Session management and security settings

**Human Testing Procedures**:
- Verify all 4 files created: `ls config/`
- Test YAML syntax: `python3 -c "import yaml; print('Valid:', yaml.safe_load(open('config/rubric.yaml')))"`
- Repeat for all 4 files
- Check file contents match healthcare focus and required fields

**Success Criteria**:
- [ ] All 4 YAML files created with valid syntax
- [ ] Healthcare-focused content in rubric and prompt files
- [ ] All required fields present per 03_Data_Model.md validation rules
- [ ] No YAML parsing errors

---

#### Step 1.4: Create Database Initialization Script
**Goal**: Implement complete database schema creation based on 03_Data_Model.md

**AI Agent Instructions**:
Create a database initialization script that implements the exact schema from the data model specification. Include all tables, indexes, and SQLite optimizations.

**Key Implementation Requirements**:
- Create all 4 tables: users, sessions, submissions, evaluations
- Implement all performance indexes from Section 8.1
- Enable WAL mode and SQLite optimizations
- Include comprehensive verification and testing

**Human Testing Procedures**:
- Run script: `cd backend && python3 init_db.py`
- Should see success messages for all tables and indexes
- Verify database file: `ls -la ../data/memoai.db`
- Check tables: `sqlite3 ../data/memoai.db ".tables"`
- Verify WAL mode: `sqlite3 ../data/memoai.db "PRAGMA journal_mode"`

**Success Criteria**:
- [ ] Database file created successfully
- [ ] All 4 tables created (users, sessions, submissions, evaluations)
- [ ] All indexes created
- [ ] WAL mode enabled
- [ ] Integrity check passes
- [ ] Write test successful

---

#### Step 1.5: Create Configuration Validation Script
**Goal**: Implement comprehensive YAML validation based on 03_Data_Model.md Section 9.7

**AI Agent Instructions**:
Create a validation script that checks all configuration files against the detailed rules specified in the data model document. Include specific validation for each file type.

**Key Validation Requirements**:
- Validate all 4 YAML files with specific rules
- Check healthcare context in rubric descriptions
- Verify JSON response schemas in prompt templates
- Validate LLM performance settings (<15 seconds)
- Check session management configurations

**Human Testing Procedures**:
- Run validation: `cd backend && python3 validate_config.py`
- Should see "All configuration files are valid"
- Test with broken YAML: temporarily add invalid syntax to a file
- Re-run validation - should show specific errors
- Fix the file and re-run - should pass again

**Success Criteria**:
- [ ] Validation script runs without Python errors
- [ ] All 4 configuration files pass validation
- [ ] Validation reports specific errors for broken files
- [ ] Healthcare-specific validation rules working

---

#### Step 1.6: Create Requirements Files and Basic Setup
**Goal**: Define Python dependencies and create basic project setup

**AI Agent Instructions**:
Create comprehensive requirements files with specific versions and basic project documentation.

**Implementation Requirements**:
- Backend requirements: FastAPI, Anthropic, SQLite, YAML, security packages
- Frontend requirements: Streamlit, requests, data visualization
- README.md with setup instructions
- .env.example with all configuration variables
- Initial devlog/changelog.md structure

**Human Testing Procedures**:
- Install backend deps: `cd backend && pip install -r requirements.txt`
- Install frontend deps: `cd frontend && pip install -r requirements.txt`
- Test imports: `python3 -c "import fastapi, streamlit, anthropic, yaml; print('All imports successful')"`
- Copy environment file: `cp .env.example .env`

**Success Criteria**:
- [ ] All dependencies install without errors
- [ ] All imports work correctly
- [ ] README.md provides clear setup instructions
- [ ] Environment file template created
- [ ] Development log initialized

---

### 4.4 Phase 1 Complete Testing and Validation

#### Master Validation Checklist
**Human Developer: Verify each item before proceeding to Phase 2**

1. **Environment Validation**:
   ```bash
   python3 --version  # Should show 3.9+
   docker --version   # Should show Docker version
   git --version      # Should show Git version
   ```

2. **Project Structure Validation**:
   ```bash
   find . -type d | sort
   ls -la config/
   ls -la backend/
   ls -la frontend/
   ```

3. **Database Validation**:
   ```bash
   cd backend
   python3 init_db.py
   sqlite3 ../data/memoai.db ".tables"
   sqlite3 ../data/memoai.db "PRAGMA journal_mode"
   ```

4. **Configuration Validation**:
   ```bash
   python3 validate_config.py
   # Should show all files valid
   ```

5. **Dependencies Validation**:
   ```bash
   pip install -r requirements.txt
   cd ../frontend
   pip install -r requirements.txt
   python3 -c "import fastapi, streamlit, anthropic, yaml"
   ```

#### Phase 1 Success Criteria
**All items must be checked before proceeding:**

- [ ] Python 3.9+ installed and working
- [ ] Docker and Docker Compose operational
- [ ] Complete project structure created per 07_Deployment.md
- [ ] All 4 YAML configuration files created and validated
- [ ] Database initialized with correct schema and WAL mode
- [ ] All performance indexes created
- [ ] Configuration validation script passes
- [ ] All Python dependencies installed successfully
- [ ] Virtual environment activated and working
- [ ] Basic project documentation in place
- [ ] Development log initialized

---

## 5.0 Phase 2: Backend Foundation

### 5.1 Phase Overview
**Goal**: Implement core backend services and API infrastructure  
**Duration**: 3-4 days  
**Key Skills**: FastAPI development, database operations, service architecture  
**Success Criteria**: API server running, database integration working, configuration loaded

### 5.2 Phase 2 Milestones

#### Milestone 2.1: Basic API Server Running
**Human Validation**: Server responds to requests in browser
- FastAPI server starts without errors on port 8000
- Health endpoint returns JSON response at `/health`
- API documentation accessible at `/docs`
- Server logs show successful startup

#### Milestone 2.2: Database Integration Working
**Human Validation**: API can create and read database records
- Database connection established from API
- Session creation working via API
- Basic CRUD operations functional
- Database health check passing

#### Milestone 2.3: Configuration System Operational
**Human Validation**: API loads and uses configuration files
- All 4 YAML files loaded on startup
- Configuration health check passing
- Environment variable overrides working
- Configuration accessible to API endpoints

---

## 6.0 Phase 3: Frontend Foundation

### 6.1 Phase Overview
**Goal**: Implement basic Streamlit frontend with navigation and API communication  
**Duration**: 2-3 days  
**Key Skills**: Streamlit development, state management, API integration  
**Success Criteria**: Frontend accessible in browser, tab navigation working, API communication established

---

## 7.0 Phase 4: Core Evaluation System

### 7.1 Phase Overview
**Goal**: Implement text evaluation using LLM integration  
**Duration**: 3-4 days  
**Key Skills**: LLM API integration, prompt engineering, response parsing  
**Success Criteria**: Text submission works, LLM evaluations generated, results displayed

---

## 8.0 Phase 5: Administrative Functions

### 8.1 Phase Overview
**Goal**: Implement configuration management and admin features  
**Duration**: 2-3 days  
**Key Skills**: Admin interfaces, configuration editing, validation  
**Success Criteria**: Admin can edit YAML files, changes validated, debug mode working

---

## 9.0 Phase 6: Integration Testing & Polish

### 9.1 Phase Overview
**Goal**: Complete system integration and user experience polish  
**Duration**: 2-3 days  
**Key Skills**: End-to-end testing, performance optimization, UX improvements  
**Success Criteria**: Full workflow working, performance targets met, system stable

---

## 10.0 Phase 7: Production Deployment

### 10.1 Phase Overview
**Goal**: Deploy system for production use  
**Duration**: 2-3 days  
**Key Skills**: Docker deployment, SSL configuration, monitoring setup  
**Success Criteria**: System deployed, SSL working, monitoring operational

---

## 11.0 Documentation and Progress Tracking

### 11.1 Changelog Requirements
For each completed step, the human developer must document in `devlog/changelog.md`:

```markdown
# Phase X Step Y: [Step Name] - [Status]

## Completion Date: [Date]
## Duration: [Time taken]

## ✅ What Was Accomplished
- [Detailed description of what was built/implemented]

## 🎯 Design Decisions Made
- [Technical choices and rationale]

## 🛠️ Issues Encountered and Resolutions
- [Problems faced and how they were solved]

## 📋 Devspec Inconsistencies Found
- [Any inconsistencies between specification documents]

## 🧠 Learning Insights
- [Key concepts learned during implementation]

## 🔍 Testing Results
- [Results of human validation procedures]
```

### 11.2 Phase Completion Summary
At the end of each phase, create a comprehensive summary:

```markdown
# Phase X: [Phase Name] - COMPLETED

## Overall Results
- Duration: [Total time]
- Steps Completed: [X/Y]
- Issues Encountered: [Count]
- Design Decisions: [Count]

## Key Achievements
- [Major milestones reached]

## Next Phase Readiness
- [Preparation for next phase]
```

---

## 12.0 Implementation Priority and Critical Path

### 12.1 Development Order
The phases must be completed in sequential order due to dependencies:

1. **Phase 1** is prerequisite for all others (environment setup)
2. **Phase 2** provides API foundation needed by frontend
3. **Phase 3** creates UI needed for user interaction
4. **Phase 4** implements core business logic
5. **Phase 5** adds administrative capabilities
6. **Phase 6** ensures system integration
7. **Phase 7** enables production deployment

### 12.2 Critical Success Factors
- **Human-AI Collaboration**: Active participation from both human and AI agent
- **Testing at Each Step**: Comprehensive validation before proceeding
- **Documentation**: Detailed progress tracking in changelog
- **Problem Resolution**: Immediate resolution of issues as they arise
- **Milestone Validation**: Clear demonstration of functionality

---

**Document ID**: 09_Dev_Roadmap.md  
**Document Version**: 1.0  
**Last Updated**: Implementation Phase  
**Next Review**: After each phase completion
