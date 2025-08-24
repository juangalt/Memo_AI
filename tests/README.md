# Memo AI Coach - Tests

This directory contains all test suites and test configuration.

## Test Files

### Configuration
- **[test_config.py](test_config.py)** - Environment-aware test configuration

### Test Runners
- **[run_tests.py](run_tests.py)** - Comprehensive test runner for all test suites

### System Tests
- **[test_system.py](test_system.py)** - Basic system integration tests

### Security Tests
- **[test_security_dev.py](test_security_dev.py)** - Security testing (development environment)
- **[test_security.py](test_security.py)** - Security testing (production environment)

## Usage

### Run All Tests
```bash
# Comprehensive test suite
python run_tests.py
```

### Run Individual Tests
```bash
# Basic system tests
python test_system.py

# Security tests (development)
python test_security_dev.py

# Security tests (production)
python test_security.py
```

### Test Configuration
The `test_config.py` file provides environment-aware configuration:
- Environment detection (development vs production)
- URL configuration for different environments
- Logging path configuration
- Test expectation settings

## Test Results

Test results are stored in the `../logs/` directory:
- `security_test_results.json` - Security test results
- `integration_test_results.json` - Integration test results
- `monitoring.log` - Monitoring logs
- `security_test.log` - Security test logs

## Environment-Specific Testing

### Development Environment
- SSL tests adapted for HTTP-only access
- Security headers tests for basic headers only
- Frontend accessibility through multiple URL strategies
- Graceful degradation for development limitations

### Production Environment
- Full SSL/TLS testing
- Complete security headers validation
- Production-appropriate expectations
- Email notifications for alerts
