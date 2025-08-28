# Troubleshooting Guide
## Memo AI Coach

**Document ID**: 12_Troubleshooting_Guide.md
**Document Version**: 1.0
**Last Updated**: Phase 9
**Status**: Draft

---

## 1.0 Common Issues

### 1.1 Backend Fails to Start
- **Symptom**: `docker compose up` shows backend exiting.
- **Resolution**: Run `python3 backend/validate_config.py` to confirm YAML validity. Check `logs/` for stack traces.

### 1.2 Frontend Cannot Reach Backend
- **Symptom**: UI displays "Backend service is not available".
- **Resolution**: Ensure backend container is running and `BACKEND_URL` environment variable points to `http://backend:8000` in docker-compose.

### 1.3 Authentication Errors
- **Symptom**: Admin login fails with `AUTHENTICATION_ERROR`.
- **Resolution**: Verify credentials in `auth.yaml` and `.env`. Check brute force settings; repeated attempts may lock account temporarily.

### 1.4 Configuration Update Fails
- **Symptom**: Admin tab returns "Configuration update failed".
- **Resolution**: YAML syntax invalid. Use validator or run `backend/validate_config.py`. Restore previous version from `config/backups/`.

### 1.5 LLM API Errors
- **Symptom**: Evaluation returns `LLM_ERROR`.
- **Resolution**: Confirm `LLM_API_KEY` is set. If running in mock mode, ensure expectations accordingly. Check network connectivity to Anthropic API.

### 1.6 Database Locked or Slow
- **Symptom**: API responses indicate database errors.
- **Resolution**: Verify WAL mode with `PRAGMA journal_mode`; ensure file permissions on `data/` allow write access. Run WAL checkpoint if file grows too large.

### 1.7 Port Conflicts
- **Symptom**: `docker compose up` reports port already in use.
- **Resolution**: Ensure no other service uses ports 80, 443, 8000 or 8501. Adjust `docker-compose.yml` to map to free ports if necessary.

### 1.8 Certificate Renewal Failures
- **Symptom**: HTTPS requests return certificate expired errors.
- **Resolution**: Check Traefik logs for Let's Encrypt errors. Confirm DNS records and port 80 availability. Delete `letsencrypt/` directory to force renewal if necessary.

### 1.9 Session Expired
- **Symptom**: Admin actions fail with `INVALID_SESSION`.
- **Resolution**: Login again to obtain a fresh token. Increase `session_timeout` in `auth.yaml` if appropriate.

## 2.0 Logs and Diagnostics
- Backend logs: `logs/backend.log` (if configured) or container logs.
- Frontend logs: `logs/frontend.log`.
- Traefik logs: container logs via `docker compose logs traefik`.
- Use `docker inspect <container>` to view environment variables and configuration when debugging.

## 3.0 Support
- Review documentation in `docs/` for detailed procedures.
- Consult `devlog/changelog.md` for context on past issues and resolutions.
- For unresolved issues, open a ticket with detailed logs and steps to reproduce.

## 4.0 References
- `backend/validate_config.py`
- `config/backups/`
- `devlog/changelog.md`
