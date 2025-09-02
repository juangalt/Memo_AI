# **Prompt Refactor Implementation Plan**
## **Enhanced LLM Service with Pydantic, Jinja2, and Robust Language Detection**

**Document ID**: prompt_refactor.md  
**Document Version**: 1.1  
**Last Updated**: Phase 1 - Planning with Enhanced Testing  
**Status**: Active Implementation Plan  

---

## **Executive Summary**

This document outlines the implementation plan for refactoring the Memo AI Coach prompt generation system to use Pydantic for configuration validation, Jinja2 for dynamic template generation, and robust language detection using Polyglot/Langdetect. The refactor will improve system robustness, flexibility, and maintainability while adding multi-language support.

### **Key Objectives**
- Replace basic string formatting with Jinja2 templating
- Add Pydantic validation for all configuration structures
- Implement robust language detection with multiple fallback methods
- Remove deprecated framework system
- Create language-specific prompt generation
- Enhance frontend adaptability to dynamic rubric structures

### **Success Criteria**
- 100% configuration validation through Pydantic
- 95%+ language detection accuracy
- Zero hardcoded prompt logic in Python code
- Frontend automatically adapts to rubric changes
- Support for English and Spanish with easy language addition

---

## **Phase 1: Backend Dependencies and Core Infrastructure**

### **Step 1.1: Install Enhanced Dependencies**

**Files to Modify**: `backend/requirements.txt`, `backend/Dockerfile`

**Implementation**:
```bash
# Install core dependencies
pip install pydantic jinja2

# Install robust language detection libraries
pip install polyglot
pip install langdetect
pip install pycld2

# Install additional language support
pip install polyglot[detection]
```

**Tests**:
```bash
# Verify installations
python3 -c "import pydantic; print('Pydantic:', pydantic.__version__)"
python3 -c "import jinja2; print('Jinja2:', jinja2.__version__)"
python3 -c "import polyglot; print('Polyglot available')"
python3 -c "import langdetect; print('Langdetect available')"
python3 -c "import pycld2; print('Pycld2 available')"
```

**Human Test**: 
- Navigate to backend container: `docker compose exec backend bash`
- Run dependency verification commands above
- Verify all packages install without errors

**Files No Longer Used**: None (new dependencies)

---

### **Step 1.2: Create Pydantic Configuration Models**

**Files to Create**: `backend/models/config_models.py`

**Implementation**:
- Create `Language` enum (EN, ES)
- Create `RubricCriterion` model with validation
- Create `RubricConfig` model with weight validation
- Create `PromptLanguageConfig` model
- Create `PromptConfig` model with language validation

**Tests**:
```python
# Test model validation
python3 -c "
from models.config_models import *
config = PromptConfig(languages={'en': PromptLanguageConfig(...)})
print('Validation successful')
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
- Remove deprecated `frameworks` section
- Add `languages` section with EN/ES configurations
- Add `default_language` and `confidence_threshold` settings
- Restructure rubric criteria for each language
- Remove framework-specific content

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
```

**Human Test**:
- Open `config/prompt.yaml` in browser
- Verify no syntax errors in YAML
- Check that frameworks section is removed
- Verify both English and Spanish sections exist

**Files No Longer Used**: 
- `config/rubric.yaml` (frameworks section deprecated)

---

### **Step 2.2: Create Jinja2 Template System**

**Files to Create**: `backend/templates/evaluation_prompt.j2`

**Implementation**:
- Create base evaluation prompt template
- Add dynamic rubric criteria rendering
- Include language-specific context and request
- Add required response format specification
- Include validation instructions

**Tests**:
```python
# Test template rendering
python3 -c "
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('backend/templates'))
template = env.get_template('evaluation_prompt.j2')
result = template.render(context='Test', request='Test', rubric={}, text_content='Test')
print('Template renders successfully')
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

### **Step 6.3: End-to-End Testing**

**Files to Create**: `tests/e2e/test_language_detection.py`

**Implementation**:
- Test complete evaluation workflow
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
```

**Human Test**:
- Complete full evaluation workflow
- Test with English and Spanish text
- Verify appropriate language prompts
- Check response quality and accuracy
- Test error scenarios

**Files No Longer Used**: None (new test files)

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

# Clean up empty directories
rmdir deprecated/ 2>/dev/null || true
```

**Tests**:
```bash
# Verify deprecated files are removed
ls backend/services/llm_service_backup.py 2>/dev/null && echo "ERROR: File still exists" || echo "File removed successfully"
ls backend/services/llm_service_improved.py 2>/dev/null && echo "ERROR: File still exists" || echo "File removed successfully"
ls deprecated/devspecs/ 2>/dev/null && echo "ERROR: Directory still exists" || echo "Directory removed successfully"
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

**Total Estimated Duration**: 10-14 weeks

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

**Document Status**: Active Implementation Plan with Enhanced Testing  
**Next Review**: After Phase 1 completion  
**Contact**: Development Team for implementation questions  
**Version Control**: Track all changes in git with descriptive commit messages
