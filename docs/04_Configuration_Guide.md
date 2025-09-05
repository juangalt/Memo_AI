# Configuration Guide
## Memo AI Coach

**Document ID**: 04_Configuration_Guide.md
**Document Version**: 3.0
**Last Updated**: Phase 11 - LLM Refactor & Health Security Implementation
**Status**: Active

---

## 1.0 Configuration Overview
All runtime behavior is controlled by four YAML files in `config/`.
Files are mounted read-only into containers at `/app/config/` and validated by Pydantic models in `backend/models/config_models.py`.
Configuration edits made through the Admin interface create timestamped backups under `config/backups/` before any changes are written.

## 2.0 Environment Variables
`.env` provides base values such as `DOMAIN`, `CLAUDE_API_KEY`, and optional `ADMIN_PASSWORD` for initial setup.
Environment variables can override YAML fields and runtime values (`CLAUDE_API_KEY`, `SESSION_TIMEOUT`).
| Variable | Description |
|----------|-------------|
| `DOMAIN` | Public domain name used by Traefik for routing and certificate generation |
| `CLAUDE_API_KEY` | Anthropic key for Claude API access |
| `ADMIN_PASSWORD` | Optional: Initial administrator password for database setup (default: admin123) |
| `MAX_CONCURRENT_USERS` | Target concurrency for performance testing |
| `SESSION_TIMEOUT` | Override for session expiration in minutes |

## 3.0 Configuration Files

### 3.1 `config/rubric.yaml` (DEPRECATED)
**Status**: This file is deprecated and no longer used for rubric logic. All rubric content has been moved to `prompt.yaml`.

**Deprecation Notice**:
```yaml
status: "deprecated"
message: "This file is no longer used. All rubric content has been moved to prompt.yaml"
deprecation_date: "2024-01-01"
replacement_file: "prompt.yaml"
```

**Note**: The old rubric structure with individual criteria definitions has been replaced by the new integrated structure in `prompt.yaml`. This file is maintained only for backward compatibility and will be removed in future versions. The configuration loader still expects the file to exist; keep a minimal placeholder (like the deprecation block above) in `config/rubric.yaml` to satisfy validation.

### 3.2 `config/prompt.yaml`
Holds language-specific prompt templates, instructions, and rubric definitions used to query the LLM.

**New Integrated Structure**:
```yaml
languages:
  en:
    context:
      context_text: "You are an expert writing coach evaluating business memos..."
    request:
      request_text: "Evaluate the following business memo using the rubric below..."
    rubric:
      scores:
        min: 1
        max: 5
      criteria:
        structure:
          name: "Structure"
          description: "pyramid principle, SCQA, clarity of opportunity, ask"
          weight: 25
        arguments_and_evidence:
          name: "Arguments and Evidence"
          description: "logic, financial metrics"
          weight: 30
        strategic_alignment:
          name: "Strategic Alignment"
          description: "help achieve strategic goals 1, 2, 3"
          weight: 25
        implementation_and_risks:
          name: "Implementation and Risks"
          description: "feasibility, risk assessment, implementation plan"
          weight: 20

  es:
    context:
      context_text: "Eres un coach de escritura experto evaluando memorandos..."
    request:
      request_text: "Evalúa el siguiente memorando comercial usando la rúbrica..."
    rubric:
      scores:
        min: 1
        max: 5
      criteria:
        structure:
          name: "Estructura"
          description: "principio de pirámide, SCQA, claridad de oportunidad, solicitud"
          weight: 25
        arguments_and_evidence:
          name: "Argumentos y Evidencia"
          description: "lógica, métricas financieras"
          weight: 30
        strategic_alignment:
          name: "Alineación Estratégica"
          description: "ayudar a lograr objetivos estratégicos 1, 2, 3"
          weight: 25
        implementation_and_risks:
          name: "Implementación y Riesgos"
          description: "viabilidad, evaluación de riesgos, plan de implementación"
          weight: 20

default_language: "en"
confidence_threshold: 0.7
```

**Key Features**:
- **Integrated Rubric**: Rubric definitions now included within each language section
- **4-Criteria Structure**: Simplified to 4 core criteria with clear weights (total 100%)
- **Language-Specific Content**: Full English and Spanish support with identical structure
- **Dynamic Weights**: Pydantic validation ensures weights sum to exactly 100%
- **Scoring Range**: Consistent 1-5 scoring scale across all languages
- **Context/Request Separation**: Clear separation of system context and user requests
        - "Ensure feedback is actionable and specific"
        - "Maintain objectivity and fairness"
        - "Consider the writer's development level"
        - "Encourage critical thinking and reflection"
        - "Always respond with valid JSON format"
        - "Ensure all scores are integers 1-5"
        - "Calculate overall_score as weighted average of rubric scores"

  es:
    name: "Spanish"
    description: "Spanish language prompts and instructions"
    evaluation_prompt:
      system_message: "Eres un coach experto en escritura..."
      user_template: |
        Evalúa el siguiente texto usando la rúbrica proporcionada.
        
        TEXTO A EVALUAR:
        {{ text_content }}
        
        RÚBRICA DE EVALUACIÓN:
        {{ rubric_content }}
        
        Proporciona tu evaluación en el siguiente formato JSON:
        {{ response_format }}
        
        Enfócate en proporcionar retroalimentación constructiva...

default_language: "en"
confidence_threshold: 0.7
```

**Key Features**:
- **Multi-Language Support**: Separate configurations for English and Spanish
- **Jinja2 Templating**: Dynamic variable substitution with `{{ variable_name }}`
- **Language Detection**: Automatic language identification with confidence scoring
- **Template Variables**: Dynamic injection of rubric content and response formats
- **No Framework Dependencies**: Clean, focused prompt structure

### 3.3 `config/llm.yaml`
Configures LLM provider and runtime limits with enhanced performance monitoring.

**Structure**:
```yaml
provider: anthropic
api_configuration:
  model: claude-3-sonnet
  timeout: 15
  max_retries: 3
  token_limit: 4000

request_settings:
  max_text_length: 10000
  chunking_enabled: true
  chunk_size: 2000

response_handling:
  parse_json: true
  validate_schema: true
  timeout_seconds: 15

performance_optimization:
  max_processing_time: 15
  caching_enabled: true
  template_cache_size: 100

language_detection:
  enabled: true
  methods: ["polyglot", "langdetect", "pycld2"]
  fallback_threshold: 0.5
  cache_results: true
```

**Key Features**:
- **Performance Monitoring**: Tracks response times and enforces <15s requirement
- **Language Detection**: Configurable detection methods and fallback strategies
- **Template Caching**: Improves performance with compiled Jinja2 templates
- **Error Handling**: Comprehensive error handling with fallback options

### 3.4 `config/auth.yaml`
Configures authentication and security parameters. See `docs/02b_Authentication_Specifications.md` for complete authentication configuration details and examples.

## 4.0 Configuration Validation
Run `python3 backend/validate_config.py` to ensure all configs exist and satisfy required fields.
The validation system uses Pydantic models to provide detailed error messages and ensure type safety.

**Validation Features**:
- **Type Safety**: All configuration values are validated against expected types
- **Required Fields**: Missing required fields are clearly identified
- **Value Ranges**: Numeric values are validated against acceptable ranges
- **Cross-Reference Validation**: Related configuration values are validated for consistency
- **Language Validation**: Language configurations are validated for completeness

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

## 6.0 New Configuration Features

### 6.1 Language Detection Configuration
```yaml
# config/llm.yaml
language_detection:
  enabled: true
  methods: ["polyglot", "langdetect", "pycld2"]
  fallback_threshold: 0.5
  cache_results: true
  confidence_scoring: true
  default_language: "en"
```

### 6.2 Dynamic Prompt Configuration
```yaml
# config/prompt.yaml
templates:
  evaluation_prompt:
    system_message: "{{ system_message }}"
    user_template: |
      {{ user_template }}
      
      TEXT TO EVALUATE:
      {{ text_content }}
      
      EVALUATION RUBRIC:
      {{ rubric_content }}
      
      {{ additional_instructions }}
```

### 6.3 Performance Configuration
```yaml
# config/llm.yaml
performance:
  max_processing_time: 15
  caching_enabled: true
  template_cache_size: 100
  language_detection_cache_size: 50
  response_cache_size: 25
```

## 7.0 Configuration Migration

### 7.1 From Framework System
The new configuration system removes the deprecated framework system:
- **Removed**: `frameworks` section from `rubric.yaml`
- **Removed**: `evaluation_framework` section
- **Removed**: `segment_evaluation` section
- **Added**: Language-specific prompt configurations
- **Added**: Dynamic rubric structure support

### 7.2 Migration Steps
1. **Backup**: Create backup of existing configuration files
2. **Update**: Modify configuration files to use new structure
3. **Validate**: Run configuration validation to ensure correctness
4. **Test**: Verify system functionality with new configurations
5. **Deploy**: Apply changes to production system

## 8.0 References
- `docs/02b_Authentication_Specifications.md` - Complete authentication configuration details
- `config/*.yaml`
- `backend/services/config_service.py`
- `backend/services/config_manager.py`
- `backend/models/config_models.py` - Pydantic configuration models
- `devlog/prompt_refactor.md` - Prompt refactor implementation plan
