# Administration Guide
## Memo AI Coach

**Document ID**: 07_Administration_Guide.md
**Document Version**: 1.2
**Last Updated**: Phase 9
**Status**: Draft

---

## 1.0 Authentication System
### 1.1 User Categories
The system implements a two-tier authentication system:

- **Regular Users**: Can submit memos for evaluation, view feedback, and access basic application functions.
- **Administrators**: Have all regular user privileges plus access to configuration management, system monitoring, debug tools, user management, and administrative functions.

### 1.2 Authentication Process
- **Homepage Login**: All users must authenticate through the centralized login page before accessing any application functions.
- **Credential Validation**: Username and password are validated against system configuration in `auth.yaml` or `.env`.
- **Session Creation**: Upon successful authentication, backend returns a `session_token` used in `X-Session-Token` header for subsequent requests.
- **Role Assignment**: User role (regular user or administrator) is determined during authentication and enforced throughout the session.
- **Session Management**: Tokens expire according to `auth.yaml` configuration with automatic logout and re-authentication prompts.

### 1.3 Admin Authentication Details
Steps for administrator access:
1. Open the application and navigate to the homepage login interface.
2. Provide administrator username and password then press **Login**.
3. The frontend stores the returned `session_token` in memory only; it is never written to disk.
4. Upon successful authentication, administrators gain access to all application tabs including Admin and Debug.
5. Upon expiration the interface will prompt for re-authentication.

---

## 2.0 Admin Dashboard
The Admin tab provides (administrators only):
- **Health Monitoring**: calls `/health` endpoint and displays service statuses including database, configuration, auth and LLM.
- **Configuration Management**: select `rubric`, `prompt`, `llm`, or `auth`, load current content, edit YAML, save or reload.
- **User Management**: add, edit, delete, and manage user accounts and roles.
- **Session Management**: view current session ID, create or refresh sessions.
- **Logout**: revoke admin session.

Each configuration update triggers:
1. YAML syntax validation.
2. Atomic write of new file with backup stored under `config/backups/`.
3. In-memory reload so changes take effect immediately without container restart.

## 3.0 Debug Tab
The Debug tab provides system diagnostics and development tools (administrators only):
- **System Diagnostics**: View system health, database status, and service connectivity.
- **API Testing**: Test backend endpoints and view request/response data.
- **Configuration Validation**: Verify YAML configuration files and settings.
- **Performance Monitoring**: Monitor response times and system metrics.
- **Development Tools**: Access debugging utilities and development aids.

## 4.0 Security Notes
- All configuration files are backed up before overwrite (`config_manager.py`).
- Brute force protection and session rotation are enforced by `auth_service.py` and `auth.yaml` settings.
- Admin tokens expire and are auto-extended when nearing expiration.
- Use strong, unique passwords and rotate regularly via configuration updates.
- Access to the Admin and Debug tabs should be restricted through network controls in production.
- Review audit logs periodically for unauthorized access attempts.
- **Universal Authentication**: All application functions require valid user authentication.
- **Role-Based Access**: Regular users cannot access administrative functions, debug tools, or user management.

## 5.0 Audit Logging
`auth.yaml` enables audit logging for events like login, logout, user management, and configuration changes. Logs are written to `logs/` within host and mounted into containers. Each log entry includes timestamp, username, role, action and outcome.

## 6.0 User Management
### 6.1 Adding Users
- **User Creation**: Administrators can create new user accounts through the Admin dashboard.
- **Role Assignment**: New users can be assigned as regular users or administrators during creation.
- **Credential Setup**: Username, password, and role are configured during user creation.
- **Validation**: System validates unique usernames and secure password requirements.

### 6.2 Editing Users
- **Profile Updates**: Administrators can modify existing user profiles including username, password, and role.
- **Role Changes**: User roles can be upgraded from regular user to administrator or downgraded as needed.
- **Password Management**: Administrators can reset user passwords and enforce password policies.
- **Account Status**: Enable or disable user accounts without deletion.

### 6.3 Deleting Users
- **Account Removal**: Administrators can permanently delete user accounts from the system.
- **Data Cleanup**: Associated sessions and submissions are cleaned up during user deletion.
- **Confirmation**: System requires confirmation before permanent user deletion.
- **Audit Trail**: All user management actions are logged for security and compliance.

### 6.4 User List and Search
- **User Directory**: View all registered users with their roles and account status.
- **Search and Filter**: Find users by username, role, or account status.
- **Bulk Operations**: Perform bulk actions on multiple users (enable, disable, role changes).
- **User Statistics**: View user activity metrics and session information.

### 6.5 Role Management
- **Role Assignment**: User roles are assigned during authentication based on credentials.
- **Permission Enforcement**: Role permissions are enforced at both frontend and backend levels.
- **Regular Users**: Cannot access administrative functions, debug tools, or user management.
- **Administrators**: Have full access to all application features including user management.

## 7.0 References
- `backend/services/auth_service.py`
- `backend/services/config_manager.py`
- `frontend/app.py` (Admin and Debug tabs)
