# 06_Testing.md

## 1.0 How to Use This File

1.1 **Audience**  
AI coding agents and human developers.

1.2 **Purpose**  
Defines testing strategy, tooling and quality gates for Memo AI Coach.  
Built on specs `01_Requirements.md`–`05_UI_UX.md`.

1.3 **Next Steps**  
Consult during implementation and before reading `07_Deployment.md`.

---

## 2.0 Testing Framework and Environment

### 2.1 Core Tools
- **pytest** for backend unit and integration tests.
- **Reflex testing utilities** for component tests.
- **Playwright** for browser end‑to‑end flows.
- **coverage.py**, **flake8**, **mypy**, **bandit** for quality checks.

### 2.2 Database Strategy
- In‑memory SQLite for unit tests.
- Temporary SQLite file for integration and e2e tests to exercise migrations.

### 2.3 LLM Strategy
- Hybrid approach: mock provider by default; optional real call smoke tests with rate limiting.

---

## 3.0 Test Types

```yaml
Tests:
  unit:
    - services and utilities
    - data access layer
    - Reflex components (logic only)
  integration:
    - REST endpoints with FastAPI TestClient
    - database migrations and queries
    - configuration editing and validation
  end_to_end:
    - user submission -> evaluation -> chat -> pdf
    - admin YAML edit
  performance:
    - load tests with Locust (target 100 concurrent users)
  security:
    - basic auth/CSRF checks
```

---

## 4.0 Fixtures and Test Data

- Factory functions generate sample submissions, sessions and users.
- Mock LLM responses stored as JSON fixtures.
- YAML fixture files for valid/invalid configurations.
- Use temporary directories for PDF exports and cleanup after tests.

---

## 5.0 Continuous Integration

- GitHub Actions workflow runs on push and pull requests:
  1. `flake8` + `mypy` + `bandit`
  2. Unit tests with coverage
  3. Integration tests
- Nightly workflow executes end‑to‑end and load tests.
- Coverage threshold: **85% overall**, **100% critical paths** (evaluation, authentication).

---

## 6.0 Test Maintenance

- Update mocks when API contracts change.
- Keep fixtures small and deterministic.
- Tag long‑running tests and exclude by default.
- Document new test cases in code comments and this file when major features added.

---

## 7.0 Traceability Links

- Covers requirements 2.1‑2.7 and non‑functional 3.1‑3.5 from `01_Requirements.md`.
- Validates API definitions in `04_API_Definitions.md` and UI flows in `05_UI_UX.md`.
