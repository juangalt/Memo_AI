# Maintenance Guide
## Memo AI Coach

**Document ID**: 11_Maintenance_Guide.md
**Document Version**: 1.0
**Last Updated**: Phase 9
**Status**: Draft

---

## 1.0 Routine Tasks
- Monitor container health with `docker compose ps` and `/health` endpoint.
- Review logs in `logs/` for backend and frontend; rotate or archive as needed.
- Ensure Let's Encrypt certificates auto-renew via Traefik.
- Check database size in `data/memoai.db` and back up regularly.
- Verify available disk space and prune unused Docker images monthly (`docker image prune`).
- Review configuration backups and remove outdated versions to conserve storage.

## 2.0 Configuration Changes
- Use Admin page or admin API to update YAML configurations.
- Each change creates a timestamped backup under `config/backups/`.
- After updates, verify using `backend/validate_config.py` and `/health` endpoints.
- Document any configuration change in internal change log or ticketing system for traceability.

## 3.0 Database Maintenance
- SQLite WAL mode requires periodic checkpointing if database grows large:
```bash
docker compose exec backend sqlite3 /app/data/memoai.db 'PRAGMA wal_checkpoint;'
```
- Maintain backups of `data/` directory.
- For large datasets, schedule automated backups and compression using cron or host scheduler.

## 4.0 Updating Containers
- Pull latest code and rebuild:
```bash
git pull
./deploy-production.sh
```
- Script handles stop/start cycle safely.
- Validate running version after deployment using `/health` and test suite.

## 5.0 Monitoring
- LLM service reports processing time and error rates in logs.
- Traefik dashboard (`https://<domain>/dashboard`) provides request metrics.
- Set up external uptime monitoring to alert when health endpoints fail.

## 6.0 Incident Response
- In case of configuration errors, restore from `config/backups/` using `config_manager.restore_backup` or manual copy.
- If container fails health checks, check logs and redeploy.
- For database corruption, restore from most recent backup and re-run pending migrations with `init_db.py`.

## 7.0 References
- `backend/services/config_manager.py`
- `backend/services/auth_service.py`
- `deploy-production.sh`
