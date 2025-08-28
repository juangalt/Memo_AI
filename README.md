# Memo AI Coach

A full-stack web application for intelligent text evaluation and feedback using LLM technology.

## Overview

Memo AI Coach is a comprehensive text evaluation system that provides:
- **Text Evaluation**: Submit text for AI-powered analysis and feedback
- **Rubric-Based Scoring**: Structured evaluation using customizable grading criteria
- **Segment-Level Feedback**: Detailed feedback on specific text segments
- **Admin Management**: Configuration management and system administration
- **Session-Based Authentication**: Secure user sessions with admin support

## Architecture

The system follows a three-layer architecture:
- **Frontend**: Streamlit-based user interface with tabbed navigation
- **Backend**: FastAPI REST services with LLM integration
- **Data Layer**: SQLite database with YAML configuration files

## Quick Start

### Prerequisites

- Docker and Docker Compose
- LLM API credentials (Claude, OpenAI, or Gemini)
- Domain name (for production deployment)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd memoai
   ```

2. **Configure environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

3. **Required environment variables**:
   ```bash
   LLM_API_KEY=your-llm-api-key
   SECRET_KEY=your-secret-key
   ADMIN_PASSWORD=your-admin-password
   DOMAIN=your-domain.com
   ADMIN_EMAIL=admin@your-domain.com
   ```

4. **Deploy the application**:
   ```bash
   docker compose up -d --build
   ```

5. **Access the application**:
   - Frontend: https://your-domain.com
   - Backend API: https://your-domain.com/api
   - Traefik Dashboard: http://localhost:8080

## Configuration

The system uses 4 essential YAML configuration files:

- `config/rubric.yaml`: Grading criteria and scoring rubrics
- `config/prompt.yaml`: LLM prompt templates and instructions
- `config/llm.yaml`: LLM provider configuration and API settings
- `config/auth.yaml`: Authentication settings and session management

### Admin Access

- **Username**: admin
- **Password**: Set via ADMIN_PASSWORD environment variable
- **Access**: Admin page for configuration management

## Features

### Text Evaluation
- Submit text for comprehensive AI evaluation
- Receive overall scores and detailed feedback
- Get segment-level analysis with specific comments
- View strengths and improvement opportunities

### Admin Functions
- Edit YAML configuration files
- Manage system settings
- Access debug information
- Monitor system performance

### Security
- Session-based authentication
- Rate limiting and CSRF protection
- Secure configuration management
- Admin-only access controls

## Development

### Project Structure
```
memo_AI/
├── backend/                 # FastAPI backend services
├── frontend/                # Streamlit frontend application
├── config/                  # YAML configuration files
├── data/                    # SQLite database and data files
├── tests/                   # Comprehensive test suite (Phase 8)
│   ├── config/             # Environment configuration tests
│   ├── integration/        # System integration tests
│   ├── performance/        # Performance and load tests
│   ├── logs/              # Test results and reports
│   ├── run_production_tests.py  # Complete test runner
│   └── run_quick_tests.py       # Quick test runner
├── devspecs/               # Development specifications
├── devlog/                 # Development changelog
├── docs/                   # Documentation
├── logs/                   # Application logs
├── letsencrypt/            # SSL certificates
├── secrets/                # Secret files
├── docker-compose.yml      # Container orchestration
├── deploy-production.sh    # Production deployment script
├── .env                    # Environment variables
└── README.md              # This file
```
├── devspecs/           # Development specifications
├── frontend/           # Streamlit frontend application
├── backend/            # FastAPI backend application
├── config/             # Configuration files
├── data/               # Persistent data storage
├── logs/               # Application logs
├── letsencrypt/        # SSL certificate storage
├── docker-compose.yml  # Container orchestration
└── README.md          # Project documentation
```

### Local Development

1. **Set development environment**:
   ```bash
   APP_ENV=development
   DEBUG_MODE=true
   ```

2. **Run with development settings**:
   ```bash
   docker compose up -d
   ```

3. **Access development environment**:
   - Frontend: http://localhost:8501
   - Backend: http://localhost:8000

### Testing

Run the test suite:
```bash
# System integration testing (comprehensive)
python testing/test_system_integration.py

# Component-specific tests
python testing/test_admin.py      # Admin authentication and config
python testing/test_llm.py        # LLM service and evaluation
python testing/test_api.py        # Frontend-backend communication

# Docker-based testing (alternative)
docker compose run backend python testing/test_system_integration.py
```

## Deployment

### Production Deployment

1. **Configure production environment**:
   ```bash
   APP_ENV=production
   DEBUG_MODE=false
   DOMAIN=your-production-domain.com
   ```

2. **Set up SSL certificates**:
   - Let's Encrypt certificates are automatically managed by Traefik
   - Ensure DNS is configured for your domain

3. **Deploy with production settings**:
   ```bash
   docker compose up -d --build
   ```

### Scaling

Scale backend services for higher load:
```bash
docker compose up -d --scale backend=3
```

## Testing

### Production Test Suite
The project includes comprehensive testing infrastructure for production validation:

```bash
# Run complete Phase 8 production test suite (includes performance tests)
python3 tests/run_production_tests.py

# Run quick Phase 8 production test suite (excludes performance tests for speed)
python3 tests/run_quick_tests.py
```

### Test Coverage
- **Environment Configuration**: Domain, SSL, database, LLM API validation
- **Critical System Tests**: Container status, API health, sessions, evaluation workflow
- **Performance Tests**: Response time benchmarks, concurrent user simulation
- **Production Readiness**: System accessibility, security, functionality, monitoring

### Test Results
Test results are stored in `tests/logs/` with detailed JSON reports for analysis.

## Monitoring

### Health Checks
- Backend: `GET /health`
- Frontend: `GET /_stcore/health`
- Database: Connection and WAL mode validation

### Logs
- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- Debug logs: `logs/debug.log`

### Metrics
- Response times and throughput
- Error rates and system health
- LLM API usage and costs
- Database performance

## Backup and Recovery

### Automated Backups
- Weekly database backups
- 4-week retention policy
- Configuration file backups

### Manual Backup
```bash
# Create backup
docker compose exec backend python backup_db.py

# Restore backup
docker compose exec backend python restore_db.py backup_file.db
```

## Security

### Authentication
- Session-based authentication for users
- Admin authentication for system management
- Secure session tokens with expiration

### Data Protection
- No PII collection
- Session-based data isolation
- Encrypted configuration storage
- Secure session management

### Network Security
- HTTPS encryption with Let's Encrypt
- Rate limiting and abuse prevention
- CSRF protection
- Input validation and sanitization

## Support

### Documentation
- Complete specifications in `devspecs/` directory
- API documentation available at `/docs` endpoint
- Configuration file documentation

### Troubleshooting
- Check application logs in `logs/` directory
- Verify configuration files in `config/` directory
- Monitor health check endpoints
- Review Traefik dashboard for routing issues

## License

[License information]

## Contributing

[Contribution guidelines]
