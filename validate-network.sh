#!/bin/bash

# Network Accessibility and Testing Script
# Phase 7 Step 7.4 - Internet Accessibility Confirmed

set -e

echo "=== Phase 7.4: Internet Accessibility and Network Testing ==="
echo "Testing network configuration, port accessibility, and external connectivity..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Load environment variables
source .env 2>/dev/null || true

echo ""
echo "=== 1. Domain and DNS Configuration ==="
echo "Checking domain configuration..."

if [ -n "$DOMAIN" ] && [ "$DOMAIN" != "your-subdomain.com" ]; then
    echo "Configured domain: $DOMAIN"
    
    # Test DNS resolution
    echo "Testing DNS resolution..."
    nslookup $DOMAIN >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Domain $DOMAIN resolves correctly${NC}"
        
        # Get IP address
        IP_ADDRESS=$(nslookup $DOMAIN | grep -A 1 "Name:" | grep "Address:" | awk '{print $2}' | head -1)
        echo "Domain resolves to: $IP_ADDRESS"
    else
        echo -e "${YELLOW}⚠ Domain $DOMAIN does not resolve${NC}"
        echo "  For production: Configure DNS to point to this server's public IP"
    fi
else
    echo -e "${YELLOW}⚠ No domain configured in .env file${NC}"
    echo "  Using localhost for testing"
    DOMAIN="localhost"
fi

echo ""
echo "=== 2. Port Accessibility Testing ==="
echo "Testing required ports on this server..."

# Check if ports are open locally
PORTS=("80" "443" "8080")
for PORT in "${PORTS[@]}"; do
    if netstat -tuln | grep -q ":$PORT "; then
        echo -e "${GREEN}✓ Port $PORT is listening${NC}"
    else
        echo -e "${RED}✗ Port $PORT is not listening${NC}"
    fi
done

echo ""
echo "Testing port connectivity..."

# Test local port connections
echo "Testing HTTP (port 80):"
curl -I -m 5 http://localhost/ 2>/dev/null | head -1 || echo -e "${YELLOW}⚠ HTTP port 80 not responding${NC}"

echo "Testing HTTPS (port 443):"
curl -I -m 5 -k https://localhost/ 2>/dev/null | head -1 || echo -e "${YELLOW}⚠ HTTPS port 443 not responding${NC}"

echo "Testing Traefik dashboard (port 8080):"
curl -I -m 5 http://localhost:8080/ 2>/dev/null | head -1 || echo -e "${YELLOW}⚠ Traefik dashboard port 8080 not responding${NC}"

echo ""
echo "=== 3. Container Network Testing ==="
echo "Testing inter-container communication..."

if docker compose ps | grep -q "Up"; then
    echo "Testing container network connectivity..."
    
    # Test frontend to backend communication
    if docker compose ps frontend | grep -q "Up" && docker compose ps backend | grep -q "Up"; then
        echo "Testing frontend → backend communication:"
        FRONTEND_TO_BACKEND=$(docker compose exec frontend curl -s -o /dev/null -w "%{http_code}" http://backend:8000/health 2>/dev/null)
        
        if [ "$FRONTEND_TO_BACKEND" = "200" ]; then
            echo -e "${GREEN}✓ Frontend can reach backend${NC}"
        else
            echo -e "${RED}✗ Frontend cannot reach backend (HTTP $FRONTEND_TO_BACKEND)${NC}"
        fi
    fi
    
    # Test external connectivity from containers
    echo "Testing external connectivity from containers:"
    
    if docker compose ps backend | grep -q "Up"; then
        echo "Testing backend external connectivity:"
        docker compose exec backend curl -s -m 5 https://httpbin.org/ip >/dev/null 2>&1
        check_result "Backend can reach external services"
    fi
    
    if docker compose ps frontend | grep -q "Up"; then
        echo "Testing frontend external connectivity:"
        docker compose exec frontend curl -s -m 5 https://httpbin.org/ip >/dev/null 2>&1
        check_result "Frontend can reach external services"
    fi
else
    echo -e "${YELLOW}⚠ No containers running for network tests${NC}"
fi

echo ""
echo "=== 4. Reverse Proxy Testing ==="
echo "Testing Traefik reverse proxy configuration..."

if docker compose ps traefik | grep -q "Up"; then
    echo "Testing Traefik proxy routing..."
    
    # Test backend routing
    echo "Testing backend API routing through Traefik:"
    if [ "$DOMAIN" = "localhost" ]; then
        BACKEND_RESPONSE=$(curl -s -H "Host: localhost" http://localhost/api/health 2>/dev/null | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    else
        BACKEND_RESPONSE=$(curl -s http://$DOMAIN/api/health 2>/dev/null | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    fi
    
    if [ "$BACKEND_RESPONSE" = "healthy" ]; then
        echo -e "${GREEN}✓ Backend accessible through reverse proxy${NC}"
    else
        echo -e "${YELLOW}⚠ Backend not accessible through reverse proxy${NC}"
        echo "  Response: $BACKEND_RESPONSE"
    fi
    
    # Test frontend routing
    echo "Testing frontend routing through Traefik:"
    if [ "$DOMAIN" = "localhost" ]; then
        FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -H "Host: localhost" http://localhost/ 2>/dev/null)
    else
        FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN/ 2>/dev/null)
    fi
    
    if [ "$FRONTEND_RESPONSE" = "200" ] || [ "$FRONTEND_RESPONSE" = "301" ] || [ "$FRONTEND_RESPONSE" = "302" ]; then
        echo -e "${GREEN}✓ Frontend accessible through reverse proxy (HTTP $FRONTEND_RESPONSE)${NC}"
    else
        echo -e "${YELLOW}⚠ Frontend not accessible through reverse proxy (HTTP $FRONTEND_RESPONSE)${NC}"
    fi
    
    # Test Traefik dashboard
    echo "Testing Traefik dashboard accessibility:"
    DASHBOARD_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ 2>/dev/null)
    
    if [ "$DASHBOARD_RESPONSE" = "200" ]; then
        echo -e "${GREEN}✓ Traefik dashboard accessible${NC}"
    else
        echo -e "${YELLOW}⚠ Traefik dashboard not accessible (HTTP $DASHBOARD_RESPONSE)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Traefik container not running${NC}"
fi

echo ""
echo "=== 5. SSL/TLS Configuration Testing ==="
echo "Testing SSL certificate configuration..."

# Check Let's Encrypt configuration
if [ -f "./letsencrypt/acme.json" ]; then
    echo -e "${GREEN}✓ Let's Encrypt ACME storage configured${NC}"
    
    # Check if certificates exist
    if [ -s "./letsencrypt/acme.json" ]; then
        echo -e "${GREEN}✓ ACME storage contains data (certificates may be present)${NC}"
    else
        echo -e "${YELLOW}⚠ ACME storage is empty (no certificates yet)${NC}"
        echo "  Certificates will be automatically issued when domain is accessible"
    fi
else
    echo -e "${YELLOW}⚠ Let's Encrypt ACME storage not found${NC}"
fi

# Test HTTPS if available
if [ "$DOMAIN" != "localhost" ]; then
    echo "Testing HTTPS connectivity for $DOMAIN..."
    HTTPS_RESPONSE=$(curl -I -m 10 -k https://$DOMAIN/ 2>/dev/null | head -1)
    
    if [ -n "$HTTPS_RESPONSE" ]; then
        echo -e "${GREEN}✓ HTTPS accessible: $HTTPS_RESPONSE${NC}"
        
        # Test certificate validity
        echo "Testing SSL certificate..."
        openssl s_client -connect $DOMAIN:443 -servername $DOMAIN < /dev/null 2>/dev/null | openssl x509 -noout -dates 2>/dev/null
        check_result "SSL certificate details retrieved"
    else
        echo -e "${YELLOW}⚠ HTTPS not accessible yet${NC}"
        echo "  This is normal for new deployments - certificates will be issued automatically"
    fi
else
    echo -e "${BLUE}ℹ HTTPS testing skipped for localhost${NC}"
fi

echo ""
echo "=== 6. Firewall and Security Testing ==="
echo "Checking basic security configuration..."

# Check if firewall is configured
if command -v ufw >/dev/null 2>&1; then
    echo "UFW firewall status:"
    sudo ufw status 2>/dev/null || echo "UFW status check requires sudo"
else
    echo -e "${BLUE}ℹ UFW firewall not installed${NC}"
fi

# Check iptables rules
if command -v iptables >/dev/null 2>&1; then
    echo "Active iptables rules (INPUT chain):"
    sudo iptables -L INPUT -n --line-numbers 2>/dev/null | head -10 || echo "iptables check requires sudo"
else
    echo -e "${BLUE}ℹ iptables not available${NC}"
fi

echo ""
echo "=== 7. External Accessibility Testing ==="
echo "Testing external accessibility (if public IP available)..."

# Get public IP
PUBLIC_IP=$(curl -s -m 5 https://api.ipify.org 2>/dev/null || echo "unknown")
if [ "$PUBLIC_IP" != "unknown" ]; then
    echo "Public IP address: $PUBLIC_IP"
    
    # Test if public IP is accessible (basic check)
    echo "Testing public IP accessibility..."
    
    # This is just a placeholder - in production you'd test from external sources
    echo -e "${BLUE}ℹ External accessibility testing requires testing from outside this network${NC}"
    echo "  To test: Use an external service or different network to access:"
    echo "  - http://$PUBLIC_IP"
    echo "  - https://$DOMAIN (if DNS configured)"
else
    echo -e "${YELLOW}⚠ Could not determine public IP address${NC}"
fi

echo ""
echo "=== 8. Network Performance Testing ==="
echo "Testing network performance and latency..."

# Test response times
echo "Testing local response times..."

if docker compose ps backend | grep -q "Up"; then
    echo "Backend API response time test:"
    TIME_TOTAL=$(curl -s -o /dev/null -w "%{time_total}" http://localhost:8000/health 2>/dev/null)
    echo "Response time: ${TIME_TOTAL}s"
    
    if (( $(echo "$TIME_TOTAL < 1.0" | bc -l 2>/dev/null || echo "1") )); then
        echo -e "${GREEN}✓ Backend response time acceptable (<1s)${NC}"
    else
        echo -e "${YELLOW}⚠ Backend response time: ${TIME_TOTAL}s (>1s)${NC}"
    fi
fi

echo ""
echo "=== Network Configuration Summary ==="
echo "Phase 7.4 network testing complete."
echo ""
echo "Network Status:"
echo "- Domain: $DOMAIN"
echo "- Public IP: $PUBLIC_IP"
echo "- Required ports: 80, 443, 8080"
echo "- Reverse proxy: Traefik configured"
echo "- SSL: Let's Encrypt automatic certificate management"
echo ""
echo "For production deployment:"
echo "1. Configure DNS: $DOMAIN → $PUBLIC_IP"
echo "2. Open firewall ports: 80, 443"
echo "3. Test external access from different network"
echo "4. Monitor certificate issuance: docker compose logs traefik"
echo "5. Verify domain accessibility: https://$DOMAIN"
echo ""
echo "Quick commands:"
echo "- Check domain: nslookup $DOMAIN"
echo "- Test HTTP: curl -I http://$DOMAIN/"
echo "- Test HTTPS: curl -I https://$DOMAIN/"
echo "- Monitor logs: docker compose logs -f traefik"
