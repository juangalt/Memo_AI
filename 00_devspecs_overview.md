# 00_DEVSPECS_OVERVIEW.md

## 1.0 How to Use This File

1.1 **Audience**
- AI coding agents and human developers.

1.2 **Purpose**
- Provides a high-level overview of the Memo AI Coach project.
- Serves as the central index for all detailed specification files (`01_Requirements.md` → `09_Dev_Roadmap.md`).

1.3 **Next Steps**
- Read this file first.
- Proceed in order through each specification file.

---

## 2.0 Rules for AI Coding Agents

> ⚠️ **Mandatory Rules**
>
> - **2.1** Do **not** edit DEVSPEC files (`00–09`) unless explicitly instructed.
> - **2.2** Always read specification files sequentially (00 → 09).
> - **2.3** Treat missing details as deferred to later files, never as permission to infer.
> - **2.4** Generate modular, single-responsibility code. Avoid coupling across concerns.
> - **2.5** Follow the design principles defined in these specifications without deviation.

---

## 3.0 Project Overview

3.1 **Name**
- Memo AI Coach

3.2 **Description**
- A full-stack web application with separate front-end and back-end components.
- Front-end: user interfaces and client-side logic.
- Back-end: server operations, data persistence, and APIs.
- Both components run in Docker containers for deployment and scalability.
- The AI coding agent will build the system following these specifications to ensure **modularity**, **simplicity**, and **extensibility**.

3.3 **Core Functionality**
- Provide text feedback based on:
  - 3.3.1 A grading rubric.
  - 3.3.2 Communication frameworks.
  - 3.3.3 Defined context template.
- Feedback includes:
  - 3.3.4 Overall strengths and improvement opportunities.
  - 3.3.5 Detailed grading according to rubric.
  - 3.3.6 Segment-level evaluation with comments and questions.
  - 3.3.7 Support for iterative improvement with chat.
  - 3.3.8 Ability to export evaluations as PDFs.
  - 3.3.9 Progress tracking via grading history and charts.

---

## 4.0 Index of Specification Files

| File | Title |
| ---- | ----- |
| `00_DEVSPECS_OVERVIEW.md` | Development Specs Overview |
| `01_Requirements.md` | Requirements |
| `02_Architecture.md` | Architecture |
| `03_Data_Model.md` | Data Model |
| `04_API_Definitions.md` | API Definitions |
| `05_UI_UX.md` | UI/UX Specifications |
| `06_Testing.md` | Testing Strategy |
| `07_Deployment.md` | Deployment Plan |
| `08_Maintenance.md` | Maintenance & Support |
| `09_Dev_Roadmap.md` | Development Roadmap |

