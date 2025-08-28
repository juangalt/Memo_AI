# AI Coding Agent Guidelines
## Memo AI Coach Project

**Purpose**: Practical guidance for AI coding agents working with novice programmers on the Memo AI Coach project.

---

## 🎯 Project Overview

**Team Composition**: Novice programmer + AI coding agent collaboration
**Goal**: Build a text evaluation system with maximum simplicity, comprehensive documentation, and learning-focused development

**Core Documents**: Read these in order before starting any implementation:
1. `devspecs/00_devspecs_overview.md` - Project overview and navigation
2. `devspecs/01_requirements.md` - Functional and non-functional requirements
3. `devspecs/02_architecture.md` - System architecture and components
4. `devspecs/03_Data_Model.md` - Database schema and data relationships
5. `devspecs/04_API_Definitions.md` - REST API specifications
6. `devspecs/05_UI_UX.md` - User interface and experience design
7. `devspecs/06_Testing.md` - Testing strategy and test cases
8. `devspecs/07_Deployment.md` - Deployment and infrastructure
9. `devspecs/08_Maintenance.md` - Maintenance and support procedures

---

## 🚨 Critical Rules

### **MANDATORY**: Never edit devspec files (00-09) unless explicitly instructed
### **MANDATORY**: Read devspec documents sequentially (00 → 09) before implementation
### **MANDATORY**: Treat missing details as deferred, never infer or assume

---

## 💡 Implementation Principles

### **Simplicity First**
- Avoid complex patterns and abstractions
- Prefer straightforward, readable code over clever solutions
- Use well-established, beginner-friendly libraries
- Minimize external dependencies

### **Comprehensive Documentation**
- Every function and class must have clear docstrings
- Inline comments explaining complex logic
- README files for each major component
- Clear explanations of design decisions

### **Modular Design**
- Single responsibility principle for all components
- Well-defined interfaces between modules
- Minimal coupling between different parts
- Easy to understand component boundaries

### **Extensibility**
- Clear extension points for new features
- Configuration-driven behavior where possible
- Plugin-like architecture for new capabilities
- Backward compatibility considerations

---

## 🔧 Technology Stack

**Backend**: FastAPI (Python) with SQLite database
**Frontend**: Streamlit (Python) with tabbed navigation
**Database**: SQLite with WAL mode for 100+ concurrent users
**Configuration**: YAML files (4 essential files)
**Deployment**: Docker containers with docker-compose

**Essential YAML Files**:
- `config/rubric.yaml` - Grading criteria and scoring
- `config/prompt.yaml` - LLM prompt templates
- `config/llm.yaml` - LLM provider configuration
- `config/auth.yaml` - Authentication settings

---

## 📋 Implementation Checklist

### Before Starting Any Code
- [ ] Read all devspec documents (00-09) sequentially
- [ ] Understand the specific requirement being implemented
- [ ] Review related architecture components
- [ ] Check data model requirements
- [ ] Verify API specifications
- [ ] Consider UI/UX implications

### Code Generation Standards
- [ ] Generate modular, single-responsibility code
- [ ] Add extensive comments and documentation
- [ ] Use simple, predictable patterns
- [ ] Follow established naming conventions
- [ ] Include error handling with educational messages
- [ ] Ensure backward compatibility

### Quality Assurance
- [ ] Code is self-documenting and easy to understand
- [ ] All functions have clear docstrings
- [ ] Error messages are helpful and educational
- [ ] Code follows the established patterns
- [ ] No complex abstractions unless absolutely necessary

---

## 🎓 Learning-Focused Development

### For the Novice Programmer
- Structure code to help understanding
- Explain design decisions and trade-offs
- Provide context for technical choices
- Use progressive complexity (simple first, advanced later)
- Include debugging support and helpful error messages

### Educational Considerations
- Document why certain approaches were chosen
- Explain alternative solutions when relevant
- Demonstrate industry-standard practices simply
- Provide clear paths for understanding and extending

---

## 🔍 Reference Quick Guide

| Document | Key Focus | Implementation Impact |
|----------|-----------|----------------------|
| **00** | Project overview, navigation, rules | Entry point, mandatory reading |
| **01** | Functional requirements, acceptance criteria | What to build, how to validate |
| **02** | System architecture, component design | How to structure the code |
| **03** | Database schema, data relationships | How to store and manage data |
| **04** | REST API specifications, endpoints | How to expose functionality |
| **05** | UI/UX design, user experience | How to present to users |
| **06** | Testing strategy, quality assurance | How to ensure reliability |
| **07** | Deployment, infrastructure | How to run the system |
| **08** | Maintenance, operational procedures | How to keep it running |

---

## ⚡ Quick Commands

### Project Structure
```
memoai/
├── backend/          # FastAPI backend
├── frontend/         # Streamlit frontend
├── config/           # YAML configuration files
├── devspecs/         # Specification documents
└── docker-compose.yml
```

### Essential Files
- `backend/main.py` - FastAPI application entry point
- `frontend/app.py` - Streamlit application entry point
- `config/*.yaml` - Configuration files (4 essential files)
- `docker-compose.yml` - Container orchestration

### Key Requirements
- **Performance**: <15 seconds for LLM evaluation responses
- **Scalability**: Support 100+ concurrent users with SQLite
- **Simplicity**: Maximum simplicity, no duplicate functions
- **Documentation**: Comprehensive comments required

---

## 🚀 Getting Started

1. **Read the Specs**: Start with `devspecs/00_devspecs_overview.md`
2. **Understand Requirements**: Review `devspecs/01_requirements.md`
3. **Plan Architecture**: Study `devspecs/02_architecture.md`
4. **Design Data Model**: Review `devspecs/03_Data_Model.md`
5. **Define APIs**: Check `devspecs/04_API_Definitions.md`
6. **Plan UI/UX**: Review `devspecs/05_UI_UX.md`
7. **Plan Testing**: Study `devspecs/06_Testing.md`
8. **Plan Deployment**: Review `devspecs/07_Deployment.md`
9. **Plan Maintenance**: Check `devspecs/08_Maintenance.md`
10. **Start Implementation**: Follow the specifications exactly

---

## 📞 When in Doubt

- **Refer to devspecs**: The specifications are the source of truth
- **Keep it simple**: Prefer straightforward solutions over complex ones
- **Document everything**: Explain your decisions and approach
- **Focus on learning**: Structure code to help the novice programmer understand
- **Ask for clarification**: If something is unclear, ask rather than assume

---

**Remember**: This project is about learning and collaboration. Every line of code should be educational, maintainable, and extensible.
