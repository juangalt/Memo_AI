# Code Simplification and Modularity Plan

## Centralize Configuration Path Detection

**Description:** Multiple services contain repeated logic to locate configuration files by checking the `CONFIG_DIR` environment variable or using their own default paths. This duplication makes behavior inconsistent and complicates updates when lookup rules change.

**Goal:** Provide one authoritative helper for locating configuration directories so every service resolves paths consistently without repeating environment checks.

### Step 1: Create Shared Utility
- **Implementation:** Add `backend/services/path_utils.py` with `resolve_config_dir()` that returns `os.getenv("CONFIG_DIR")` if set and valid, otherwise `"/app/config"`.
- **Tests:** `pytest tests/unit/services/test_path_utils.py::test_resolve_config_dir`
- **Success Criteria:** The helper returns the correct path for env-var set and unset scenarios; test passes.

### Step 2: Refactor Services
- **Implementation:** In constructors for `ConfigService`, `ConfigManager`, `AuthService`, and `EnhancedLLMService`, import and call `resolve_config_dir()` instead of duplicating path logic.
- **Tests:** `pytest tests/integration/test_critical_system_local.py::test_config_loading`
- **Success Criteria:** All tests pass and constructors no longer contain direct environment checks.

### Step 3: Remove Obsolete Checks
- **Implementation:** Search for remaining `CONFIG_DIR` references outside `path_utils.py` and delete any duplicated logic.
- **Verification:** `rg "CONFIG_DIR" -l backend | grep -v path_utils`
- **Success Criteria:** Command returns no files, confirming the helper is the single source of path logic.

---

## Consolidate Response-Formatting Helpers

**Description:** `create_standardized_response` and `create_error_response` are defined both in `main.py` and `decorators.py`, forcing two implementations to stay in sync and risking inconsistent API outputs.

**Goal:** Ensure all API responses share the same structure by storing response helpers in one module and importing them wherever needed.

### Step 1: Create Central Module
- **Implementation:** Add `backend/utils/responses.py` with shared `create_standardized_response(data, status_code=200)` and `create_error_response(code, message, field=None, details=None, status_code=400)`.
- **Tests:** `pytest tests/unit/utils/test_responses.py`
- **Success Criteria:** Unit tests confirm helper outputs match expected structures.

### Step 2: Refactor Existing Modules
- **Implementation:** Remove local helper definitions from `backend/main.py` and `backend/decorators.py`; import the shared functions instead.
- **Tests:** `pytest tests/integration/test_critical_system_local.py::test_response_shapes`
- **Success Criteria:** API responses remain consistent and duplicated functions are eliminated.

### Step 3: Guard Against Future Duplication
- **Implementation:** Run a linter or add a check to ensure helpers are imported rather than redefined.
- **Verification:** `pylint backend/main.py backend/decorators.py`
- **Success Criteria:** Linter passes with no warnings about redefining helpers.

---

## Streamline Health-Check Routes

**Description:** Health endpoints repeat similar logic and instantiate new service objects for each request, increasing overhead and clutter.

**Goal:** Group health checks into a dedicated router with shared service instances so endpoints remain lightweight and maintainable.

### Step 1: Introduce Router and Helpers
- **Implementation:** Create `backend/routes/health.py` containing a FastAPI router that instantiates shared services once and defines helper functions for repeated checks.
- **Tests:** `pytest tests/unit/routes/test_health.py`
- **Success Criteria:** Router returns correct structures and mocks verify services are instantiated only once.

### Step 2: Refactor Main Application
- **Implementation:** Remove individual health endpoints from `backend/main.py` and include the new router via `app.include_router(health.router)`.
- **Tests:** `pytest tests/integration/test_critical_system_local.py::test_health_endpoints`
- **Success Criteria:** All health routes remain accessible and return expected data.

### Step 3: Document and Simplify
- **Implementation:** Add module docstring and comments in `health.py` explaining service reuse and how to extend checks.
- **Verification:** `pydocstyle backend/routes/health.py`
- **Success Criteria:** Documentation lints pass without errors.

---

## Centralize Logging Configuration

**Description:** Several modules call `logging.basicConfig` separately, leading to inconsistent formats and levels across the codebase.

**Goal:** Configure logging once during application startup so all modules share the same formatting and log level.

### Step 1: Create Logging Configuration Module
- **Implementation:** Add `backend/logging_config.py` with `configure_logging()` that defines handlers, formatters, and log levels (optionally read from environment variables).
- **Tests:** `pytest tests/unit/test_logging_config.py`
- **Success Criteria:** Running `configure_logging()` initializes logging without errors and applies the expected format.

### Step 2: Apply at Startup
- **Implementation:** Call `configure_logging()` in `backend/main.py` during startup and remove `logging.basicConfig` calls from `auth_service.py`, `language_detection.py`, `llm_service.py`, `config_manager.py`, `init_db.py`, and `validate_config.py`.
- **Tests:** `pytest tests/integration/test_critical_system_local.py::test_logging_format`
- **Success Criteria:** Logs from different modules share the same format and level.

### Step 3: Verify Usage
- **Implementation:** Ensure all modules acquire loggers via `logging.getLogger(__name__)` and search for leftover `basicConfig` calls.
- **Verification:** `rg "basicConfig" -n backend`
- **Success Criteria:** Command returns no results, confirming unified logging configuration.

---

## Simplify Session Validation and Service Creation

**Description:** `AuthService` exposes both module-level and instance `validate_session` functions, and `Session.create` repeatedly instantiates `ConfigService`. This duplication complicates the authentication flow and wastes resources.

**Goal:** Rely on injected service instances for session validation and configuration, avoiding redundant object creation and clarifying responsibilities.

### Step 1: Remove Module-Level Wrapper
- **Implementation:** Delete the top-level `validate_session` from `backend/services/auth_service.py` and stop exporting it in `backend/services/__init__.py`.
- **Tests:** `pytest tests/unit/services/test_auth_service.py::test_validate_session`
- **Success Criteria:** Tests interact solely with the class method; wrapper no longer exists.

### Step 2: Inject AuthService
- **Implementation:** Modify `backend/decorators.py::require_auth` and related routes in `backend/main.py` to receive an `AuthService` instance via dependency injection instead of importing a global function.
- **Tests:** `pytest tests/integration/test_critical_system_local.py::test_auth_flow`
- **Success Criteria:** Authentication works using the injected service; no module-level wrappers remain.

### Step 3: Refactor Session.create
- **Implementation:** In `backend/models/entities.py::Session.create`, accept a `ConfigService` parameter and remove internal instantiation. Update `AuthService.authenticate` and other call sites to pass the shared instance.
- **Tests:** `pytest tests/unit/models/test_session.py::test_create_uses_injected_config_service`
- **Success Criteria:** Session creation uses the injected `ConfigService`; mocks show no new instances.

### Step 4: Update Call Sites
- **Implementation:** Ensure a single `ConfigService` is created at startup and reused wherever `Session.create` or `AuthService` needs it.
- **Tests:** `pytest tests/integration/test_production_readiness.py::test_single_config_service_instance`
- **Success Criteria:** Only one `ConfigService` instance exists during request handling; all tests pass.

