# 07_Deployment.md

## 1.0 How to Use This File

1.1 **Audience**
- AI coding agents and human developers.

1.2 **Purpose**
- Defines the deployment strategy, infrastructure requirements, and operational procedures for the Memo AI Coach project.
- Builds on the architecture and ensures the system can be deployed and scaled effectively.

1.3 **Next Steps**
- Review this file before proceeding to `08_Maintenance.md`.

---

## 2.0 Key High-Level Decisions Needed

### 2.1 Container Strategy and Docker Architecture
**Question**: How should we structure the Docker containers for optimal deployment?
- Single container vs multi-container (frontend/backend separation)?
- How do we handle the SQLite database in containerized environments?
- What's the strategy for YAML configuration files in containers?
- Should we use Docker Compose for development vs production?

### 2.2 Authentication and Security Configuration
**DECISION**: Environment-based authentication configuration with secure secrets management
- **MVP Mode**: Authentication disabled by default, session-only isolation
- **Production Mode**: JWT + Session hybrid with configurable toggle
- **Secrets Management**: Environment variables for JWT secrets, bcrypt salt rounds
- **Configuration**: Authentication settings in `auth.yaml` with environment overrides
- **Security**: HTTPS enforcement, secure cookie settings, CSRF protection

### 2.3 Environment Configuration Management
**Question**: How should we manage different environments (dev/staging/production)?
- Environment variables vs configuration files vs both?
- How do we handle sensitive data (LLM API keys, database paths)?
- What's the strategy for environment-specific YAML configurations?

### 2.4 Database Deployment and Persistence
**Question**: How should we handle SQLite database persistence in production?
- Docker volumes vs external storage vs database migration to PostgreSQL?
- Backup and recovery strategies in containerized environments?
- How do we handle database migrations during deployments?
- What's the scaling path from SQLite to PostgreSQL?

### 2.5 LLM Provider Integration and API Management
**Question**: How should we manage LLM provider credentials and configurations?
- API key management and rotation strategies?
- How do we handle different LLM providers in different environments?
- Rate limiting and cost management for LLM API calls?
- Fallback strategies for LLM provider outages?

### 2.6 Scaling and Load Balancing
**Question**: How should we prepare for scaling from 1 to 100+ users?
- Horizontal scaling strategies for stateless applications?
- How do we handle session persistence across multiple instances?
- Load balancing requirements and strategies?
- Database scaling considerations (connection pooling, read replicas)?

### 2.7 Monitoring and Observability
**Question**: What monitoring should we implement for production operations?
- Application health checks and readiness probes?
- Performance monitoring for LLM response times?
- Error tracking and alerting strategies?
- Log aggregation and analysis requirements?

### 2.7 Security and Network Configuration
**Question**: How should we secure the production deployment?
- HTTPS/TLS configuration and certificate management?
- Network security and firewall configurations?
- Authentication system security when enabled?
- Input sanitization and rate limiting at the infrastructure level?

### 2.8 Deployment Automation and CI/CD
**Question**: How should we automate the deployment process?
- Continuous deployment vs manual releases?
- Blue-green deployments vs rolling updates vs recreate strategy?
- Automated testing requirements before deployment?
- Rollback strategies for failed deployments?

### 2.9 File Storage and Static Assets
**Question**: How should we handle file storage for PDFs and configurations?
- Local file storage vs cloud storage (S3, etc.)?
- Temporary file cleanup strategies?
- Static asset serving (CSS, JS, images)?
- YAML configuration file storage and versioning?

### 2.10 Backup and Disaster Recovery
**Question**: What backup and recovery procedures should we implement?
- Database backup frequency and retention policies?
- Configuration file backup strategies?
- Full system backup and recovery procedures?
- Testing backup restoration processes?

---

## 3.0 Placeholder Sections

### 3.1 Infrastructure Requirements
- (Pending) Server resource requirements (CPU, RAM, storage)
- (Pending) Network requirements and bandwidth
- (Pending) External service dependencies

### 3.2 Docker Configuration
- (Pending) Dockerfile specifications
- (Pending) Docker Compose configurations
- (Pending) Container orchestration strategies

### 3.3 Authentication and Security Configuration

#### 3.3.1 Environment Variables
```yaml
# Authentication Configuration
AUTH_ENABLED=false  # Toggle for MVP vs Production
JWT_SECRET_KEY=${JWT_SECRET_KEY}  # Required in production
JWT_EXPIRATION_HOURS=24
SESSION_TIMEOUT=3600  # seconds
BCRYPT_ROUNDS=12

# Database Configuration
DATABASE_URL=sqlite:///data/memoai.db
DATABASE_BACKUP_ENABLED=true

# Security Settings
HTTPS_ONLY=true  # Production only
SECURE_COOKIES=true  # Production only
CSRF_PROTECTION=true
RATE_LIMIT_PER_MINUTE=60

# LLM Provider
LLM_PROVIDER=claude
CLAUDE_API_KEY=${CLAUDE_API_KEY}
```

#### 3.3.2 Docker Compose Configuration
```yaml
# docker-compose.yml for MVP Mode
version: '3.8'
services:
  memoai:
    build: .
    ports:
      - "8080:8080"
    environment:
      - AUTH_ENABLED=false
      - SESSION_TIMEOUT=3600
      - DATABASE_URL=sqlite:///data/memoai.db
    volumes:
      - ./data:/app/data
      - ./config:/app/config
      
# docker-compose.prod.yml for Production Mode  
version: '3.8'
services:
  memoai:
    build: .
    ports:
      - "443:8080"
    environment:
      - AUTH_ENABLED=true
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - HTTPS_ONLY=true
      - SECURE_COOKIES=true
    volumes:
      - memoai_data:/app/data
      - memoai_config:/app/config
    secrets:
      - jwt_secret
      - claude_api_key
      
volumes:
  memoai_data:
  memoai_config:
  
secrets:
  jwt_secret:
    external: true
  claude_api_key:
    external: true
```

#### 3.3.3 Authentication Configuration Files
```yaml
# config/auth.yaml
authentication:
  enabled: ${AUTH_ENABLED:-false}
  mode: "jwt_session"  # jwt_session | session_only
  jwt:
    secret_key: ${JWT_SECRET_KEY}
    algorithm: "HS256"
    expiration_hours: ${JWT_EXPIRATION_HOURS:-24}
  session:
    timeout: ${SESSION_TIMEOUT:-3600}
    secure_cookies: ${SECURE_COOKIES:-false}
    csrf_protection: ${CSRF_PROTECTION:-true}
  security:
    bcrypt_rounds: ${BCRYPT_ROUNDS:-12}
    max_login_attempts: 5
    lockout_duration: 900
    rate_limit_per_minute: ${RATE_LIMIT_PER_MINUTE:-60}
```

### 3.4 Environment Management
- (Pending) Additional environment variable specifications
- (Pending) Configuration file management beyond authentication
- (Pending) Secret rotation strategies

### 3.5 Deployment Procedures
- (Pending) Step-by-step deployment instructions
- (Pending) Database migration procedures
- (Pending) Configuration update procedures

### 3.6 Scaling Strategies
- (Pending) Horizontal scaling procedures
- (Pending) Database scaling migration plans
- (Pending) Performance optimization guidelines

---

## 4.0 Traceability Links

- **Source of Truth**: `02_Architecture.md`, `03_Data_Model.md`
- **Mapped Requirements**: 
  - Scalability (3.2)
  - Reliability (3.3)
  - Performance (3.1)
  - Docker deployment (Overview 3.2)
  - MVP to production scaling path
