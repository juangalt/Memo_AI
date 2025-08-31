# Development Guide
## Memo AI Coach

**Document ID**: 08_Development_Guide.md
**Document Version**: 1.0
**Last Updated**: Phase 9
**Status**: Draft

---

## 1.0 Coding Principles
Derived from project AGENTS guidelines:
- Favor simplicity and readability over abstraction.
- Each module serves a single responsibility.
- Provide docstrings and inline comments for educational clarity.
- Avoid editing `devspecs/` documents; `docs/` now acts as source of truth.
- Follow PEP 8 style with 4-space indentation and descriptive variable names.

## 2.0 Repository Structure
```
backend/       FastAPI service
vue-frontend/  Vue.js reactive interface
config/        YAML configuration files
tests/         Test suites
docs/          Comprehensive project documentation
```

## 3.0 Backend Development
- Entry point: `backend/main.py`.
- Data models in `backend/models/entities.py` reflect tables created by `init_db.py`.
- Services in `backend/services/` handle configuration, authentication and LLM integration.
- Use `evaluate_text_with_llm` for all evaluations; it handles prompt generation and error management.
- Error responses should use the standard `{data: null, meta, errors}` schema defined in API documentation.
- Add new endpoints by extending `backend/main.py` and documenting them in `docs/05_API_Documentation.md`.

## 4.0 Frontend Development
- Entry point: `vue-frontend/src/main.js`.
- `vue-frontend/src/services/api.js` provides HTTP client with automatic authentication headers.
- `vue-frontend/src/stores/auth.js` manages authentication state using Pinia.
- `vue-frontend/src/router/index.js` handles route-based navigation and access control.
- Follow Vue 3 Composition API patterns for reactive components.
- Views should be added under `vue-frontend/src/views/` with corresponding routes.
- Components should be added under `vue-frontend/src/components/` with clear, commented functions.
- **Layout Component**: Use Layout wrapper in view components when navigation is needed.
- **Tailwind CSS**: Use v3.4.17 (stable) with proper PostCSS configuration.
- **Authentication Flow**: Login redirects to `/text-input`, logout redirects to `/`.
- **Admin Access**: Conditional menu items based on `isAdmin` status.

## 5.0 Configuration & Secrets
- Never commit API keys or passwords. Use environment variables or `.env`.
- Configuration editing should go through admin API or `config_manager.py` to ensure validation and backups.
- When adding new configuration keys, update both `docs/04_Configuration_Guide.md` and validation logic.

## 5.1 Frontend Configuration
- **Tailwind CSS**: Use v3.4.17 (stable) for production. Avoid v4.x (beta) versions.
- **PostCSS**: Configure with `tailwindcss` plugin (not `@tailwindcss/postcss`).
- **Build Process**: Use `npm install` instead of `npm ci` for better dependency management.
- **CSS Classes**: All components use Tailwind classes for consistent styling.

## 6.0 Testing
- Tests reside in `tests/` and cover environment, integration, performance and security.
- `tests/run_quick_tests.py` runs fast checks; `tests/run_production_tests.py` includes performance suite.
- New features require corresponding unit or integration tests.
- Test files mirror module paths to simplify discovery.

## 7.0 Contribution Workflow
1. Review relevant docs in this directory before coding.
2. Implement changes in small, well-documented commits.
3. Update changelog in `devlog/changelog.md` for historical context.
4. Add or update tests when modifying behavior.
5. Run appropriate test suites and document results in pull requests.

## 8.0 References
- `AGENTS.md`
- `tests/README.md`
