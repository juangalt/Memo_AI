# Configuration Guide
## Memo AI Coach

**Document ID**: 04_Configuration_Guide.md
**Document Version**: 2.0
**Last Updated**: Phase 10 - Prompt Refactor Implementation
**Status**: Active

---

## 1.0 Configuration Overview
All runtime behavior is controlled by four YAML files in `config/`.
Files are mounted read-only into containers at `/app/config/` and validated by Pydantic models in `backend/models/config_models.py`.
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

## 3.0 Configuration Files

### 3.1 `config/rubric.yaml`
Defines the evaluation rubric and scoring criteria with dynamic structure support.

**Structure**:
```yaml
rubric:
  name: "Business Memo Evaluation Rubric for Healthcare Investment Projects"
  description: "This rubric is designed to evaluate business memos..."
  total_weight: 100
  scoring_scale: "1-5"  # 1: Poor, 2: Fair, 3: Good, 4: Very Good, 5: Excellent

  criteria:
    - name: "Structure and Logic"
      description: "Assesses the memo's organization..."
      scoring_guidance:
        1: "Severely disorganized..."
        2: "Basic structure present but flawed..."
        3: "Adequate organization..."
        4: "Strong structure..."
        5: "Exemplary structure..."
      weight: 15

    - name: "Arguments and Evidence"
      description: "Evaluates the strength of claims..."
      scoring_guidance:
        1: "Arguments are weak..."
        2: "Some arguments supported..."
        3: "Arguments are generally solid..."
        4: "Strong, well-supported arguments..."
        5: "Outstanding arguments..."
      weight: 20

    # Additional criteria with similar structure...
```

**Key Features**:
- **Dynamic Structure**: Criteria can be added, removed, or modified without code changes
- **Weight Validation**: Pydantic ensures total weights equal 100%
- **Flexible Scoring**: Supports any number of criteria with custom weights
- **No Framework Dependencies**: Removed deprecated framework system for cleaner configuration

### 3.2 `config/prompt.yaml`
Holds language-specific prompt templates and instruction lists used to query the LLM.

**New Structure**:
```yaml
languages:
  en:
    name: "English"
    description: "English language prompts and instructions"
    evaluation_prompt:
      system_message: "You are an expert writing coach..."
      user_template: |
        Evaluate the following text using the provided rubric.
        
        TEXT TO EVALUATE:
        {{ text_content }}
        
        EVALUATION RUBRIC:
        {{ rubric_content }}
        
        Provide your evaluation in the following JSON format:
        {{ response_format }}
        
        Focus on providing constructive, actionable feedback...
    
    instructions:
      evaluation_guidelines:
        - "Be constructive and encouraging in your feedback"
        - "Provide specific examples and suggestions"
        - "Focus on both strengths and areas for improvement"
        - "Use clear, professional language"
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
