# 01_Requirements.md

## 1.0 How to Use This File

1.1 **Audience**
- AI coding agents and human developers.

1.2 **Purpose**
- Defines the functional and non-functional requirements of the Memo AI Coach project.
- Builds directly on the high-level overview in `00_DEVSPECS_OVERVIEW.md`.

1.3 **Next Steps**
- Review this file before proceeding to `02_Architecture.md`.

---

## 2.0 Functional Requirements

2.1 **User Interface (GUI)**
- 2.1.1 On load, the text input page is displayed.
- 2.1.2 Navigation between functions (help, text input, overall feedback, detailed feedback, progress tracking, debug) is implemented as tab switches that preserve session data and load quickly.
- 2.1.3 Information bubbles appear on hover, explaining each section.
- 2.1.4 The Help tab displays usage information and resources to learn the rubric and frameworks.
- 2.1.5 The site must be visually clean but also pleasing.

2.2 **Text Submission and Evaluation [MVP]**
- 2.2.1 The system provides a text input box for users.
- 2.2.2 Upon submission, the system processes the text using an LLM synchronously.
- 2.2.3 The system returns:
  - (a) Overall evaluation including strengths, opportunities, and rubric grading.
  - (b) Segment-level evaluation with comments and insight questions.
- 2.2.4 Evaluation processing is straightforward with immediate feedback.

2.3 **Admin Functions [MVP]**
- 2.3.1 Admins can edit essential YAML files (4 files): `rubric.yaml`, `prompt.yaml`, `llm.yaml`, `auth.yaml`.
- 2.3.2 All configuration changes are validated.
- 2.3.3 Simple configuration management without version tracking for MVP.

2.4 **Debug Mode [MVP]**
- 2.4.1 In debug mode, admins can review debug output for system diagnostics.
- 2.4.2 Debug includes performance data, raw prompts, and raw responses.
- 2.4.3 Debug mode is admin-only to prevent security risks.

---

## 3.0 Non-Functional Requirements

3.1 **Performance**
- 3.1.1 General use should be very responsive.
- 3.1.2 LLM submissions may take a few seconds.

3.2 **Scalability**
- 3.2.1 MVP supports 10-20 concurrent users.
- 3.2.2 System scales to 100+ concurrent users using SQLite with WAL mode optimizations.

3.3 **Reliability**
- 3.3.1 High uptime is expected.
- 3.3.2 Robust error handling and logging required.

3.4 **Security**
- 3.4.1 Session-based authentication system using secure session tokens for user isolation.
- 3.4.2 Secure session management with expiration and cleanup.
- 3.4.3 CSRF protection and rate limiting per session/user.
- 3.4.4 Admin authentication for system management functions.
- 3.4.5 Optional JWT authentication can be added in future if complex user management is needed.

3.5 **Maintainability**
- 3.5.1 Maintainability is top priority.
- 3.5.2 Maximum simplicity, no duplicate functions.
- 3.5.3 Comprehensive comments required.
- 3.5.4 Modular architecture.

---

## 4.0 Acceptance Criteria

4.1 **GUI**
- Main page load < 1s.
- Submission response < 15s.
- Tab switching preserves session data and is fast.
- Info bubbles explain each section.
- Help tab shows rubric/framework resources.
- Site is clean and visually pleasing.

4.2 **Text Evaluation**
- Returns consistent overall evaluation (strengths, weaknesses, rubric) via synchronous processing.
- Returns segment-level feedback with comments and questions.
- Provides immediate feedback after evaluation processing.
- Simple, straightforward evaluation system for reliable user experience.

4.3 **Admin Functions**
- Admin can edit 4 essential YAML configuration files.
- YAML validated to prevent malformed input with basic checking.
- Debug mode toggle available for system diagnostics.
- Simple configuration management interface.

4.4 **Debug Mode**
- Debug shows raw prompts, raw responses, performance data.
- Admin-only access to debug information for security.

4.8 **Non-Functional**
- Response times acceptable.
- Scales to 100+ concurrent users using SQLite optimizations.
- Error handling comprehensive.
- Code modular, simple, and well-commented.

---

## 5.0 Traceability Matrix

| Req ID | Requirement Description       | Acceptance Criteria | Test Case ID |
| ------ | ----------------------------- | ------------------- | ------------ |
| 2.1.1  | Main page shows text input    | 4.1                 | TC-001       |
| 2.1.2  | Tab navigation fast           | 4.1                 | TC-002       |
| 2.1.3  | Info bubbles                  | 4.1                 | TC-003       |
| 2.1.4  | Help tab resources            | 4.1                 | TC-004       |
| 2.1.5  | Clean visuals                 | 4.1                 | TC-005       |
| 2.2.1  | Text input box available      | 4.2                 | TC-006       |
| 2.2.2  | Submission processed by LLM   | 4.2                 | TC-007       |
| 2.2.3a | Overall evaluation returned   | 4.2                 | TC-008       |
| 2.2.3b | Segment evaluation returned   | 4.2                 | TC-009       |
| 2.3.1  | Chat after feedback           | 4.3                 | TC-010       |
| 2.3.2  | Chat uses context             | 4.3                 | TC-011       |
| 2.4.1  | Admin edits YAML              | 4.4                 | TC-012       |
| 2.5.1  | Debug output accessible       | 4.5                 | TC-013       |
| 2.5.2  | Raw prompts/responses shown   | 4.5                 | TC-014       |
| 2.6.1  | Grading history recorded      | 4.6                 | TC-015       |
| 2.6.2  | Progress data with evaluation | 4.6                 | TC-016       |
| 2.7.1  | PDF generated                 | 4.7                 | TC-017       |
| 2.7.2  | PDF includes text/feedback    | 4.7                 | TC-018       |
| 3.1.1  | Responsive system             | 4.8                 | TC-019       |
| 3.1.2  | LLM response within seconds   | 4.8                 | TC-020       |
| 3.2.1  | MVP handles 10-20 users       | 4.8                 | TC-021       |
| 3.2.2  | Scales to 100+ users with SQLite | 4.8                 | TC-022       |
| 3.3.1  | High uptime                   | 4.8                 | TC-023       |
| 3.3.2  | Robust error handling         | 4.8                 | TC-024       |
| 3.5.1  | Maintainability priority      | 4.8                 | TC-025       |
| 3.5.2  | Simplicity no duplicates      | 4.8                 | TC-026       |
| 3.5.3  | Comprehensive comments        | 4.8                 | TC-027       |
| 3.5.4  | Modular architecture          | 4.8                 | TC-028       |

