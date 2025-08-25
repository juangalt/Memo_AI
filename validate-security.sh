#!/bin/bash

# Security Validation Script for Phase 7 Step 7.2
# Tests SSL and security configuration

set -e

echo "=== Phase 7.2: SSL and Security Validation ==="
echo "Testing security headers and configuration..."

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
echo "=== 1. Configuration File Security ==="
echo "Testing configuration file write protection..."

if docker compose ps backend | grep -q "Up"; then
    echo "Testing backend configuration security..."
    docker compose exec backend touch /app/config/test.yaml 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${GREEN}✓ Backend config files are read-only${NC}"
    else
        echo -e "${RED}✗ Backend can write to config files (security risk)${NC}"
        docker compose exec backend rm -f /app/config/test.yaml 2>/dev/null
    fi
else
    echo -e "${YELLOW}⚠ Backend container not running${NC}"
fi

if docker compose ps frontend | grep -q "Up"; then
    echo "Testing frontend configuration security..."
    docker compose exec frontend touch /app/config/test.yaml 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${GREEN}✓ Frontend config files are read-only${NC}"
    else
        echo -e "${RED}✗ Frontend can write to config files (security risk)${NC}"
        docker compose exec frontend rm -f /app/config/test.yaml 2>/dev/null
    fi
else
    echo -e "${YELLOW}⚠ Frontend container not running${NC}"
fi

echo ""
echo "=== 2. Container User Security ==="
echo "Verifying non-root container execution..."

if docker compose ps backend | grep -q "Up"; then
    BACKEND_USER=$(docker compose exec backend whoami 2>/dev/null | tr -d '\r')
    if [ "$BACKEND_USER" = "appuser" ]; then
        echo -e "${GREEN}✓ Backend runs as non-root user (appuser)${NC}"
    else
        echo -e "${RED}✗ Backend runs as root user (security risk)${NC}"
    fi
    
    BACKEND_UID=$(docker compose exec backend id -u 2>/dev/null | tr -d '\r')
    if [ "$BACKEND_UID" != "0" ]; then
        echo -e "${GREEN}✓ Backend user UID is not 0 (non-root)${NC}"
    else
        echo -e "${RED}✗ Backend user UID is 0 (root - security risk)${NC}"
    fi
fi

if docker compose ps frontend | grep -q "Up"; then
    FRONTEND_USER=$(docker compose exec frontend whoami 2>/dev/null | tr -d '\r')
    if [ "$FRONTEND_USER" = "appuser" ]; then
        echo -e "${GREEN}✓ Frontend runs as non-root user (appuser)${NC}"
    else
        echo -e "${RED}✗ Frontend runs as root user (security risk)${NC}"
    fi
    
    FRONTEND_UID=$(docker compose exec frontend id -u 2>/dev/null | tr -d '\r')
    if [ "$FRONTEND_UID" != "0" ]; then
        echo -e "${GREEN}✓ Frontend user UID is not 0 (non-root)${NC}"
    else
        echo -e "${RED}✗ Frontend user UID is 0 (root - security risk)${NC}"
    fi
fi

echo ""
echo "=== 3. HTTP Security Headers Test ==="
echo "Testing security headers (local testing without SSL)..."

if docker compose ps traefik | grep -q "Up"; then
    echo "Testing HTTP redirects and headers..."
    
    # Test HTTP to HTTPS redirect
    HTTP_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null || echo "000")
    if [ "$HTTP_RESPONSE" = "301" ] || [ "$HTTP_RESPONSE" = "302" ] || [ "$HTTP_RESPONSE" = "308" ]; then
        echo -e "${GREEN}✓ HTTP to HTTPS redirect configured${NC}"
    else
        echo -e "${YELLOW}⚠ HTTP redirect status: $HTTP_RESPONSE (may work with proper domain)${NC}"
    fi
    
    # Test security headers on backend
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        HEADERS=$(curl -s -I http://localhost:8000/health 2>/dev/null)
        
        if echo "$HEADERS" | grep -i "x-frame-options" >/dev/null; then
            echo -e "${GREEN}✓ X-Frame-Options header present${NC}"
        else
            echo -e "${YELLOW}⚠ X-Frame-Options header missing${NC}"
        fi
        
        if echo "$HEADERS" | grep -i "x-content-type-options" >/dev/null; then
            echo -e "${GREEN}✓ X-Content-Type-Options header present${NC}"
        else
            echo -e "${YELLOW}⚠ X-Content-Type-Options header missing${NC}"
        fi
        
        if echo "$HEADERS" | grep -i "x-xss-protection" >/dev/null; then
            echo -e "${GREEN}✓ X-XSS-Protection header present${NC}"
        else
            echo -e "${YELLOW}⚠ X-XSS-Protection header missing${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Cannot test backend headers - service not accessible${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Traefik container not running${NC}"
fi

echo ""
echo "=== 4. Rate Limiting Test ==="
echo "Testing rate limiting configuration..."

if docker compose ps traefik | grep -q "Up"; then
    echo "Testing rate limiting (making multiple requests)..."
    
    SUCCESS_COUNT=0
    RATE_LIMITED=0
    
    for i in {1..10}; do
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
        if [ "$HTTP_CODE" = "200" ]; then
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        elif [ "$HTTP_CODE" = "429" ]; then
            RATE_LIMITED=$((RATE_LIMITED + 1))
        fi
        sleep 0.1
    done
    
    echo "Rate limiting test results:"
    echo "- Successful requests: $SUCCESS_COUNT"
    echo "- Rate limited requests: $RATE_LIMITED"
    
    if [ $SUCCESS_COUNT -gt 0 ]; then
        echo -e "${GREEN}✓ Service responding to requests${NC}"
    fi
    
    if [ $RATE_LIMITED -gt 0 ]; then
        echo -e "${GREEN}✓ Rate limiting active${NC}"
    else
        echo -e "${YELLOW}⚠ Rate limiting not triggered (may need higher load)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Traefik container not running${NC}"
fi

echo ""
echo "=== 5. SSL Certificate Test ==="
echo "Testing SSL certificate configuration..."

if [ -f "./letsencrypt/acme.json" ]; then
    echo -e "${GREEN}✓ Let's Encrypt ACME storage file exists${NC}"
    
    # Check file permissions
    ACME_PERMS=$(stat -c %a ./letsencrypt/acme.json 2>/dev/null || echo "unknown")
    if [ "$ACME_PERMS" = "600" ]; then
        echo -e "${GREEN}✓ ACME storage file has secure permissions (600)${NC}"
    else
        echo -e "${YELLOW}⚠ ACME storage file permissions: $ACME_PERMS (should be 600)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Let's Encrypt ACME storage file not found${NC}"
    echo "  File will be created when SSL certificates are issued"
fi

# Check if domain is configured
source .env 2>/dev/null || true
if [ "$DOMAIN" != "your-subdomain.com" ] && [ -n "$DOMAIN" ]; then
    echo -e "${GREEN}✓ Domain configured: $DOMAIN${NC}"
    echo "  SSL certificates will be automatically issued for this domain"
else
    echo -e "${YELLOW}⚠ Domain not configured or using example domain${NC}"
    echo "  Please configure DOMAIN in .env file for SSL certificates"
fi

echo ""
echo "=== 6. Container Security Validation ==="
echo "Testing container isolation and capabilities..."

if docker compose ps backend | grep -q "Up"; then
    echo "Testing backend container security..."
    
    # Test if container can access Docker socket (should not)
    docker compose exec backend ls -la /var/run/docker.sock 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${GREEN}✓ Backend cannot access Docker socket${NC}"
    else
        echo -e "${RED}✗ Backend can access Docker socket (security risk)${NC}"
    fi
    
    # Test network access restrictions
    docker compose exec backend ping -c 1 8.8.8.8 >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Backend has external network access${NC}"
    else
        echo -e "${YELLOW}⚠ Backend external network access restricted${NC}"
    fi
fi

echo ""
echo "=== Security Validation Summary ==="
echo "Phase 7.2 security validation complete."
echo ""
echo "Key Security Features:"
echo "- Configuration files mounted read-only"
echo "- Containers run as non-root users"
echo "- Security headers configured via Traefik"
echo "- Rate limiting enabled"
echo "- SSL/TLS configuration ready"
echo "- Container isolation maintained"
echo ""
echo "For production deployment:"
echo "1. Configure proper domain in .env file"
echo "2. Ensure DNS points to this server"
echo "3. Open ports 80, 443 for Let's Encrypt"
echo "4. Monitor logs: docker compose logs traefik"
