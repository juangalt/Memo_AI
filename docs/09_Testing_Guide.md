# Testing Guide
## Memo AI Coach

**Document ID**: 09_Testing_Guide.md
**Document Version**: 2.0
**Last Updated**: Phase 10 - Prompt Refactor Implementation
**Status**: Active

---

## 1.0 Testing Overview
The testing suite covers all aspects of the Memo AI Coach system including the new enhanced architecture with language detection, dynamic prompt generation, and Pydantic validation. Tests are organized by category and can be run individually or as complete suites.

## 2.0 Test Categories

### 2.1 Configuration Tests
- Environment and configuration file validation
- Pydantic model validation for all configuration structures
- Language detection configuration validation
- Jinja2 template syntax validation

### 2.2 Integration Tests
- API endpoints and session management
- LLM responses with language detection
- Dynamic prompt generation and template rendering
- Configuration validation and error handling

### 2.3 Performance Tests
- Load testing against <15s requirement
- Language detection performance under various conditions
- Template rendering performance with caching
- Configuration validation performance

### 2.4 Security Tests
- Basic security validation
- Input validation and sanitization
- Template security and variable access control
- Configuration validation security

### 2.5 Language Detection Tests
- Accuracy testing with multiple languages
- Fallback strategy validation
- Performance testing with various text lengths
- Edge case handling (mixed languages, short text, special characters)

### 2.6 Prompt Generation Tests
- Jinja2 template rendering accuracy
- Language-specific prompt generation
- Dynamic rubric adaptation
- Error handling and fallback mechanisms

### 2.7 Frontend Tests
- Component rendering and adaptability
- Dynamic rubric display functionality
- Language detection display components
- Responsive design and accessibility

### 2.8 End-to-End Tests
- Complete evaluation workflow with language detection
- Configuration changes and validation
- Performance monitoring and health checks
- Production deployment verification

## 3.0 Running Tests

### 3.1 Quick Test Suite (Non-Performance Tests)
```bash
# Run quick suite for development
python3 tests/run_quick_tests.py

# Run specific test categories
python3 tests/run_quick_tests.py --category=config
python3 tests/run_quick_tests.py --category=integration
python3 tests/run_quick_tests.py --category=security
```

### 3.2 Full Production Suite (Includes Performance)
```bash
# Run complete test suite
python3 tests/run_production_tests.py

# Run with specific performance targets
python3 tests/run_production_tests.py --max-response-time=15
python3 tests/run_production_tests.py --concurrent-users=100
```

### 3.3 Language Detection Tests
```bash
# Run language detection accuracy tests
python3 tests/accuracy/test_language_detection.py

# Run with specific language focus
python3 tests/accuracy/test_language_detection.py --language=en
python3 tests/accuracy/test_language_detection.py --language=es
```

### 3.4 Prompt Generation Tests
```bash
# Run prompt generation quality tests
python3 tests/quality/test_prompt_generation.py

# Test specific template types
python3 tests/quality/test_prompt_generation.py --template=evaluation
python3 tests/quality/test_prompt_generation.py --language=en
```

### 3.5 Frontend Tests
```bash
# Run frontend component tests
cd vue-frontend
npm run test

# Run specific component tests
npm run test -- --grep="DynamicRubricScores"
npm run test -- --grep="LanguageDetectionDisplay"
```

## 4.0 Test Outputs
- Results stored in `logs/` directory
- JSON files with summary statistics and assertion outcomes
- Category-specific results for each test type
- Performance metrics and timing data
- Language detection accuracy reports

## 5.0 Test Data Requirements

### 5.1 Language Detection Test Data
```python
# English test samples (100+ samples)
english_samples = [
    "Hello world",  # Very short
    "This is a business memo about healthcare investments...",  # Medium
    "The comprehensive analysis demonstrates...",  # Long formal
    "Hey there! How's it going?",  # Informal
    "ROI analysis shows 15% return...",  # Technical
    # ... 95+ more samples
]

# Spanish test samples (100+ samples)
spanish_samples = [
    "Hola mundo",  # Very short
    "Este es un memorando comercial sobre inversiones en salud...",  # Medium
    "El análisis integral demuestra...",  # Long formal
    "¡Hola! ¿Cómo estás?",  # Informal
    "El análisis de ROI muestra un retorno del 15%...",  # Technical
    # ... 95+ more samples
]

# Mixed language and edge case samples
edge_cases = [
    "12345",  # Numbers only
    "!@#$%^&*()",  # Special characters
    "Hello mundo",  # Mixed languages
    "A",  # Single character
    "A" * 1000,  # Very long text
    # ... more edge cases
]
```

### 5.2 Prompt Generation Test Data
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

### 5.3 Performance Test Scenarios
```python
# Performance test scenarios
performance_tests = [
    {"name": "Single User", "concurrent_users": 1, "evaluations_per_user": 10},
    {"name": "Low Load", "concurrent_users": 10, "evaluations_per_user": 5},
    {"name": "Medium Load", "concurrent_users": 50, "evaluations_per_user": 3},
    {"name": "High Load", "concurrent_users": 100, "evaluations_per_user": 2},
]
```

## 6.0 Success Criteria

### 6.1 Language Detection Accuracy
- **English detection accuracy**: ≥98%
- **Spanish detection accuracy**: ≥95%
- **Mixed language handling**: ≥90%
- **Confidence score correlation**: ≥0.8
- **Fallback mechanism effectiveness**: 100% (no detection failures)

### 6.2 Prompt Generation Quality
- **All prompts generate without errors**: 100%
- **Prompts include all required sections**: 100%
- **Language-specific content accuracy**: ≥95%
- **Response format clarity**: 100%
- **Generation time**: <500ms

### 6.3 LLM Response Quality
- **All responses parse without errors**: 100%
- **Response structure matches expected format**: 100%
- **Language-specific content appropriateness**: ≥95%
- **Scores within valid ranges**: 100%
- **Response time**: <15 seconds

### 6.4 Frontend Display
- **All rubric structures display correctly**: 100%
- **Language detection information visibility**: 100%
- **Error state handling**: 100%
- **Performance requirements**: <1s load time
- **Accessibility standards compliance**: 100%

### 6.5 System Performance
- **Single evaluation**: <15 seconds
- **Low load (10 users)**: <30 seconds average
- **Medium load (50 users)**: <45 seconds average
- **High load (100 users)**: <60 seconds average
- **Resource usage within limits**: 100%

## 7.0 Test Environment Requirements

### 7.1 Backend Testing
- Running FastAPI service with all dependencies
- SQLite database with test data
- Mock LLM responses for consistent testing
- Configuration files for all test scenarios

### 7.2 Frontend Testing
- Vue.js development server
- Browser automation tools (if needed)
- Responsive design testing tools
- Accessibility testing tools

### 7.3 Performance Testing
- Load testing tools (e.g., Locust, Artillery)
- Resource monitoring tools
- Network simulation capabilities
- Concurrent user simulation

## 8.0 Continuous Integration

### 8.1 Automated Testing
- Run quick tests on every commit
- Run full suite on pull requests
- Performance regression testing
- Language detection accuracy monitoring

### 8.2 Test Reporting
- Automated test result reporting
- Performance trend analysis
- Language detection accuracy tracking
- Configuration validation success rates

## 9.0 Manual Testing Procedures

### 9.1 Language Detection Testing
1. **Submit English text** and verify English detection
2. **Submit Spanish text** and verify Spanish detection
3. **Submit mixed language text** and verify appropriate handling
4. **Submit very short text** and verify fallback behavior
5. **Submit text with special characters** and verify robustness

### 9.2 Prompt Generation Testing
1. **Verify English prompts** are generated correctly
2. **Verify Spanish prompts** are generated correctly
3. **Test different rubric structures** and verify adaptation
4. **Verify template variable substitution** works correctly
5. **Test error handling** with invalid configurations

### 9.3 Frontend Component Testing
1. **Test DynamicRubricScores** with various rubric structures
2. **Test LanguageDetectionDisplay** with different detection results
3. **Verify responsive design** on different screen sizes
4. **Test accessibility features** with screen readers
5. **Verify error handling** and user feedback

## 10.0 Troubleshooting Common Test Issues

### 10.1 Language Detection Issues
- **Low accuracy**: Check detection method configuration
- **Fallback failures**: Verify fallback threshold settings
- **Performance issues**: Check caching configuration
- **Method errors**: Verify dependency installation

### 10.2 Prompt Generation Issues
- **Template errors**: Check Jinja2 syntax
- **Variable substitution**: Verify template variable names
- **Performance issues**: Check template caching
- **Configuration errors**: Verify Pydantic validation

### 10.3 Frontend Issues
- **Component rendering**: Check Vue.js compilation
- **Styling issues**: Verify Tailwind CSS configuration
- **Responsive problems**: Test on different devices
- **Accessibility issues**: Use accessibility testing tools

## 11.0 References
- `tests/README.md` - Test suite documentation
- `devlog/prompt_refactor.md` - Implementation plan with testing requirements
- `backend/models/config_models.py` - Pydantic models for testing
- `backend/services/language_detection.py` - Language detection service
- `backend/templates/` - Jinja2 templates for testing
- `vue-frontend/src/components/` - Frontend components for testing
