# Authentication Specifications
## Memo AI Coach

**Document ID**: 02b_Authentication_Specifications.md
**Document Version**: 1.0
**Last Updated**: Implementation Phase
**Status**: Active

---

## 1.0 Overview

### 1.1 Purpose
The Memo AI Coach authentication system provides secure, role-based access control for all application functions. This document specifies the complete authentication flow, security requirements, and implementation guidelines.

### 1.2 Key Principles
- **Universal Authentication**: All users must authenticate before accessing any application functions
- **Role-Based Access**: Clear distinction between regular users and administrators
- **Session-Based**: Stateless session tokens for scalable authentication
- **Defense in Depth**: Multiple security layers with prioritized protection levels

### 1.3 User Types
| User Type | Description | Permissions |
|-----------|-------------|-------------|
| **Regular User** | Writers seeking memo feedback | Submit evaluations, view results |
| **Administrator** | System managers | All user permissions + configuration, user management, debug access |

---

## 2.0 Authentication Flow

### 2.1 Complete Auth Sequence Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Login    │    │   Validation    │    │   Session       │
│                 │    │                 │    │   Creation      │
│ 1. Enter creds  │───▶│ 2. Check brute  │───▶│ 3. Generate     │
│    (username/   │    │    force        │    │    token        │
│     password)   │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Token         │    │   Request       │    │   Validation    │
│   Storage       │    │   Processing    │    │   & Access      │
│                 │    │                 │    │                 │
│ 4. Store in     │◀───│ 5. Include      │───▶│ 6. Check token  │
│    memory       │    │    X-Session-   │    │    validity     │
│                 │    │    Token header │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2.2 Login Process

#### API Endpoint: `POST /api/v1/auth/login`
```json
{
  "username": "admin",
  "password": "secret"
}
```

#### Success Response:
```json
{
  "data": {
    "session_token": "aB3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW3xY5zA2bC4dE6fG8hI0jK2lM4nO6pQ8rS0tU2vW4xY6z",
    "username": "admin",
    "is_admin": true,
    "user_id": 1
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "placeholder"
  },
  "errors": []
}
```

### 2.3 Session Validation Flow

```
Request → Extract X-Session-Token → Validate in DB → Check Expiration → Verify User Active → Grant/deny access
```

### 2.4 Logout Process

#### API Endpoint: `POST /api/v1/auth/logout`
- Requires `X-Session-Token` header
- Marks session as inactive in database
- Clears client-side token storage

---

## 3.0 Security Architecture

### 3.1 Security Priority Levels

#### 🔴 **Critical** (Must Implement)
- Session token validation on all requests
- Password hashing with bcrypt
- Secure token generation
- User account status validation

#### 🟡 **Important** (Strongly Recommended)
- Brute force protection (3 attempts/5min window)
- Rate limiting (20 req/hr per session, 100 req/hr admin)
- Input validation and sanitization
- Session expiration (1 hour default)

#### 🟢 **Recommended** (Enhance Security)
- Audit logging for all auth events
- CSRF protection
- Secure cookie settings (HttpOnly, SameSite)
- Session activity monitoring

#### 🔵 **Optional** (Advanced Security)
- Advanced threat detection
- Session hijacking prevention
- Encryption key rotation
- Comprehensive audit trails

### 3.2 Threat Mitigation

| Threat | Mitigation | Priority |
|--------|------------|----------|
| Brute Force | Attempt tracking + temporary lockout | Critical |
| Session Hijacking | Secure token generation + expiration | Critical |
| Unauthorized Access | Role-based permissions | Critical |
| DoS Attacks | Rate limiting + request throttling | Important |
| Credential Stuffing | Account lockout + complexity requirements | Important |

---

## 4.0 Configuration Management

### 4.1 Configuration Presets

#### Development Preset
```yaml
preset: development
session_timeout: 7200  # 2 hours
rate_limiting: false
brute_force_protection: true
audit_logging: basic
debug_mode: true
```

#### Production Preset
```yaml
preset: production
session_timeout: 3600  # 1 hour
rate_limiting: true
brute_force_protection: true
audit_logging: comprehensive
debug_mode: false
csrf_protection: true
```

#### Enterprise Preset
```yaml
preset: enterprise
session_timeout: 1800  # 30 minutes
rate_limiting: true
brute_force_protection: true
audit_logging: comprehensive
session_monitoring: true
threat_detection: true
encryption_key_rotation: true
```

### 4.2 Core Configuration Options

#### Session Management
```yaml
session_management:
  session_timeout: 3600          # Seconds
  max_sessions_per_user: 5       # Concurrent sessions
  session_token_length: 32       # Token length
  cleanup_interval: 300          # Cleanup frequency
```

#### Authentication Security
```yaml
authentication_methods:
  brute_force_threshold: 3        # Max failed attempts
  brute_force_window: 300         # Time window (seconds)
  max_login_attempts: 5           # Lockout threshold
  lockout_duration: 900           # Lockout time (seconds)
```

#### Password Policy
```yaml
password_policy:
  min_length: 8
  require_uppercase: true
  require_lowercase: true
  require_digits: true
  require_special_chars: true
  prevent_common_passwords: true
```

---

## 5.0 API Integration

### 5.1 Authentication Headers
```http
X-Session-Token: aB3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW3xY5zA2bC4dE6fG8hI0jK2lM4nO6pQ8rS0tU2vW4xY6z
```

### 5.2 Protected Endpoints

#### Authentication Endpoints
- `POST /api/v1/auth/login` - Unified login for all users (admins and regular users)
- `POST /api/v1/auth/logout` - Unified logout for all users
- `GET /api/v1/auth/validate` - Validate session token and get user info

#### Admin Endpoints (Require `is_admin: true`)
- `GET /api/v1/admin/config/{name}` - Read configuration
- `PUT /api/v1/admin/config/{name}` - Update configuration
- `POST /api/v1/admin/users/create` - Create new user account
- `GET /api/v1/admin/users` - List all users
- `DELETE /api/v1/admin/users/{username}` - Delete user account

#### Regular User Endpoints (Require valid session)
- `POST /api/v1/evaluations/submit` - Submit evaluation
- `GET /api/v1/evaluations/{id}` - Get evaluation result
- `GET /api/v1/sessions/{id}` - Get session info

### 5.3 Error Responses

#### Standard Error Format:
```json
{
  "data": null,
  "meta": {"timestamp": "...", "request_id": "..."},
  "errors": [
    {
      "code": "AUTH_INVALID_CREDENTIALS",
      "message": "Invalid username or password"
    }
  ]
}
```

#### Common Error Codes:
- `AUTH_INVALID_CREDENTIALS` - Wrong username/password
- `AUTH_ACCOUNT_LOCKED` - Brute force protection activated
- `AUTH_SESSION_EXPIRED` - Session timeout reached
- `AUTH_INSUFFICIENT_PERMISSIONS` - Role access denied
- `AUTH_INVALID_TOKEN` - Malformed or missing token

---

## 6.0 Error Handling & Troubleshooting

### 6.1 Common Issues

#### Session Expiration
**Symptom**: "Session has expired. Please log in again"
**Cause**: Session timeout reached (default: 1 hour)
**Solution**: User must re-authenticate

#### Brute Force Lockout
**Symptom**: "Account temporarily locked due to multiple failed attempts"
**Cause**: 3+ failed login attempts within 5 minutes
**Solution**: Wait for lockout duration (15 minutes) or contact admin

#### Invalid Token
**Symptom**: "Invalid session token"
**Cause**: Token corrupted, session deleted, or user deactivated
**Solution**: Re-authenticate to get new token

#### Permission Denied
**Symptom**: "Insufficient permissions for this action"
**Cause**: Regular user attempting admin function
**Solution**: Use admin account or contact administrator

### 6.2 Recovery Procedures

#### Emergency Admin Access
1. Access unified login endpoint: `POST /api/v1/auth/login`
2. Use emergency admin credentials from `.env`
3. Reset affected user sessions
4. Review audit logs for security events

#### Session Cleanup
```sql
-- Manual cleanup if needed
DELETE FROM sessions WHERE expires_at < datetime('now');
UPDATE sessions SET is_active = 0 WHERE user_id = ?;
```

---

## 7.0 Performance Specifications

### 7.1 Response Time Targets
- **Authentication**: <500ms response time
- **Session Validation**: <100ms per request
- **Token Generation**: <50ms
- **Logout**: <200ms

### 7.2 Scalability Requirements
- **Concurrent Users**: Support 100+ active users
- **Active Sessions**: Handle 500+ concurrent sessions
- **Memory Usage**: <50MB per 100 active sessions
- **Database Load**: Minimal impact on evaluation performance

### 7.3 Monitoring Metrics
- Authentication success/failure rates
- Session creation/validation frequency
- Brute force attempt patterns
- Response time percentiles
- Active session counts

---

## 8.0 Implementation Guidelines

### 8.1 Backend Implementation
- Use `auth_service.py` for all authentication logic
- Implement middleware for automatic session validation
- Store sessions in database with proper indexing
- Use bcrypt for password hashing (12 rounds minimum)

### 8.2 Frontend Implementation (Vue.js)
- Use Pinia store (`stores/auth.js`) for authentication state management
- Store tokens in memory only (never localStorage/cookies) per security requirements
- Use Axios interceptors in `services/api.js` for automatic `X-Session-Token` headers
- Implement Vue Router guards for route-based access control
- Handle token expiration gracefully with automatic logout and re-auth prompts
- Clear tokens from memory on logout or session errors

### 8.3 Database Schema
```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions table
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    user_id INTEGER,
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 9.0 Security Testing

### 9.1 Required Tests
- [ ] Brute force protection validation
- [ ] Session expiration enforcement
- [ ] Role-based access control
- [ ] Token integrity validation
- [ ] Password policy compliance
- [ ] Rate limiting effectiveness

### 9.2 Penetration Testing Checklist
- [ ] SQL injection attempts on auth endpoints
- [ ] Session fixation attacks
- [ ] Token replay attacks
- [ ] Privilege escalation attempts
- [ ] DoS attack resilience

---

## 10.0 References
- `devlog/vue_frontend_implementation_plan.md` - Vue.js frontend implementation plan
- `backend/services/auth_service.py` - Authentication service implementation
- `config/auth.yaml` - Authentication configuration
- `backend/main.py` - API endpoint implementations
- `vue-frontend/services/api.js` - Vue.js API client with authentication
- `vue-frontend/stores/auth.js` - Vue.js authentication state management

---

**Document ID**: 02b_Authentication_Specifications.md
**Version**: 1.0
**Last Updated**: Implementation Phase
**Status**: Active
