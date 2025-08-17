# 07_Deployment.md

## 1.0 How to Use This File

1.1 **Audience**  
AI coding agents and human developers.

1.2 **Purpose**  
Outlines deployment architecture and procedures for Memo AI Coach.  
Based on specifications `01_Requirements.md`–`06_Testing.md`.

1.3 **Next Steps**  
Consult before setting up environments and automation.

---

## 2.0 Container and Environment Strategy

### 2.1 Architecture
- Docker Compose with separate containers for **frontend**, **backend**, and **reverse proxy**.
- Shared volume for SQLite database and YAML configuration files.

### 2.2 Compose Files
- `docker-compose.yml` – development/MVP.
- `docker-compose.prod.yml` – production overrides (resource limits, replicas, proxy config).

### 2.3 Environment Configuration
- Values supplied via `.env` files; production secrets injected using Docker secrets or host environment variables.
- LLM API keys and JWT secret never committed to repository.

---

## 3.0 Deployment Workflow

```yaml
Workflow:
  build_images:
    - docker compose build
  run_local:
    - docker compose up
  run_prod:
    - docker compose -f docker-compose.prod.yml up -d
  ci_cd:
    - GitHub Actions builds and pushes images on main branch
    - optional manual approval step for production deploy
```

---

## 4.0 Networking and Security

- Reverse proxy (Caddy or Nginx) terminates TLS and routes to frontend/backends.
- Only ports 80/443 exposed externally.
- HTTP security headers enabled; rate limiting at proxy level.
- CSRF and session cookies set as `secure` and `httpOnly` in production.

---

## 5.0 Persistence and Backups

- SQLite database stored on Docker volume `db_data`.
- Nightly cron job copies database and YAML configs to off‑container storage.
- PDF exports written to temporary directory and removed after download.

---

## 6.0 Scaling Path

- MVP: single instance of each container on one host.
- Production: scale backend containers horizontally behind proxy (`docker compose up --scale backend=3`).
- If concurrency >100, migrate to PostgreSQL and externalize database service.

---

## 7.0 Monitoring and Logging

- Containers log to stdout; aggregated with `docker logs` or external service (e.g., Loki).
- Basic health endpoints checked by proxy.
- Optional Prometheus/Grafana stack for metrics.

---

## 8.0 Disaster Recovery

- Backup restore script recreates volume from latest snapshot.
- Versioned Docker images allow rollback by redeploying previous tag.

---

## 9.0 Traceability Links

- Requirements: scalability (3.2), reliability (3.3), security (3.4), performance (3.1).
- Architecture references: Docker deployment and scaling plan from `02_Architecture.md`.

## 10.0 Deployment Directory Structure
```
/
├── docker-compose.yml          # base compose file for development/MVP
├── docker-compose.prod.yml     # production overrides
├── frontend/
│   ├── Dockerfile
│   └── app/...
├── backend/
│   ├── Dockerfile
│   └── app/...
├── reverse-proxy/
│   └── Caddyfile or nginx.conf
├── .env.example                # sample environment variables
└── devspecs/
    └── *.md                    # project specifications
```
