# Project Overview
## Memo AI Coach

**Document ID**: 00_ProjectOverview.md  
**Document Version**: 1.4  
**Last Updated**: Implementation Phase (Complete consistency fixes and standardization)  
**Next Review**: After initial deployment  
**Status**: Approved

---

## 1.0 Document Information

### 1.1 Purpose
Provides a high-level overview of the Memo AI Coach project and serves as the central navigation guide for all detailed specification files.

### 1.2 Scope
- Project definition and core functionality
- Document navigation and reading order
- Implementation rules and guidelines
- High-level system overview

### 1.3 Dependencies
- **Prerequisites**: None (entry point document)
- **Related Documents**: All specification documents (01-09)
- **Requirements**: Defines core functionality that maps to requirements in 01_Requirements.md

### 1.4 Document Structure
1. Document Information
2. Project Overview
3. Core Functionality
4. Document Navigation
5. Implementation Rules

### 1.5 Traceability Summary
| Requirement ID | Requirement Description | Document Reference | Status |
|---------------|------------------------|-------------------|---------|
| 2.3.1 | System uses grading rubric | 01_Requirements.md | ✅ Defined |
| 2.3.2 | System uses prompt templates | 01_Requirements.md | ✅ Defined |
| 2.3.3 | Overall strengths/opportunities | 01_Requirements.md | ✅ Defined |
| 2.3.4 | Detailed rubric grading | 01_Requirements.md | ✅ Defined |
| 2.3.5 | Segment-level evaluation | 01_Requirements.md | ✅ Defined |
| 2.3.6 | Immediate feedback processing | 01_Requirements.md | ✅ Defined |

### 1.6 Document Navigation
- **Next Document**: 01_Requirements.md
- **Related Documents**: All specification documents (01-09)

---

## 2.0 Project Overview

### 2.1 Project Name
Memo AI Coach

### 2.2 Project Description
A full-stack web application with separate front-end and back-end components designed to provide intelligent text evaluation and feedback.

**Key Components**:
- **Front-end**: User interfaces and client-side logic (Streamlit)
- **Back-end**: Server operations, data persistence with SQLite, and APIs (FastAPI)
- **Deployment**: Both components run in Docker containers for scalability
- **Database**: SQLite with WAL mode optimizations for 100+ concurrent users
- **Design Principles**: Modularity, simplicity, and extensibility

### 2.3 System Architecture Overview
The system consists of three major layers:
- **Frontend Layer**: Streamlit-based user interface with tabbed navigation
- **Backend Layer**: FastAPI REST services with LLM integration
- **Data Layer**: SQLite database with YAML configuration files

---

## 3.0 Core Functionality

### 3.1 Text Evaluation System
The system provides comprehensive text feedback based on:

- **3.1.1 Grading Rubric**: Structured evaluation criteria for consistent assessment
- **3.1.2 Prompt Templates**: Standardized LLM interaction patterns
- **3.1.3 Overall Analysis**: Strengths and improvement opportunities identification
- **3.1.4 Detailed Grading**: Rubric-based scoring with specific criteria
- **3.1.5 Segment Evaluation**: Targeted feedback with comments and questions
- **3.1.6 Immediate Feedback**: Real-time processing status and results

### 3.2 User Interface Features
- Tabbed navigation with state preservation
- Information tooltips for user guidance
- Help resources and framework documentation
- Clean, visually pleasing design

### 3.3 Administrative Functions
- YAML configuration management (4 essential files)
- Debug mode with system diagnostics
- Session-based authentication system
- Admin-only access controls

---

## 4.0 Document Navigation

### 4.1 Reading Order
Documents must be read sequentially to ensure proper understanding:

1. **00_ProjectOverview.md** (This document) - Start here
2. **01_Requirements.md** - Functional and non-functional requirements
3. **02_Architecture.md** - System architecture and component design
4. **03_Data_Model.md** - Database schema and data relationships
5. **04_API_Definitions.md** - REST API specifications
6. **05_UI_UX.md** - User interface and experience design
7. **06_Testing.md** - Testing strategy and test cases
8. **07_Deployment.md** - Deployment and infrastructure
9. **08_Maintenance.md** - Maintenance and support procedures
10. **09_Dev_Roadmap.md** - Development roadmap and milestones

### 4.2 Document Relationships
```
00_ProjectOverview.md
├── 01_Requirements.md (Core functionality → Requirements)
├── 02_Architecture.md (Requirements → Architecture)
├── 03_Data_Model.md (Architecture → Data Model)
├── 04_API_Definitions.md (Architecture → API Design)
├── 05_UI_UX.md (Requirements + Architecture → UI/UX)
├── 06_Testing.md (All previous → Testing Strategy)
├── 07_Deployment.md (Architecture → Deployment)
├── 08_Maintenance.md (All previous → Maintenance)
└── 09_Dev_Roadmap.md (All previous → Roadmap)
```

### 4.3 Document Index
| Document | Title | Purpose | Dependencies |
|----------|-------|---------|--------------|
| `00_ProjectOverview.md` | Project Overview | Entry point and navigation | None |
| `01_Requirements.md` | Requirements | Functional and non-functional requirements | 00 |
| `02_Architecture.md` | Architecture | System architecture and components | 01 |
| `03_Data_Model.md` | Data Model | Database schema and relationships | 02 |
| `04_API_Definitions.md` | API Definitions | REST API specifications | 02, 03 |
| `05_UI_UX.md` | UI/UX Specifications | User interface design | 01, 02 |
| `06_Testing.md` | Testing Strategy | Testing approach and test cases | 01-05 |
| `07_Deployment.md` | Deployment Plan | Infrastructure and deployment | 02 |
| `08_Maintenance.md` | Maintenance & Support | Operational procedures | All previous |
| `09_Dev_Roadmap.md` | Development Roadmap | Development timeline | All previous |

---

## 5.0 Implementation Rules

### 5.1 Mandatory Rules for AI Coding Agents
> ⚠️ **Critical Implementation Guidelines**

- **5.1.1** Do **not** edit DEVSPEC files (`00–09`) unless explicitly instructed
- **5.1.2** Always read specification files sequentially (00 → 09)
- **5.1.3** Treat missing details as deferred to later files, never as permission to infer
- **5.1.4** Generate modular, single-responsibility code. Avoid coupling across concerns
- **5.1.5** Follow the design principles defined in these specifications without deviation

### 5.2 Design Principles
- **Modularity**: Clear separation of concerns and responsibilities
- **Simplicity**: Maximum simplicity, no duplicate functions
- **Extensibility**: Design for future enhancements and scalability
- **Maintainability**: Comprehensive comments and clear code structure

### 5.3 Quality Standards
- **Code Quality**: Modular, well-commented, single-responsibility code
- **Documentation**: Comprehensive inline documentation and comments
- **Testing**: Thorough testing with clear test cases
- **Performance**: Responsive system with <1s page loads and <15s evaluation responses

---

## 6.0 Next Steps

### 6.1 For Developers
1. Read this document completely
2. Proceed to `01_Requirements.md` for detailed requirements
3. Follow the sequential reading order through all documents
4. Implement according to the specifications and rules defined

### 6.2 For AI Coding Agents
1. Follow the mandatory rules in Section 5.1
2. Ensure all implementations trace back to specific requirements
3. Maintain consistency with the design principles
4. Generate code that aligns with the modular architecture

---

**Document ID**: 00_ProjectOverview.md  
**Document Version**: 1.4  
**Last Updated**: Implementation Phase (Complete consistency fixes and standardization)  
**Next Review**: After initial deployment

