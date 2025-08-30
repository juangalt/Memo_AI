# User Guide
## Memo AI Coach

**Document ID**: 06_User_Guide.md
**Document Version**: 1.1
**Last Updated**: Phase 9
**Status**: Draft

---

## 1.0 Accessing the Application
- Run locally: `streamlit run frontend/app.py` (backend must be running on port 8000).
- Production: open `https://<domain>` served via Traefik with automatic HTTPS.
- Browser support: recent versions of Chrome, Firefox or Edge.
- **Authentication Required**: All users must log in through the homepage before accessing any application functions.

## 2.0 Authentication and User Types
### 2.1 User Categories
- **Regular Users**: Can submit memos for evaluation, view feedback, and access basic application functions.
- **Administrators**: Have all regular user privileges plus access to configuration management, system monitoring, debug tools, and administrative functions.

### 2.2 Login Process
1. **Homepage Access**: Upon accessing the application, users are directed to the centralized login page.
2. **Credential Entry**: Enter username and password as configured in the system.
3. **Session Creation**: Upon successful authentication, the system creates a session and provides access to appropriate application functions.
4. **Session Management**: Sessions persist for the configured duration with automatic logout upon expiration.

## 3.0 Interface Overview
The frontend (`frontend/app.py`) provides six tabs, all requiring authentication:
1. **Login** – centralized authentication interface for all users.
2. **Text Input** – submit content for evaluation (regular users and admins).
3. **Overall Feedback** – displays overall score, strengths and opportunities (regular users and admins).
4. **Detailed Feedback** – shows rubric scores and segment-level comments (regular users and admins).
5. **Debug** – system diagnostics, API testing, and development tools (administrators only).
6. **Admin** – configuration management and system monitoring (administrators only).

Tooltips on each input explain expected format. Navigation buttons at the top allow switching between tabs without losing session state. Access to tabs is controlled by user role and authentication status.

## 4.0 Submitting Text
1. **Authenticate**: Ensure you are logged in through the homepage login interface.
2. Open the **Text Input** tab.
3. Paste or type memo text (maximum 10,000 characters).
4. Click **Submit for Evaluation**.
5. The application creates a session if one does not exist and sends the text to backend.
6. A progress spinner appears while waiting for the LLM response (target <15s).
7. Results populate the **Overall Feedback** and **Detailed Feedback** tabs.

## 5.0 Viewing Results
### Overall Feedback Tab
- Shows aggregate score and key metrics.
- Displays strengths and improvement opportunities.
- Provides elapsed processing time and timestamp for auditing.

### Detailed Feedback Tab
- Presents rubric criteria with individual scores and justifications.
- Lists segment feedback objects containing comments, questions and suggestions.
- Allows collapsing or expanding each criterion for readability.

### Debug Tab (Administrators Only)
- **System Diagnostics**: View system health, database status, and service connectivity.
- **API Testing**: Test backend endpoints and view request/response data.
- **Configuration Validation**: Verify YAML configuration files and settings.
- **Performance Monitoring**: Monitor response times and system metrics.
- **Development Tools**: Access debugging utilities and development aids.

## 6.0 Session Management
- Session identifier displayed in Text Input tab.
- Session persists for configured duration on backend; refresh or create new session from Admin tab.
- Use the **Reset Session** button in Admin tab to clear history and begin a new submission cycle.
- **Session Expiration**: Automatic logout occurs when sessions expire, requiring re-authentication.

## 7.0 Limitations
- LLM evaluation may run in mock mode if `LLM_API_KEY` is not set; results then are simulated.
- Evaluation retrieval endpoint `/api/v1/evaluations/{id}` currently returns placeholder data.
- Export/import of sessions is planned but not yet implemented.
- The interface expects plain text; rich formatting is stripped before evaluation.
- **Authentication Required**: All application functions require valid user authentication.
- **Role-Based Access**: Some features are restricted based on user role (regular user vs administrator).

## 8.0 References
- `frontend/app.py`
- `frontend/components/state_manager.py`
- `frontend/components/api_client.py`
