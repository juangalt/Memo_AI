# **Prompt Refactor Implementation Plan**
## **Enhanced LLM Service with Pydantic, Jinja2, and Robust Language Detection**

**Document ID**: prompt_refactor.md  
**Document Version**: 1.2  
**Last Updated**: Phase 11 - Implementation Lessons Learned and Best Practices  
**Status**: Active Implementation Plan with Lessons Learned  

---

## **Executive Summary**

This document outlines the comprehensive implementation plan for refactoring the Memo AI Coach prompt generation system. Based on lessons learned from previous implementations, this plan incorporates Pydantic for robust configuration validation, Jinja2 for dynamic template generation, and a multi-layered language detection system with comprehensive fallback strategies.

### **Key Objectives**
- Replace basic string formatting with Jinja2 templating for dynamic prompt generation
- Implement Pydantic validation with flexible, progressive schema enforcement
- Create robust language detection using multiple libraries with intelligent fallback
- **NEW**: Simplify rubric structure to 4 core criteria with clear weights and descriptions
- **NEW**: Move all rubric content into prompt.yaml, deprecate rubric.yaml entirely
- **NEW**: Use context/request/rubric structure for cleaner prompt generation
- Establish multi-language support with extensible language configuration (English/Spanish)
- Build frontend adaptability to dynamic rubric structures without hardcoding
- Implement comprehensive validation coordination across all system layers

---

## **🚨 CRITICAL IMPLEMENTATION LEARNINGS (From Actual Implementation)**

### **What We Discovered During Implementation**

After implementing this plan, we encountered several critical issues that **MUST** be addressed before starting any implementation:

#### **1. Configuration Service Validation (CRITICAL - Causes Startup Failures)**
- **Problem**: Existing `config_service.py` validation functions expect old configuration structure
- **Impact**: Backend fails to start, validation errors prevent system initialization
- **Solution**: Update validation functions FIRST before implementing new features
- **Files**: `backend/services/config_service.py` - update `_validate_rubric_config` and `_validate_prompt_config`

#### **2. YAML File Content Requirements (CRITICAL - Causes Parsing Failures)**
- **Problem**: YAML parsers treat comment-only files as empty, causing validation failures
- **Impact**: `rubric.yaml` deprecation fails, system can't start
- **Solution**: Ensure deprecated files contain valid YAML content, not just comments
- **Files**: `config/rubric.yaml` - add actual YAML fields, not just comment lines

#### **3. Language Enum Duplication (CRITICAL - Causes Runtime Errors)**
- **Problem**: Multiple Language enum definitions cause AttributeError and import confusion
- **Impact**: Language detection fails, system crashes during evaluation
- **Solution**: Single Language enum definition in `config_models.py` only
- **Files**: `backend/services/language_detection.py` - remove duplicate enum

#### **4. Template Path Resolution (CRITICAL - Causes Template Errors)**
- **Problem**: Jinja2 template paths assume specific working directory context
- **Impact**: TemplateNotFound errors, prompt generation fails
- **Solution**: Use relative paths that work from backend directory context
- **Files**: `backend/services/llm_service.py` - fix template loader paths

#### **5. Container Rebuild Requirements (CRITICAL - Changes Don't Take Effect)**
- **Problem**: Python code changes require container rebuilds, not just restarts
- **Impact**: Code changes appear to have no effect, debugging confusion
- **Solution**: Always rebuild containers after significant code changes
- **Command**: `docker compose build backend` not `docker compose restart backend`

### **Implementation Priority Order**
1. **FIRST**: Fix configuration service validation functions
2. **SECOND**: Ensure all YAML files contain valid content
3. **THIRD**: Fix import and enum duplication issues
4. **FOURTH**: Fix template path and service export issues
5. **FIFTH**: Test backend startup and health endpoints
6. **SIXTH**: Continue with planned implementation phases

### **Why These Issues Occurred**
- Original plan assumed clean implementation without existing validation logic
- Configuration structure changes weren't fully coordinated across all components
- Docker containerization requirements weren't fully understood
- Import and module dependency issues weren't anticipated

**Bottom Line**: This plan works, but requires addressing these critical issues FIRST before any other implementation work.

### **Success Criteria**
- 100% configuration validation through coordinated Pydantic and service validation
- 95%+ language detection accuracy with graceful degradation
- Zero hardcoded prompt logic in Python code
- **NEW**: Simplified 4-criteria rubric structure with clear weights and descriptions
- **NEW**: All rubric content contained within prompt.yaml (no separate rubric.yaml)
- **NEW**: Context/request/rubric structure for cleaner, more maintainable prompts
- Frontend automatically adapts to rubric changes without code modifications
- Support for English and Spanish with seamless language addition process
- Configuration hot-reload capability without service restarts
- Comprehensive error handling and user feedback at all validation levels

---

## **NEW: Simplified Rubric Structure**

### **New Rubric Design**
The new rubric structure simplifies evaluation to 4 core criteria, all contained within `prompt.yaml`:

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
```

### **Key Benefits**
- **Simplified**: Only 4 criteria instead of complex nested structures
- **Clear Weights**: Total adds to 100% with logical distribution
- **Language-Specific**: Full English and Spanish support
- **Self-Contained**: All rubric content in one file
- **Maintainable**: Easy to modify criteria, weights, and descriptions

---

## **Phase 1: Comprehensive Planning and Schema Analysis**

### **Step 1.1: Configuration Structure Analysis and Documentation**

**Objective**: Understand existing configuration structures before implementing any models or validation.

**Implementation**:
- [ ] Analyze all existing YAML configuration files for actual structure
- [ ] Create detailed configuration structure diagrams showing nested vs. flat patterns
- [ ] Document field type requirements, constraints, and relationships
- [ ] Identify configuration evolution patterns and versioning needs
- [ ] Map configuration dependencies and cross-references

**Deliverables**:
```python
# Configuration structure analysis script
def analyze_config_structures():
    configs = ['rubric.yaml', 'prompt.yaml', 'llm.yaml', 'auth.yaml']
    for config_file in configs:
        with open(f'config/{config_file}') as f:
            config = yaml.safe_load(f)
        print(f"\n{config_file} structure:")
        print(json.dumps(config, indent=2))
        
        # Analyze field types and nesting
        analyze_field_types(config)
        analyze_nesting_patterns(config)
```

**Tests**:
```bash
# Run configuration analysis
python3 backend/scripts/analyze_configs.py

# Expected output: Detailed structure analysis for each config file
# This prevents validation failures and model mismatches
```

**Human Test**:
- Open each configuration file and map the actual structure
- Create visual diagrams of nested configurations
- Document any inconsistencies between expected and actual structures
- Identify fields that might need special handling

**Files Modified**: None (planning phase)

---

### **Step 1.2: Module Dependency Planning and Architecture Design**

**Objective**: Plan module dependencies and initialization sequence to avoid import and startup issues.

**Implementation**:
- [ ] Create comprehensive module dependency graph
- [ ] Plan global function placement and service instances
- [ ] Document startup sequence and initialization order
- [ ] Design service locator or dependency injection patterns
- [ ] Plan for lazy initialization to avoid startup-time issues

**Module Dependency Graph**:
```
main.py (entry point)
├── services/__init__.py (service exports)
├── services/config_service.py (configuration management)
├── services/llm_service.py (LLM integration)
├── services/language_detection.py (language detection)
├── models/config_models.py (Pydantic models)
└── validate_config.py (configuration validation)
```

**Implementation Strategy**:
```python
# Service manager pattern to avoid circular imports
class ServiceManager:
    def __init__(self):
        self._services = {}
    
    def get_service(self, service_name: str):
        if service_name not in self._services:
            self._services[service_name] = self._create_service(service_name)
        return self._services[service_name]
    
    def _create_service(self, service_name: str):
        # Lazy initialization to avoid startup issues
        if service_name == 'llm':
            return EnhancedLLMService()
        elif service_name == 'language_detector':
            return RobustLanguageDetector()
        # ... other services
```

**Tests**:
```python
# Test module initialization
def test_module_dependencies():
    # Verify no circular imports
    # Test startup sequence
    # Verify global functions are available when needed
    # Test service availability after startup
```

**Human Test**:
- Create dependency graph visualization
- Verify no circular import paths exist
- Test startup sequence in development environment
- Verify all services are accessible after initialization

**Files Modified**: None (planning phase)

---

### **Step 1.3: Install Enhanced Dependencies with Validation**

**Files to Modify**: `backend/requirements.txt`, `backend/Dockerfile`

**Implementation**:
```bash
# Core dependencies with version pinning
pip install "pydantic>=2.0.0" "jinja2>=3.1.0"

# Robust language detection libraries with fallback options
pip install "polyglot>=16.7.4"
pip install "langdetect>=1.0.9"
pip install "pycld2>=0.42"

# Additional language support and utilities
pip install "polyglot[detection]"
pip install "typing-extensions>=4.0.0"  # For advanced typing support
```

**Dependency Validation**:
```python
# Comprehensive dependency verification
def verify_dependencies():
    required_packages = {
        'pydantic': '2.0.0',
        'jinja2': '3.1.0',
        'polyglot': '16.7.4',
        'langdetect': '1.0.9',
        'pycld2': '0.42'
    }
    
    for package, min_version in required_packages.items():
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            print(f"✓ {package}: {version}")
        except ImportError:
            print(f"✗ {package}: Not installed")
            return False
    return True
```

**Tests**:
```bash
# Verify installations with version checking
python3 backend/scripts/verify_dependencies.py

# Expected output: All packages installed with correct versions
```

**Human Test**: 
- Navigate to backend container: `docker compose exec backend bash`
- Run dependency verification script
- Verify all packages install without errors
- Test import functionality for each package

**Files No Longer Used**: None (new dependencies)

---

### **Step 1.2: Create Pydantic Configuration Models**

**Files to Create**: `backend/models/config_models.py`

**Implementation**:
- Create `Language` enum (EN, ES)
- Create `RubricCriterion` model with weight validation (total must equal 100%)
- Create `RubricConfig` model with 4 criteria and scoring range validation
- Create `PromptLanguageConfig` model with context/request/rubric structure
- Create `PromptConfig` model with language validation
- **NEW**: Validate that criteria weights sum to exactly 100%
- **NEW**: Validate scoring range (min: 1, max: 5)

**Tests**:
```python
# Test model validation
python3 -c "
from models.config_models import *
config = PromptConfig(languages={'en': PromptLanguageConfig(...)})
print('Validation successful')
"

# Test weight validation (must equal 100%)
python3 -c "
from models.config_models import *
# Test valid weights
valid_config = PromptConfig(languages={'en': PromptLanguageConfig(
    context={'context_text': 'test'},
    request={'request_text': 'test'},
    rubric={
        'scores': {'min': 1, 'max': 5},
        'criteria': {
            'structure': {'name': 'Structure', 'description': 'test', 'weight': 25},
            'arguments_and_evidence': {'name': 'Arguments', 'description': 'test', 'weight': 30},
            'strategic_alignment': {'name': 'Strategy', 'description': 'test', 'weight': 25},
            'implementation_and_risks': {'name': 'Implementation', 'description': 'test', 'weight': 20}
        }
    }
)})
print('✓ Valid weights (100%) validation successful')

# Test invalid weights (should fail)
try:
    invalid_config = PromptConfig(languages={'en': PromptLanguageConfig(
        context={'context_text': 'test'},
        request={'request_text': 'test'},
        rubric={
            'scores': {'min': 1, 'max': 5},
            'criteria': {
                'structure': {'name': 'Structure', 'description': 'test', 'weight': 30},
                'arguments_and_evidence': {'name': 'Arguments', 'description': 'test', 'weight': 30},
                'strategic_alignment': {'name': 'Strategy', 'description': 'test', 'weight': 30},
                'implementation_and_risks': {'name': 'Implementation', 'description': 'test', 'weight': 30}
            }
        }
    )})
    print('✗ Invalid weights (120%) should have failed')
except Exception as e:
    print('✓ Invalid weights correctly rejected:', str(e))
"
```

**Human Test**:
- Create test configuration file with invalid weights (sum != 100%)
- Verify Pydantic throws validation error
- Create valid configuration and verify no errors

**Files No Longer Used**: None (new file)

---

### **Step 1.3: Create Language Detection Service**

**Files to Create**: `backend/services/language_detection.py`

**Implementation**:
- Create `RobustLanguageDetector` class
- Implement Polyglot detection method
- Implement Langdetect detection method  
- Implement Pycld2 detection method
- Implement heuristic fallback detection
- Create result aggregation logic
- Add confidence scoring

**Tests**:
```python
# Test language detection
python3 -c "
from services.language_detection import RobustLanguageDetector
detector = RobustLanguageDetector()
result = detector.detect_language('This is English text')
print('English detection:', result)
result = detector.detect_language('Este es texto en español')
print('Spanish detection:', result)
"
```

**Human Test**:
- Test with short English text (< 10 characters)
- Test with mixed language text
- Test with text containing special characters
- Verify confidence scores are reasonable (0.5-1.0)

**Files No Longer Used**: None (new file)

---

## **Phase 2: Configuration Refactoring**

### **Step 2.1: Refactor prompt.yaml Structure**

**Files to Modify**: `config/prompt.yaml`

**Implementation**:
- **NEW**: Implement context/request/rubric structure for each language
- **NEW**: Add 4 core criteria with clear weights (total = 100%)
- **NEW**: Include scoring range (min: 1, max: 5) for each language
- Add `default_language` and `confidence_threshold` settings
- Remove deprecated `frameworks` section and framework-specific content
- **NEW**: Ensure both English and Spanish have identical structure and weights

**Tests**:
```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('config/prompt.yaml'))"

# Validate with Pydantic models
python3 -c "
from models.config_models import PromptConfig
import yaml
config = PromptConfig(**yaml.safe_load(open('config/prompt.yaml')))
print('Configuration valid')
"

# Test weight validation (must equal 100%)
python3 -c "
from models.config_models import PromptConfig
import yaml
config = PromptConfig(**yaml.safe_load(open('config/prompt.yaml')))

# Verify English weights sum to 100%
en_weights = sum(criterion.weight for criterion in config.languages['en'].rubric.criteria.values())
print(f'English weights sum: {en_weights}%')
assert en_weights == 100, f'English weights must equal 100%, got {en_weights}%'

# Verify Spanish weights sum to 100%
es_weights = sum(criterion.weight for criterion in config.languages['es'].rubric.criteria.values())
print(f'Spanish weights sum: {es_weights}%')
assert es_weights == 100, f'Spanish weights must equal 100%, got {es_weights}%'

# Verify scoring range
en_scores = config.languages['en'].rubric.scores
assert en_scores.min == 1, f'English min score must be 1, got {en_scores.min}'
assert en_scores.max == 5, f'English max score must be 5, got {en_scores.max}'

es_scores = config.languages['es'].rubric.scores
assert es_scores.min == 1, f'Spanish min score must be 1, got {es_scores.min}'
assert es_scores.max == 5, f'Spanish max score must be 5, got {es_scores.max}'

print('✓ All validation tests passed')
"

# Test that rubric.yaml is no longer referenced
python3 -c "
import yaml
prompt_config = yaml.safe_load(open('config/prompt.yaml'))
assert 'frameworks' not in prompt_config, 'Frameworks section should be removed'
print('✓ Frameworks section successfully removed')
"
```

**Human Test**:
- Open `config/prompt.yaml` in browser
- Verify no syntax errors in YAML
- Check that frameworks section is removed
- Verify both English and Spanish sections exist

**Files No Longer Used**: 
- `config/rubric.yaml` (entire file deprecated - all content moved to prompt.yaml)
- `config/rubric.yaml` (frameworks section deprecated)

---

### **Step 2.2: Deprecate rubric.yaml**

**Files to Modify**: `config/rubric.yaml`

**Implementation**:
- **NEW**: Mark entire file as deprecated
- **NEW**: Add deprecation notice at top of file
- **NEW**: Remove all content except deprecation notice
- **NEW**: Ensure no other files reference this configuration
- **NEW**: Update validation scripts to ignore this file

**Tests**:
```bash
# Verify deprecation notice exists
grep -q "DEPRECATED" config/rubric.yaml && echo "✓ Deprecation notice found" || echo "✗ Deprecation notice missing"

# Verify no other files reference rubric.yaml
grep -r "rubric.yaml" backend/ --exclude="*.pyc" --exclude="__pycache__" && echo "✗ References to rubric.yaml found" || echo "✓ No references to rubric.yaml found"

# Verify validation script ignores rubric.yaml
python3 backend/validate_config.py 2>&1 | grep -q "rubric.yaml.*deprecated" && echo "✓ Validation script correctly handles deprecated file" || echo "✗ Validation script may still reference rubric.yaml"
```

**Human Test**:
- Open `config/rubric.yaml` and verify deprecation notice
- Check that no other configuration files reference rubric.yaml
- Verify that the application still functions without rubric.yaml
- Confirm that all rubric content is now in prompt.yaml

---

### **Step 2.3: Create Jinja2 Template System**

**Files to Create**: `backend/templates/evaluation_prompt.j2`

**Implementation**:
- **NEW**: Create context/request/rubric template structure
- **NEW**: Add dynamic 4-criteria rendering with weights
- **NEW**: Include language-specific context and request text
- **NEW**: Add scoring range validation (1-5 scale)
- **NEW**: Include weight-based scoring instructions
- Add required response format specification
- Include validation instructions

**Tests**:
```python
# Test template rendering
python3 -c "
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('backend/templates'))
template = env.get_template('evaluation_prompt.j2')

# Test with new rubric structure
test_context = {
    'context_text': 'You are an expert writing coach...',
    'request_text': 'Evaluate the following business memo...',
    'rubric': {
        'scores': {'min': 1, 'max': 5},
        'criteria': {
            'structure': {'name': 'Structure', 'description': 'pyramid principle, SCQA, clarity of opportunity, ask', 'weight': 25},
            'arguments_and_evidence': {'name': 'Arguments and Evidence', 'description': 'logic, financial metrics', 'weight': 30},
            'strategic_alignment': {'name': 'Strategic Alignment', 'description': 'help achieve strategic goals 1, 2, 3', 'weight': 25},
            'implementation_and_risks': {'name': 'Implementation and Risks', 'description': 'feasibility, risk assessment, implementation plan', 'weight': 20}
        }
    }
}

result = template.render(
    context=test_context['context_text'],
    request=test_context['request_text'],
    rubric=test_context['rubric'],
    text_content='Test business memo content',
    language='en'
)

print('✓ Template renders successfully')

# Verify template contains expected content
assert 'Structure' in result, 'Structure criterion missing'
assert 'Arguments and Evidence' in result, 'Arguments criterion missing'
assert 'Strategic Alignment' in result, 'Strategic Alignment criterion missing'
assert 'Implementation and Risks' in result, 'Implementation criterion missing'
assert '25%' in result, 'Structure weight missing'
assert '30%' in result, 'Arguments weight missing'
assert '1-5' in result, 'Scoring range missing'

print('✓ All expected content found in template')
"
```

**Human Test**:
- Open template file in browser
- Verify template syntax is correct
- Check that all variables are properly referenced
- Verify response format is clearly specified

**Files No Longer Used**: None (new file)

---

## **Phase 3: LLM Service Refactoring**

### **Step 3.1: Update LLM Service with New Architecture**

**Files to Modify**: `backend/services/llm_service.py`

**Implementation**:
- Integrate Pydantic configuration models
- Add Jinja2 template rendering
- Integrate robust language detection
- Update prompt generation logic
- Remove framework-related code
- Add language detection metadata to responses

**Tests**:
```python
# Test enhanced LLM service
python3 -c "
from services.llm_service import EnhancedLLMService
service = EnhancedLLMService()
prompt = service.generate_prompt('Test text')
print('Prompt generation successful')
"
```

**Human Test**:
- Submit English text for evaluation
- Submit Spanish text for evaluation
- Verify appropriate language prompts are generated
- Check that language detection metadata is included in responses

**Files No Longer Used**: 
- `backend/services/llm_service_backup.py` (DEPRECATED - DELETE)
- `backend/services/llm_service_improved.py` (DEPRECATED - DELETE)

---

### **Step 3.3: Comprehensive Testing of Enhanced LLM Service**

**Objective**: Verify that the enhanced LLM service works correctly with the new rubric structure.

**Tests**:
```python
# Test complete evaluation workflow with new rubric
python3 -c "
from services.llm_service import EnhancedLLMService
import json

# Initialize service
service = EnhancedLLMService()
print('✓ Service initialized successfully')

# Test English evaluation
en_result = service.evaluate_text_with_llm('This is a test business memo in English.')
print('✓ English evaluation completed')

# Verify English result structure
assert 'metadata' in en_result, 'Metadata missing from English result'
assert 'language_detection' in en_result['metadata'], 'Language detection missing'
assert en_result['metadata']['language_detection']['detected_language'] == 'en', 'English not detected'
assert 'rubric_scores' in en_result, 'Rubric scores missing'

# Verify 4 criteria are present
en_criteria = en_result['rubric_scores']
expected_criteria = ['structure', 'arguments_and_evidence', 'strategic_alignment', 'implementation_and_risks']
for criterion in expected_criteria:
    assert criterion in en_criteria, f'Criterion {criterion} missing from English result'

print('✓ English evaluation structure correct')

# Test Spanish evaluation
es_result = service.evaluate_text_with_llm('Este es un memorando comercial de prueba en español.')
print('✓ Spanish evaluation completed')

# Verify Spanish result structure
assert 'metadata' in es_result, 'Metadata missing from Spanish result'
assert 'language_detection' in es_result['metadata'], 'Language detection missing'
assert es_result['metadata']['language_detection']['detected_language'] == 'es', 'Spanish not detected'
assert 'rubric_scores' in es_result, 'Rubric scores missing'

# Verify 4 criteria are present
es_criteria = es_result['rubric_scores']
for criterion in expected_criteria:
    assert criterion in es_criteria, f'Criterion {criterion} missing from Spanish result'

print('✓ Spanish evaluation structure correct')

# Test weight calculation
def calculate_weighted_score(scores, weights):
    total_score = 0
    for criterion, score_data in scores.items():
        if isinstance(score_data, dict) and 'score' in score_data:
            score = score_data['score']
            weight = weights.get(criterion, 0) / 100.0
            total_score += score * weight
    return round(total_score, 2)

# Test with known weights
test_weights = {
    'structure': 25,
    'arguments_and_evidence': 30,
    'strategic_alignment': 25,
    'implementation_and_risks': 20
}

# Test weight validation
total_weight = sum(test_weights.values())
assert total_weight == 100, f'Total weight must be 100%, got {total_weight}%'
print('✓ Weight validation passed')

print('✓ All tests passed successfully')
"
```

**Human Test**:
- Submit English business memo for evaluation
- Submit Spanish business memo for evaluation
- Verify that both evaluations use the correct 4-criteria rubric
- Check that language detection works correctly
- Verify that weights are properly applied in scoring
- Confirm that the response structure matches the new rubric

---

### **Step 3.2: Update API Endpoints**

**Files to Modify**: `backend/main.py`

**Implementation**:
- Update evaluation submission endpoint
- Add language detection logging
- Update response structure
- Add language metadata to API responses

**Tests**:
```bash
# Test API endpoint
curl -X POST http://localhost:8000/api/v1/evaluations/submit \
  -H "Content-Type: application/json" \
  -H "X-Session-Token: test" \
  -d '{"text_content": "This is English text"}'
```

**Human Test**:
- Submit evaluation through frontend
- Check browser network tab for API response
- Verify language detection metadata in response
- Test with both English and Spanish text

**Files No Longer Used**: None (modifications only)

---

## **Phase 4: Frontend Type System and Components**

### **Step 4.1: Update Frontend Type Definitions**

**Files to Modify**: `vue-frontend/src/types/evaluation.ts`

**Implementation**:
- Add `LanguageDetection` interface
- Update `Evaluation` interface with language metadata
- Update `RubricCriterion` interface
- Remove deprecated framework-related types

**Tests**:
```typescript
// Test type definitions
const testEvaluation: Evaluation = {
  // ... test data
}
console.log('Types valid')
```

**Human Test**:
- Open TypeScript files in browser
- Verify no type errors in IDE
- Check that new interfaces are properly defined
- Verify deprecated types are removed

**Files No Longer Used**: 
- Any framework-related type definitions

---

### **Step 4.4: Comprehensive Testing of Frontend Components**

**Objective**: Verify that frontend components work correctly with the new 4-criteria rubric structure.

**Tests**:
```bash
# Test frontend compilation
cd vue-frontend
npm run build

# Test component compilation individually
npm run build -- --target lib --name DynamicRubricScores src/components/DynamicRubricScores.vue
npm run build -- --target lib --name LanguageDetectionDisplay src/components/LanguageDetectionDisplay.vue
```

**Component Testing**:
```typescript
// Test DynamicRubricScores component with new rubric structure
import { mount } from '@vue/test-utils'
import DynamicRubricScores from '@/components/DynamicRubricScores.vue'

const testEvaluation = {
  rubric_scores: {
    structure: { score: 4, justification: 'Good structure' },
    arguments_and_evidence: { score: 5, justification: 'Excellent arguments' },
    strategic_alignment: { score: 4, justification: 'Good alignment' },
    implementation_and_risks: { score: 3, justification: 'Basic implementation' }
  },
  overall_score: 4.0
}

const wrapper = mount(DynamicRubricScores, {
  props: { evaluation: testEvaluation }
})

// Verify all 4 criteria are displayed
expect(wrapper.text()).toContain('Structure')
expect(wrapper.text()).toContain('Arguments and Evidence')
expect(wrapper.text()).toContain('Strategic Alignment')
expect(wrapper.text()).toContain('Implementation and Risks')

// Verify scores are displayed
expect(wrapper.text()).toContain('4')
expect(wrapper.text()).toContain('5')
expect(wrapper.text()).toContain('3')

// Verify overall score is calculated correctly
const expectedScore = (4 * 0.25) + (5 * 0.30) + (4 * 0.25) + (3 * 0.20)
expect(wrapper.text()).toContain(expectedScore.toFixed(1))

console.log('✓ DynamicRubricScores component tests passed')
```

**Human Test**:
- Navigate to Overall Feedback page
- Verify that all 4 criteria are displayed with correct names
- Check that weights are visible (25%, 30%, 25%, 20%)
- Verify that scores are displayed correctly
- Confirm that overall score calculation uses the new weights
- Test with different evaluation results
- Verify responsive design on mobile and desktop

---

### **Step 4.2: Create Dynamic Rubric Display Component**

**Files to Create**: `vue-frontend/src/components/DynamicRubricScores.vue`

**Implementation**:
- Create component that adapts to any rubric structure
- Add dynamic criterion rendering
- Include weight and score display
- Add confidence indicators
- Support for different scoring scales

**Tests**:
```bash
# Test component compilation
cd vue-frontend
npm run build
# Verify no compilation errors
```

**Human Test**:
- Navigate to Overall Feedback page
- Verify rubric scores display correctly
- Check that criterion names are properly formatted
- Verify weights and scores are displayed
- Test with different evaluation results

**Files No Longer Used**: 
- `vue-frontend/src/components/RubricScores.vue` (replaced by DynamicRubricScores)

---

### **Step 4.3: Create Language Detection Display Component**

**Files to Create**: `vue-frontend/src/components/LanguageDetectionDisplay.vue`

**Implementation**:
- Display detected language with flag
- Show confidence score with visual indicator
- Display detection method used
- Add confidence level descriptions
- Support for multiple languages

**Tests**:
```bash
# Test component compilation
cd vue-frontend
npm run build
# Verify no compilation errors
```

**Human Test**:
- Submit text in different languages
- Verify language detection display shows correct language
- Check confidence indicators are visible
- Verify detection method is displayed
- Test with low-confidence detections

**Files No Longer Used**: None (new file)

---

## **Phase 5: View Updates and Integration**

### **Step 5.1: Update Overall Feedback View**

**Files to Modify**: `vue-frontend/src/views/OverallFeedback.vue`

**Implementation**:
- Integrate `DynamicRubricScores` component
- Add `LanguageDetectionDisplay` component
- Update data binding for new evaluation structure
- Remove hardcoded rubric logic
- Add language-specific content display

**Tests**:
```bash
# Test view compilation
cd vue-frontend
npm run build
# Verify no compilation errors
```

**Human Test**:
- Navigate to Overall Feedback page
- Verify language detection is displayed
- Check that rubric scores are dynamic
- Verify strengths/opportunities display correctly
- Test with different evaluation results

**Files No Longer Used**: None (modifications only)

---

### **Step 5.2: Update Detailed Feedback View**

**Files to Modify**: `vue-frontend/src/views/DetailedFeedback.vue`

**Implementation**:
- Update segment feedback display
- Add language detection information
- Update data binding for new structure
- Remove hardcoded feedback categories
- Add dynamic question type support

**Tests**:
```bash
# Test view compilation
cd vue-frontend
npm run build
# Verify no compilation errors
```

**Human Test**:
- Navigate to Detailed Feedback page
- Verify segment feedback displays correctly
- Check that language information is shown
- Verify questions for improvement are displayed
- Test with different evaluation results

**Files No Longer Used**: None (modifications only)

---

### **Step 5.3: Update Evaluation Store**

**Files to Modify**: `vue-frontend/src/stores/evaluation.ts`

**Implementation**:
- Update store interfaces for new evaluation structure
- Add language detection state management
- Update response parsing logic
- Remove deprecated framework-related code

**Tests**:
```bash
# Test store compilation
cd vue-frontend
npm run build
# Verify no compilation errors
```

**Human Test**:
- Submit new evaluation
- Verify store updates correctly
- Check that language detection is stored
- Verify new evaluation structure is handled
- Test store state persistence

**Files No Longer Used**: None (modifications only)

---

## **Phase 6: Testing and Validation**

### **Step 6.1: Backend Integration Testing**

**Files to Create**: `tests/integration/test_enhanced_llm.py`

**Implementation**:
- Test language detection accuracy
- Test prompt generation with different languages
- Test configuration validation
- Test error handling and fallbacks
- Test performance under load

**Tests**:
```bash
# Run integration tests
cd tests/integration
python3 test_enhanced_llm.py
# Verify all tests pass
```

**Human Test**:
- Run test suite and verify 100% pass rate
- Check test coverage for new functionality
- Verify error scenarios are properly handled
- Test performance benchmarks

**Files No Longer Used**: 
- `tests/integration/test_critical_system_local.py` (update for new structure)

---

### **Step 6.2: Frontend Integration Testing**

**Files to Create**: `tests/frontend/test_enhanced_components.py`

**Implementation**:
- Test dynamic rubric display
- Test language detection display
- Test component adaptability
- Test error handling
- Test responsive design

**Tests**:
```bash
# Run frontend tests
cd vue-frontend
npm run test
# Verify all tests pass
```

**Human Test**:
- Test all components in different browsers
- Verify responsive design on mobile/desktop
- Test error scenarios and edge cases
- Verify accessibility features

**Files No Longer Used**: None (new test files)

---

### **Step 6.3: End-to-End Testing with New Rubric Structure**

**Files to Create**: `tests/e2e/test_language_detection.py`

**Implementation**:
- **NEW**: Test complete evaluation workflow with 4-criteria rubric
- **NEW**: Verify weight calculation and scoring accuracy
- **NEW**: Test both English and Spanish evaluation paths
- Test language detection accuracy
- Test prompt generation quality
- Test response parsing and display
- Test error recovery

**Tests**:
```bash
# Run E2E tests
cd tests/e2e
python3 test_language_detection.py
# Verify all tests pass

# Test new rubric structure specifically
python3 -c "
import requests
import json

# Test configuration
base_url = 'http://localhost:8000'
test_texts = {
    'en': 'This is a test business memo in English. It demonstrates good structure and clear arguments.',
    'es': 'Este es un memorando comercial de prueba en español. Demuestra buena estructura y argumentos claros.'
}

def test_new_rubric_structure():
    print('Testing new 4-criteria rubric structure...')
    
    # Test English evaluation
    en_response = requests.post(f'{base_url}/api/v1/evaluations/submit', 
                               json={'text_content': test_texts['en']},
                               headers={'Content-Type': 'application/json'})
    
    assert en_response.status_code == 200, f'English evaluation failed: {en_response.status_code}'
    en_result = en_response.json()
    
    # Verify 4 criteria are present
    en_criteria = en_result['data']['evaluation']['rubric_scores']
    expected_criteria = ['structure', 'arguments_and_evidence', 'strategic_alignment', 'implementation_and_risks']
    for criterion in expected_criteria:
        assert criterion in en_criteria, f'Criterion {criterion} missing from English result'
    
    print('✓ English evaluation uses new rubric structure')
    
    # Test Spanish evaluation
    es_response = requests.post(f'{base_url}/api/v1/evaluations/submit', 
                               json={'text_content': test_texts['es']},
                               headers={'Content-Type': 'application/json'})
    
    assert es_response.status_code == 200, f'Spanish evaluation failed: {es_response.status_code}'
    es_result = es_response.json()
    
    # Verify 4 criteria are present
    es_criteria = es_result['data']['evaluation']['rubric_scores']
    for criterion in expected_criteria:
        assert criterion in es_criteria, f'Criterion {criterion} missing from Spanish result'
    
    print('✓ Spanish evaluation uses new rubric structure')
    
    # Test weight validation
    expected_weights = {
        'structure': 25,
        'arguments_and_evidence': 30,
        'strategic_alignment': 25,
        'implementation_and_risks': 20
    }
    
    total_weight = sum(expected_weights.values())
    assert total_weight == 100, f'Total weight must be 100%, got {total_weight}%'
    print('✓ Weight validation passed (100%)')
    
    print('✓ All new rubric structure tests passed!')

# Run tests
test_new_rubric_structure()
"
```

**Human Test**:
- **NEW**: Complete full evaluation workflow with new 4-criteria rubric
- **NEW**: Verify that all 4 criteria are displayed correctly
- **NEW**: Check that weights (25%, 30%, 25%, 20%) are applied properly
- Test with English and Spanish text
- Verify appropriate language prompts
- Check response quality and accuracy
- Test error scenarios

**Files No Longer Used**: None (new test files)

---

## **Phase 6.5: Comprehensive Testing Summary**

### **Testing Checklist for New Rubric Structure**

**Backend Testing**:
- [ ] Pydantic models validate new rubric structure correctly
- [ ] Weight validation ensures total equals 100%
- [ ] Scoring range validation (1-5 scale) works correctly
- [ ] Language detection works for both English and Spanish
- [ ] Jinja2 templates render new rubric structure properly
- [ ] Enhanced LLM service processes new rubric correctly
- [ ] API endpoints return new rubric structure
- [ ] Weight calculation produces correct overall scores

**Frontend Testing**:
- [ ] DynamicRubricScores component displays 4 criteria correctly
- [ ] Weights are visible and accurate (25%, 30%, 25%, 20%)
- [ ] Scores are displayed correctly for each criterion
- [ ] Overall score calculation uses new weights
- [ ] LanguageDetectionDisplay component works correctly
- [ ] Responsive design works on all devices
- [ ] Error handling works gracefully

**Integration Testing**:
- [ ] Complete evaluation workflow works end-to-end
- [ ] Both English and Spanish evaluations complete successfully
- [ ] New rubric structure is consistent across all components
- [ ] Performance meets requirements (<15 seconds)
- [ ] Error scenarios are handled properly
- [ ] Configuration changes take effect without restarts

**Configuration Testing**:
- [ ] prompt.yaml contains new rubric structure
- [ ] rubric.yaml is properly deprecated
- [ ] No references to old rubric structure exist
- [ ] Validation scripts work with new structure
- [ ] Hot-reload capability works correctly

**Run All Tests**:
```bash
# Backend tests
cd backend
python3 -m pytest tests/ -v

# Frontend tests
cd ../vue-frontend
npm run test

# Integration tests
cd ../tests/integration
python3 test_enhanced_llm.py

# End-to-end tests
cd ../tests/e2e
python3 test_language_detection.py

# Configuration validation
cd ../../backend
python3 validate_config.py
```

---

## **Phase 7: Documentation and Deployment**

### **Step 7.1: Update API Documentation**

**Files to Modify**: `docs/05_API_Documentation.md`

**Implementation**:
- Document new language detection endpoints
- Update evaluation response structure
- Add language detection examples
- Update configuration documentation
- Remove deprecated framework documentation

**Tests**:
```bash
# Verify documentation accuracy
python3 -c "
# Test documented API endpoints
print('Documentation validation complete')
"
```

**Human Test**:
- Review API documentation for accuracy
- Test documented endpoints
- Verify examples work correctly
- Check that deprecated content is removed

**Files No Longer Used**: 
- Framework-related documentation sections

---

### **Step 7.2: Update Configuration Guide**

**Files to Modify**: `docs/04_Configuration_Guide.md`

**Implementation**:
- Document new prompt.yaml structure
- Add language configuration examples
- Update validation requirements
- Remove framework configuration docs
- Add language detection configuration

**Tests**:
```bash
# Validate configuration examples
python3 -c "
from models.config_models import PromptConfig
import yaml
# Test documented configuration examples
print('Configuration examples valid')
"
```

**Human Test**:
- Review configuration guide for accuracy
- Test documented configuration examples
- Verify validation requirements are clear
- Check that deprecated content is removed

**Files No Longer Used**: 
- Framework configuration documentation

---

### **Step 7.3: Update Development Guide**

**Files to Modify**: `docs/08_Development_Guide.md`

**Implementation**:
- Document new architecture patterns
- Add Pydantic model usage examples
- Document Jinja2 template system
- Add language detection development guide
- Remove deprecated framework development docs

**Tests**:
```bash
# Verify development examples
python3 -c "
# Test documented development examples
print('Development examples valid')
"
```

**Human Test**:
- Review development guide for accuracy
- Test documented examples
- Verify architecture patterns are clear
- Check that deprecated content is removed

**Files No Longer Used**: 
- Framework development documentation

---

## **Phase 8: Performance Optimization and Monitoring**

### **Step 8.1: Add Performance Monitoring**

**Files to Create**: `backend/services/performance_monitor.py`

**Implementation**:
- Monitor language detection performance
- Track prompt generation timing
- Monitor LLM response times
- Add performance metrics to health checks
- Implement caching strategies

**Tests**:
```python
# Test performance monitoring
python3 -c "
from services.performance_monitor import PerformanceMonitor
monitor = PerformanceMonitor()
print('Performance monitoring active')
"
```

**Human Test**:
- Check performance metrics in admin interface
- Verify monitoring data is collected
- Test performance under load
- Check caching effectiveness

**Files No Longer Used**: None (new file)

---

### **Step 8.2: Implement Caching Strategies**

**Files to Modify**: `backend/services/llm_service.py`

**Implementation**:
- Cache compiled Jinja2 templates
- Cache language detection results
- Cache configuration validation results
- Implement cache invalidation
- Add cache performance metrics

**Tests**:
```python
# Test caching functionality
python3 -c "
from services.llm_service import EnhancedLLMService
service = EnhancedLLMService()
# Test caching behavior
print('Caching functional')
"
```

**Human Test**:
- Submit multiple evaluations
- Verify caching improves performance
- Check cache hit rates in monitoring
- Test cache invalidation scenarios

**Files No Longer Used**: None (modifications only)

---

## **Phase 9: Comprehensive Testing and Validation**

### **Step 9.1: Language Detection Accuracy Testing**

**Files to Create**: `tests/accuracy/test_language_detection.py`

**Implementation**:
- Test with 100+ English text samples (various lengths, topics, styles)
- Test with 100+ Spanish text samples (various dialects, formal/informal)
- Test with mixed language text
- Test with code, numbers, and special characters
- Test edge cases (very short text, very long text, gibberish)

**Test Data Requirements**:
```python
# English test samples
english_samples = [
    "Hello world",  # Very short
    "This is a business memo about healthcare investments...",  # Medium
    "The comprehensive analysis demonstrates...",  # Long formal
    "Hey there! How's it going?",  # Informal
    "ROI analysis shows 15% return...",  # Technical
    # ... 95+ more samples
]

# Spanish test samples
spanish_samples = [
    "Hola mundo",  # Very short
    "Este es un memorando comercial sobre inversiones en salud...",  # Medium
    "El análisis integral demuestra...",  # Long formal
    "¡Hola! ¿Cómo estás?",  # Informal
    "El análisis de ROI muestra un retorno del 15%...",  # Technical
    # ... 95+ more samples
]
```

**Success Criteria**:
- English detection accuracy: ≥98%
- Spanish detection accuracy: ≥95%
- Mixed language handling: ≥90%
- Confidence score correlation: ≥0.8

**Human Test**:
- Run accuracy test suite
- Review misclassified samples
- Verify confidence scores correlate with accuracy
- Check detection method distribution

**Files No Longer Used**: None (new test files)

---

### **Step 9.2: Prompt Generation Quality Testing**

**Files to Create**: `tests/quality/test_prompt_generation.py`

**Implementation**:
- Test prompt generation with all language configurations
- Test prompt generation with various rubric structures
- Test prompt generation with different text lengths
- Test prompt generation error handling
- Test prompt generation performance

**Test Scenarios**:
```python
# Test different rubric structures
test_rubrics = [
    {"criteria": [{"name": "Test", "weight": 100}]},  # Single criterion
    {"criteria": [{"name": "A", "weight": 50}, {"name": "B", "weight": 50}]},  # Two criteria
    {"criteria": [{"name": "X", "weight": 25}, {"name": "Y", "weight": 25}, {"name": "Z", "weight": 50}]},  # Three criteria
    # ... more complex structures
]

# Test different text lengths
test_texts = [
    "Short",  # Very short
    "This is a medium length text for testing purposes.",  # Medium
    "This is a very long text that exceeds normal evaluation lengths..." * 100,  # Very long
]
```

**Success Criteria**:
- All prompts generate without errors
- Prompts include all required sections
- Language-specific content is correct
- Response format is clearly specified
- Generation time <500ms

**Human Test**:
- Run prompt generation test suite
- Manually review generated prompts
- Verify language-specific content accuracy
- Check response format clarity

**Files No Longer Used**: None (new test files)

---

### **Step 9.3: LLM Response Quality Testing**

**Files to Create**: `tests/quality/test_llm_responses.py`

**Implementation**:
- Test LLM responses with different languages
- Test LLM responses with different rubric structures
- Test LLM response parsing and validation
- Test LLM response error handling
- Test LLM response performance

**Test Scenarios**:
```python
# Test different evaluation types
test_evaluations = [
    {"language": "en", "rubric": "simple", "text": "English business memo"},
    {"language": "es", "rubric": "simple", "text": "Spanish business memo"},
    {"language": "en", "rubric": "complex", "text": "Complex English memo"},
    {"language": "es", "rubric": "complex", "text": "Complex Spanish memo"},
]
```

**Success Criteria**:
- All responses parse without errors
- Response structure matches expected format
- Language-specific content is appropriate
- Scores are within valid ranges
- Response time <15 seconds

**Human Test**:
- Run LLM response test suite
- Manually review parsed responses
- Verify response structure accuracy
- Check language-specific content quality

**Files No Longer Used**: None (new test files)

---

### **Step 9.4: Frontend Display Testing**

**Files to Create**: `tests/frontend/test_display_adaptability.py`

**Implementation**:
- Test frontend with different rubric structures
- Test frontend with different languages
- Test frontend error handling
- Test frontend performance
- Test frontend accessibility

**Test Scenarios**:
```python
# Test different evaluation results
test_evaluations = [
    {"rubric": "simple", "language": "en", "criteria_count": 3},
    {"rubric": "complex", "language": "en", "criteria_count": 7},
    {"rubric": "simple", "language": "es", "criteria_count": 3},
    {"rubric": "complex", "language": "es", "criteria_count": 7},
]
```

**Success Criteria**:
- All rubric structures display correctly
- Language detection information is visible
- Error states are handled gracefully
- Performance meets requirements (<1s load time)
- Accessibility standards are met

**Human Test**:
- Run frontend display test suite
- Test with different browsers and devices
- Verify responsive design works
- Check accessibility compliance

**Files No Longer Used**: None (new test files)

---

### **Step 9.5: System Integration Testing**

**Files to Create**: `tests/integration/test_system_integration.py`

**Implementation**:
- Test complete system workflow
- Test system performance under load
- Test system error handling
- Test system monitoring and health checks
- Test system configuration management

**Test Scenarios**:
```python
# Test complete workflows
workflows = [
    {"name": "English Evaluation", "language": "en", "complexity": "simple"},
    {"name": "Spanish Evaluation", "language": "es", "complexity": "simple"},
    {"name": "Complex English", "language": "en", "complexity": "complex"},
    {"name": "Complex Spanish", "language": "es", "complexity": "complex"},
    {"name": "Mixed Language", "language": "mixed", "complexity": "simple"},
]
```

**Success Criteria**:
- All workflows complete successfully
- System performance meets requirements
- Error handling works correctly
- Monitoring provides accurate data
- Configuration changes take effect

**Human Test**:
- Run system integration test suite
- Monitor system performance metrics
- Verify error handling effectiveness
- Check monitoring data accuracy

**Files No Longer Used**: None (new test files)

---

### **Step 9.6: Performance and Load Testing**

**Files to Create**: `tests/performance/test_system_performance.py`

**Implementation**:
- Test system performance under normal load
- Test system performance under high load
- Test system performance with different configurations
- Test system resource usage
- Test system scalability

**Test Scenarios**:
```python
# Performance test scenarios
performance_tests = [
    {"name": "Single User", "concurrent_users": 1, "evaluations_per_user": 10},
    {"name": "Low Load", "concurrent_users": 10, "evaluations_per_user": 5},
    {"name": "Medium Load", "concurrent_users": 50, "evaluations_per_user": 3},
    {"name": "High Load", "concurrent_users": 100, "evaluations_per_user": 2},
]
```

**Success Criteria**:
- Single evaluation: <15 seconds
- Low load: <30 seconds average
- Medium load: <45 seconds average
- High load: <60 seconds average
- Resource usage within limits

**Human Test**:
- Run performance test suite
- Monitor system resources
- Verify performance targets are met
- Check resource usage patterns

**Files No Longer Used**: None (new test files)

---

### **Step 9.7: Security and Error Handling Testing**

**Files to Create**: `tests/security/test_security_and_errors.py`

**Implementation**:
- Test input validation and sanitization
- Test error handling and user feedback
- Test security boundaries
- Test configuration validation
- Test fallback mechanisms

**Test Scenarios**:
```python
# Security and error test scenarios
security_tests = [
    {"name": "Malicious Input", "input": "<script>alert('xss')</script>"},
    {"name": "Invalid Configuration", "config": {"invalid": "config"}},
    {"name": "Large Input", "input": "A" * 100000},
    {"name": "Empty Input", "input": ""},
    {"name": "Special Characters", "input": "!@#$%^&*()_+-=[]{}|;':\",./<>?"},
]
```

**Success Criteria**:
- All malicious inputs are rejected
- Invalid configurations are caught
- Large inputs are handled gracefully
- Empty inputs are rejected appropriately
- Special characters are handled correctly

**Human Test**:
- Run security and error test suite
- Verify error messages are user-friendly
- Check that security boundaries are enforced
- Test fallback mechanisms work correctly

**Files No Longer Used**: None (new test files)

---

## **Phase 10: File Cleanup and Deprecation**

### **Step 10.1: Identify and Remove Deprecated Files**

**Files to DELETE** (confirmed no longer needed):

**Backend Services**:
- `backend/services/llm_service_backup.py` - Backup file, replaced by enhanced service
- `backend/services/llm_service_improved.py` - Intermediate version, replaced by final implementation
- `backend/services/auth_service_backup.py` - Backup file, not needed

**Deprecated Documentation**:
- `deprecated/devspecs/` - Entire directory, replaced by `docs/` directory
  - `deprecated/devspecs/00_Devspecs_Overview.md`
  - `deprecated/devspecs/01_Requirements.md`
  - `deprecated/devspecs/02_Architecture.md`
  - `deprecated/devspecs/03_Data_Model.md`
  - `deprecated/devspecs/04_API_Definitions.md`
  - `deprecated/devspecs/05_UI_UX.md`
  - `deprecated/devspecs/06_Testing.md`
  - `deprecated/devspecs/07_Deployment.md`
  - `deprecated/devspecs/08_Maintenance.md`
  - `deprecated/devspecs/09_Dev_Roadmap.md`

**Frontend Components**:
- `vue-frontend/src/components/RubricScores.vue` - Replaced by DynamicRubricScores.vue

**Configuration Files**:
- **NEW**: `config/rubric.yaml` - Entire file deprecated, all content moved to prompt.yaml
- Remove `frameworks` section from `config/rubric.yaml` (deprecated content)

**Implementation**:
```bash
# Remove deprecated backend files
rm backend/services/llm_service_backup.py
rm backend/services/llm_service_improved.py
rm backend/services/auth_service_backup.py

# Remove deprecated documentation
rm -rf deprecated/devspecs/

# Remove deprecated frontend components
rm vue-frontend/src/components/RubricScores.vue

# **NEW**: Deprecate rubric.yaml (move content to prompt.yaml first)
echo "# DEPRECATED: This file is no longer used. All rubric content has been moved to prompt.yaml" > config/rubric.yaml
echo "# The new rubric structure uses 4 criteria with weights totaling 100%" >> config/rubric.yaml
echo "# See prompt.yaml for the current rubric configuration" >> config/rubric.yaml

# Clean up empty directories
rmdir deprecated/ 2>/dev/null || true
```

**Tests**:
```bash
# Verify deprecated files are removed
ls backend/services/llm_service_backup.py 2>/dev/null && echo "ERROR: File still exists" || echo "File removed successfully"
ls backend/services/llm_service_improved.py 2>/dev/null && echo "ERROR: File still exists" || echo "File removed successfully"
ls deprecated/devspecs/ 2>/dev/null && echo "ERROR: Directory still exists" || echo "Directory removed successfully"

# **NEW**: Verify rubric.yaml is properly deprecated
grep -q "DEPRECATED" config/rubric.yaml && echo "✓ rubric.yaml properly deprecated" || echo "✗ rubric.yaml not properly deprecated"

# **NEW**: Verify no references to old rubric structure exist
grep -r "frameworks" backend/ --exclude="*.pyc" --exclude="__pycache__" && echo "✗ References to frameworks found" || echo "✓ No references to frameworks found"
grep -r "evaluation_framework" backend/ --exclude="*.pyc" --exclude="__pycache__" && echo "✗ References to evaluation_framework found" || echo "✓ No references to evaluation_framework found"

# **NEW**: Verify new rubric structure is accessible
python3 -c "
from models.config_models import PromptConfig
import yaml
config = PromptConfig(**yaml.safe_load(open('config/prompt.yaml')))
print('✓ New rubric structure accessible')
"
```

**Human Test**:
- Verify deprecated files are removed from file system
- Check that application still functions correctly
- Verify no broken imports or references
- Confirm system is cleaner and more maintainable

---

### **Step 10.2: Update Configuration Files**

**Files to Modify**: `config/rubric.yaml`

**Implementation**:
- Remove entire `frameworks` section
- Remove `evaluation_framework` section
- Remove `segment_evaluation` section
- Keep only essential rubric criteria and scoring

**Tests**:
```bash
# Validate configuration after cleanup
python3 -c "
import yaml
config = yaml.safe_load(open('config/rubric.yaml'))
assert 'frameworks' not in config, 'Frameworks section still exists'
assert 'evaluation_framework' not in config, 'Evaluation framework section still exists'
print('Configuration cleanup successful')
"
```

**Human Test**:
- Open `config/rubric.yaml` in browser
- Verify deprecated sections are removed
- Check that essential rubric content remains
- Verify configuration is still valid

---

### **Step 10.3: Update Import Statements and References**

**Files to Check and Update**:
- `backend/main.py` - Remove any imports of deprecated services
- `backend/__init__.py` - Remove deprecated service imports
- `vue-frontend/src/views/OverallFeedback.vue` - Update component import
- Any other files that reference deprecated components

**Tests**:
```bash
# Check for remaining references to deprecated files
grep -r "llm_service_backup" backend/ || echo "No backup service references found"
grep -r "llm_service_improved" backend/ || echo "No improved service references found"
grep -r "RubricScores" vue-frontend/src/ || echo "No RubricScores references found"
```

**Human Test**:
- Search codebase for deprecated file references
- Verify no broken imports exist
- Check that application compiles and runs
- Confirm all functionality works correctly

---

## **Implementation Timeline**

| Phase | Duration | Dependencies | Key Deliverables |
|-------|----------|--------------|------------------|
| Phase 1 | 1-2 weeks | None | Dependencies, models, language detection |
| Phase 2 | 1 week | Phase 1 | Configuration refactoring, templates |
| Phase 3 | 1-2 weeks | Phase 2 | LLM service refactoring |
| Phase 4 | 1 week | Phase 3 | Frontend types and components |
| Phase 5 | 1 week | Phase 4 | View updates and integration |
| Phase 6 | 1-2 weeks | Phase 5 | Testing and validation |
| Phase 7 | 1 week | Phase 6 | Documentation updates |
| Phase 8 | 1 week | Phase 7 | Performance optimization |
| Phase 9 | 2-3 weeks | Phase 8 | Comprehensive testing |
| Phase 10 | 1 week | Phase 9 | File cleanup and deprecation |

**Total Estimated Duration**: 11-15 weeks (includes Phase 11: Lessons Learned)

---

## **Phase 11: Implementation Lessons Learned and Best Practices**

### **Step 11.1: Schema Analysis and Planning (NEW)**

**What Was Missing**: The original plan didn't account for the mismatch between YAML structure and Pydantic model expectations.

**Implementation**:
- [ ] Analyze existing YAML structures in detail before implementing models
- [ ] Create configuration structure diagrams showing nested vs. flat patterns
- [ ] Document field type requirements and constraints
- [ ] Identify configuration evolution patterns and versioning needs

**Tests**:
```python
# Test config structure analysis
def test_config_structure():
    with open('config/llm.yaml') as f:
        config = yaml.safe_load(f)
    print("Actual structure:", json.dumps(config, indent=2))
    # This reveals nested structures early and prevents validation failures
```

**Human Test**:
- Open each configuration file and map the actual structure
- Create visual diagrams of nested configurations
- Document any inconsistencies between expected and actual structures

**Files Modified**: None (planning phase)

---

### **Step 11.2: Critical Configuration Validation Fixes (IMPLEMENTATION EXPERIENCE)**

**What We Learned**: The existing `config_service.py` validation functions were incompatible with the new configuration structure and caused startup failures.

**CRITICAL FIXES REQUIRED**:

#### **Fix 1: Update _validate_rubric_config in config_service.py**
```python
def _validate_rubric_config(self, config: Dict[str, Any]) -> None:
    """Validate rubric configuration - now deprecated and skipped"""
    logger.info("✓ rubric.yaml - Deprecated file, skipping validation")
    return
```

#### **Fix 2: Update _validate_prompt_config in config_service.py**
```python
def _validate_prompt_config(self, config: Dict[str, Any]) -> None:
    """Validate prompt configuration with new structure"""
    required_fields = ['languages', 'default_language', 'confidence_threshold']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field '{field}' in prompt.yaml")
    
    # Check required languages
    if 'languages' in config:
        required_languages = ['en', 'es']
        for lang in required_languages:
            if lang not in config['languages']:
                raise ValueError(f"Missing required language: {lang}")
            
            lang_config = config['languages'][lang]
            for section in ['context', 'request', 'rubric']:
                if section not in lang_config:
                    raise ValueError(f"Missing {section} section in {lang} language")
```

#### **Fix 3: Ensure rubric.yaml Contains Valid YAML Content**
```yaml
# config/rubric.yaml - MUST contain valid YAML, not just comments
status: "deprecated"
message: "This file is no longer used. All rubric content has been moved to prompt.yaml"
deprecation_date: "2024-01-01"
replacement_file: "prompt.yaml"
```

**Why This Happened**:
- YAML parsers treat files with only comments as empty
- Empty files fail `validate_yaml_file` function
- Old validation logic expected deprecated fields that no longer exist
- `config_service.py` runs during startup and must handle new structure

**Implementation Order**:
1. **FIRST**: Update `config_service.py` validation functions
2. **SECOND**: Ensure `rubric.yaml` has valid YAML content
3. **THIRD**: Test backend startup
4. **FOURTH**: Continue with other implementation phases

**Files Modified**: `backend/services/config_service.py`, `config/rubric.yaml`

---

### **Step 11.3: Pydantic Model Design Strategy (REVISED)**

**What Was Missing**: The plan assumed static configuration schemas and didn't plan for flexibility.

**Implementation**:
- [ ] Start with flexible `Dict[str, Any]` models for complex configurations
- [ ] Implement property-based access for nested structures
- [ ] Add validation gradually, not all at once
- [ ] Include schema versioning from the start
- [ ] Plan for backward compatibility and migrations

**Implementation Tip**:
```python
# Instead of this (causes validation failures):
class LLMConfig(BaseModel):
    provider: str = Field(...)
    language_detection: Dict[str, Union[str, int, float, bool, List[str]]] = Field(...)

# Start with this (allows flexibility):
class LLMConfig(BaseModel):
    provider: Dict[str, Any] = Field(...)
    language_detection: Dict[str, Any] = Field(...)
```

**Tests**:
```python
# Test progressive validation
def test_config_progressive(config_data: dict, strict: bool = False):
    if strict:
        return StrictConfigModel(**config_data)
    else:
        return FlexibleConfigModel(**config_data)
```

**Human Test**:
- Create test configurations with various complexity levels
- Verify models can handle both simple and nested structures
- Test schema evolution scenarios

**Files Modified**: `backend/models/config_models.py`

---

### **Step 11.2: Pydantic Model Design Strategy (REVISED)**

**What Was Missing**: The plan assumed static configuration schemas and didn't plan for flexibility.

**Implementation**:
- [ ] Start with flexible `Dict[str, Any]` models for complex configurations
- [ ] Implement property-based access for nested structures
- [ ] Add validation gradually, not all at once
- [ ] Include schema versioning from the start
- [ ] Plan for backward compatibility and migrations

**Implementation Tip**:
```python
# Instead of this (causes validation failures):
class LLMConfig(BaseModel):
    provider: str = Field(...)
    language_detection: Dict[str, Union[str, int, float, bool, List[str]]] = Field(...)

# Start with this (allows flexibility):
class LLMConfig(BaseModel):
    provider: Dict[str, Any] = Field(...)
    language_detection: Dict[str, Any] = Field(...)
```

**Tests**:
```python
# Test progressive validation
def test_config_progressive(config_data: dict, strict: bool = False):
    if strict:
        return StrictConfigModel(**config_data)
    else:
        return FlexibleConfigModel(**config_data)
```

**Human Test**:
- Create test configurations with various complexity levels
- Verify models can handle both simple and nested structures
- Test schema evolution scenarios

**Files Modified**: `backend/models/config_models.py`

---

### **Step 11.3: Validation Coordination Planning (NEW)**

**What Was Missing**: The plan didn't address coordination between multiple validation layers.

**Implementation**:
- [ ] Map validation responsibilities across components
- [ ] Create validation execution order and hierarchy
- [ ] Implement progressive validation levels
- [ ] Add configuration hot-reload capability
- [ ] Plan for validation error handling and user feedback

**Validation Hierarchy**:
```
1. YAML Syntax Validation (yaml.safe_load)
2. Pydantic Schema Validation (config_models.py)
3. Service-Level Validation (config_service.py)
4. Runtime Validation (llm_service.py)
5. User Input Validation (API endpoints)
```

**Implementation Tip**:
```python
# Create validation coordination matrix
VALIDATION_MATRIX = {
    'rubric.yaml': ['syntax', 'schema', 'service', 'runtime'],
    'prompt.yaml': ['syntax', 'schema', 'service', 'runtime'],
    'llm.yaml': ['syntax', 'schema', 'service', 'runtime'],
    'auth.yaml': ['syntax', 'schema', 'service', 'runtime']
}
```

**Tests**:
```python
# Test validation coordination
def test_validation_flow():
    # Test each validation level in sequence
    # Verify errors are caught at appropriate levels
    # Test hot-reload functionality
```

**Human Test**:
- Modify configuration files and verify validation catches errors
- Test hot-reload capability without container restarts
- Verify validation error messages are helpful

**Files Modified**: `backend/services/config_service.py`, `backend/validate_config.py`

---

### **Step 11.4: Import and Module Dependency Management (NEW)**

**What Was Missing**: The plan didn't account for circular imports and module initialization order.

**Implementation**:
- [ ] Create module dependency graph before implementation
- [ ] Plan global function placement and service instances
- [ ] Document startup sequence to avoid "name not defined" errors
- [ ] Implement lazy initialization patterns
- [ ] Plan for dependency injection or service locator patterns

**Module Dependency Graph**:
```
main.py
├── services/__init__.py
├── services/config_service.py
├── services/llm_service.py
├── services/language_detection.py
├── models/config_models.py
└── validate_config.py
```

**Implementation Tip**:
```python
# Use lazy initialization to avoid startup-time import issues
class ServiceManager:
    def __init__(self):
        self._llm_service = None
        self._language_detector = None
    
    @property
    def llm_service(self):
        if self._llm_service is None:
            self._llm_service = EnhancedLLMService()
        return self._llm_service
```

**Tests**:
```python
# Test module initialization
def test_module_dependencies():
    # Verify no circular imports
    # Test startup sequence
    # Verify global functions are available when needed
```

**Human Test**:
- Start backend container and monitor startup logs
- Verify no import errors or "name not defined" issues
- Test service availability after startup

**Files Modified**: `backend/main.py`, `backend/services/__init__.py`

---

### **Step 11.5: Language Detection and Template Path Issues (IMPLEMENTATION EXPERIENCE)**

**What We Learned**: Several critical issues emerged during implementation that weren't anticipated in the original plan.

#### **Fix 1: Language Enum Duplication**
**Problem**: Two `Language` enums were defined, causing `AttributeError: UNKNOWN`.

**Solution**:
```python
# REMOVE from backend/services/language_detection.py:
# class Language(str, Enum):
#     EN = "en"
#     ES = "es"

# KEEP in backend/models/config_models.py:
class Language(str, Enum):
    EN = "en"
    ES = "es"
    UNKNOWN = "unknown"  # Add this for fallback scenarios
```

#### **Fix 2: Jinja2 Template Path Resolution**
**Problem**: Template paths were incorrect when running from different contexts.

**Solution**:
```python
# In backend/services/llm_service.py:
# WRONG (causes TemplateNotFound):
self.jinja_env = Environment(loader=FileSystemLoader('backend/templates'))

# CORRECT (works from backend directory):
self.jinja_env = Environment(loader=FileSystemLoader('templates'))

# ALTERNATIVE (absolute path for reliability):
import os
template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
```

#### **Fix 3: Service Export Updates**
**Problem**: After updating service names, imports failed because `__init__.py` wasn't updated.

**Solution**:
```python
# In backend/services/__init__.py:
# OLD (causes ImportError):
from .llm_service import LLMService, get_llm_service, evaluate_text_with_llm

# NEW (exports new service):
from .llm_service import EnhancedLLMService

__all__ = ['EnhancedLLMService']
```

**Why These Issues Occurred**:
- Language detection service was created independently without checking existing models
- Template paths assumed specific working directory context
- Service refactoring didn't update all import/export references
- Docker container rebuilds required after code changes

**Implementation Order**:
1. **FIRST**: Ensure single Language enum definition in `config_models.py`
2. **SECOND**: Use relative paths for Jinja2 templates
3. **THIRD**: Update all service exports in `__init__.py`
4. **FOURTH**: Test imports and template loading
5. **FIFTH**: Rebuild containers to apply changes

**Files Modified**: 
- `backend/services/language_detection.py` (remove duplicate Language enum)
- `backend/services/llm_service.py` (fix template paths)
- `backend/services/__init__.py` (update exports)
- `backend/models/config_models.py` (ensure UNKNOWN enum value)

---

### **Step 11.6: Container Rebuild Requirements (IMPLEMENTATION EXPERIENCE)**

**What We Learned**: Python code changes require container rebuilds, not just restarts.

**Critical Understanding**:
- `docker compose restart` only restarts the container with existing code
- `docker compose build backend` rebuilds the container with new code
- Python import caching can cause old code to persist even after rebuilds
- Always rebuild after significant code changes

**Implementation Workflow**:
```bash
# After code changes:
docker compose build backend
docker compose up backend -d

# Verify changes took effect:
docker compose logs backend --tail=20

# Test functionality:
curl http://localhost:8000/health
```

**Why This Matters**:
- Language detection service changes require rebuild
- Pydantic model updates require rebuild
- Service refactoring requires rebuild
- Configuration validation changes require rebuild

**Files Modified**: All backend Python files require container rebuilds

---

### **Step 11.5: Configuration Schema Evolution Planning (NEW)**

**What Was Missing**: The plan assumed static configuration schemas, but real-world configs evolve.

**Implementation**:
- [ ] Include version fields in all configuration files
- [ ] Implement schema migration logic and validation
- [ ] Plan for backward compatibility without breaking deployments
- [ ] Create configuration upgrade scripts and procedures
- [ ] Document schema change procedures and testing

**Schema Versioning**:
```yaml
# Add to all config files
version: "1.0.0"
schema_version: "2024.1"
compatibility: ["1.0.0", "0.9.0"]  # Backward compatible versions
```

**Implementation Tip**:
```python
# Implement schema migration
class ConfigMigrator:
    def migrate_config(self, config_data: dict, target_version: str):
        current_version = config_data.get('version', '0.0.0')
        if current_version != target_version:
            return self._apply_migrations(config_data, current_version, target_version)
        return config_data
```

**Tests**:
```python
# Test schema evolution
def test_schema_migration():
    # Test migration from old to new schemas
    # Verify backward compatibility
    # Test rollback scenarios
```

**Human Test**:
- Create configurations with different versions
- Test migration scripts and procedures
- Verify backward compatibility works as expected

**Files Modified**: All configuration files, `backend/services/config_service.py`

---

## **Implementation Best Practices Summary**

### **Configuration Management**
1. **Configuration First**: Always analyze existing configs before designing models
2. **Flexibility Over Strictness**: Start with loose validation, tighten gradually
3. **Schema Evolution**: Plan for configuration changes and migrations
4. **Version Control**: Include versioning in all configuration files

### **Validation Strategy**
1. **Progressive Implementation**: Implement features incrementally with working checkpoints
2. **Validation Coordination**: Plan how multiple validation layers work together
3. **Error Handling**: Comprehensive error handling and user feedback
4. **Testing Strategy**: Test config loading before implementing complex validation

### **Module and Import Planning**
1. **Dependency Mapping**: Create module dependency graph before coding
2. **Startup Sequence**: Document and test startup sequence
3. **Lazy Initialization**: Use lazy initialization patterns for services
4. **Global Function Planning**: Plan global function placement carefully

### **Testing and Quality Assurance**
1. **Configuration Testing**: Test with real configuration files
2. **Progressive Validation**: Test validation at each level
3. **Migration Testing**: Test schema evolution scenarios
4. **Performance Testing**: Test configuration loading performance

---

## **CRITICAL IMPLEMENTATION CHECKLIST (From Experience)**

### **Phase 1: Pre-Implementation Setup**
- [ ] **MANDATORY**: Update `config_service.py` validation functions FIRST
- [ ] **MANDATORY**: Ensure `rubric.yaml` contains valid YAML (not just comments)
- [ ] **MANDATORY**: Plan container rebuild workflow for all code changes
- [ ] **MANDATORY**: Create single Language enum definition in `config_models.py`

### **Phase 2: Configuration Updates**
- [ ] **MANDATORY**: Use `Dict[str, Any]` for complex nested configurations
- [ ] **MANDATORY**: Test YAML parsing before Pydantic validation
- [ ] **MANDATORY**: Verify template paths work from backend directory
- [ ] **MANDATORY**: Update all service exports in `__init__.py`

### **Phase 3: Service Implementation**
- [ ] **MANDATORY**: Import Language enum from `config_models.py` only
- [ ] **MANDATORY**: Use relative paths for Jinja2 templates
- [ ] **MANDATORY**: Test imports before implementing complex logic
- [ ] **MANDATORY**: Rebuild container after each significant change

### **Phase 4: Testing and Validation**
- [ ] **MANDATORY**: Test configuration loading before service initialization
- [ ] **MANDATORY**: Verify no circular imports or "name not defined" errors
- [ ] **MANDATORY**: Test template rendering with actual configuration data
- [ ] **MANDATORY**: Validate startup sequence in container environment

### **Phase 5: Deployment and Verification**
- [ ] **MANDATORY**: Always rebuild containers after code changes
- [ ] **MANDATORY**: Check container logs for startup errors
- [ ] **MANDATORY**: Test health endpoints before proceeding
- [ ] **MANDATORY**: Verify configuration validation works end-to-end

### **Common Failure Points (Avoid These)**:
1. **Empty YAML files**: YAML parsers treat comment-only files as empty
2. **Duplicate enum definitions**: Causes AttributeError and import confusion
3. **Incorrect template paths**: Causes TemplateNotFound errors
4. **Missing service exports**: Causes ImportError in other modules
5. **Container restart vs rebuild**: Restart doesn't load new code
6. **Validation order**: Old validation logic must be updated before new features

---

## **Risk Assessment and Mitigation**

### **High Risk Items**
1. **Language Detection Accuracy**: Implement multiple fallback methods
2. **Configuration Migration**: Provide migration scripts and validation
3. **Performance Impact**: Implement caching and monitoring early

### **Medium Risk Items**
1. **Template Complexity**: Start with simple templates and iterate
2. **Frontend Compatibility**: Test across different browsers and devices
3. **Error Handling**: Comprehensive error handling and user feedback

### **Low Risk Items**
1. **Dependency Installation**: Standard package management
2. **Documentation Updates**: Incremental updates with validation
3. **Testing Implementation**: Standard testing frameworks

---

## **Success Metrics**

### **Technical Metrics**
- 100% configuration validation through Pydantic
- 95%+ language detection accuracy
- <2 second prompt generation time
- <15 second total evaluation time
- 100% test coverage for new functionality

### **User Experience Metrics**
- Zero hardcoded prompt logic
- Frontend automatically adapts to rubric changes
- Support for English and Spanish with easy expansion
- Improved error messages and user feedback
- Better performance and responsiveness

### **Maintenance Metrics**
- Reduced configuration errors
- Easier prompt modification
- Simplified language addition process
- Better debugging and monitoring capabilities
- Improved code maintainability

---

## **Rollback Plan**

### **Immediate Rollback (Phase 1-3)**
- Revert to previous LLM service implementation
- Restore original prompt.yaml structure
- Disable new language detection features
- Maintain existing functionality

### **Partial Rollback (Phase 4-6)**
- Keep backend improvements
- Revert frontend changes
- Maintain configuration validation
- Disable dynamic rubric display

### **Full Rollback (Phase 7-10)**
- Complete system reversion
- Restore all original files
- Maintain database compatibility
- Preserve user data

---

## **Post-Implementation Review**

### **Technical Review**
- Performance impact assessment
- Error rate reduction measurement
- Configuration validation effectiveness
- Language detection accuracy validation

### **User Experience Review**
- User feedback collection
- Interface usability assessment
- Error message effectiveness
- Performance perception

### **Maintenance Review**
- Configuration modification ease
- Debugging capability improvement
- Monitoring effectiveness
- Code maintainability assessment

---

**Document Status**: Active Implementation Plan with Lessons Learned and Best Practices  
**Next Review**: After Phase 11 completion  
**Contact**: Development Team for implementation questions  
**Version Control**: Track all changes in git with descriptive commit messages
