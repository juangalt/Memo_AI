# 05_UI_UX.md

## 1.0 How to Use This File

1.1 **Audience**  
AI coding agents and human developers.

1.2 **Purpose**  
Defines user interface and experience rules for Memo AI Coach.  
Builds on `01_Requirements.md` and `02_Architecture.md`.

1.3 **Next Steps**  
Read before starting testing strategy (`06_Testing.md`).

---

## 2.0 Framework and Technology Stack

### 2.1 Frontend Framework
- **Reflex** selected for reactive Python development and built‑in state handling.

### 2.2 Styling
- **Tailwind CSS** via Reflex integration for a clean, utility‑first design.
- Light theme with CSS variables for future theming.

### 2.3 State Management
- Reflex global state holds session data, evaluation results, progress metrics and chat history.
- State persists across tabs and page refreshes using browser storage.

---

## 3.0 Layout and Navigation

### 3.1 Navigation Structure
```yaml
Tabs:
  - TextInput (default)
  - OverallFeedback
  - DetailedFeedback
  - ProgressTracking
  - Debug
  - Help
  - Admin
```
- Implemented with Reflex router; switching tabs only updates the view, preserving global state.
- Tab change time target: **<1s**.

### 3.2 Chat Access
- After an evaluation, a collapsible chat panel is available on Feedback and Detailed pages.
- Chat state references most recent evaluation and session context.

---

## 4.0 Page Specifications

### 4.1 TextInput Page
```yaml
Components:
  - TextArea (10k character limit)
  - SubmitButton with spinner
  - CharCounter
  - InfoBubble explaining rubric/framework usage
  - SessionStatus indicator
Behavior:
  - Auto‑focus on load
  - Validate non‑empty and length
  - On submit -> call `/evaluation` endpoint then navigate to OverallFeedback
```

### 4.2 Overall Feedback Page
```yaml
Components:
  - StrengthsList
  - OpportunitiesList
  - RubricTable
  - Actions: [OpenChat, ViewDetailed, ExportPDF]
Behavior:
  - Displays latest evaluation summary from global state
  - ExportPDF triggers `/export/pdf/{id}`
```

### 4.3 Detailed Feedback Page
```yaml
Components:
  - SegmentAccordion (segment text, comment, questions)
  - ChatPanel (collapsible)
Behavior:
  - Segment data loaded from global state
  - ChatPanel sends messages to `/chat`
```

### 4.4 Progress Tracking Page
```yaml
Components:
  - LineChart (overall score over time)
  - RubricBreakdownChart (bar)
  - SubmissionHistoryTable
Behavior:
  - Data loaded via `/progress` endpoint then cached
```

### 4.5 Debug Page
- Visible when debug mode enabled.  
- Shows raw prompts/responses, timing data, and links to log files.

### 4.6 Help Page
- Static content with rubric descriptions, framework explanations, and usage tips.

### 4.7 Admin Page
- YAML editor for rubric/framework/context/prompt/auth files.  
- Client‑side validation and submit to `/admin` endpoints.

---

## 5.0 UI Components and Patterns

- **NavigationBar**: highlights active tab, collapses on mobile.
- **Forms**: labelled inputs, inline validation, disabled submit until valid.
- **Loading States**: skeleton screens for pages, spinners for actions, progress bar for long operations (PDF export).
- **Notifications**: toast messages for success/error, inline messages for field errors.
- **Responsive Design**: mobile‑first with breakpoints at 640px, 1024px.
- **Error Pages**: generic error component with retry and support link.

---

## 6.0 Accessibility and Usability

- Target **WCAG 2.1 AA** compliance.  
- Keyboard navigation for all interactive elements.  
- ARIA labels on custom components.  
- Colour contrast ≥ 4.5:1.  
- Focus outlines preserved; skip‑to‑content link provided.

---

## 7.0 Performance Targets

```yaml
Performance:
  initial_page_load: "<1s"
  tab_switch: "<1s"
  evaluation_response: "<15s"
  progress_load: "<2s (cached)"
  pdf_generation: "<10s"
```
- Lazy‑load heavy components (charts, admin editor).  
- Cache evaluation and progress data in global state.

---

## 8.0 Implementation Guidelines

- Each page implemented as a Reflex component with single responsibility.  
- Shared components placed in `/components` directory.  
- All API calls go through a small `api_client` module for reuse and error handling.

---

## 9.0 Traceability Links

- Requirements: GUI (2.1), Text Evaluation (2.2), Chat (2.3), Admin (2.4), Debug (2.5), Progress Tracking (2.6), PDF Export (2.7), Performance (3.1).
- Architecture References: Frontend structure and global state (02_Architecture §4.1).
