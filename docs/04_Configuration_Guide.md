# Configuration Guide
## Memo AI Coach

**Document ID**: 04_Configuration_Guide.md
**Document Version**: 1.0
**Last Updated**: Phase 9
**Status**: Draft

---

## 1.0 Configuration Overview
All runtime behavior is controlled by four YAML files in `config/`.
Files are mounted read-only into containers at `/app/config/` and validated by `backend/validate_config.py`.
Configuration edits made through the Admin interface create timestamped backups under `config/backups/` before any changes are written.

## 2.0 Environment Variables
`.env` provides base values such as `DOMAIN`, `LLM_API_KEY`, and optional `ADMIN_PASSWORD` for initial setup.
Environment variables can override YAML fields (`LLM_API_KEY`, `SESSION_TIMEOUT`).
| Variable | Description |
|----------|-------------|
| `DOMAIN` | Public domain name used by Traefik for routing and certificate generation |
| `LLM_API_KEY` | Anthropic key for Claude API access |
| `ADMIN_PASSWORD` | Optional: Initial administrator password for database setup (default: admin123) |
| `MAX_CONCURRENT_USERS` | Target concurrency for performance testing |
| `SESSION_TIMEOUT` | Override for session expiration in minutes |

## 3.0 YAML Files

### 3.1 rubric.yaml
Defines evaluation rubric and scoring categories.
Key sections:
- `rubric`: name, description, total_weight, scoring_scale, criteria with weights and scoring guidance.
- `scoring_categories`: machine-friendly keys for each criterion.
- `evaluation_framework`: lists strengths, improvement opportunities, segment evaluation metadata and frameworks.
Example:
```yaml
rubric:
  name: Healthcare Investment Memo
  total_weight: 100
  criteria:
    thesis_clarity:
      weight: 20
      description: "Clarity of investment thesis"
```

### 3.2 prompt.yaml
Holds prompt templates and instruction lists used to query the LLM.
Important keys:
- `templates.evaluation_prompt.system_message` and `user_template`.
- `instructions` blocks for evaluation, scoring and segment feedback.
- `prompt_variables` describing dynamic fields injected by backend.
Example snippet showing variable substitution:
```yaml
templates:
  evaluation_prompt:
    user_template: |
      Evaluate the following memo:
      {{ submission_text }}
```

### 3.3 llm.yaml
Configures LLM provider and runtime limits.
- `provider`: name, base URL, model, API version.
- `api_configuration`: API key, timeouts, retries and token limits.
- `request_settings` for text length and chunking.
- `response_handling` and `error_handling` options.
- `performance_optimization` enforcing <15s processing.
- `fallback_configuration` for alternate providers.
- `validation_rules` defining allowed ranges for key settings.
Example configuration:
```yaml
provider: anthropic
api_configuration:
  model: claude-3-sonnet
  timeout: 15
```

### 3.4 auth.yaml
Configures authentication and security parameters. See `docs/02b_Authentication_Specifications.md` for complete authentication configuration details and examples.

## 4.0 Validation
Run `python3 backend/validate_config.py` to ensure all configs exist and satisfy required fields.
Failure details are logged and exit code signals success.

## 5.0 Frontend Configuration
The Vue.js frontend has specific configuration requirements:

### 5.1 Tailwind CSS Configuration
- **Version**: Use Tailwind CSS v3.4.17 (stable) for production
- **PostCSS**: Configure with `tailwindcss` plugin (not `@tailwindcss/postcss`)
- **Build Process**: Use `npm install` instead of `npm ci` for better dependency management
- **CSS Classes**: All components use Tailwind classes for consistent styling

### 5.2 Package Configuration
```json
// package.json
{
  "dependencies": {
    "tailwindcss": "^3.4.17"
  },
  "devDependencies": {
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

### 5.3 PostCSS Configuration
```javascript
// postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

### 5.4 Docker Configuration
```dockerfile
# Dockerfile
RUN npm install  # Use npm install, not npm ci
```

## 6.0 References
- `docs/02b_Authentication_Specifications.md` - Complete authentication configuration details
- `config/*.yaml`
- `backend/services/config_service.py`
- `backend/services/config_manager.py`
- `devlog/vue_frontend_implementation_plan.md` - Vue.js frontend implementation plan
