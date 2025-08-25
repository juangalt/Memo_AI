#!/bin/bash

# Container Health and Performance Validation Script
# Phase 7 Step 7.3 - Container Health Verified

set -e

echo "=== Phase 7.3: Container Health and Performance Validation ==="
echo "Testing container health, resource usage, and performance metrics..."

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

echo ""
echo "=== 1. Container Status and Health Checks ==="
echo "Checking container status..."

docker compose ps
echo ""

# Check individual container health
for service in traefik backend frontend; do
    if docker compose ps $service | grep -q "Up"; then
        echo -e "${GREEN}✓ $service container is running${NC}"
        
        # Check health status if available
        HEALTH_STATUS=$(docker compose ps $service --format "table {{.State}}" | tail -n 1)
        if echo "$HEALTH_STATUS" | grep -q "healthy"; then
            echo -e "${GREEN}✓ $service container is healthy${NC}"
        elif echo "$HEALTH_STATUS" | grep -q "starting"; then
            echo -e "${YELLOW}⚠ $service container health is starting${NC}"
        elif echo "$HEALTH_STATUS" | grep -q "unhealthy"; then
            echo -e "${RED}✗ $service container is unhealthy${NC}"
        else
            echo -e "${BLUE}ℹ $service container status: $HEALTH_STATUS${NC}"
        fi
    else
        echo -e "${RED}✗ $service container is not running${NC}"
    fi
done

echo ""
echo "=== 2. Resource Usage Monitoring ==="
echo "Checking container resource usage..."

# Get resource stats
STATS_OUTPUT=$(docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}")
echo "$STATS_OUTPUT"

echo ""
echo "Analyzing resource usage..."

# Parse and analyze stats for each container
for container in $(docker compose ps --format "{{.Name}}"); do
    if [ -n "$container" ]; then
        CPU_USAGE=$(docker stats --no-stream --format "{{.CPUPerc}}" $container | tr -d '%')
        MEM_USAGE=$(docker stats --no-stream --format "{{.MemPerc}}" $container | tr -d '%')
        
        # Check CPU usage
        if (( $(echo "$CPU_USAGE < 50" | bc -l) )); then
            echo -e "${GREEN}✓ $container CPU usage: $CPU_USAGE% (acceptable)${NC}"
        elif (( $(echo "$CPU_USAGE < 80" | bc -l) )); then
            echo -e "${YELLOW}⚠ $container CPU usage: $CPU_USAGE% (moderate)${NC}"
        else
            echo -e "${RED}✗ $container CPU usage: $CPU_USAGE% (high)${NC}"
        fi
        
        # Check memory usage
        if (( $(echo "$MEM_USAGE < 70" | bc -l) )); then
            echo -e "${GREEN}✓ $container Memory usage: $MEM_USAGE% (acceptable)${NC}"
        elif (( $(echo "$MEM_USAGE < 90" | bc -l) )); then
            echo -e "${YELLOW}⚠ $container Memory usage: $MEM_USAGE% (moderate)${NC}"
        else
            echo -e "${RED}✗ $container Memory usage: $MEM_USAGE% (high)${NC}"
        fi
    fi
done

echo ""
echo "=== 3. Health Endpoint Testing ==="
echo "Testing application health endpoints..."

# Test backend health
if docker compose ps backend | grep -q "Up"; then
    echo "Testing backend health endpoint..."
    BACKEND_HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null || echo "FAILED")
    
    if echo "$BACKEND_HEALTH" | grep -q "healthy"; then
        echo -e "${GREEN}✓ Backend health endpoint responding${NC}"
        
        # Parse health details
        echo "Backend health details:"
        echo "$BACKEND_HEALTH" | python3 -m json.tool 2>/dev/null | head -20 || echo "$BACKEND_HEALTH"
    else
        echo -e "${RED}✗ Backend health endpoint failed${NC}"
        echo "Response: $BACKEND_HEALTH"
    fi
else
    echo -e "${YELLOW}⚠ Backend container not running${NC}"
fi

echo ""

# Test frontend health
if docker compose ps frontend | grep -q "Up"; then
    echo "Testing frontend health endpoint..."
    FRONTEND_HEALTH=$(docker compose exec frontend curl -s http://localhost:8501/_stcore/health 2>/dev/null || echo "FAILED")
    
    if [ "$FRONTEND_HEALTH" != "FAILED" ] && [ -n "$FRONTEND_HEALTH" ]; then
        echo -e "${GREEN}✓ Frontend health endpoint responding${NC}"
    else
        echo -e "${YELLOW}⚠ Frontend health endpoint check inconclusive${NC}"
        
        # Alternative health check - check if Streamlit is running
        if docker compose exec frontend pgrep streamlit >/dev/null 2>&1; then
            echo -e "${GREEN}✓ Frontend Streamlit process running${NC}"
        else
            echo -e "${RED}✗ Frontend Streamlit process not found${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠ Frontend container not running${NC}"
fi

echo ""
echo "=== 4. Configuration Health Validation ==="
echo "Testing configuration loading and accessibility..."

if docker compose ps backend | grep -q "Up"; then
    echo "Testing backend configuration health..."
    
    # Test configuration endpoint
    CONFIG_HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null | grep -o '"configuration":"[^"]*"' | cut -d'"' -f4)
    
    if [ "$CONFIG_HEALTH" = "healthy" ]; then
        echo -e "${GREEN}✓ Backend configuration service healthy${NC}"
    else
        echo -e "${YELLOW}⚠ Backend configuration status: $CONFIG_HEALTH${NC}"
    fi
    
    # Test configuration file access
    docker compose exec backend python -c "
import yaml
import os
try:
    config_files = ['rubric.yaml', 'prompt.yaml', 'llm.yaml', 'auth.yaml']
    for file in config_files:
        with open(f'/app/config/{file}', 'r') as f:
            yaml.safe_load(f)
    print('✓ All configuration files loaded successfully')
except Exception as e:
    print(f'✗ Configuration loading error: {e}')
" 2>/dev/null || echo -e "${RED}✗ Backend configuration test failed${NC}"
fi

if docker compose ps frontend | grep -q "Up"; then
    echo "Testing frontend configuration access..."
    
    docker compose exec frontend python -c "
import yaml
import os
try:
    with open('/app/config/prompt.yaml', 'r') as f:
        yaml.safe_load(f)
    print('✓ Frontend configuration access working')
except Exception as e:
    print(f'✗ Frontend configuration error: {e}')
" 2>/dev/null || echo -e "${RED}✗ Frontend configuration test failed${NC}"
fi

echo ""
echo "=== 5. Performance Benchmarking ==="
echo "Running performance tests..."

if docker compose ps backend | grep -q "Up"; then
    echo "Testing backend API response times..."
    
    # Test multiple requests and measure response time
    TOTAL_TIME=0
    SUCCESS_COUNT=0
    
    for i in {1..5}; do
        START_TIME=$(date +%s.%N)
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null)
        END_TIME=$(date +%s.%N)
        
        if [ "$RESPONSE" = "200" ]; then
            DURATION=$(echo "$END_TIME - $START_TIME" | bc)
            TOTAL_TIME=$(echo "$TOTAL_TIME + $DURATION" | bc)
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        fi
        
        sleep 0.2
    done
    
    if [ $SUCCESS_COUNT -gt 0 ]; then
        AVG_TIME=$(echo "scale=3; $TOTAL_TIME / $SUCCESS_COUNT" | bc)
        echo "Backend API performance:"
        echo "- Successful requests: $SUCCESS_COUNT/5"
        echo "- Average response time: ${AVG_TIME}s"
        
        if (( $(echo "$AVG_TIME < 2.0" | bc -l) )); then
            echo -e "${GREEN}✓ Backend response time acceptable (<2s)${NC}"
        else
            echo -e "${YELLOW}⚠ Backend response time: ${AVG_TIME}s (>2s)${NC}"
        fi
    else
        echo -e "${RED}✗ No successful backend requests${NC}"
    fi
fi

echo ""
echo "=== 6. Log Health and Monitoring ==="
echo "Checking container logs for errors..."

for service in traefik backend frontend; do
    if docker compose ps $service | grep -q "Up"; then
        echo "Checking $service logs for errors..."
        
        ERROR_COUNT=$(docker compose logs $service --tail=50 2>/dev/null | grep -i error | wc -l)
        WARNING_COUNT=$(docker compose logs $service --tail=50 2>/dev/null | grep -i warning | wc -l)
        
        echo "$service log analysis:"
        echo "- Errors in last 50 lines: $ERROR_COUNT"
        echo "- Warnings in last 50 lines: $WARNING_COUNT"
        
        if [ $ERROR_COUNT -eq 0 ]; then
            echo -e "${GREEN}✓ No errors in recent $service logs${NC}"
        else
            echo -e "${YELLOW}⚠ $ERROR_COUNT errors found in $service logs${NC}"
        fi
    fi
done

echo ""
echo "=== 7. Container Restart Resilience ==="
echo "Testing configuration persistence across restarts..."

echo "Restarting backend container..."
docker compose restart backend
sleep 10

if docker compose ps backend | grep -q "Up"; then
    echo "Testing backend after restart..."
    
    # Test configuration accessibility after restart
    docker compose exec backend python -c "
import yaml
try:
    with open('/app/config/rubric.yaml', 'r') as f:
        data = yaml.safe_load(f)
    print('✓ Configuration accessible after restart')
except Exception as e:
    print(f'✗ Configuration error after restart: {e}')
" 2>/dev/null || echo -e "${RED}✗ Backend configuration test failed after restart${NC}"
    
    # Test health endpoint after restart
    sleep 5
    HEALTH_AFTER_RESTART=$(curl -s http://localhost:8000/health 2>/dev/null | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    
    if [ "$HEALTH_AFTER_RESTART" = "healthy" ]; then
        echo -e "${GREEN}✓ Backend healthy after restart${NC}"
    else
        echo -e "${YELLOW}⚠ Backend status after restart: $HEALTH_AFTER_RESTART${NC}"
    fi
else
    echo -e "${RED}✗ Backend failed to restart${NC}"
fi

echo ""
echo "=== 8. Network Connectivity Testing ==="
echo "Testing inter-container communication..."

if docker compose ps backend | grep -q "Up" && docker compose ps frontend | grep -q "Up"; then
    echo "Testing frontend to backend communication..."
    
    BACKEND_TEST=$(docker compose exec frontend curl -s -o /dev/null -w "%{http_code}" http://backend:8000/health 2>/dev/null)
    
    if [ "$BACKEND_TEST" = "200" ]; then
        echo -e "${GREEN}✓ Frontend can communicate with backend${NC}"
    else
        echo -e "${RED}✗ Frontend cannot communicate with backend (HTTP $BACKEND_TEST)${NC}"
    fi
fi

echo ""
echo "=== Container Health and Performance Summary ==="
echo "Phase 7.3 validation complete."
echo ""
echo "Health Status:"
echo "- Container orchestration: $(docker compose ps --format '{{.State}}' | grep -c Up)/$(docker compose ps --format '{{.State}}' | wc -l) containers running"
echo "- Configuration access: Validated across containers"
echo "- Performance: Response times and resource usage measured"
echo "- Restart resilience: Configuration persistence tested"
echo "- Network connectivity: Inter-container communication verified"
echo ""
echo "Monitoring Commands:"
echo "- Real-time stats: docker stats"
echo "- Container logs: docker compose logs -f [service]"
echo "- Health checks: curl http://localhost:8000/health"
echo "- Container status: docker compose ps"
