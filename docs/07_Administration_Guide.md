# Administration Guide
## Memo AI Coach

**Document ID**: 07_Administration_Guide.md
**Document Version**: 1.0
**Last Updated**: Phase 9
**Status**: Draft

---

## 1.0 Admin Authentication
- Navigate to **Admin** tab.
- Enter credentials defined in `auth.yaml` or `.env` (default `admin`).
- On success, backend returns a `session_token` used in `X-Session-Token` header for subsequent admin requests.
- Logout invalidates the token.
Steps in detail:
1. Open the **Admin** tab and locate the login form.
2. Provide username and password then press **Login**.
3. The frontend stores the returned `session_token` in memory only; it is never written to disk.
4. Upon expiration the interface will prompt for re-authentication.

## 2.0 Admin Dashboard
The Admin tab provides:
- **Health Monitoring**: calls `/health` endpoint and displays service statuses including database, configuration, auth and LLM.
- **Configuration Management**: select `rubric`, `prompt`, `llm`, or `auth`, load current content, edit YAML, save or reload.
- **Session Management**: view current session ID, create or refresh sessions.
- **Logout**: revoke admin session.
Each configuration update triggers:
1. YAML syntax validation.
2. Atomic write of new file with backup stored under `config/backups/`.
3. In-memory reload so changes take effect immediately without container restart.

## 3.0 Security Notes
- All configuration files are backed up before overwrite (`config_manager.py`).
- Brute force protection and session rotation are enforced by `auth_service.py` and `auth.yaml` settings.
- Admin tokens expire and are auto-extended when nearing expiration.
- Use strong, unique passwords and rotate regularly via configuration updates.
- Access to the Admin tab should be restricted through network controls in production.
- Review audit logs periodically for unauthorized access attempts.

## 4.0 Audit Logging
`auth.yaml` enables audit logging for events like login, logout and configuration changes. Logs are written to `logs/` within host and mounted into containers. Each log entry includes timestamp, username, action and outcome.

## 5.0 References
- `backend/services/auth_service.py`
- `backend/services/config_manager.py`
- `frontend/app.py` (Admin tab)
