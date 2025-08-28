# Testing Guide
## Memo AI Coach

**Document ID**: 09_Testing_Guide.md
**Document Version**: 1.0
**Last Updated**: Phase 9
**Status**: Draft

---

## 1.0 Test Philosophy
Testing covers configuration, integration, performance and security. All tests reside in the `tests/` directory and are executable with standard Python.
The goal is to maintain high confidence without requiring complex infrastructure. Tests use mock services where external dependencies would otherwise be required.

## 2.0 Test Categories
- **Configuration Tests** – ensure environment and config files are valid (`tests/config/test_environment.py`).
- **Integration Tests** – verify API endpoints, session management and LLM mock responses (`tests/integration/test_critical_system_local.py` and `test_production_readiness.py`).
- **Performance Tests** – load testing against response time requirements (`tests/performance/test_load.py`).
- **Security Tests** – basic security validation for development (`tests/test_security_dev.py`).
- **End-to-End Smoke Tests** – run against production deployment to verify critical paths (`tests/integration/test_production_readiness.py`).

## 3.0 Running Tests
### Quick Suite
Runs all non-performance tests.
```bash
python3 tests/run_quick_tests.py
```

### Full Production Suite
Includes performance tests; may take longer.
```bash
python3 tests/run_production_tests.py
```
This suite spins up additional load to verify the <15s response requirement. Ensure the environment variable `LLM_API_KEY` is set or mock mode is enabled.

### Individual Tests
Execute any module directly with Python, e.g. `python3 tests/config/test_environment.py`.
Use `-k` to run subsets with pytest style discovery if preferred.

## 4.0 Test Outputs
Results are stored in `logs/`:
- `quick_production_test_results.json`
- `production_test_suite_results.json`
- Category-specific results for environment, critical system, performance, readiness and security.
Each JSON result file includes summary statistics and individual assertion outcomes. Logs are rotated between runs to avoid stale data.

## 5.0 Test Data
Tests interact with running containers; ensure backend and frontend services are available when running integration or performance tests.
For local development, use mock LLM responses by leaving `LLM_API_KEY` unset. Performance tests can be adjusted via environment variables in `.env` such as `MAX_CONCURRENT_USERS`.

## 6.0 References
- `tests/README.md`
- `tests/run_quick_tests.py`
- `tests/run_production_tests.py`
