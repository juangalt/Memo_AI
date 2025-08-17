# 02_Architecture.md

## 1.0 How to Use This File

- Defines the high-level system architecture.
- Builds on `01_Requirements.md`.
- Review before proceeding to `03_Data_Model.md`.
- **Traceability Hook**: Each component and flow must map back to requirements in `01_Requirements.md`.

---

## 2.0 System Overview

The Memo AI Coach system consists of a modular architecture designed for clarity, maintainability, and scalability. It is composed of three major layers:

- **Frontend (GUI)**

  - Provides the main user interface as tabbed navigation (Req 2.1).
  - Pages: Text Input, Overall Feedback, Detailed Feedback, Progress Tracking, Debug, Help, Admin.
  - Supports fast load times (<1s main load, <15s submission response) and usability features (hover info bubbles, rubric/framework resources) (Req 3.1, 2.1).

- **Backend Services**

  - REST API layer providing endpoints for evaluation and progress reports, chat, admin functions, debugging info and exports (Req 2.2–2.7).
  - Handles orchestration between frontend requests and the LLM engine.
  - Provides error handling, logging, and PDF generation (Req 2.7, 3.3).

- **LLM Engine Integration**

  - Connects with the chosen LLM provider.
  - Uses context template, rubric, frameworks, and user submissions to produce evaluations and progress reports (Req 2.2).
  - Supports debug mode by exposing raw prompts, raw responses, and performance metrics (Req 2.5).

- **Data Layer**

  - Stores user submissions, evaluation history, YAML configuration files, and logs (Req 2.6, 2.4, 3.5).
  - Enables charting for progress tracking (Req 2.6).

### Key Properties

- Modular, API-driven architecture (Req 3.5).
- Cloud-ready design that supports scaling from MVP single-user to 100+ users (Req 3.2).
- Emphasis on maintainability and error handling (Req 3.3, 3.5).

---

## 3.0 Architecture Diagram
(To be defined. Ensure diagram components map to requirement IDs.)

---

## 4.0 Components

### 4.1 Frontend (GUI)

- Framework/library: **Reflex**
- Tabbed navigation
- **State persistence**: Use a **Global State Manager** to maintain a centralized source of truth for all frontend components.
  - Ensures data (submitted text, evaluation results, chat history, progress chart data) is instantly available across tabs without re-fetching.
  - Leverages Reflex’s built-in global state capabilities.
  - Provides consistent user experience and scalability.

**Components:**
- `TextInputPage`
- `OverallFeedbackPage`
- `DetailedFeedbackPage`
- `ProgressTrackingPage`
- `DebugPage`
- `HelpPage`
- `AdminPage`

### 4.2 Backend Services
**Decisions:**
- API style: REST (simple, maintainable).
- Framework: **FastAPI** (lightweight, async-friendly).
- Endpoint grouping per function: evaluation, chat, progress, admin, export.

**Suggested Components:**
- `EvaluationService`
- `ChatService`
- `ProgressService`
- `AdminService`
- `ExportService`
- `DebugService`

### 4.3 LLM Engine Integration
**Decisions:**
- Provider: **Claude** (per 00 Overview), pluggable for future alternatives.
- Prompt engineering: combine context template, rubric, frameworks, and user text.
- Expose debug data without leaking sensitive info.

**Suggested Components:**
- `LLMConnector`
- `PromptBuilder`
- `ResponseParser`
- `DebugAdapter`

### 4.4 Data Layer
**Decisions:**
- Database: SQLite (MVP), upgradeable later.
- Schema: support user submissions, evaluations, YAML configs, logs.
- Store history and generate progress charts.

**Suggested Components:**
- `SubmissionRepository`
- `EvaluationRepository`
- `ConfigRepository`
- `LogRepository`
- `ChartDataAdapter`

---

## 5.0 Data Flow
(To be defined. Data flow steps must trace back to input/output requirements.)

---

## 6.0 Extensibility Points
(To be defined. Document how extensibility supports requirements and future scalability.)

---

## 7.0 Traceability Links

- **Source of Truth**: `01_Requirements.md`
- **Mapped Requirements (placeholders)**:
  - GUI (2.1)
  - Text Evaluation (2.2)
  - Chat with LLM (2.3)
  - Admin Functions (2.4)
  - Debug Mode (2.5)
  - Progress Tracking (2.6)
  - PDF Export (2.7)
  - Performance (3.1)
  - Scalability (3.2)
  - Reliability (3.3)
  - Maintainability (3.5)

