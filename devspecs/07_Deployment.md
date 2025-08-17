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

## 2.0 Container Strategy and Docker Architecture

### 2.1 Container Architecture Decision ✅ **DECIDED**
**Decision**: **Multi-container Docker Compose** architecture
**Rationale**: 
- Separation of concerns (frontend/backend)
- Independent scaling of components
- Shared volumes for data persistence
- Development and production parity

### 2.2 Docker Configuration Strategy ✅ **DECIDED**
**Decision**: **Environment-specific Docker Compose files**
**Implementation**:
- `docker-compose.yml` for development/MVP
- `docker-compose.prod.yml` for production
- Shared base configuration with environment overrides
- Volume management for data persistence

---

## 3.0 Key High-Level Decisions Needed

### 3.1 Environment Configuration Management
**Question**: How should we manage different environments (dev/staging/production)?
- **Options**: Environment variables vs configuration files vs both
- **Consideration**: Sensitive data handling (LLM API keys, database paths)
- **Impact**: Security, maintainability, and deployment flexibility

### 3.2 Database Deployment and Persistence
**Question**: How should we handle SQLite database persistence in production?
- **Options**: Docker volumes vs external storage vs migration to PostgreSQL
- **Consideration**: Backup strategies, scaling path from SQLite to PostgreSQL
- **Impact**: Data durability, performance, and operational complexity

### 3.3 LLM Provider Integration and API Management
**Question**: How should we manage LLM provider credentials and configurations?
- **Options**: Environment variables vs secrets management vs external config
- **Consideration**: API key rotation, rate limiting, cost management
- **Impact**: Security, reliability, and operational overhead

### 3.4 Scaling and Load Balancing
**Question**: How should we prepare for scaling from 1 to 100+ users?
- **Options**: Horizontal scaling vs vertical scaling vs hybrid approach
- **Consideration**: Session persistence, load balancing, database scaling
- **Impact**: Performance, cost, and operational complexity

### 3.5 Monitoring and Observability
**Question**: What monitoring should we implement for production operations?
- **Options**: Application monitoring vs infrastructure monitoring vs both
- **Consideration**: Health checks, performance metrics, error tracking
- **Impact**: Operational visibility and incident response

### 3.6 Security and Network Configuration
**Question**: How should we secure the production deployment?
- **Options**: HTTPS/TLS configuration, network security, authentication
- **Consideration**: Certificate management, firewall rules, input sanitization
- **Impact**: Security posture and compliance requirements

### 3.7 Deployment Automation and CI/CD
**Question**: How should we automate the deployment process?
- **Options**: Continuous deployment vs manual releases vs hybrid
- **Consideration**: Blue-green deployments, rollback strategies, testing
- **Impact**: Deployment frequency, reliability, and operational overhead

---

## 4.0 Infrastructure Requirements

### 4.1 Server Resource Requirements (Based on Req 3.2)
```yaml
ResourceRequirements:
  mvp_deployment:
    cpu: "1-2 cores"
    memory: "2-4 GB RAM"
    storage: "20 GB SSD"
    network: "100 Mbps"
  
  production_deployment:
    cpu: "4-8 cores"
    memory: "8-16 GB RAM"
    storage: "100 GB SSD"
    network: "1 Gbps"
  
  scaling_requirements:
    concurrent_users: "100+ users"
    database_connections: "50+ concurrent"
    llm_api_calls: "100+ requests/minute"
    file_storage: "10 GB for PDFs and logs"
```

### 4.2 Network Requirements
```yaml
NetworkRequirements:
  external_connections:
    - LLM provider APIs (Anthropic Claude)
    - HTTPS for user access
    - DNS resolution
  
  internal_networking:
    - Container-to-container communication
    - Database access
    - File system access
  
  security_requirements:
    - HTTPS/TLS encryption
    - Firewall rules
    - Rate limiting
    - DDoS protection
```

---

## 5.0 Docker Configuration

### 5.1 Development Environment (MVP Mode)
```yaml
# docker-compose.yml
version: '3.8'
services:
  memoai-backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - AUTH_ENABLED=false
      - SESSION_TIMEOUT=3600
      - DATABASE_URL=sqlite:///data/memoai.db
      - LLM_PROVIDER=claude
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - DEBUG_MODE=true
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    depends_on:
      - memoai-frontend

  memoai-frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - BACKEND_URL=http://memoai-backend:8000
      - AUTH_ENABLED=false
    volumes:
      - ./frontend/src:/app/src
    depends_on:
      - memoai-backend

volumes:
  data:
  config:
```

### 5.2 Production Environment
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  memoai-backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - AUTH_ENABLED=true
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - SESSION_TIMEOUT=3600
      - DATABASE_URL=sqlite:///data/memoai.db
      - LLM_PROVIDER=claude
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - HTTPS_ONLY=true
      - SECURE_COOKIES=true
      - CSRF_PROTECTION=true
      - RATE_LIMIT_PER_MINUTE=60
    volumes:
      - memoai_data:/app/data
      - memoai_config:/app/config
    secrets:
      - jwt_secret
      - claude_api_key
    restart: unless-stopped

  memoai-frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "3000:3000"
    environment:
      - BACKEND_URL=https://memoai-backend:8000
      - AUTH_ENABLED=true
    volumes:
      - memoai_static:/app/static
    depends_on:
      - memoai-backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - memoai_static:/var/www/static
    depends_on:
      - memoai-frontend
      - memoai-backend
    restart: unless-stopped

volumes:
  memoai_data:
  memoai_config:
  memoai_static:

secrets:
  jwt_secret:
    external: true
  claude_api_key:
    external: true
```

### 5.3 Dockerfile Specifications
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data and config directories
RUN mkdir -p /app/data /app/config

# Run as non-root user
RUN useradd -m -u 1000 memoai && chown -R memoai:memoai /app
USER memoai

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 6.0 Authentication and Security Configuration

### 6.1 Environment Variables
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

# Application Settings
DEBUG_MODE=false  # Production only
LOG_LEVEL=INFO
```

### 6.2 Authentication Configuration Files
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

### 6.3 Security Implementation
```yaml
SecurityMeasures:
  https_enforcement:
    - TLS 1.3 configuration
    - Secure cipher suites
    - HSTS headers
    - Certificate auto-renewal
  
  authentication_security:
    - JWT token rotation
    - Secure session management
    - Password policy enforcement
    - Brute force protection
  
  input_validation:
    - XSS prevention
    - SQL injection protection
    - CSRF token validation
    - Rate limiting per session/user
```

---

## 7.0 Environment Management

### 7.1 Environment-Specific Configurations
```yaml
EnvironmentConfigs:
  development:
    auth_enabled: false
    debug_mode: true
    log_level: DEBUG
    database_url: "sqlite:///data/memoai_dev.db"
  
  staging:
    auth_enabled: true
    debug_mode: false
    log_level: INFO
    database_url: "sqlite:///data/memoai_staging.db"
  
  production:
    auth_enabled: true
    debug_mode: false
    log_level: WARNING
    database_url: "sqlite:///data/memoai_prod.db"
    https_only: true
    secure_cookies: true
```

### 7.2 Secrets Management
```yaml
SecretsManagement:
  jwt_secret:
    - Environment variable: JWT_SECRET_KEY
    - Rotation: Quarterly
    - Generation: Secure random 32 bytes
  
  llm_api_key:
    - Environment variable: CLAUDE_API_KEY
    - Rotation: As needed
    - Storage: Docker secrets or environment variables
  
  database_credentials:
    - Future: PostgreSQL credentials
    - Current: SQLite file permissions
    - Backup: Encrypted backup files
```

---

## 8.0 Database Deployment and Persistence

### 8.1 SQLite Deployment Strategy (Based on Req 3.2)
```yaml
SQLiteDeployment:
  storage_strategy:
    - Docker volumes for data persistence
    - Regular backups to external storage
    - WAL mode for concurrent access
    - Connection pooling for performance
  
  backup_strategy:
    - Daily automated backups
    - Weekly full backups
    - Backup verification and testing
    - Encrypted backup storage
  
  scaling_considerations:
    - SQLite performance up to 100+ concurrent users
    - WAL mode optimizations
    - Connection pooling
    - Future migration path to PostgreSQL
```

### 8.2 Database Migration Strategy
```yaml
MigrationStrategy:
  current_state:
    - SQLite with WAL mode
    - Version-based migrations
    - Automated migration scripts
  
  future_scaling:
    - PostgreSQL migration when needed
    - Data migration procedures
    - Connection string updates
    - Performance optimization
```

---

## 9.0 Deployment Procedures

### 9.1 Initial Deployment
```yaml
InitialDeployment:
  1. environment_setup:
     - Install Docker and Docker Compose
     - Configure environment variables
     - Set up SSL certificates (production)
  
  2. database_setup:
     - Initialize SQLite database
     - Run migration scripts
     - Create initial admin user (if auth enabled)
  
  3. application_deployment:
     - Build Docker images
     - Start containers with docker-compose
     - Verify health checks
     - Test core functionality
  
  4. configuration_setup:
     - Upload YAML configuration files
     - Configure authentication settings
     - Set up monitoring and logging
```

### 9.2 Update Procedures
```yaml
UpdateProcedures:
  application_updates:
    - Pull latest code changes
    - Build new Docker images
    - Run database migrations
    - Deploy with zero-downtime strategy
  
  configuration_updates:
    - Update YAML configuration files
    - Validate configuration syntax
    - Restart affected services
    - Verify configuration changes
  
  security_updates:
    - Update base images
    - Rotate secrets and keys
    - Apply security patches
    - Verify security posture
```

### 9.3 Rollback Procedures
```yaml
RollbackProcedures:
  application_rollback:
    - Revert to previous Docker image
    - Rollback database migrations
    - Restore configuration files
    - Verify system functionality
  
  configuration_rollback:
    - Restore previous YAML files
    - Revert environment variables
    - Restart services
    - Validate system state
```

---

## 10.0 Scaling Strategies

### 10.1 Horizontal Scaling (Based on Req 3.2)
```yaml
HorizontalScaling:
  load_balancing:
    - Nginx reverse proxy
    - Round-robin load distribution
    - Health check monitoring
    - Session affinity (if needed)
  
  container_scaling:
    - Docker Swarm or Kubernetes
    - Auto-scaling based on metrics
    - Resource limits and requests
    - Service discovery
  
  database_scaling:
    - Connection pooling
    - Read replicas (future PostgreSQL)
    - Query optimization
    - Caching strategies
```

### 10.2 Performance Optimization
```yaml
PerformanceOptimization:
  application_optimization:
    - Async processing for LLM calls
    - Caching for frequently accessed data
    - Database query optimization
    - Static asset optimization
  
  infrastructure_optimization:
    - CDN for static assets
    - Database indexing
    - Memory and CPU optimization
    - Network optimization
```

---

## 11.0 Monitoring and Observability

### 11.1 Health Checks and Monitoring
```yaml
HealthChecks:
  application_health:
    - HTTP health check endpoint
    - Database connectivity check
    - LLM API connectivity check
    - Response time monitoring
  
  infrastructure_health:
    - Container health status
    - Resource utilization monitoring
    - Network connectivity
    - Disk space monitoring
  
  business_metrics:
    - User activity monitoring
    - LLM API usage tracking
    - Error rate monitoring
    - Performance metrics
```

### 11.2 Logging and Alerting
```yaml
LoggingStrategy:
  log_collection:
    - Structured logging (JSON format)
    - Log aggregation and centralization
    - Log retention policies
    - Log level configuration
  
  alerting:
    - Error rate thresholds
    - Performance degradation alerts
    - Resource utilization alerts
    - Security incident alerts
```

---

## 12.0 Backup and Disaster Recovery

### 12.1 Backup Strategy
```yaml
BackupStrategy:
  database_backups:
    - Daily automated backups
    - Point-in-time recovery capability
    - Backup verification and testing
    - Off-site backup storage
  
  configuration_backups:
    - YAML configuration files
    - Environment variables
    - SSL certificates
    - Docker Compose files
  
  application_backups:
    - Docker images
    - Static assets
    - User uploads (PDFs)
    - Log files
```

### 12.2 Disaster Recovery
```yaml
DisasterRecovery:
  recovery_procedures:
    - System restoration from backups
    - Database recovery procedures
    - Configuration restoration
    - Service restart procedures
  
  business_continuity:
    - Minimum viable system requirements
    - Alternative deployment options
    - Communication procedures
    - Recovery time objectives
```

---

## 13.0 Traceability Links

- **Source of Truth**: `02_Architecture.md`, `03_Data_Model.md`
- **Mapped Requirements**: 
  - Scalability (3.2)
  - Reliability (3.3)
  - Performance (3.1)
  - Security (3.4)
  - Docker deployment (Overview 3.2)
  - MVP to production scaling path
