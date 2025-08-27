# User Guide
## Memo AI Coach

**Document ID**: 06_User_Guide.md
**Document Version**: 1.0
**Last Updated**: Phase 9
**Status**: Draft

---

## 1.0 Accessing the Application
- Run locally: `streamlit run frontend/app.py` (backend must be running on port 8000).
- Production: open `https://<domain>` served via Traefik with automatic HTTPS.
- Browser support: recent versions of Chrome, Firefox or Edge.

## 2.0 Interface Overview
The frontend (`frontend/app.py`) provides five tabs:
1. **Text Input** – submit content for evaluation.
2. **Overall Feedback** – displays overall score, strengths and opportunities.
3. **Detailed Feedback** – shows rubric scores and segment-level comments.
4. **Help** – usage tips and session export/import (when implemented).
5. **Admin** – login and administrative tools (visible to all but functions require authentication).

Tooltips on each input explain expected format. Navigation buttons at the top allow switching between tabs without losing session state.

## 3.0 Submitting Text
1. Open the **Text Input** tab.
2. Paste or type memo text (maximum 10,000 characters).
3. Click **Submit for Evaluation**.
4. The application creates a session if one does not exist and sends the text to backend.
5. A progress spinner appears while waiting for the LLM response (target <15s).
6. Results populate the **Overall Feedback** and **Detailed Feedback** tabs.

## 4.0 Viewing Results
### Overall Feedback Tab
- Shows aggregate score and key metrics.
- Displays strengths and improvement opportunities.
- Provides elapsed processing time and timestamp for auditing.

### Detailed Feedback Tab
- Presents rubric criteria with individual scores and justifications.
- Lists segment feedback objects containing comments, questions and suggestions.
- Allows collapsing or expanding each criterion for readability.

## 5.0 Session Management
- Session identifier displayed in Text Input tab.
- Session persists for 24 hours on backend; refresh or create new session from Admin tab.
- Use the **Reset Session** button in Admin tab to clear history and begin a new submission cycle.

## 6.0 Limitations
- LLM evaluation may run in mock mode if `LLM_API_KEY` is not set; results then are simulated.
- Evaluation retrieval endpoint `/api/v1/evaluations/{id}` currently returns placeholder data.
- Export/import of sessions is planned but not yet implemented.
- The interface expects plain text; rich formatting is stripped before evaluation.

## 7.0 References
- `frontend/app.py`
- `frontend/components/state_manager.py`
- `frontend/components/api_client.py`
