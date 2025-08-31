# Administration Guide
## Memo AI Coach

**Document ID**: 07_Administration_Guide.md
**Document Version**: 1.2
**Last Updated**: Phase 9
**Status**: Draft

---

## 1.0 Access Requirements
Administrators must authenticate with valid admin credentials to access administrative functions. The system supports two user categories:

- **Regular Users**: Basic application access for memo evaluation
- **Administrators**: Full system access including configuration validation and user administration

See `docs/02b_Authentication_Specifications.md` for complete authentication details and security requirements.

---

## 2.0 Admin Dashboard
The Admin page provides (administrators only):
- **Health Monitoring**: calls `/health` endpoint and displays service statuses including database, configuration, auth and LLM.
- **Configuration Validation**: verify YAML configuration files and settings.
- **User Management**: add, edit, delete, and manage user accounts and roles.
- **Session Management**: view current session ID, create or refresh sessions.
- **Logout**: revoke admin session.

## 3.0 Debug Page
The Debug page provides system diagnostics and development tools (administrators only):
- **System Diagnostics**: View system health, database status, and service connectivity.
- **API Testing**: Test backend endpoints and view request/response data.

- **Performance Monitoring**: Monitor response times and system metrics.
- **Development Tools**: Access debugging utilities and development aids.

## 4.0 Security Notes
- All configuration changes are backed up automatically before modification.
- Use strong passwords and rotate them regularly through the admin interface.
- Restrict access to administrative functions through network controls in production.
- Review system logs periodically for security monitoring.
- Role-based access controls prevent unauthorized administrative access.

## 5.0 Audit Logging
The system maintains comprehensive audit logs for administrative actions and security events. Logs are stored in the `logs/` directory and include timestamps, user information, and action details. See `docs/02b_Authentication_Specifications.md` for audit logging configuration.

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
User roles determine access levels throughout the application. Role assignments and permissions are managed through the admin interface and enforced at both frontend and backend levels. See `docs/02b_Authentication_Specifications.md` for complete role management details.

## 7.0 References
- `docs/02b_Authentication_Specifications.md` - Complete authentication and role management details
- `devlog/vue_frontend_implementation_plan.md` - Vue.js frontend implementation plan
- `backend/services/auth_service.py`
- `backend/services/config_manager.py`
- `vue-frontend/views/Admin.vue` - Vue.js admin interface
- `vue-frontend/views/Debug.vue` - Vue.js debug interface
