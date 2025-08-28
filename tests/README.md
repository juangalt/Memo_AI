# Memo AI Coach - Tests

This directory contains all test suites for the Memo AI Coach application, organized by test type and phase.

## Test Structure

### Configuration Tests
- **[config/test_environment.py](config/test_environment.py)** - Environment configuration validation (Phase 8.2)

### Integration Tests
- **[integration/test_critical_system_local.py](integration/test_critical_system_local.py)** - Critical system functionality tests using local containers (Phase 8.3)
- **[integration/test_production_readiness.py](integration/test_production_readiness.py)** - Production readiness verification (Phase 8.5)

### Performance Tests
- **[performance/test_load.py](performance/test_load.py)** - Performance and load testing (Phase 8.4)

### Security Tests
- **[test_security_dev.py](test_security_dev.py)** - Security testing for development environment

## Phase 8 Test Suite

The current test suite implements Phase 8 of the development roadmap:

### 8.1: Production Test Suite ✅
- Complete test directory structure validated
- Test configuration files in place
- Logging and reporting system functional

### 8.2: Environment Configuration Validation ✅
- All environment variables validated
- Production domain accessibility
- SSL certificates validation
- Database connections functional
- LLM API key validation

### 8.3: Critical System Tests ✅
- Container status verification
- API health endpoints testing
- Session management validation
- Text evaluation workflow testing
- Database operations verification
- LLM integration testing
- Error handling validation

### 8.4: Performance and Load Tests ✅
- Response time benchmarks
- Concurrent user simulation
- Resource usage monitoring
- Performance requirements validation

### 8.5: Production Readiness Verification ✅
- System accessibility testing
- Security measures validation
- Complete functionality verification
- Monitoring and alerting validation
- Backup and recovery testing
- Performance under load validation

## Usage

### Run All Production Tests (Recommended)
```bash
# Run complete Phase 8 production test suite (includes performance tests)
python3 tests/run_production_tests.py

# Run quick Phase 8 production test suite (excludes performance tests for speed)
python3 tests/run_quick_tests.py
```

### Run Complete Phase 8 Validation (Individual)
```bash
# Environment configuration validation
python3 tests/config/test_environment.py

# Critical system tests (local containers)
python3 tests/integration/test_critical_system_local.py

# Performance and load tests
python3 tests/performance/test_load.py

# Production readiness verification
python3 tests/integration/test_production_readiness.py
```

### Run Individual Test Categories
```bash
# Security tests (development)
python3 tests/test_security_dev.py

# Environment validation only
python3 tests/config/test_environment.py
```

## Test Results

Test results are stored in the `logs/` directory:
- `production_test_suite_results.json` - Complete production test suite results
- `quick_production_test_results.json` - Quick production test suite results
- `environment_validation_results.json` - Environment configuration test results
- `critical_system_test_results.json` - Critical system test results
- `performance_test_results.json` - Performance test results
- `production_readiness_test_results.json` - Production readiness test results
- `security_test_results.json` - Security test results

## Current Status

**Phase 8 Test Results:**
- **Environment Configuration**: 100% success rate (21/21 tests)
- **Critical System Tests**: 100% success rate (16/16 tests)
- **Production Readiness**: 100% success rate (15/15 tests)
- **Overall Phase 8**: 100% success rate (52/52 tests)

## Test Environment

### Local Container Testing
- Tests use `docker compose exec` for reliable container access
- No external domain dependencies
- Consistent test environment across runs
- Fast execution times

### Error Handling
- Comprehensive error handling validation
- HTTP status code verification
- JSON response format validation
- Graceful degradation for test failures

### Performance Benchmarks
- Average response time: < 15 seconds
- Maximum response time: < 20 seconds
- Concurrent user load testing
- Resource usage monitoring

## Maintenance

### Adding New Tests
1. Create test file in appropriate directory
2. Follow existing test structure and naming conventions
3. Update this README with new test information
4. Ensure test results are saved to logs directory

### Test Cleanup
- Old test results are automatically cleaned up
- Deprecated test files have been removed
- Only current and relevant tests are maintained
- Test structure is optimized for Phase 8 requirements
