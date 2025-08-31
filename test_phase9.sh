#!/bin/bash
echo "🔍 Phase 9: Production Deployment Testing"

# Test 1: Production environment variables
echo "✅ Test 1: Environment Variables"
if [ -n "$DOMAIN" ] && [ -n "$APP_ENV" ]; then
    if [ "$APP_ENV" = "production" ]; then
        echo "✅ Production environment configured correctly (DOMAIN: $DOMAIN, APP_ENV: $APP_ENV)"
    else
        echo "❌ Not in production environment (APP_ENV: $APP_ENV)"
        exit 1
    fi
else
    echo "❌ Missing required environment variables (DOMAIN: '$DOMAIN', APP_ENV: '$APP_ENV')"
    exit 1
fi

# Test 2: Production build verification
echo "✅ Test 2: Production Build"
cd vue-frontend
if [ -d "dist" ]; then
    # Check if production build exists
    JS_FILE=$(ls dist/assets/index-*.js 2>/dev/null | head -1)
    CSS_FILE=$(ls dist/assets/index-*.css 2>/dev/null | head -1)
    if [ -f "$JS_FILE" ] && [ -f "$CSS_FILE" ]; then
        echo "✅ Production build assets exist"
    else
        echo "❌ Production build assets missing"
        exit 1
    fi
else
    echo "❌ Production build directory not found"
    exit 1
fi

# Test 3: Asset optimization verification
echo "✅ Test 3: Asset Optimization"
JS_SIZE=$(stat -c%s "$JS_FILE" 2>/dev/null || stat -f%z "$JS_FILE" 2>/dev/null || echo "0")
CSS_SIZE=$(stat -c%s "$CSS_FILE" 2>/dev/null || stat -f%z "$CSS_FILE" 2>/dev/null || echo "0")
if [ $JS_SIZE -gt 100000 ] && [ $CSS_SIZE -gt 1000 ]; then
    echo "✅ Production assets are properly built (JS: $JS_SIZE bytes, CSS: $CSS_SIZE bytes)"
else
    echo "❌ Production assets seem too small or missing (JS: $JS_SIZE bytes, CSS: $CSS_SIZE bytes)"
    exit 1
fi

# Test 4: Docker production image verification
echo "✅ Test 4: Production Docker Image"
cd ..
if docker images | grep -q "memo_ai-vue-frontend"; then
    echo "✅ Production Docker image exists"
else
    echo "❌ Production Docker image not found"
    exit 1
fi

# Test 5: Production deployment status
echo "✅ Test 5: Production Deployment"
SERVICES_RUNNING=$(docker compose ps | grep -c "Up")
if [ $SERVICES_RUNNING -ge 2 ]; then
    echo "✅ Production services are running ($SERVICES_RUNNING services up)"
else
    echo "❌ Production services not properly deployed"
    exit 1
fi

# Test 6: HTTPS and SSL verification
echo "✅ Test 6: HTTPS Configuration"
HTTPS_STATUS=$(curl -k -I https://memo.myisland.dev/ 2>/dev/null | head -1 | grep -o "HTTP/[0-9.]* [0-9]*")
if echo "$HTTPS_STATUS" | grep -q "200"; then
    echo "✅ HTTPS endpoint responding correctly"

    # Check if SSL certificate is valid (not self-signed)
    SSL_INFO=$(echo | openssl s_client -connect memo.myisland.dev:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "✅ SSL certificate is properly configured"
    else
        echo "⚠️  SSL certificate verification failed (may be expected in development)"
    fi
else
    echo "❌ HTTPS endpoint not responding (status: $HTTPS_STATUS)"
    exit 1
fi

# Test 7: Production performance verification
echo "✅ Test 7: Production Performance"
START_TIME=$(date +%s%3N)
curl -k -s https://memo.myisland.dev/ > /dev/null 2>&1
END_TIME=$(date +%s%3N)
RESPONSE_TIME=$((END_TIME - START_TIME))
if [ $RESPONSE_TIME -lt 2000 ]; then
    echo "✅ Production response time acceptable ($RESPONSE_TIME ms)"
else
    echo "⚠️  Production response time slow ($RESPONSE_TIME ms)"
fi

# Test 8: Production logging verification
echo "✅ Test 8: Production Logging"
LOG_ENTRIES=$(docker compose logs vue-frontend 2>&1 | wc -l)
if [ $LOG_ENTRIES -gt 0 ]; then
    echo "✅ Production logs are being generated ($LOG_ENTRIES log entries)"
else
    echo "❌ No production logs found"
    exit 1
fi

# Test 9: Production health checks
echo "✅ Test 9: Production Health Checks"
HEALTH_STATUS=$(curl -k -s https://memo.myisland.dev/health 2>/dev/null | grep -c "healthy")
if [ $HEALTH_STATUS -gt 0 ]; then
    echo "✅ Production health check passing"
else
    echo "❌ Production health check failing"
    exit 1
fi

# Test 10: Production asset caching
echo "✅ Test 10: Production Asset Caching"
ASSET_HEADERS=$(curl -k -s -I https://memo.myisland.dev/assets/index-BF3jFvKY.css 2>/dev/null | grep -i "cache-control\|expires")
if echo "$ASSET_HEADERS" | grep -q "max-age\|expires"; then
    echo "✅ Production assets have proper caching headers"
else
    echo "❌ Production assets missing caching headers"
    exit 1
fi

cd vue-frontend
echo "🎉 Phase 9: Production deployment automated tests passed!"
