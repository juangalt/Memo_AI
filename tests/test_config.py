import os

# Environment detection
ENVIRONMENT = os.getenv('APP_ENV', 'development')
IS_CONTAINER = os.path.exists('/.dockerenv') or os.getenv('DOCKER_ENV') == 'true'

# Base URLs
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost')

# Container-specific URLs
if IS_CONTAINER:
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:8501')
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

# Logging paths
LOG_DIR = './logs' if ENVIRONMENT == 'development' else '/app/logs'

# Test expectations
EXPECT_SSL = ENVIRONMENT == 'production'
EXPECT_SECURITY_HEADERS = ENVIRONMENT == 'production'
EXPECT_RATE_LIMITING = True  # Should work in both environments

print(f"Test Configuration:")
print(f"  Environment: {ENVIRONMENT}")
print(f"  Is Container: {IS_CONTAINER}")
print(f"  Backend URL: {BACKEND_URL}")
print(f"  Frontend URL: {FRONTEND_URL}")
print(f"  Log Directory: {LOG_DIR}")
print(f"  Expect SSL: {EXPECT_SSL}")
print(f"  Expect Security Headers: {EXPECT_SECURITY_HEADERS}")
