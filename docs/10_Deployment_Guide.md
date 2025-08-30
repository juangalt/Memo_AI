# Deployment Guide
## Memo AI Coach

**Document ID**: 10_Deployment_Guide.md
**Document Version**: 1.0
**Last Updated**: Phase 9
**Status**: Draft

---

## 1.0 Overview
Production deployment uses Docker Compose with Traefik reverse proxy and automatic SSL via Let's Encrypt.
All services run as non-root users and depend only on Docker, keeping the host environment minimal.

## 2.0 Pre-Deployment Steps
1. Install Docker and docker-compose.
2. Copy `env.example` to `.env` and configure domain, email, API keys, secret key and performance limits.
3. Ensure directories `config/`, `data/`, `logs/` and `letsencrypt/` exist.
4. Validate configuration files:
```bash
cd backend
python3 validate_config.py
cd ..
```

## 3.0 Deployment Script
Run:
```bash
./deploy-production.sh
```
The script:
- Loads `.env`.
- Sets file permissions for mounted volumes.
- Validates configuration files.
- Builds images with `docker compose build`.
- Stops existing containers and launches new ones with `docker compose up -d`.
- Performs health checks and configuration path tests inside containers.
- Emits status messages and aborts on any failure to prevent partial deployments.

## 4.0 Container Services
- **traefik**: HTTPS termination, rate limiting and security headers.
- **backend**: FastAPI API at port 8000.
- **vue-frontend**: Vue.js UI served via nginx at port 80.
- All services run behind Traefik; only ports 80/443 are exposed externally.

## 5.0 Volume Mapping
| Host Path | Container Path | Mode |
|-----------|----------------|------|
| `./config` | `/app/config` | read-only |
| `./data` | `/app/data` | read-write |
| `./logs` | `/app/logs` | read-write |
Backups of configuration files are written under `config/backups/` and persist across deployments.

## 6.0 Health Verification
- `docker compose ps` shows running services.
- `curl http://localhost:8000/health` backend status.
- `curl http://localhost:80` Vue frontend status.
- Traefik dashboard (optional) available at `:8080` if enabled in `.env`.

## 7.0 SSL
Traefik automatically issues certificates for `DOMAIN` defined in `.env`. Ensure DNS points to server and ports 80/443 are open.
Certificates are stored in `./letsencrypt` and renewed automatically; back up this directory for migrations.

## 8.0 Scaling and Updates
- Scale services by adjusting `docker-compose.yml` replicas and re-running the deployment script.
- To update images, pull latest code, rebuild with `docker compose build` and redeploy.
- Roll back by restoring previous config backups and redeploying with prior commit.

## 9.0 Monitoring and Logs
- All containers log to `logs/` with separate files per service.
- Use `docker compose logs -f <service>` for live monitoring.
- Health endpoint failures should trigger investigation of respective service logs.

## 10.0 References
- `docker-compose.yml`
- `deploy-production.sh`
