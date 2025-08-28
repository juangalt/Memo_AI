# AI Agent Documentation Guidelines

## Memo AI Coach Project

**Document ID**: AGENTS.md
**Document Version**: 1.0
**Last Updated**: Implementation Phase
**Status**: Active

---

## ⚠️ CRITICAL: Documentation Editing Policy

### **MANDATORY RULE: DO NOT EDIT DOCS FILES UNLESS EXPLICITLY REQUESTED**

- **AI agents MUST NOT modify, update, or edit any files in the `docs/` directory**
- **This includes adding, removing, or changing content in any documentation files**
- **The `docs/` directory contains the authoritative project specifications**
- **Only make changes to `docs/` files when the user explicitly requests it**
- **All other directories (backend/, frontend/, config/, etc.) can be modified as needed**
- **Violation of this rule will result in incorrect project implementation**

---

## 1.0 Documentation Guidelines

### 1.1 Purpose

This guide provides standards and procedures for AI agents working on the Memo AI Coach project. It ensures consistent, high-quality documentation that serves both human developers and AI coding agents.

### 1.2 Core Principles

- **Comprehensive**: Cover all aspects of the system in detail
- **Structured**: Consistent organization and formatting
- **Accessible**: Clear language suitable for both humans and AI agents
- **Maintainable**: Easy to update and extend
- **Traceable**: Clear links between related documentation

### 1.3 Documentation Structure Template

All documentation files must follow this structure:

```markdown
# [Document Title]
## [Project Name]

**Document ID**: [filename]
**Document Version**: [version]
**Last Updated**: [date]
**Next Review**: [date]
**Status**: [draft/ready/approved]

---

## 1.0 Document Information

### 1.1 Purpose
[Clear statement of what this document covers and why it exists]

### 1.2 Scope
[What is included and excluded from this document]

### 1.3 Target Audience
[Who should read this document and what they need to know]

### 1.4 Dependencies
[Related documents and prerequisites]

---

## 2.0 [Main Content Section]

### 2.1 [Subsection]
[Detailed content with examples]

### 2.2 [Subsection]
[Detailed content with examples]

---

## 3.0 [Additional Sections]

[Additional sections as needed]

---

## 4.0 References and Links

### 4.1 Related Documents
- [Link to related documentation]

### 4.2 External Resources
- [Links to external resources]

---

**Document ID**: [filename]
**Document Version**: [version]
**Last Updated**: [date]
**Next Review**: [date]
```

### 1.4 Content Standards

#### Clarity and Precision

- Use clear, concise language
- Define technical terms when first used
- Provide concrete examples
- Use consistent terminology throughout

#### Structure and Organization

- Use hierarchical headings (H1, H2, H3)
- Group related information together
- Use bullet points and numbered lists appropriately
- Include table of contents for long documents

#### Code and Configuration Examples

- Use syntax highlighting for code blocks
- Include complete, working examples
- Explain what each example does
- Provide both simple and complex examples

#### Cross-References

- Link to related documentation
- Reference specific sections when needed
- Maintain consistent linking patterns
- Update links when documents change

### 1.5 Quality Standards

#### Completeness Requirements

- **Coverage**: All aspects of the topic must be covered
- **Depth**: Provide sufficient detail for the target audience
- **Examples**: Include practical examples for all procedures
- **References**: Link to related documentation and resources

#### Accuracy Requirements

- **Technical Accuracy**: All technical information must be correct
- **Current Status**: Reflect the current state of the system
- **Consistency**: Information must be consistent across documents
- **Validation**: All procedures must be tested and verified

#### Usability Requirements

- **Navigation**: Easy to find specific information
- **Searchability**: Use clear, descriptive headings and terms
- **Readability**: Appropriate for the target audience
- **Maintainability**: Easy to update and extend

---

## 2.0 Project Documentation Index

### 2.1 Docs Directory Structure

The `docs/` directory contains the complete project specifications and documentation:

```plaintext
docs/
├── AGENTS.md                          # This file - AI agent guidelines
├── 01_Project_Overview.md             # High-level project overview
├── 02_Architecture_Documentation.md   # Detailed system architecture
├── 03_Installation_Guide.md           # Complete installation procedures
├── 04_Configuration_Guide.md          # Configuration management
├── 05_API_Documentation.md            # Complete API reference
├── 06_User_Guide.md                   # End-user documentation
├── 07_Administration_Guide.md         # System administration
├── 08_Development_Guide.md            # Development procedures
├── 09_Testing_Guide.md                # Testing procedures and frameworks
├── 10_Deployment_Guide.md             # Production deployment
├── 11_Maintenance_Guide.md            # System maintenance
├── 12_Troubleshooting_Guide.md        # Problem resolution
└── 13_Reference_Manual.md             # Technical reference
```

### 2.2 Documentation Categories

#### **Project Foundation**

- **01_Project_Overview.md**: Goals, features, technology stack, target users
- **02_Architecture_Documentation.md**: System design, component relationships, data flow

#### **Implementation Guides**

- **03_Installation_Guide.md**: Prerequisites, environment setup, Docker configuration
- **04_Configuration_Guide.md**: Environment variables, YAML files, validation procedures
- **08_Development_Guide.md**: Development environment, code structure, workflow
- **09_Testing_Guide.md**: Testing frameworks, procedures, automation

#### **Operational Guides**

- **05_API_Documentation.md**: Complete API reference, authentication, error handling
- **06_User_Guide.md**: Application usage, evaluation workflow, best practices
- **07_Administration_Guide.md**: Admin procedures, monitoring, security
- **10_Deployment_Guide.md**: Production deployment, scaling, monitoring
- **11_Maintenance_Guide.md**: Regular maintenance, updates, optimization
- **12_Troubleshooting_Guide.md**: Issue resolution, diagnostics, recovery

#### **Reference Materials**

- **13_Reference_Manual.md**: Technical specifications, schemas, error codes

### 2.3 Reading Order Recommendations

#### **For New AI Agents**

1. Read `AGENTS.md` (this file) - **MANDATORY**
2. Read `01_Project_Overview.md` - Understand project scope
3. Read `02_Architecture_Documentation.md` - Understand system design
4. Read relevant specific guides based on task

#### **For Implementation Tasks**

1. Always read `AGENTS.md` first (**MANDATORY**)
2. Read `01_Project_Overview.md` for context
3. Read `02_Architecture_Documentation.md` for design principles
4. Read specific guides relevant to the task:
   - API development: `05_API_Documentation.md`
   - Configuration: `04_Configuration_Guide.md`
   - Testing: `09_Testing_Guide.md`
   - Deployment: `10_Deployment_Guide.md`

---

## 3.0 AI Agent Procedures

### 3.1 Before Starting Work

- [ ] **MANDATORY**: Read `AGENTS.md` (this file) completely
- [ ] Understand the specific task requirements
- [ ] Identify which documentation files are relevant
- [ ] Read the identified documentation files
- [ ] Plan implementation approach based on specifications

### 3.2 During Implementation

- [ ] Follow documentation guidelines and standards
- [ ] Maintain code quality and documentation standards
- [ ] Use consistent patterns and practices
- [ ] Include comprehensive comments and docstrings
- [ ] Test all procedures and examples

### 3.3 Quality Assurance

- [ ] Verify technical accuracy against specifications
- [ ] Ensure consistency with existing codebase
- [ ] Test all code changes thoroughly
- [ ] Update any related documentation (only if explicitly requested)
- [ ] Validate that changes meet acceptance criteria

---

## 4.0 Integration with Project Workflow

### 4.1 Devspecs Relationship

- The `docs/` directory contains the canonical project specifications
- Historical `devspecs/` documents remain for context but are deprecated
- When discrepancies arise, `docs/` files take precedence
- Always reference `docs/` for current specifications

### 4.2 Code Implementation

- **Code Examples**: Include relevant code snippets in documentation
- **File References**: Link to specific source files when documenting
- **API Documentation**: Document all public APIs comprehensively
- **Configuration**: Document all configuration options completely

### 4.3 Development Process

- Use specifications in `docs/` as the source of truth
- Implement features according to documented requirements
- Test against documented acceptance criteria
- Document any deviations or clarifications needed

---

## 5.0 Best Practices for AI Agents

### 5.1 Documentation Generation

- Use provided templates and structures consistently
- Maintain consistent formatting and style across all outputs
- Ensure all required sections are included
- Verify all technical information is accurate and current

### 5.2 Code Development

- Write clear, understandable code with comprehensive comments
- Include practical examples in documentation
- Link to related documentation and resources
- Verify procedures and examples work correctly

### 5.3 Quality Standards

- Review content for completeness and accuracy
- Test all procedures and examples before finalizing
- Ensure consistency with existing documentation
- Update related documentation when system changes occur

---

## ⚠️ FINAL REMINDER

**DO NOT EDIT ANY FILES IN THE `docs/` DIRECTORY UNLESS EXPLICITLY REQUESTED BY THE USER**

This rule is critical to maintain the integrity of the project specifications. The `docs/` directory contains the authoritative documentation that guides all development work.

---

**Document ID**: AGENTS.md
**Document Version**: 1.0
**Last Updated**: Implementation Phase
**Status**: Active
