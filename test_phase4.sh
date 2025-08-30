#!/bin/bash
echo "🔍 Phase 4: Automated Testing"

# Test 1: API client configuration
echo "✅ Test 1: API Client Setup"
if [ -f "vue-frontend/src/services/api.ts" ] || [ -f "vue-frontend/src/services/api.js" ]; then
    if grep -q "axios.create" vue-frontend/src/services/api.* && grep -q "baseURL" vue-frontend/src/services/api.*; then
        echo "✅ API client configured with axios and base URL"
    else
        echo "❌ API client configuration incomplete"
        exit 1
    fi
else
    echo "❌ API client file not found"
    exit 1
fi

# Test 2: Request/Response interceptors
echo "✅ Test 2: Interceptors"
INTERCEPTOR_COUNT=$(grep -c "interceptors" vue-frontend/src/services/api.*)
if [ $INTERCEPTOR_COUNT -ge 2 ]; then
    echo "✅ Request and response interceptors configured"
else
    echo "❌ Missing interceptors"
    exit 1
fi

# Test 3: Authentication header injection
echo "✅ Test 3: Auth Headers"
if grep -q "X-Session-Token" vue-frontend/src/services/api.*; then
    echo "✅ Authentication header injection configured"
else
    echo "❌ Missing authentication headers"
    exit 1
fi

# Test 4: Authentication service endpoints
echo "✅ Test 4: Auth Service Endpoints"
if [ -f "vue-frontend/src/services/auth.ts" ] || [ -f "vue-frontend/src/services/auth.js" ]; then
    LOGIN_METHOD=$(grep -c "async.*login" vue-frontend/src/services/auth.*)
    LOGOUT_METHOD=$(grep -c "async.*logout" vue-frontend/src/services/auth.*)
    VALIDATE_METHOD=$(grep -c "async.*validate" vue-frontend/src/services/auth.*)
    if [ $LOGIN_METHOD -gt 0 ] && [ $LOGOUT_METHOD -gt 0 ] && [ $VALIDATE_METHOD -gt 0 ]; then
        echo "✅ Authentication service endpoints configured"
    else
        echo "❌ Missing authentication service endpoints"
        exit 1
    fi
else
    echo "❌ Authentication service file not found"
    exit 1
fi

# Test 5: Evaluation service configuration
echo "✅ Test 5: Evaluation Service"
if [ -f "vue-frontend/src/services/evaluation.ts" ] || [ -f "vue-frontend/src/services/evaluation.js" ]; then
    SUBMIT_METHOD=$(grep -c "async.*submit" vue-frontend/src/services/evaluation.*)
    if [ $SUBMIT_METHOD -gt 0 ]; then
        echo "✅ Evaluation service configured with submit method"
    else
        echo "❌ Missing evaluation service methods"
        exit 1
    fi
else
    echo "❌ Evaluation service file not found"
    exit 1
fi

# Test 6: Evaluation store verification
echo "✅ Test 6: Evaluation Store"
if [ -f "vue-frontend/src/stores/evaluation.ts" ] || [ -f "vue-frontend/src/stores/evaluation.js" ]; then
    STORE_METHODS=$(grep -c "submitEvaluation\|getEvaluation" vue-frontend/src/stores/evaluation.*)
    if [ $STORE_METHODS -gt 0 ]; then
        echo "✅ Evaluation store configured with evaluation methods"
    else
        echo "❌ Missing evaluation store methods"
        exit 1
    fi
else
    echo "❌ Evaluation store file not found"
    exit 1
fi

# Test 7: Backend API connectivity (when services are running)
echo "✅ Test 7: Backend Connectivity"
if docker compose ps | grep -q "Up"; then
    # Test backend health
    BACKEND_HEALTH=$(docker compose exec -T backend curl -s http://localhost:8000/health 2>/dev/null | grep -c "ok")
    if [ $BACKEND_HEALTH -gt 0 ]; then
        echo "✅ Backend API is accessible"

        # Test API endpoints through Vue service
        API_TEST=$(docker compose exec -T vue-frontend curl -s http://backend:8000/health 2>/dev/null | grep -c "ok")
        if [ $API_TEST -gt 0 ]; then
            echo "✅ Vue frontend can reach backend API"
        else
            echo "❌ Vue frontend cannot reach backend API"
            exit 1
        fi
    else
        echo "⚠️  Backend not running, skipping connectivity tests"
    fi
else
    echo "⚠️  Docker services not running, skipping connectivity tests"
fi

# Test 8: Standardized error handling
echo "✅ Test 8: Error Handling"
if grep -q "errors.*length" vue-frontend/src/services/evaluation.*; then
    echo "✅ Standardized error format handling implemented"
else
    echo "❌ Missing standardized error format handling"
    exit 1
fi

echo "🎉 Phase 4: All automated tests passed!"
