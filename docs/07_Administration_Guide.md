# Administration Guide
## Memo AI Coach

**Document ID**: 07_Administration_Guide.md
**Document Version**: 2.0
**Last Updated**: Phase 11 - LLM Refactor & Health Security Implementation
**Status**: Active

---

## 1.0 Access Requirements
Administrators must authenticate with valid admin credentials to access administrative functions. The system supports two user categories:

- **Regular Users**: Basic application access for memo evaluation
- **Administrators**: Full system access including configuration validation and user administration

See `docs/02b_Authentication_Specifications.md` for complete authentication details and security requirements.

---

## 2.0 Admin Dashboard
The Admin page provides (administrators only):
- **Health Monitoring**: calls `/health/detailed` endpoint (admin-only) and displays comprehensive service statuses including database, configuration, auth and LLM with detailed metrics.
- **Configuration Validation**: verify YAML configuration files and settings.
- **User Management**: add, edit, delete, and manage user accounts and roles.
- **Session Management**: view current session ID, create or refresh sessions.
- **Logout**: revoke admin session.

### 2.1 Admin Components
The Admin dashboard consists of the following components:

#### HealthStatus Component
- **System Health Overview**: Displays overall system status from `/health/detailed` endpoint (admin-only)
- **Service Status**: Shows individual service health (API, Database, Config, LLM, Auth) with detailed metrics
- **Database Details**: Connection status, table count, journal mode, user count, and performance metrics
- **Real-time Updates**: Automatic refresh of health status with fallback to basic `/health` if detailed access fails
- **Error Display**: Shows detailed error information for unhealthy services
- **Security**: Only accessible to authenticated admin users

#### ConfigValidator Component
- **Configuration File Management**: View and edit the YAML configuration files
- **File Selection**: Dropdown to select prompt.yaml, llm.yaml, or auth.yaml (rubric is embedded in prompt.yaml)
- **Content Display**: Syntax-highlighted YAML content display
- **Edit Mode**: Inline editing with validation
- **Backup Creation**: Automatic timestamped backups before changes
- **Validation**: YAML syntax validation and error reporting
- **Save/Cancel**: Save changes or cancel without modification

#### UserManagement Component
- **User Creation**: Create new user accounts with username, password, and role assignment
- **User Directory**: Display all registered users with roles and account status
- **User Actions**: Delete users with confirmation
- **Role Management**: Assign admin or regular user privileges
- **Account Status**: View active/inactive status for all users
- **Bulk Operations**: Refresh user list and perform bulk actions

#### SessionManagement Component
- **Current Session**: Display current session ID and user information
- **Session Creation**: Create new authenticated sessions
- **Session Refresh**: Refresh existing sessions to extend validity
- **Session Reset**: Clear current session and start fresh
- **Session Status**: Show session expiration and validity status

## 3.0 Debug Page
The Debug page provides system diagnostics and development tools (administrators only):
- **System Diagnostics**: View system health, database status, and service connectivity.
- **API Testing**: Test backend endpoints and view request/response data.
- **Performance Monitoring**: Monitor response times and system metrics.
- **Development Tools**: Access debugging utilities and development aids.

### 3.1 Debug Components
The Debug page consists of the following components:

#### SystemDiagnostics Component
- **System Overview**: Display uptime, version, environment, and debug mode status
- **Database Status**: Connection status, table count, database size, last backup
- **Service Connectivity**: Test and display status of all backend services
- **Error Log**: Display recent system errors with timestamps
- **Manual Diagnostics**: Run system diagnostics on demand
- **Real-time Monitoring**: Continuous monitoring of system health

#### ApiHealthTesting Component
- **Comprehensive Endpoint Testing**: Test all 12 API endpoints including health, auth, config, and evaluation
- **Real-time Status Monitoring**: Shows healthy, error, or testing status for each endpoint
- **Response Time Tracking**: Displays response times for performance monitoring
- **Error Details**: Shows specific error messages for failed endpoints with debug information
- **Health Summary**: Provides overview of system health with counts and status
- **Manual Testing**: "Test All Endpoints" button for on-demand testing
- **Auto-testing**: Automatically runs tests when component loads
- **Tooltip Functionality**: Hover tooltips show full response/error details
- **Clipboard Integration**: Click error messages to copy debug information
- **Response Preview**: Shows truncated response data with full view on hover
- **Evaluation Testing**: Manual LLM evaluation testing with sample memo text

**API Endpoints Tested**:
- **Health Endpoints**: System, Database, Config, LLM, Auth health checks
- **Authentication**: Session validation
- **Admin Functions**: User management
- **Configuration**: All 4 config files (rubric, prompt, auth, llm)
- **Evaluation**: Text submission endpoint (manual testing with sample memo)

#### PerformanceMonitoring Component
- **Performance Metrics**: Average response time, total requests, success rate, error rate
- **Response Time Chart**: Visual chart showing response time history
- **Endpoint Performance**: Individual endpoint performance metrics
- **System Resources**: Memory usage, CPU usage with visual progress bars
- **Real-time Updates**: Continuous monitoring of performance metrics
- **Historical Data**: Track performance trends over time

#### DevelopmentTools Component
- **Environment Information**: Display current environment variables and settings
- **API Client Testing**: Test API endpoints with custom requests
- **Session Management**: View and manage authentication sessions
- **Configuration Testing**: Test configuration loading and validation
- **Error Simulation**: Simulate various error conditions for testing
- **Debug Utilities**: Various debugging and development utilities

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
