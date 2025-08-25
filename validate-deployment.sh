#!/bin/bash

# Configuration Path and Permission Validation Script
# Validates Phase 7 deployment requirements

set -e

echo "=== Phase 7 Deployment Validation ==="
echo "Validating configuration paths and permissions..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check function
check_result() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
        return 0
    else
        echo -e "${RED}✗ $1${NC}"
        return 1
    fi
}

echo ""
echo "=== 1. Configuration Path Validation ==="
echo "Checking host configuration paths..."
[ -d "./config" ] && echo -e "${GREEN}✓ Host config directory exists${NC}" || echo -e "${RED}✗ Host config directory missing${NC}"
[ -f "./config/rubric.yaml" ] && echo -e "${GREEN}✓ rubric.yaml exists${NC}" || echo -e "${RED}✗ rubric.yaml missing${NC}"
[ -f "./config/prompt.yaml" ] && echo -e "${GREEN}✓ prompt.yaml exists${NC}" || echo -e "${RED}✗ prompt.yaml missing${NC}"
[ -f "./config/llm.yaml" ] && echo -e "${GREEN}✓ llm.yaml exists${NC}" || echo -e "${RED}✗ llm.yaml missing${NC}"
[ -f "./config/auth.yaml" ] && echo -e "${GREEN}✓ auth.yaml exists${NC}" || echo -e "${RED}✗ auth.yaml missing${NC}"

echo ""
echo "=== 2. Container Configuration Access ==="
echo "Testing backend container configuration access..."
if docker compose ps backend | grep -q "Up"; then
    docker compose exec backend ls -la /app/config/ > /dev/null 2>&1
    check_result "Backend can list /app/config/ directory"
    
    docker compose exec backend cat /app/config/rubric.yaml > /dev/null 2>&1
    check_result "Backend can read rubric.yaml"
    
    docker compose exec backend python -c "import yaml; yaml.safe_load(open('/app/config/rubric.yaml'))" > /dev/null 2>&1
    check_result "Backend can load rubric.yaml with Python"
else
    echo -e "${YELLOW}⚠ Backend container not running - skipping tests${NC}"
fi

echo ""
echo "Testing frontend container configuration access..."
if docker compose ps frontend | grep -q "Up"; then
    docker compose exec frontend ls -la /app/config/ > /dev/null 2>&1
    check_result "Frontend can list /app/config/ directory"
    
    docker compose exec frontend cat /app/config/prompt.yaml > /dev/null 2>&1
    check_result "Frontend can read prompt.yaml"
    
    docker compose exec frontend python -c "import yaml; yaml.safe_load(open('/app/config/prompt.yaml'))" > /dev/null 2>&1
    check_result "Frontend can load prompt.yaml with Python"
else
    echo -e "${YELLOW}⚠ Frontend container not running - skipping tests${NC}"
fi

echo ""
echo "=== 3. User Permission Validation ==="
echo "Testing container user permissions..."
if docker compose ps backend | grep -q "Up"; then
    BACKEND_USER=$(docker compose exec backend whoami 2>/dev/null | tr -d '\r')
    BACKEND_UID=$(docker compose exec backend id -u 2>/dev/null | tr -d '\r')
    echo "Backend container user: $BACKEND_USER (UID: $BACKEND_UID)"
    [ "$BACKEND_USER" = "appuser" ] && check_result "Backend runs as non-root user" || echo -e "${RED}✗ Backend not running as appuser${NC}"
    [ "$BACKEND_UID" = "1000" ] && check_result "Backend user UID is 1000" || echo -e "${RED}✗ Backend user UID is not 1000${NC}"
else
    echo -e "${YELLOW}⚠ Backend container not running - skipping user tests${NC}"
fi

if docker compose ps frontend | grep -q "Up"; then
    FRONTEND_USER=$(docker compose exec frontend whoami 2>/dev/null | tr -d '\r')
    FRONTEND_UID=$(docker compose exec frontend id -u 2>/dev/null | tr -d '\r')
    echo "Frontend container user: $FRONTEND_USER (UID: $FRONTEND_UID)"
    [ "$FRONTEND_USER" = "appuser" ] && check_result "Frontend runs as non-root user" || echo -e "${RED}✗ Frontend not running as appuser${NC}"
    [ "$FRONTEND_UID" = "1000" ] && check_result "Frontend user UID is 1000" || echo -e "${RED}✗ Frontend user UID is not 1000${NC}"
else
    echo -e "${YELLOW}⚠ Frontend container not running - skipping user tests${NC}"
fi

echo ""
echo "=== 4. Configuration Security Validation ==="
echo "Testing configuration file write protection..."
if docker compose ps backend | grep -q "Up"; then
    docker compose exec backend touch /app/config/test.yaml 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${GREEN}✓ Backend cannot write to config directory (read-only mount)${NC}"
    else
        echo -e "${RED}✗ Backend can write to config directory (security risk)${NC}"
        docker compose exec backend rm -f /app/config/test.yaml 2>/dev/null
    fi
else
    echo -e "${YELLOW}⚠ Backend container not running - skipping security tests${NC}"
fi

if docker compose ps frontend | grep -q "Up"; then
    docker compose exec frontend touch /app/config/test.yaml 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${GREEN}✓ Frontend cannot write to config directory (read-only mount)${NC}"
    else
        echo -e "${RED}✗ Frontend can write to config directory (security risk)${NC}"
        docker compose exec frontend rm -f /app/config/test.yaml 2>/dev/null
    fi
else
    echo -e "${YELLOW}⚠ Frontend container not running - skipping security tests${NC}"
fi

echo ""
echo "=== 5. Configuration Persistence Validation ==="
echo "Testing configuration persistence across container restarts..."
if docker compose ps | grep -q "Up"; then
    echo "Restarting containers..."
    docker compose restart backend frontend
    sleep 10
    
    if docker compose ps backend | grep -q "Up"; then
        docker compose exec backend python -c "import yaml; print('Config after restart:', bool(yaml.safe_load(open('/app/config/rubric.yaml'))))" > /dev/null 2>&1
        check_result "Backend config accessible after restart"
    fi
    
    if docker compose ps frontend | grep -q "Up"; then
        docker compose exec frontend python -c "import yaml; print('Config after restart:', bool(yaml.safe_load(open('/app/config/prompt.yaml'))))" > /dev/null 2>&1
        check_result "Frontend config accessible after restart"
    fi
else
    echo -e "${YELLOW}⚠ No containers running - skipping persistence tests${NC}"
fi

echo ""
echo "=== 6. Volume Mount Validation ==="
echo "Testing volume mount points..."
if docker compose ps backend | grep -q "Up"; then
    CONFIG_FILES=$(docker compose exec backend ls /app/config/ 2>/dev/null | wc -l)
    DATA_DIR=$(docker compose exec backend ls -la /app/data/ 2>/dev/null | grep -c "memoai.db" || echo "0")
    LOGS_DIR=$(docker compose exec backend ls -d /app/logs/ 2>/dev/null | wc -l)
    
    [ "$CONFIG_FILES" -gt "0" ] && check_result "Backend config volume mounted ($CONFIG_FILES files)" || echo -e "${RED}✗ Backend config volume not mounted${NC}"
    [ "$DATA_DIR" -gt "0" ] && check_result "Backend data volume mounted (database found)" || echo -e "${YELLOW}⚠ Backend data volume mounted but no database found${NC}"
    [ "$LOGS_DIR" -gt "0" ] && check_result "Backend logs volume mounted" || echo -e "${RED}✗ Backend logs volume not mounted${NC}"
fi

echo ""
echo "=== 7. Health Check Validation ==="
echo "Testing application health endpoints..."
if docker compose ps backend | grep -q "Up"; then
    curl -f http://localhost:8000/health > /dev/null 2>&1
    check_result "Backend health endpoint responding"
fi

if docker compose ps frontend | grep -q "Up"; then
    curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1
    check_result "Frontend health endpoint responding"
fi

echo ""
echo "=== Phase 7 Validation Summary ==="
echo "Configuration path validation complete."
echo "Review any failed checks above and fix before proceeding to Phase 8."
echo ""
echo "For detailed logs, run: docker compose logs"
echo "To check container status: docker compose ps"
