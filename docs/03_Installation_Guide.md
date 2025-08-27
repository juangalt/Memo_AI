# Installation Guide
## Memo AI Coach

**Document ID**: 03_Installation_Guide.md
**Document Version**: 1.0
**Last Updated**: Phase 9
**Status**: Draft

---

## 1.0 Prerequisites
- Docker and docker-compose installed.
- Python 3.11+ for local utilities.
- Valid Anthropic API key for production use.
- Unix-like environment tested on Ubuntu 22.04 LTS.
- At least 2 GB free disk space for containers and database.

## 2.0 Repository Setup
```bash
git clone https://github.com/.../Memo_AI.git
cd Memo_AI
cp env.example .env
```
Configure `.env` with domain, API key and secret values.
The `.env` file is used by both the deploy script and `docker-compose.yml` to set environment variables at runtime.

## 3.0 Configuration Files
Ensure `config/` contains:
- `rubric.yaml`
- `prompt.yaml`
- `llm.yaml`
- `auth.yaml`
All files are mounted read-only into containers at `/app/config`.
Each file should be validated prior to starting services:
```bash
python3 backend/validate_config.py
```

## 4.0 Database Initialization
For local setup:
```bash
cd backend
python3 init_db.py
cd ..
```
This creates `data/memoai.db` with WAL mode and default admin user.
The script can be run repeatedly; it will ensure schema migrations and default data are present without damaging existing records.

## 5.0 Running the Application
### 5.1 Development (local Python)
- Start backend: `uvicorn backend.main:app --reload`
- Start frontend: `streamlit run frontend/app.py`
Environment variables from `.env` should be exported before launching services:
```bash
export $(grep -v '^#' .env | xargs)
```

### 5.2 Production (containers)
```bash
./deploy-production.sh
```
Script validates configs, builds images, sets permissions and starts services via `docker compose up -d`.
Logs are written to `logs/` and can be tailed for troubleshooting:
```bash
docker compose logs -f backend
```

## 6.0 Verification
- Backend health: `curl http://localhost:8000/health`
- Frontend health: `curl http://localhost:8501/_stcore/health`
- Database check: ensure `data/memoai.db` exists and contains tables `sessions`, `submissions`, `evaluations`.
- Configuration check: from Admin tab verify YAML content loads without errors.

---

## 7.0 References
- `deploy-production.sh`
- `backend/init_db.py`
