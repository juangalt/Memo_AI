# Development Guide
## Memo AI Coach

**Document ID**: 08_Development_Guide.md
**Document Version**: 3.0
**Last Updated**: Phase 11 - LLM Refactor & Health Security Implementation
**Status**: Active

---

## 1.0 Coding Principles
Derived from project AGENTS guidelines:
- Favor simplicity and readability over abstraction.
- Each module serves a single responsibility.
- Provide docstrings and inline comments for educational clarity.
- Use Pydantic models for configuration validation and type safety.
- Implement Jinja2 templating for dynamic prompt generation.
- Follow PEP 8 style with 4-space indentation and descriptive variable names.

## 2.0 Repository Structure
```
backend/       FastAPI service with enhanced LLM processing
vue-frontend/  Vue.js reactive interface with dynamic components
config/        YAML configuration files with Pydantic validation
tests/         Test suites including language detection and prompt generation
docs/          Comprehensive project documentation
```

## 3.0 Backend Development
- Entry point: `backend/main.py`.
- Data models in `backend/models/entities.py` reflect tables created by `init_db.py`.
- **Configuration models** in `backend/models/config_models.py` provide Pydantic validation.
- Services in `backend/services/` handle configuration, authentication, LLM integration, and language detection.
- **Language detection service** (`backend/services/language_detection.py`) provides robust multi-language identification.
- Use `evaluate_text_with_llm` for all evaluations; it handles prompt generation, language detection, and error management.
- Error responses should use the standard `{data: null, meta, errors}` schema defined in API documentation.
- Add new endpoints by extending `backend/main.py` and documenting them in `docs/05_API_Documentation.md`.

### 3.1 New Architecture Components

#### 3.1.0 Authentication Decorators (`backend/decorators.py`)
```python
from decorators import require_auth

@require_auth(admin_only=True)
async def protected_endpoint(request: Request):
    """Endpoint that requires admin authentication."""
    # Access session data from request.state.session_data
    session_data = request.state.session_data
    user_id = session_data.get('user_id')
    is_admin = session_data.get('is_admin', False)
    
    # Your endpoint logic here
    return {"message": "Admin access granted"}
```

**Usage**:
- `@require_auth()` - Requires any authenticated user
- `@require_auth(admin_only=True)` - Requires admin user
- Session data available in `request.state.session_data`
- Automatic 401/403 responses for unauthorized access

#### 3.1.1 Configuration Models (`backend/models/config_models.py`)

```python
from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import Dict, List, Optional

class Language(str, Enum):
    EN = "en"
    ES = "es"
    UNKNOWN = "unknown"  # For fallback scenarios

class RubricCriterion(BaseModel):
    name: str
    description: str
    weight: int = Field(..., ge=1, le=100)
    
    @validator('weight')
    def validate_weight(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Weight must be between 1 and 100')
        return v

class RubricScores(BaseModel):
    min: int = Field(1, ge=1, le=5)
    max: int = Field(5, ge=1, le=5)

class RubricConfig(BaseModel):
    scores: RubricScores
    criteria: Dict[str, RubricCriterion]
    
    @validator('criteria')
    def validate_total_weight(cls, v):
        total_weight = sum(criterion.weight for criterion in v.values())
        if total_weight != 100:
            raise ValueError(f'Total criteria weights must equal 100%, got {total_weight}%')
        return v

class PromptLanguageConfig(BaseModel):
    context: Dict[str, str]
    request: Dict[str, str]
    rubric: RubricConfig

class PromptConfig(BaseModel):
    languages: Dict[str, PromptLanguageConfig]
    default_language: Language = Language.EN
    confidence_threshold: float = Field(0.7, ge=0.0, le=1.0)
```

#### 3.1.2 Language Detection Service (`backend/services/language_detection.py`)
```python
from typing import Dict, List, Optional
import polyglot
import langdetect
import pycld2

class RobustLanguageDetector:
    def __init__(self, methods: List[str] = None):
        self.methods = methods or ["polyglot", "langdetect", "pycld2"]
    
    def detect_language(self, text: str) -> Dict:
        """Detect language using multiple methods with fallback strategies."""
        results = {}
        
        for method in self.methods:
            try:
                if method == "polyglot":
                    results[method] = self._detect_polyglot(text)
                elif method == "langdetect":
                    results[method] = self._detect_langdetect(text)
                elif method == "pycld2":
                    results[method] = self._detect_pycld2(text)
            except Exception as e:
                results[method] = {"error": str(e)}
        
        return self._aggregate_results(results, text)
    
    def _aggregate_results(self, results: Dict, text: str) -> Dict:
        """Aggregate results from multiple detection methods."""
        # Implementation details...
        pass
```

#### 3.1.3 Enhanced LLM Service (`backend/services/llm_service.py`)
```python
from jinja2 import Environment, FileSystemLoader
from services.language_detection import RobustLanguageDetector
from models.config_models import PromptConfig

class EnhancedLLMService:
    def __init__(self):
        self.language_detector = RobustLanguageDetector()
        self.jinja_env = Environment(loader=FileSystemLoader('backend/templates'))
        self.template_cache = {}
    
    def generate_prompt(self, text: str, rubric: Dict) -> str:
        """Generate language-appropriate prompt using Jinja2 templates."""
        # Detect language
        language_result = self.language_detector.detect_language(text)
        language = language_result.get('detected_language', 'en')
        
        # Load language-specific configuration
        prompt_config = self._load_prompt_config(language)
        
        # Render template
        template = self._get_template('evaluation_prompt.j2')
        return template.render(
            text_content=text,
            rubric_content=rubric,
            language_config=prompt_config,
            **language_result
        )
    
    def _get_template(self, template_name: str):
        """Get compiled Jinja2 template with caching."""
        if template_name not in self.template_cache:
            self.template_cache[template_name] = self.jinja_env.get_template(template_name)
        return self.template_cache[template_name]
```

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

### 4.1 New Frontend Components

#### 4.1.1 Dynamic Rubric Scores (`vue-frontend/src/components/DynamicRubricScores.vue`)
```vue
<template>
  <div class="rubric-scores">
    <h3 class="text-lg font-semibold mb-4">Rubric Scores</h3>
    <div class="space-y-4">
      <div 
        v-for="(criterion, key) in rubricScores" 
        :key="key"
        class="criterion-item p-4 bg-white rounded-lg border"
      >
        <div class="flex justify-between items-center mb-2">
          <h4 class="font-medium text-gray-900">
            {{ formatCriterionName(key) }}
          </h4>
          <div class="flex items-center space-x-2">
            <span class="text-sm text-gray-500">
              Weight: {{ getCriterionWeight(key) }}%
            </span>
            <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
              Score: {{ criterion.score }}/5
            </span>
          </div>
        </div>
        <p class="text-gray-600 text-sm">{{ criterion.justification }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  rubricScores: {
    type: Object,
    required: true
  },
  rubricConfig: {
    type: Object,
    default: () => ({})
  }
})

const formatCriterionName = (key) => {
  return key.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const getCriterionWeight = (key) => {
  const criterion = props.rubricConfig.criteria?.find(c => 
    c.name.toLowerCase().replace(/\s+/g, '_') === key
  )
  return criterion?.weight || 0
}
</script>
```

#### 4.1.2 Language Detection Display (`vue-frontend/src/components/LanguageDetectionDisplay.vue`)
```vue
<template>
  <div class="language-detection">
    <div class="flex items-center space-x-3 p-4 bg-blue-50 rounded-lg">
      <div class="flex-shrink-0">
        <img 
          :src="getLanguageFlag(languageInfo.detected_language)" 
          :alt="languageInfo.detected_language"
          class="w-6 h-6 rounded"
        />
      </div>
      <div class="flex-1">
        <h4 class="text-sm font-medium text-gray-900">
          Detected Language: {{ getLanguageName(languageInfo.detected_language) }}
        </h4>
        <div class="flex items-center space-x-2 mt-1">
          <div class="flex-1 bg-gray-200 rounded-full h-2">
            <div 
              class="bg-blue-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${languageInfo.confidence * 100}%` }"
            ></div>
          </div>
          <span class="text-xs text-gray-500">
            {{ Math.round(languageInfo.confidence * 100) }}% confidence
          </span>
        </div>
        <p class="text-xs text-gray-500 mt-1">
          Method: {{ languageInfo.detection_method }}
          <span v-if="languageInfo.fallback_used" class="text-orange-600">
            (fallback used)
          </span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  languageInfo: {
    type: Object,
    required: true
  }
})

const getLanguageFlag = (langCode) => {
  const flags = {
    'en': '/flags/en.png',
    'es': '/flags/es.png'
  }
  return flags[langCode] || flags['en']
}

const getLanguageName = (langCode) => {
  const names = {
    'en': 'English',
    'es': 'Spanish'
  }
  return names[langCode] || 'Unknown'
}
</script>
```

### 4.2 Debug and Admin Component Development
Debug and admin components follow specific patterns for consistency and maintainability:

#### Component Structure
- **Location**: Debug components in `vue-frontend/src/components/debug/`
- **Location**: Admin components in `vue-frontend/src/components/admin/`
- **Naming**: Use descriptive names ending with `.vue` (e.g., `ApiHealthTesting.vue`)
- **Layout**: Consistent white background with rounded borders and proper spacing

#### Common Patterns
- **Status Indicators**: Use color-coded badges (green=healthy, red=error, blue=testing, gray=unknown)
- **Loading States**: Show spinners during async operations with disabled buttons
- **Error Handling**: Display errors with copy-to-clipboard functionality for debug info
- **Tooltips**: Use hover tooltips for detailed information display
- **Responsive Design**: Grid layouts that adapt to different screen sizes

#### API Integration
- **Standardized Responses**: All components handle `{data, meta, errors}` response format
- **Authentication**: Include `X-Session-Token` header for all admin/debug requests
- **Error Display**: Show detailed error information with debug context
- **Response Preview**: Display truncated responses with full view on hover

#### Debug Component Features
- **ApiHealthTesting**: Comprehensive endpoint testing with evaluation testing integration
- **SystemDiagnostics**: System health monitoring with real-time updates
- **PerformanceMonitoring**: Response time tracking and system resource monitoring
- **DevelopmentTools**: Various debugging utilities and development aids
- **LanguageDetectionTesting**: Test language detection with various text samples

#### Admin Component Features
- **HealthStatus**: System health overview and service status monitoring
- **ConfigValidator**: YAML configuration file management with Pydantic validation
- **UserManagement**: User account creation, management, and role assignment
- **SessionManagement**: Session creation, refresh, and management
- **PromptTemplateEditor**: Edit Jinja2 templates with live preview
- **LanguageConfiguration**: Configure language detection settings and thresholds

#### Last Evaluation Page Development
- **Location**: `vue-frontend/src/views/LastEvaluation.vue`
- **Purpose**: Dedicated page for viewing raw LLM evaluation data with language detection metadata
- **Access Control**: Admin-only access with proper route protection
- **Component Integration**: Hosts LastEvaluationsViewer component with Layout wrapper
- **Navigation**: Integrated with main navigation menu for admin users

#### Copyright Footer Implementation
- **Universal Footer**: All pages include consistent "© Copyright FGS" footer
- **Layout Integration**: Footer added to Layout component for authenticated pages
- **Standalone Pages**: Custom footer implementation for Home and Login pages
- **Styling**: Consistent design with white background, gray border, and centered text
- **Responsive Design**: Footer adapts to different page layouts and screen sizes
- **Accessibility**: Uses semantic HTML `<footer>` tag for screen readers

### 4.3 Dynamic Prompt Generation Development
- **Backend Integration**: Language detection and Jinja2 templating for dynamic prompt generation
- **LLM Service Methods**: `generate_prompt()`, `_get_template()`, and `_load_prompt_config()`
- **Template Management**: Jinja2 templates stored in `backend/templates/` with caching
- **Language Support**: Automatic adaptation to detected language with fallback strategies
- **Configuration Validation**: Pydantic models ensure prompt configuration integrity

## 5.0 Configuration & Secrets
- Never commit API keys or passwords
- Use environment variables or `.env` for sensitive data
- Configuration editing through admin API or `config_manager.py`
- **Pydantic Validation**: All configurations validated against type-safe models
- **Template Security**: Jinja2 templates use safe rendering with limited variable access
- Update documentation when adding new config keys

## 6.0 New Development Patterns

### 6.1 Language Detection Development
```python
# Testing language detection
def test_language_detection():
    detector = RobustLanguageDetector()
    
    # Test English
    result = detector.detect_language("This is English text")
    assert result['detected_language'] == 'en'
    assert result['confidence'] > 0.8
    
    # Test Spanish
    result = detector.detect_language("Este es texto en español")
    assert result['detected_language'] == 'es'
    assert result['confidence'] > 0.8
    
    # Test fallback
    result = detector.detect_language("12345")
    assert result['fallback_used'] == True
```

### 6.2 Jinja2 Template Development
```jinja2
{# backend/templates/evaluation_prompt.j2 #}
{{ language_config.evaluation_prompt.system_message }}

{{ language_config.evaluation_prompt.user_template }}

TEXT TO EVALUATE:
{{ text_content }}

EVALUATION RUBRIC:
{% for criterion in rubric.criteria %}
{{ criterion.name }} (Weight: {{ criterion.weight }}%)
{{ criterion.description }}

Scoring Guide:
{% for score, description in criterion.scoring_guidance.items() %}
{{ score }}: {{ description }}
{% endfor %}

{% endfor %}

RESPONSE FORMAT:
{{ language_config.response_format }}
```

### 6.3 Pydantic Configuration Development
```python
# Validating configuration
def validate_config():
    try:
        config = PromptConfig(**yaml.safe_load(open('config/prompt.yaml')))
        print("Configuration valid")
        return config
    except ValidationError as e:
        print(f"Configuration validation failed: {e}")
        return None
```

## 7.0 References
- `docs/02b_Authentication_Specifications.md` - Complete authentication specifications
- `devlog/prompt_refactor.md` - Prompt refactor implementation plan
- `backend/models/config_models.py` - Pydantic configuration models
- `backend/services/language_detection.py` - Language detection service
- `backend/templates/` - Jinja2 template directory
- `vue-frontend/src/components/DynamicRubricScores.vue` - Dynamic rubric component
- `vue-frontend/src/components/LanguageDetectionDisplay.vue` - Language detection component
