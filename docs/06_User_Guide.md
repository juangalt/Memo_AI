# User Guide
## Memo AI Coach

**Document ID**: 06_User_Guide.md
**Document Version**: 2.0
**Last Updated**: Phase 11 - LLM Refactor & Health Security Implementation
**Status**: Active

---

## 1.0 Accessing the Application
- Run locally: `cd vue-frontend && npm run dev` (backend must be running on port 8000).
- Production: open `https://<domain>/` served via Traefik with automatic HTTPS.
- Browser support: modern browsers with JavaScript enabled (Chrome, Firefox, Edge, Safari).
- **Welcome Page**: Users land on a beautiful welcome page explaining the application.
- **Authentication Required**: All users must log in through the login page before accessing any application functions.

## 2.0 Authentication and User Types
### 2.1 User Categories
- **Regular Users**: Can submit memos for evaluation, view feedback, and access basic application functions.
- **Administrators**: Have all regular user privileges plus access to configuration validation, system monitoring, debug tools, and administrative functions.

### 2.2 Login Process
1. **Welcome Page**: Upon accessing the application, users land on a beautiful welcome page explaining the application.
2. **Authentication Access**: Users click "Get Started" to access the login interface.
3. **Credential Entry**: Enter username and password as configured in the system.
4. **Session Creation**: Upon successful authentication, the system creates a session and redirects to the Text Input page.
5. **Session Management**: Sessions persist for the configured duration with automatic logout upon expiration.

## 3.0 Interface Overview
The Vue.js frontend provides a single-page application with eight main views:

1. **Home** (`/`) – beautiful welcome page with application overview (public).
2. **Login** (`/login`) – centralized authentication interface for all users (public).
3. **Text Input** (`/text-input`) – submit content for evaluation (authenticated).
4. **Overall Feedback** (`/overall-feedback`) – displays overall score, strengths and opportunities (authenticated).
5. **Detailed Feedback** (`/detailed-feedback`) – shows rubric scores and segment-level comments (authenticated).
6. **Help** (`/help`) – comprehensive documentation and rubric explanation (authenticated).
7. **Admin** (`/admin`) – system monitoring, configuration validation, and user management (administrators only).
8. **Debug** (`/debug`) – system diagnostics, API testing, and development tools (administrators only).

Tooltips on each input explain expected format. Navigation links at the top allow switching between views without losing session state. Access to views is controlled by user role and authentication status through Vue Router guards.

## 4.0 Submitting Text
1. **Welcome Page**: Start at the beautiful welcome page explaining the application.
2. **Authenticate**: Click "Get Started" to access the login interface.
3. **Navigate**: After login, you'll be redirected to the **Text Input** page.
4. **Submit Text**: Paste or type memo text (maximum 10,000 characters).
5. **Evaluation**: Click **Submit for Evaluation** to process your text.
6. **Progress**: A progress indicator shows evaluation status (target <15s).
7. **Results**: Results populate the **Overall Feedback** and **Detailed Feedback** pages.

## 5.0 Viewing Results
### Overall Feedback Page
- Shows aggregate score and key metrics.
- Displays strengths and improvement opportunities.
- Provides elapsed processing time and timestamp for auditing.

### Detailed Feedback Page
- Presents the new 4-criteria rubric with individual scores and justifications:
  - **Structure** (25%): Pyramid principle, SCQA, clarity of opportunity, ask
  - **Arguments and Evidence** (30%): Logic, financial metrics
  - **Strategic Alignment** (25%): Help achieve strategic goals
  - **Implementation and Risks** (20%): Feasibility, risk assessment, implementation plan
- Lists segment feedback objects containing comments, questions and suggestions.
- Allows collapsing or expanding each criterion for readability.
- **Dynamic Rubric Display**: Automatically adapts to any rubric structure without code changes.

### Help Page
- **Comprehensive Documentation**: Complete guide to using the application.
- **Evaluation Rubric**: Detailed explanation of scoring criteria and scale.
- **Quick Start Guide**: Step-by-step instructions for new users.
- **Tips for Better Results**: Practical advice for improving writing.
- **Support Information**: Contact details and next steps.

### Debug Page (Administrators Only)
- **System Diagnostics**: View system health, database status, and service connectivity with real-time monitoring.
- **API Health Testing**: Comprehensive testing of all 12 API endpoints including health, auth, config, and evaluation endpoints with detailed error reporting and debug information.
- **Performance Monitoring**: Monitor response times, system metrics, and resource usage with visual charts and historical data.
- **Development Tools**: Access debugging utilities, environment information, and development aids for system troubleshooting.

## 6.0 Session Management
- Session identifier displayed in Text Input page.
- Session persists for configured duration on backend; refresh or create new session from Admin page.
- Use the **Reset Session** button in Admin page to clear history and begin a new submission cycle.
- **Session Expiration**: Automatic logout occurs when sessions expire, redirecting to the home page and requiring re-authentication.

## 7.0 Limitations
- LLM evaluation may run in mock mode if `LLM_API_KEY` is not set; results then are simulated.
- Evaluation retrieval endpoint `/api/v1/evaluations/{id}` currently returns placeholder data.
- Export/import of sessions is planned but not yet implemented.
- The interface expects plain text; rich formatting is stripped before evaluation.
- **Authentication Required**: All application functions require valid user authentication.
- **Role-Based Access**: Some features are restricted based on user role (regular user vs administrator).

## 8.0 References
- `devlog/vue_frontend_implementation_plan.md` - Vue.js frontend implementation plan
- `vue-frontend/src/App.vue` - Main Vue.js application
- `vue-frontend/src/stores/evaluation.js` - Vue.js evaluation state management
- `vue-frontend/src/services/api.js` - Vue.js API client
