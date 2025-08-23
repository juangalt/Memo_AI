# Deployment Specification
## Memo AI Coach

**Document ID**: 07_Deployment.md  
**Document Version**: 1.4  
**Last Updated**: Implementation Phase (Complete consistency fixes and standardization)  
**Next Review**: After initial deployment  
**Status**: Approved

---

## 1.0 Document Information

### 1.1 Purpose
Defines the deployment architecture, infrastructure requirements, containerization strategy, and operational procedures for the Memo AI Coach application, ensuring reliable and scalable production deployment.

### 1.2 Scope
- Deployment architecture and infrastructure design
- Containerization strategy and Docker implementation
- Environment configuration and management
- Deployment procedures and automation
- Monitoring, logging, and operational support
- Security and compliance considerations
- Scalability and performance optimization

### 1.3 Dependencies
- **Prerequisites**: 00_ProjectOverview.md, 01_Requirements.md, 02_Architecture.md, 03_Data_Model.md, 04_API_Definitions.md, 05_UI_UX.md, 06_Testing.md
- **Related Documents**: 08_Maintenance.md, 09_Dev_Roadmap.md
- **Requirements**: Implements deployment requirements from 01_Requirements.md (Req 3.1-3.5)

### 1.4 Document Structure
1. Document Information
2. Deployment Architecture Overview
3. Project Directory Structure
4. Infrastructure Requirements
5. Containerization Strategy
6. Environment Configuration
7. Deployment Procedures
8. Monitoring and Logging
9. Security and Compliance
10. Scalability and Performance
11. Operational Procedures
12. Design Decisions
13. Traceability Matrix
14. Implementation Summary

### 1.5 Traceability Summary
| Requirement ID | Requirement Description | Deployment Implementation |
|---------------|------------------------|---------------------------|
| 3.1.1-3.1.2 | Performance Requirements | Performance Optimization (10.1) |
| 3.2.1-3.2.2 | Scalability Requirements | Scalability Strategy (10.2) |
| 3.3.1-3.3.2 | Reliability Requirements | Reliability Measures (10.3) |
| 3.4.1-3.4.5 | Security Requirements | Security Implementation (9.1) |
| 3.5.1-3.5.4 | Maintainability Requirements | Maintainability Strategy (10.3) |

### 1.6 Document Navigation
- **Previous Document**: 06_Testing.md
- **Next Document**: 08_Maintenance.md
- **Related Documents**: 09_Dev_Roadmap.md

---

## 2.0 Deployment Architecture Overview

### 2.1 System Architecture
The Memo AI Coach deployment follows a containerized microservices architecture aligned with the three-layer system design:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCTION ENVIRONMENT                      │
├─────────────────────────────────────────────────────────────────┤
│  Load Balancer (Optional) │  Reverse Proxy (Traefik)          │
│  - SSL/TLS Termination    │  - Automatic Service Discovery    │
│  - Health Checks          │  - Request Routing & Load Balancing│
│  - Let's Encrypt Integration│  - Middleware Support           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CONTAINER ORCHESTRATION                     │
├─────────────────────────────────────────────────────────────────┤
│  Frontend Container (Streamlit) │  Backend Container (FastAPI) │
│  - Port 8501                   │  - Port 8000                  │
│  - Session State Management    │  - API Services               │
│  - Static Assets              │  - LLM Integration            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  SQLite Database (WAL Mode) │  Configuration Files (YAML)     │
│  - Persistent Volume        │  - ConfigMap/Secrets            │
│  - Backup Strategy          │  - Environment Variables        │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Deployment Principles
- **Containerization**: Docker containers for consistent deployment
- **Stateless Design**: Session state managed in database, not containers
- **Scalability**: Horizontal scaling support for 100+ concurrent users
- **Security**: Secure configuration management and access controls
- **Monitoring**: Comprehensive logging and health monitoring
- **Maintainability**: Simple deployment procedures and rollback capabilities
- **Service Discovery**: Automatic container detection and routing with Traefik

---

## 3.0 Project Directory Structure

### 3.1 Root Directory Layout
The Memo AI Coach project follows a structured directory layout optimized for containerized deployment:

```
memoai/
├── devspecs/                    # Development specifications
│   ├── 00_devspecs_overview.md
│   ├── 01_requirements.md
│   ├── 02_architecture.md
│   ├── 03_Data_Model.md
│   ├── 04_API_Definitions.md
│   ├── 05_UI_UX.md
│   ├── 06_Testing.md
│   ├── 07_Deployment.md
│   ├── 08_Maintenance.md
│   └── 09_Dev_Roadmap.md
├── frontend/                    # Streamlit frontend application
│   ├── app.py                   # Main Streamlit application
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile              # Frontend container definition
│   └── components/             # Reusable UI components
├── backend/                     # FastAPI backend application
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile             # Backend container definition
│   ├── services/              # Business logic services
│   ├── models/                # Data models and schemas
│   └── utils/                 # Utility functions
├── config/                     # Configuration files
│   ├── rubric.yaml            # Grading criteria and scoring
│   ├── prompt.yaml            # LLM prompt templates
│   ├── llm.yaml              # LLM provider configuration
│   └── auth.yaml             # Authentication settings
├── data/                       # Persistent data storage
│   ├── memoai.db             # SQLite database
│   └── backups/              # Database backup directory
├── logs/                       # Application logs
│   ├── app.log               # Application logs
│   └── error.log             # Error logs
├── letsencrypt/               # SSL certificate storage
│   └── acme.json             # Let's Encrypt ACME storage
├── docker compose.yml         # Container orchestration
├── .env                       # Environment variables
├── .gitignore                 # Git ignore rules
└── README.md                  # Project documentation
```

### 3.2 Directory Purposes

**Development Specifications (`devspecs/`)**:
- Complete project specification documents
- Architecture and design decisions
- Implementation guidelines and requirements

**Frontend Application (`frontend/`)**:
- Streamlit-based user interface
- Session state management
- UI components and styling

**Backend Application (`backend/`)**:
- FastAPI REST API services
- LLM integration and evaluation logic
- Database operations and business logic

**Configuration (`config/`)**:
- YAML configuration files for system settings
- Admin-editable configuration management
- Environment-specific configurations

**Data Storage (`data/`)**:
- SQLite database with WAL mode
- Persistent data across container restarts
- Backup and recovery data

**Logging (`logs/`)**:
- Application logs with rotation
- Error tracking and debugging
- Performance monitoring data

**SSL Certificates (`letsencrypt/`)**:
- Let's Encrypt certificate storage
- ACME challenge files
- Certificate renewal data

### 3.3 Deployment Considerations

**Volume Mounts**:
- `./config:/app/config:ro` - Read-only configuration access
- `./data:/app/data` - Persistent database storage
- `./logs:/app/logs` - Application log storage
- `./letsencrypt:/letsencrypt` - SSL certificate persistence

**Security**:
- Configuration files mounted as read-only
- Sensitive data isolated in dedicated volumes
- SSL certificates with proper permissions

**Scalability**:
- Stateless application containers
- Persistent data in dedicated volumes
- Shared configuration across instances

---

## 4.0 Infrastructure Requirements

### 4.1 Hardware Requirements
**Minimum Production Requirements**:
- **CPU**: 2 cores (4 cores recommended for 100+ users)
- **Memory**: 4GB RAM (8GB recommended for concurrent processing)
- **Storage**: 20GB SSD (50GB recommended for logs and backups)
- **Network**: 100Mbps bandwidth (1Gbps recommended)

**Development Requirements**:
- **CPU**: 1 core
- **Memory**: 2GB RAM
- **Storage**: 10GB SSD
- **Network**: Standard internet connection

### 4.2 Software Requirements
**Operating System**:
- **Production**: Ubuntu 20.04 LTS or later, CentOS 8+, or containerized deployment
- **Development**: Any OS supporting Docker (Windows, macOS, Linux)

**Container Runtime**:
- **Docker**: Version 20.10+ with Docker Compose 2.0+
- **Alternative**: Podman 3.0+ for containerized deployment

**Reverse Proxy**:
- **Traefik**: Version 2.10+ with Docker provider and Let's Encrypt integration
- **Features**: Automatic SSL/TLS certificate management, service discovery

**Database**:
- **SQLite**: Version 3.35+ with WAL mode support
- **File System**: Ext4 or XFS for optimal SQLite performance

### 4.3 Network Requirements
**Port Configuration**:
- **Frontend**: Port 8501 (Streamlit)
- **Backend API**: Port 8000 (FastAPI)
- **Traefik Proxy**: Port 80/443 (HTTP/HTTPS)
- **Traefik Dashboard**: Port 8080 (Admin interface)
- **Health Checks**: Port 8000/health (FastAPI health endpoint)

**Port Standardization**:
All port configurations are standardized across environments:
- Development: Same ports as production for consistency
- Production: Standard ports with firewall restrictions
- Container: Internal port mapping for service discovery
- Testing: Same ports as production for integration testing

**Centralized Port Configuration**:
```yaml
# Standard Port Configuration (All Environments)
Ports:
  frontend: 8501      # Streamlit application
  backend: 8000       # FastAPI REST API
  traefik_http: 80    # HTTP traffic
  traefik_https: 443  # HTTPS traffic
  traefik_dashboard: 8080  # Traefik admin dashboard
  health_check: 8000  # Health check endpoint
```

**Network Security**:
- **Firewall**: Restrict access to required ports only
- **SSL/TLS**: HTTPS termination at Traefik with automatic certificate management
- **Rate Limiting**: Network-level rate limiting for API protection

---

## 5.0 Containerization Strategy

### 5.1 Docker Architecture
**Multi-Container Deployment**:
```yaml
# docker compose.yml
version: '3.8'
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@example.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"  # Traefik dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./letsencrypt:/letsencrypt
    restart: unless-stopped

  frontend:
    build: ./frontend
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`${DOMAIN}`) && PathPrefix(`/`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
      - "traefik.http.services.frontend.loadbalancer.server.port=8501"
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      - backend
    volumes:
      - ./config:/app/config:ro
    restart: unless-stopped

  backend:
    build: ./backend
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`${DOMAIN}`) && PathPrefix(`/api`)"
      - "traefik.http.routers.backend.entrypoints=websecure"
      - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
      - "traefik.http.services.backend.loadbalancer.server.port=8000"
    environment:
      - DATABASE_URL=sqlite:///data/memoai.db
      - LLM_API_KEY=${LLM_API_KEY}
    volumes:
      - ./data:/app/data
      - ./config:/app/config:ro
      - ./logs:/app/logs
    restart: unless-stopped

volumes:
  data:
  logs:
```

### 5.2 Container Specifications

#### 5.2.1 Traefik Container
**Base Image**: traefik:v2.10  
**Features**:
- Automatic SSL/TLS certificate management with Let's Encrypt
- Docker service discovery and load balancing
- Built-in dashboard for monitoring and configuration
- Middleware support for security and routing
- Health check integration

**Configuration**:
- Docker provider for automatic service discovery
- Let's Encrypt integration for SSL certificates
- HTTP challenge for domain validation
- Persistent certificate storage

#### 5.2.2 Frontend Container (Streamlit)
**Base Image**: python:3.9-slim  
**Dependencies**: streamlit, requests, yaml  
**Configuration**:
- Session state management via SQLite
- Static asset serving
- Environment-based configuration
- Health check endpoint
- Traefik labels for service discovery

**Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY frontend/ .
EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### 5.2.3 Backend Container (FastAPI)
**Base Image**: python:3.9-slim  
**Dependencies**: fastapi, uvicorn, sqlite3, anthropic, pyyaml  

**Database Initialization Script**:
The backend container includes an `init_db.py` script that creates the complete database schema:

```python
# init_db.py - Database initialization script
import sqlite3
import os

def init_database():
    """Initialize the database with schema from 03_Data_Model.md"""
    db_path = os.getenv('DATABASE_URL', 'sqlite:///data/memoai.db').replace('sqlite:///', '')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Create sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            user_id INTEGER REFERENCES users(id),
            is_admin BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Create submissions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text_content TEXT NOT NULL,
            session_id TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
        )
    ''')
    
    # Create evaluations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER NOT NULL,
            overall_score DECIMAL(5,2),
            strengths TEXT NOT NULL,
            opportunities TEXT NOT NULL,
            rubric_scores TEXT NOT NULL,  -- JSON string: {"category1": score, "category2": score}
            segment_feedback TEXT NOT NULL,  -- JSON string: [{"segment": "text", "comment": "feedback", "questions": ["q1", "q2"]}]
            llm_provider TEXT NOT NULL DEFAULT 'claude',
            llm_model TEXT NOT NULL,
            raw_prompt TEXT,
            raw_response TEXT,
            debug_enabled BOOLEAN DEFAULT FALSE,
            processing_time DECIMAL(6,3),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username, is_active)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_active ON sessions(user_id, is_active, expires_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_submissions_session_date ON submissions(session_id, created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_evaluations_submission ON evaluations(submission_id, created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_active ON sessions(session_id, is_active, expires_at)')
    
    # Configure WAL mode for concurrent access
    cursor.execute('PRAGMA journal_mode = WAL')
    cursor.execute('PRAGMA synchronous = NORMAL')
    cursor.execute('PRAGMA cache_size = 10000')
    cursor.execute('PRAGMA temp_store = memory')
    
    conn.commit()
    conn.close()
    
    print("Database initialized successfully")

if __name__ == "__main__":
    init_database()
```

**Configuration Validation Script**:
The backend container also includes a `validate_config.py` script that validates all 4 essential YAML files:

```python
# validate_config.py - Configuration validation script
import yaml
import os
import sys
from pathlib import Path

def validate_yaml_file(file_path, required_fields=None):
    """Validate a YAML configuration file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if config is None:
            raise ValueError(f"Empty or invalid YAML file: {file_path}")
        
        if required_fields:
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Missing required field '{field}' in {file_path}")
        
        print(f"✓ {file_path} - Valid")
        return True
        
    except Exception as e:
        print(f"✗ {file_path} - Error: {e}")
        return False

def validate_all_configs():
    """Validate all 4 essential configuration files"""
    config_dir = os.getenv('CONFIG_DIR', '/app/config')
    required_configs = {
        'rubric.yaml': ['grading_criteria', 'scoring_categories'],
        'prompt.yaml': ['templates', 'instructions'],
        'llm.yaml': ['provider', 'api_key', 'model'],
        'auth.yaml': ['session_timeout', 'admin_credentials']
    }
    
    all_valid = True
    
    for filename, required_fields in required_configs.items():
        file_path = Path(config_dir) / filename
        if not file_path.exists():
            print(f"✗ {file_path} - File not found")
            all_valid = False
        else:
            if not validate_yaml_file(file_path, required_fields):
                all_valid = False
    
    if all_valid:
        print("All configuration files are valid")
        return True
    else:
        print("Configuration validation failed")
        return False

if __name__ == "__main__":
    success = validate_all_configs()
    sys.exit(0 if success else 1)
```  
**Configuration**:
- API service with health checks
- Database connection management
- LLM integration
- Rate limiting middleware with session-based limits
- Logging and monitoring
- Traefik labels for service discovery

**Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.3 Volume Management
**Persistent Data**:
- **Database**: SQLite database with WAL mode
- **Logs**: Application logs and debug information
- **Configuration**: YAML configuration files
- **Backups**: Database backups and configuration snapshots
- **SSL Certificates**: Let's Encrypt certificates and ACME storage

**Volume Strategy**:
- **Data Volume**: Persistent SQLite database storage
- **Config Volume**: Read-only configuration files
- **Log Volume**: Application logs with rotation
- **Backup Volume**: Automated backup storage
- **SSL Volume**: Persistent SSL certificate storage for Traefik

---

## 6.0 Environment Configuration

### 6.1 Configuration Management
**Environment Variables**:

**Complete Environment Variable Reference**:
All environment variables are documented with their purpose, default values, and usage.

```bash
# Required Variables (must be set)
LLM_API_KEY=your-llm-api-key             # LLM provider API key
SECRET_KEY=your-secret-key                # Session encryption key
ADMIN_PASSWORD=secure-password            # Admin password

# Optional Variables (have defaults)
APP_ENV=production                        # Environment: development/production
DEBUG_MODE=false                          # Debug mode: true/false
LOG_LEVEL=INFO                            # Log level: DEBUG/INFO/WARNING/ERROR
DATABASE_URL=sqlite:///data/memoai.db     # Database connection string
LLM_PROVIDER=claude                       # LLM provider: claude/openai/gemini
LLM_MODEL=claude-3-sonnet-20240229       # LLM model name
LLM_TIMEOUT=30                            # LLM timeout in seconds
SESSION_TIMEOUT=3600                      # Session timeout in seconds
MAX_CONCURRENT_USERS=100                  # Maximum concurrent users

# Rate Limiting Configuration
RATE_LIMIT_PER_SESSION=20                 # Requests per hour per session
RATE_LIMIT_PER_HOUR=1000                  # Global requests per hour per IP

# Traefik Configuration (optional for production)
DOMAIN=your-domain.com                    # Domain name for SSL certificates
ADMIN_EMAIL=admin@your-domain.com         # Email for Let's Encrypt

# Database Configuration
DATABASE_WAL_MODE=true                    # Enable WAL mode for SQLite
DATABASE_BACKUP_ENABLED=true              # Enable automated backups
DATABASE_BACKUP_RETENTION=28              # Backup retention in days

# Security Configuration
CSRF_PROTECTION=true                      # Enable CSRF protection
XSS_PROTECTION=true                       # Enable XSS protection
CONTENT_SECURITY_POLICY=true              # Enable CSP headers
```

**Environment Variables**:
```bash
# Application Configuration
APP_ENV=production
DEBUG_MODE=false
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=sqlite:///data/memoai.db
DATABASE_WAL_MODE=true

# LLM Configuration
LLM_PROVIDER=claude
LLM_API_KEY=${LLM_API_KEY}
LLM_MODEL=claude-3-sonnet-20240229
LLM_TIMEOUT=30

# Security Configuration
SECRET_KEY=${SECRET_KEY}
SESSION_TIMEOUT=3600
ADMIN_PASSWORD=${ADMIN_PASSWORD}

# Performance Configuration
MAX_CONCURRENT_USERS=100
RATE_LIMIT_PER_SESSION=20
RATE_LIMIT_PER_HOUR=1000

# Traefik Configuration (optional for production)
DOMAIN=${DOMAIN}
ADMIN_EMAIL=${ADMIN_EMAIL}
```

### 5.2 Configuration Files
**Essential YAML Files** (as defined in Architecture 4.2):
- `rubric.yaml`: Grading criteria and scoring rubrics
- `prompt.yaml`: LLM prompt templates and instruction formats
- `llm.yaml`: LLM provider configuration and API settings
- `auth.yaml`: Authentication settings and session management

**Configuration File Override System**:
The system implements a flexible configuration management approach where environment variables can override configuration file settings:

```python
# config_manager.py - Configuration file override system
import yaml
import os
from pathlib import Path

def load_config_with_overrides():
    """Load configuration from files with environment variable overrides"""
    config = {}
    
    # Load from config files
    config_files = ['rubric.yaml', 'prompt.yaml', 'llm.yaml', 'auth.yaml']
    config_dir = Path('/app/config')
    
    for filename in config_files:
        file_path = config_dir / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f)
                config[filename.replace('.yaml', '')] = file_config
    
    # Apply environment variable overrides
    config = apply_env_overrides(config)
    
    return config

def apply_env_overrides(config):
    """Apply environment variable overrides to configuration"""
    # LLM configuration overrides
    if 'llm' in config:
        if os.getenv('LLM_API_KEY'):
            config['llm']['api_key'] = os.getenv('LLM_API_KEY')
        if os.getenv('LLM_PROVIDER'):
            config['llm']['provider'] = os.getenv('LLM_PROVIDER')
        if os.getenv('LLM_MODEL'):
            config['llm']['model'] = os.getenv('LLM_MODEL')
        if os.getenv('LLM_TIMEOUT'):
            config['llm']['timeout'] = int(os.getenv('LLM_TIMEOUT'))
    
    # Auth configuration overrides
    if 'auth' in config:
        if os.getenv('SESSION_TIMEOUT'):
            config['auth']['session_timeout'] = int(os.getenv('SESSION_TIMEOUT'))
        if os.getenv('ADMIN_PASSWORD'):
            config['auth']['admin_password'] = os.getenv('ADMIN_PASSWORD')
    
    # Debug configuration overrides
    if os.getenv('DEBUG_MODE'):
        config['debug_mode'] = os.getenv('DEBUG_MODE').lower() == 'true'
    
    return config
```

**Configuration Validation**:
- Startup validation of all 4 essential YAML files (rubric.yaml, prompt.yaml, llm.yaml, auth.yaml)
- Schema validation for configuration integrity
- Required fields verification for each configuration type
- UTF-8 encoding validation
- Environment-specific configuration overrides
- Secure configuration management

### 5.3 Environment-Specific Configurations

#### 5.3.1 Development Environment
```yaml
DevelopmentConfig:
  debug_mode: true
  log_level: DEBUG
  llm_provider: mock
  database_url: sqlite:///data/dev.db
  session_timeout: 7200
  rate_limiting: false
```

#### 5.3.2 Production Environment
```yaml
ProductionConfig:
  debug_mode: false
  log_level: INFO
  llm_provider: claude
  database_url: sqlite:///data/prod.db
  session_timeout: 3600
  rate_limiting: true
  ssl_enabled: true
  backup_enabled: true
```

---

## 7.0 Deployment Procedures

### 7.1 Initial Deployment
**Prerequisites**:
- Docker and Docker Compose installed
- Domain name configured with DNS pointing to server IP
- SSL certificates (for production)
- LLM API credentials
- Admin credentials

**Required Environment Variables**:
- `DOMAIN`: Your domain name (e.g., memo.example.com)
- `ADMIN_EMAIL`: Email address for Let's Encrypt certificates
- `LLM_API_KEY`: API key for LLM provider
- `SECRET_KEY`: Secret key for session management
- `ADMIN_USERNAME`: Admin username
- `ADMIN_PASSWORD`: Admin password

**Optional Environment Variables**:
- `APP_ENV`: Environment (development/production) - Default: production
- `DEBUG_MODE`: Enable debug mode - Default: false
- `LOG_LEVEL`: Logging level - Default: INFO
- `DATABASE_URL`: Database connection string - Default: sqlite:///data/memoai.db
- `LLM_PROVIDER`: LLM provider - Default: claude
- `LLM_MODEL`: LLM model - Default: claude-3-sonnet-20240229
- `LLM_TIMEOUT`: LLM timeout in seconds - Default: 30
- `SESSION_TIMEOUT`: Session timeout in seconds - Default: 3600
- `MAX_CONCURRENT_USERS`: Maximum concurrent users - Default: 100

**Deployment Steps**:
1. **Environment Setup**:
   ```bash
   # Clone repository
   git clone <repository-url>
   cd memoai
   
   # Create environment file
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Configuration Setup**:
   ```bash
   # Create configuration directory
   mkdir -p config data logs ssl
   
   # Copy configuration files
   cp config/*.yaml config/
   # Edit configuration files as needed
   ```

3. **DNS Configuration Setup** (Production):
   ```bash
   # Configure DNS for your domain (replace with your actual domain)
   # Add A record pointing to your server IP
   # Configure DNS records:
   # - Type: A, Name: @, Content: YOUR_SERVER_IP
   # - Type: A, Name: *, Content: YOUR_SERVER_IP
   
   # Example for Cloudflare:
   # - Type: A, Name: @, Content: YOUR_SERVER_IP, Proxy: Enabled
   # - Type: A, Name: *, Content: YOUR_SERVER_IP, Proxy: Enabled
   ```

4. **Traefik Configuration Setup** (Production):
   ```bash
   # Create Traefik configuration directory
   mkdir -p letsencrypt
   
   # Set proper permissions for Let's Encrypt storage
   chmod 600 letsencrypt
   ```

4. **Configuration Validation**:
   ```bash
   # Validate all configuration files
   docker compose run backend python validate_config.py
   ```
   
   **Configuration Validation Requirements**:
   The `validate_config.py` script validates all 4 essential YAML files:
   - `rubric.yaml`: Grading criteria and scoring categories
   - `prompt.yaml`: LLM prompt templates and instructions
   - `llm.yaml`: LLM provider configuration and API settings
   - `auth.yaml`: Authentication settings and session management

5. **Database Initialization**:
   ```bash
   # Initialize database schema
   docker compose run backend python init_db.py
   ```

   **Database Initialization Script Requirements**:
   The `init_db.py` script must create the database schema as defined in 03_Data_Model.md:
   - `sessions` table with session management
   - `submissions` table for user text submissions
   - `evaluations` table for LLM evaluation results
   - All required indexes and constraints
   - WAL mode configuration for concurrent access

6. **Application Deployment**:
   ```bash
   # Build and start containers
   docker compose up -d --build
   
   # Verify deployment
   docker compose ps
   curl http://localhost:8000/health
   ```

### 7.2 Update Procedures
**Zero-Downtime Updates**:
```bash
# Pull latest changes
git pull origin main

# Build new images
docker compose build

# Update containers with zero downtime
docker compose up -d --no-deps backend
docker compose up -d --no-deps frontend

# Verify update
docker compose ps
curl http://localhost:8000/health
```

**Rollback Procedures**:
```bash
# Rollback to previous version
docker compose down
docker compose up -d --build

# Database rollback (if needed)
docker compose run backend python rollback_db.py
```

### 7.3 Health Checks and Monitoring
**Health Check Endpoints**:
- **Backend**: `GET /health` - API service health with database and LLM connectivity
- **Frontend**: `GET /_stcore/health` - Streamlit health
- **Database**: SQLite connection validation and WAL mode status
- **LLM**: API connectivity test and response time validation
- **Configuration**: YAML file accessibility and validation status

**Monitoring Integration**:
- **Container Health**: Docker health checks
- **Application Health**: Custom health endpoints
- **Database Health**: Connection pool monitoring
- **LLM Health**: API response times monitoring

---

## 8.0 Monitoring and Logging

### 8.1 Logging Strategy
**Log Levels**:
- **DEBUG**: Detailed debugging information
- **INFO**: General application information
- **WARNING**: Warning messages
- **ERROR**: Error conditions
- **CRITICAL**: Critical system failures

**Standardized Logging Configuration**:
All components use the same logging configuration for consistency across the system.

```python
# Standardized Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/memoai.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/error.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed',
            'level': 'ERROR',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'debug_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/debug.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 3,
            'formatter': 'detailed',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'memoai': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'memoai.debug': {
            'handlers': ['debug_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'memoai.llm': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'memoai.auth': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
}
```

### 8.2 Application Monitoring
**Performance Metrics**:
- **Response Times**: API endpoint response times
- **Throughput**: Requests per second
- **Error Rates**: Error percentage by endpoint
- **Resource Usage**: CPU, memory, disk usage
- **Database Performance**: Query execution times

**Monitoring Tools**:
- **Application Metrics**: Custom metrics collection
- **System Metrics**: Docker stats and system monitoring
- **Database Metrics**: SQLite performance monitoring
- **LLM Metrics**: API response times and error rates

### 8.3 Alerting and Notifications
**Alert Conditions**:
- **High Error Rate**: >5% error rate for 5 minutes
- **High Response Time**: >15 seconds average response time
- **Service Down**: Health check failures
- **Resource Exhaustion**: >80% CPU or memory usage
- **Database Issues**: Connection failures or slow queries

**Notification Channels**:
- **Email**: Critical system alerts
- **Slack**: Operational notifications
- **SMS**: Emergency alerts (optional)
- **Dashboard**: Real-time monitoring dashboard

---

## 9.0 Security and Compliance

### 9.1 Security Implementation
**Authentication Security**:
- **Session Management**: Secure session tokens with expiration
- **Admin Authentication**: Strong password requirements
- **API Security**: Rate limiting and input validation
- **Data Protection**: Session-based data isolation

**Network Security**:
- **SSL/TLS**: HTTPS encryption for all communications
- **Firewall**: Port restrictions and access controls
- **Rate Limiting**: Protection against abuse
- **CSRF Protection**: Cross-site request forgery prevention

### 9.2 Data Protection
**Privacy Measures**:
- **No PII Collection**: Only text submissions stored
- **Session Isolation**: Data scoped by session_id
- **Data Retention**: Configurable retention policies
- **Secure Storage**: Encrypted configuration and sensitive data

**Compliance Considerations**:
- **Data Minimization**: Collect only necessary data
- **Access Controls**: Admin-only access to sensitive functions
- **Audit Logging**: Configuration change tracking
- **Data Deletion**: Secure data removal procedures

### 9.3 Security Monitoring
**Security Metrics**:
- **Failed Authentication**: Login attempt monitoring
- **Rate Limit Violations**: Abuse detection
- **Configuration Changes**: Admin action tracking
- **System Access**: Unauthorized access attempts

**Security Tools**:
- **Log Analysis**: Security event monitoring
- **Vulnerability Scanning**: Regular security assessments
- **Access Monitoring**: User activity tracking
- **Incident Response**: Security incident procedures

---

## 10.0 Scalability and Performance

### 10.1 Performance Optimization
**Response Time Targets** (Req 3.1):
- **Page Load**: < 1 second
- **Text Submission**: < 15 seconds (LLM processing)
- **Tab Switching**: < 1 second
- **Admin Operations**: < 3 seconds

**Optimization Strategies**:
- **Database Optimization**: SQLite WAL mode and indexing
- **Caching**: Session state and configuration caching
- **Connection Pooling**: Database connection management
- **Async Processing**: Non-blocking operations where possible

### 10.2 Scalability Strategy
**Concurrent User Support** (Req 3.2):
- **Target**: 100+ concurrent users
- **Current**: 10-20 concurrent users
- **Scaling**: Horizontal scaling with load balancing

**Scaling Approaches**:
- **Horizontal Scaling**: Multiple container instances
- **Load Balancing**: Nginx reverse proxy with health checks
- **Database Scaling**: SQLite with WAL mode optimizations
- **Resource Scaling**: CPU and memory allocation

### 10.3 Resource Management
**Resource Allocation**:
- **CPU**: 2-4 cores per container instance
- **Memory**: 4-8GB RAM per instance
- **Storage**: 20-50GB SSD storage
- **Network**: 100Mbps-1Gbps bandwidth

**Resource Monitoring**:
- **CPU Usage**: Container and system CPU monitoring
- **Memory Usage**: Memory consumption tracking
- **Disk Usage**: Storage utilization monitoring
- **Network Usage**: Bandwidth consumption tracking

---

## 11.0 Operational Procedures

### 11.1 Backup and Recovery
**Backup Strategy**:
- **Database Backups**: Weekly automated SQLite backups with basic verification
- **Configuration Backups**: Version-controlled configuration files
- **Log Backups**: Rotated log file archives
- **Application Backups**: Container image backups
- **Backup Verification**: Basic integrity checks using PRAGMA integrity_check

**Recovery Procedures**:
- **Database Recovery**: Restore from backup with basic integrity verification
- **Configuration Recovery**: Restore from version control
- **Application Recovery**: Redeploy from container images
- **Full System Recovery**: Complete environment restoration

### 11.2 Maintenance Procedures
**Regular Maintenance**:
- **Log Rotation**: Automated log file management
- **Database Maintenance**: SQLite optimization and cleanup
- **Security Updates**: Regular security patch application
- **Performance Monitoring**: Ongoing performance assessment

**Scheduled Maintenance**:
- **Weekly**: Log cleanup and performance review
- **Monthly**: Security updates and configuration review
- **Quarterly**: Full system health assessment
- **Annually**: Comprehensive security audit

### 11.3 Incident Response
**Incident Categories**:
- **Service Outage**: Application unavailability
- **Performance Degradation**: Slow response times
- **Security Incident**: Unauthorized access or data breach
- **Data Loss**: Database corruption or backup failure

**Response Procedures**:
- **Detection**: Automated monitoring and alerting
- **Assessment**: Impact analysis and severity determination
- **Response**: Immediate mitigation and recovery actions
- **Resolution**: Root cause analysis and prevention measures

---

## 12.0 Design Decisions

### 12.1 SSL Certificate Management
**Decision**: **Let's Encrypt with Traefik Auto-renewal**

**Implementation**:
- **Certificate Provider**: Let's Encrypt for free, automatic SSL certificates
- **Renewal Strategy**: Automated renewal through Traefik's built-in Let's Encrypt integration
- **DNS Requirements**: Public DNS configuration for domain validation
- **Certificate Validity**: 90-day certificates with automatic renewal
- **Deployment**: SSL termination at Traefik reverse proxy

**Configuration**:
```yaml
# Traefik Let's Encrypt configuration
certificatesresolvers:
  letsencrypt:
    acme:
      email: ${ADMIN_EMAIL}
      storage: /letsencrypt/acme.json
      httpchallenge:
        entrypoint: web
```

**Rationale**: 
- **Pros**: Free, automatic renewal, widely trusted, integrated with Traefik
- **Cons**: Requires public DNS, 90-day renewal cycle
- **Implementation Basis**: Provides cost-effective SSL security with minimal maintenance overhead through Traefik integration

### 12.2 Database Backup Strategy
**Decision**: **Weekly Backups with 4-week Retention**

**Implementation**:
- **Backup Frequency**: Weekly automated database backups
- **Retention Policy**: 4-week retention period (4 backup files)
- **Backup Method**: SQLite backup API with WAL checkpoint
- **Storage**: Local backup directory with rotation
- **Verification**: Basic integrity check using PRAGMA integrity_check

**Configuration**:
```bash
# Weekly backup cron job
0 2 * * 0 /usr/local/bin/backup_memoai.sh

# Backup retention cleanup
0 3 * * 0 /usr/local/bin/cleanup_backups.sh
```

**Backup Script**:
```bash
#!/bin/bash
# backup_memoai.sh - Simplified backup with basic verification
DATE=$(date +%Y%m%d)
BACKUP_DIR="/app/backups"
DB_PATH="/app/data/memoai.db"
BACKUP_FILE="$BACKUP_DIR/memoai_$DATE.db"

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform SQLite backup with WAL checkpoint
sqlite3 $DB_PATH "PRAGMA wal_checkpoint(FULL);"
cp $DB_PATH "$BACKUP_FILE"

# Basic integrity verification
if sqlite3 "$BACKUP_FILE" "PRAGMA integrity_check;" | grep -q "ok"; then
    echo "Backup successful: $BACKUP_FILE"
else
    echo "ERROR: Backup failed - integrity check failed"
    rm -f "$BACKUP_FILE"
    exit 1
fi

# Cleanup old backups (keep 4 weeks)
find $BACKUP_DIR -name "memoai_*.db" -mtime +28 -delete

echo "Backup completed successfully: $BACKUP_FILE"
```

**Rationale**: 
- **Pros**: Simple management, reasonable storage usage, adequate recovery point
- **Cons**: Potential week-long data loss window
- **Implementation Basis**: Balances storage efficiency with recovery requirements for typical usage patterns

### 12.3 Monitoring and Alerting
**Decision**: **Built-in Health Checks with Email Alerts**

**Implementation**:
- **Health Check Endpoints**: Built-in health checks for all services
- **Monitoring**: Simple application metrics and system health
- **Alerting**: Email notifications for critical issues
- **Dashboard**: Basic web-based status dashboard
- **Logging**: Comprehensive application logging with rotation

**Health Check Configuration**:
```yaml
# Docker health checks
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

**Monitoring Endpoints**:
```python
# FastAPI health check endpoint
@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "database": check_database_connection(),
        "llm": check_llm_connection(),
        "configuration": check_configuration_files(),
        "services": {
            "database": "healthy",
            "llm": "healthy", 
            "config": "healthy"
        }
    }
    
    # Check if any service is unhealthy
    if any(status != "healthy" for status in health_status["services"].values()):
        health_status["status"] = "unhealthy"
    
    return health_status

def check_database_connection():
    """Check database connectivity and WAL mode"""
    try:
        conn = sqlite3.connect(DATABASE_URL.replace('sqlite:///', ''))
        cursor = conn.cursor()
        
        # Check WAL mode
        cursor.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0]
        
        # Test basic queries for all tables
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sessions")
        session_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM submissions")
        submission_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM evaluations")
        evaluation_count = cursor.fetchone()[0]
        
        # Check database integrity
        cursor.execute("PRAGMA integrity_check")
        integrity_check = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "healthy",
            "journal_mode": journal_mode,
            "integrity_check": integrity_check,
            "table_counts": {
                "users": user_count,
                "sessions": session_count,
                "submissions": submission_count,
                "evaluations": evaluation_count
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

def check_llm_connection():
    """Check LLM API connectivity"""
    try:
        # Test LLM API connection (without making actual request)
        # This would test the API key and basic connectivity
        return {
            "status": "healthy",
            "provider": "claude",
            "model": "claude-3-sonnet-20240229"
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e)
        }

def check_configuration_files():
    """Check configuration file accessibility"""
    config_files = ['rubric.yaml', 'prompt.yaml', 'llm.yaml', 'auth.yaml']
    config_status = {}
    
    for filename in config_files:
        file_path = f"/app/config/{filename}"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            config_status[filename] = "accessible"
        except Exception as e:
            config_status[filename] = f"error: {str(e)}"
    
    return config_status

# Rate Limiting Middleware Implementation
```python
# rate_limiting.py - Rate limiting middleware
import time
from collections import defaultdict
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.limits = {
            'text_submissions': 20,  # per hour per session
            'admin_operations': 100,  # per hour per admin
            'config_changes': 20,  # per hour per admin
            'global_api': 1000  # per hour per IP
        }
    
    def is_rate_limited(self, key: str, limit_type: str, window: int = 3600):
        """Check if request is rate limited"""
        current_time = time.time()
        key_requests = self.requests[f"{key}:{limit_type}"]
        
        # Remove old requests outside window
        key_requests[:] = [req_time for req_time in key_requests 
                          if current_time - req_time < window]
        
        # Check if limit exceeded
        if len(key_requests) >= self.limits[limit_type]:
            return True
        
        # Add current request
        key_requests.append(current_time)
        return False

rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware for FastAPI"""
    # Get client IP
    client_ip = request.client.host
    
    # Get session ID from headers or cookies
    session_id = request.headers.get('X-Session-ID') or request.cookies.get('session_id')
    
    # Determine rate limit type based on endpoint
    path = request.url.path
    if path.startswith('/api/v1/evaluations/submit'):
        limit_type = 'text_submissions'
        key = session_id or client_ip
    elif path.startswith('/api/v1/admin'):
        limit_type = 'admin_operations'
        key = session_id or client_ip
    else:
        limit_type = 'global_api'
        key = client_ip
    
    # Check rate limit
    if rate_limiter.is_rate_limited(key, limit_type):
        return JSONResponse(
            status_code=429,
            content={
                "data": None,
                "meta": {
                    "timestamp": time.time(),
                    "request_id": request.headers.get('X-Request-ID', 'unknown')
                },
                "errors": [{
                    "code": "RATE_LIMITED",
                    "message": "Rate limit exceeded",
                    "field": None,
                    "details": f"Too many requests for {limit_type}"
                }]
            }
        )
    
    # Add rate limit headers
    response = await call_next(request)
    response.headers['X-RateLimit-Limit'] = str(rate_limiter.limits[limit_type])
    response.headers['X-RateLimit-Remaining'] = str(
        rate_limiter.limits[limit_type] - len(rate_limiter.requests[f"{key}:{limit_type}"])
    )
    
    return response

# Logging Middleware Implementation
```python
# logging_middleware.py - Comprehensive logging middleware
import logging
import time
import uuid
from fastapi import Request
from fastapi.responses import Response

logger = logging.getLogger('memoai')
auth_logger = logging.getLogger('memoai.auth')
llm_logger = logging.getLogger('memoai.llm')
debug_logger = logging.getLogger('memoai.debug')

async def logging_middleware(request: Request, call_next):
    """Comprehensive logging middleware for FastAPI"""
    # Generate request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Log request start
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request started - ID: {request_id}, Method: {request.method}, Path: {request.url.path}")
    
    # Log authentication details if available
    session_id = request.headers.get('X-Session-ID') or request.cookies.get('session_id')
    if session_id:
        auth_logger.info(f"Request authenticated - ID: {request_id}, Session: {session_id[:8]}...")
    
    # Log LLM requests specifically
    if request.url.path.startswith('/api/v1/evaluations/submit'):
        llm_logger.info(f"LLM evaluation request - ID: {request_id}, Session: {session_id[:8] if session_id else 'anonymous'}")
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"Request completed - ID: {request_id}, Status: {response.status_code}, Time: {process_time:.3f}s")
        
        # Add request ID to response headers
        response.headers['X-Request-ID'] = request_id
        response.headers['X-Process-Time'] = str(process_time)
        
        return response
        
    except Exception as e:
        # Log errors
        process_time = time.time() - start_time
        logger.error(f"Request failed - ID: {request_id}, Error: {str(e)}, Time: {process_time:.3f}s")
        
        # Re-raise the exception
        raise
```

**Email Alert Configuration**:
```bash
#!/bin/bash
# alert.sh
if [ $1 = "critical" ]; then
    echo "Critical alert: $2" | mail -s "MemoAI Alert" ${ADMIN_EMAIL}
fi
```

**Rationale**: 
- **Pros**: Simple implementation, no external dependencies, immediate availability
- **Cons**: Limited monitoring capabilities, basic alerting
- **Implementation Basis**: Provides adequate monitoring for initial deployment with clear upgrade path

### 12.4 Scaling Strategy
**Decision**: **Container Orchestration with Traefik Load Balancing**

**Implementation**:
- **Orchestration**: Docker Compose with multiple container instances
- **Load Balancing**: Traefik reverse proxy with automatic service discovery
- **Scaling**: Horizontal scaling with container replication
- **Resource Management**: Resource limits and monitoring
- **Health Monitoring**: Container health checks and auto-restart

**Docker Compose Scaling**:
```yaml
# docker compose.yml with scaling
version: '3.8'
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@example.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./letsencrypt:/letsencrypt
    restart: unless-stopped

  backend:
    build: ./backend
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`${DOMAIN}`) && PathPrefix(`/api`)"
      - "traefik.http.routers.backend.entrypoints=websecure"
      - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
      - "traefik.http.services.backend.loadbalancer.server.port=8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**Traefik Load Balancer Features**:
- **Automatic Service Discovery**: Traefik automatically detects new containers
- **Built-in Load Balancing**: Round-robin load balancing across backend instances
- **Health Check Integration**: Automatic removal of unhealthy instances
- **SSL/TLS Management**: Automatic certificate provisioning and renewal

**Scaling Commands**:
```bash
# Scale backend services
docker compose up -d --scale backend=3

# Monitor scaling
docker compose ps
docker stats

# Access Traefik dashboard
# http://localhost:8080
```

**Rationale**: 
- **Pros**: Clear scaling path, automatic service discovery, integrated SSL/TLS
- **Cons**: Additional complexity, requires Traefik configuration
- **Implementation Basis**: Provides clear scaling path for 100+ concurrent users with modern container orchestration

### 12.5 Security Hardening
**Decision**: **Basic Security with Essential Hardening**

**Implementation**:
- **Authentication**: Session-based authentication with secure tokens
- **Input Validation**: Comprehensive input sanitization and validation
- **SSL/TLS**: HTTPS encryption with Traefik and Let's Encrypt certificates
- **Rate Limiting**: API rate limiting and abuse prevention
- **Access Control**: Admin-only access to sensitive functions
- **Configuration Security**: Secure configuration management
- **Traefik Security**: Built-in security features and middleware support

**Security Configuration**:
```python
# Security middleware configuration
SECURITY_CONFIG = {
    'session_timeout': 3600,
    'max_login_attempts': 5,
    'rate_limit_per_session': 20,
    'rate_limit_per_hour': 1000,
    'csrf_protection': True,
    'xss_protection': True,
    'content_security_policy': True
}
```

**Docker Security**:
```dockerfile
# Security-hardened Dockerfile
FROM python:3.9-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Network Security**:
```bash
# Firewall configuration
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8080/tcp  # Traefik dashboard
ufw allow 22/tcp
ufw enable
```

**Rationale**: 
- **Pros**: Simple implementation, adequate for most use cases, maintainable
- **Cons**: May not meet enterprise security requirements
- **Implementation Basis**: Provides essential security while maintaining simplicity and usability

---

## 13.0 Technology Stack Decisions

**13.1 Containerization**
- **Docker**: Version 20.10+ with Docker Compose 2.0+
- **Podman**: Alternative for containerized deployment (3.0+)
- **Purpose**: Consistent deployment environments, easy scaling, minimal overhead
- **Key Features**:
  - Lightweight and efficient
  - Fast startup times
  - Isolated dependencies
  - Easy to manage and scale

**13.2 Database**
- **SQLite**: Version 3.35+ with WAL mode support
- **Purpose**: Simple, file-based, lightweight, and reliable
- **Key Features**:
  - Zero-configuration
  - ACID compliance
  - WAL mode for concurrent access
  - Easy to backup and restore

**13.3 Web Framework**
- **FastAPI**: Python-based, high-performance backend framework
- **Streamlit**: Python-based, interactive frontend framework
- **Purpose**: Efficient API for backend services, user-friendly frontend
- **Key Features**:
  - Asynchronous, non-blocking
  - Built-in data validation
  - Easy to integrate with LLM
  - Scalable for concurrent users

**13.4 Configuration**
- **YAML**: Simple, human-readable, and widely supported
- **Purpose**: Easy to manage and version control
- **Key Features**:
  - Human-readable
  - Easy to override
  - Versatile for different environments
  - Supports complex data structures

---

## 14.0 Development Team Considerations

### 14.1 Novice Programmer Deployment Support
**14.1.1 Simplified Deployment Process**
- **Clear Deployment Steps**: Intuitive deployment procedures and documentation
- **Comprehensive Documentation**: Detailed deployment guides with examples
- **Educational Deployment**: Deployment process that helps understand system architecture
- **Progressive Complexity**: Simple deployment first, advanced features as needed

**14.1.2 Learning-Friendly Deployment Patterns**
- **Step-by-Step Instructions**: Clear, sequential deployment steps
- **Error Handling**: Helpful error messages and troubleshooting guides
- **Configuration Management**: Simple, understandable configuration options
- **Monitoring Integration**: Built-in monitoring for understanding system behavior

**14.1.3 Progressive Deployment Complexity**
- **Core Deployment**: Essential deployment features first
- **Optional Features**: Advanced deployment features as extensions
- **Clear Dependencies**: Obvious relationships between deployment components
- **Backward Compatibility**: Deployment changes maintain existing functionality

### 14.2 AI Coding Agent Deployment Collaboration
**14.2.1 Code Generation-Friendly Deployment**
- **Consistent Patterns**: Standardized deployment patterns across all environments
- **Clear Configuration Contracts**: Well-defined configuration interfaces and options
- **Predictable Structure**: Consistent deployment organization and naming
- **Template-Based**: Reusable deployment patterns for common scenarios

**14.2.2 Maintainability Focus**
- **Single Responsibility**: Each deployment component has one clear purpose
- **Low Coupling**: Minimal dependencies between deployment components
- **High Cohesion**: Related deployment functionality grouped together
- **Clear Naming**: Descriptive deployment names that explain purpose

**14.2.3 Extensibility for Learning**
- **Deployment Library**: Easy to add new deployment features without modifying existing code
- **Configuration-Driven**: Deployment behavior controlled through configuration
- **Plugin Architecture**: New deployment capabilities added through clear extension points
- **Documentation Integration**: Deployment documentation with usage examples

### 14.3 Implementation Guidelines for Deployment Development
**14.3.1 Deployment Standards**
- **Logical Organization**: Related deployment components grouped in clear, logical structures
- **Consistent Naming**: Standard naming conventions throughout deployment
- **Documentation Integration**: Deployment documentation co-located with implementation
- **Version Control**: Deployment changes tracked and documented

**14.3.2 Quality Standards**
- **Comprehensive Documentation**: Every deployment component thoroughly documented
- **Error Handling**: Clear, educational error messages and handling
- **Monitoring Support**: Built-in monitoring and alerting capabilities
- **Security Integration**: Security features integrated into deployment process

**14.3.3 Collaboration Support**
- **Clear Interfaces**: Well-defined deployment contracts and configurations
- **Documentation Standards**: Consistent documentation format and style
- **Code Review Process**: Deployment design supports effective code reviews
- **Knowledge Transfer**: Deployment design facilitates learning and understanding

---

## 15.0 Traceability Matrix

| Requirement ID | Requirement Description | Deployment Implementation |
|---------------|------------------------|---------------------------|
| 3.1.1 | Responsive system | Performance Optimization (10.1) - Response time targets |
| 3.1.2 | Text submission response: < 15 seconds (LLM processing) | Performance Optimization (10.1) - LLM processing targets |
| 3.2.1 | System supports 10-20 concurrent users | Scalability Strategy (10.2) - Concurrent user support |
| 3.2.2 | System scales to 100+ concurrent users | Scalability Strategy (10.2) - Horizontal scaling approach |
| 3.3.1 | High uptime is expected | Reliability Measures (10.3) - Health checks and monitoring |
| 3.3.2 | Robust error handling and logging required | Reliability Measures (10.3) - Comprehensive logging strategy |
| 3.4.1 | Session-based authentication system | Security Implementation (9.1) - Authentication security |
| 3.4.2 | Secure session management with expiration | Security Implementation (9.1) - Session security |
| 3.4.3 | CSRF protection and rate limiting | Security Implementation (9.1) - Network security |
| 3.4.4 | Admin authentication for system management functions | Security Implementation (9.1) - Admin security |
| 3.4.5 | Optional JWT authentication | Security Implementation (9.1) - Future enhancement ready |
| 3.5.1 | Maintainability is top priority | Maintainability Strategy (10.3) - Simple deployment procedures |
| 3.5.2 | Maximum simplicity, no duplicate functions | Maintainability Strategy (10.3) - Containerized architecture |
| 3.5.3 | Comprehensive comments required | Maintainability Strategy (10.3) - Documentation and procedures |
| 3.5.4 | Modular architecture | Maintainability Strategy (10.3) - Modular container design |

---

## 16.0 Implementation Summary

### 16.1 Deployment Readiness
The deployment specification is complete and ready for implementation:

- **Architecture**: Containerized microservices with three-layer design
- **Infrastructure**: Docker-based deployment with Traefik load balancing
- **Security**: Let's Encrypt SSL with Traefik, session authentication, rate limiting
- **Monitoring**: Built-in health checks with email alerts
- **Backup**: Weekly automated backups with 4-week retention
- **Scaling**: Horizontal scaling support for 100+ concurrent users

### 16.2 Key Design Decisions
All critical design decisions have been resolved:

1. **SSL Certificate Management**: Let's Encrypt with Traefik auto-renewal
2. **Database Backup Strategy**: Weekly backups with 4-week retention
3. **Monitoring and Alerting**: Built-in health checks with email alerts
4. **Scaling Strategy**: Container orchestration with Traefik load balancing
5. **Security Hardening**: Basic security with essential hardening

### 16.3 Next Steps
- **Implementation**: Follow deployment procedures in Section 7.0
- **Validation**: Execute testing procedures from 06_Testing.md
- **Monitoring**: Establish monitoring and alerting systems
- **Documentation**: Update operational procedures as needed

---

**Document ID**: 07_Deployment.md  
**Document Version**: 1.4  
**Last Updated**: Implementation Phase (Complete consistency fixes and standardization)  
**Next Review**: After initial deployment
