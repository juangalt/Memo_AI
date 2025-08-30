#!/bin/bash
echo "🔍 Phase 3: Automated Testing"

# Test 1: Vue Router structure verification
echo "✅ Test 1: Vue Router Setup"
if [ -f "vue-frontend/src/router/index.ts" ]; then
    ROUTE_COUNT=$(grep -c "path:" vue-frontend/src/router/index.ts)
    if [ $ROUTE_COUNT -gt 3 ]; then
        echo "✅ Vue Router configured with $ROUTE_COUNT routes"
    else
        echo "❌ Insufficient routes configured"
        exit 1
    fi
else
    echo "❌ Vue Router file not found"
    exit 1
fi

# Test 2: Authentication store verification
echo "✅ Test 2: Authentication Store"
if [ -f "vue-frontend/src/stores/auth.ts" ] || [ -f "vue-frontend/src/stores/auth.js" ]; then
    AUTH_METHODS=$(grep -c "const.*=" vue-frontend/src/stores/auth.*)
    if [ $AUTH_METHODS -gt 5 ]; then
        echo "✅ Authentication store configured with $AUTH_METHODS methods"
    else
        echo "❌ Insufficient auth methods"
        exit 1
    fi
else
    echo "❌ Authentication store file not found"
    exit 1
fi

# Test 3: Main app file verification
echo "✅ Test 3: App Initialization"
if [ -f "vue-frontend/src/main.ts" ]; then
    if grep -q "createApp" vue-frontend/src/main.ts && grep -q "createPinia" vue-frontend/src/main.ts; then
        echo "✅ App initialization configured correctly"
    else
        echo "❌ App initialization incomplete"
        exit 1
    fi
else
    echo "❌ Main app file not found"
    exit 1
fi

# Test 4: Route protection verification
echo "✅ Test 4: Route Protection"
PROTECTED_ROUTES=$(grep -c "requiresAuth\|requiresAdmin" vue-frontend/src/router/index.ts)
if [ $PROTECTED_ROUTES -gt 0 ]; then
    echo "✅ Route protection configured ($PROTECTED_ROUTES protected routes)"
else
    echo "❌ No route protection configured"
    exit 1
fi

# Test 5: API service layer verification
echo "✅ Test 5: API Service Layer"
if [ -f "vue-frontend/src/services/api.ts" ] || [ -f "vue-frontend/src/services/api.js" ]; then
    INTERCEPTORS=$(grep -c "interceptors" vue-frontend/src/services/api.*)
    if [ $INTERCEPTORS -gt 0 ]; then
        echo "✅ API service configured with interceptors"
    else
        echo "❌ API service missing interceptors"
        exit 1
    fi
else
    echo "❌ API service file not found"
    exit 1
fi

# Test 6: Authentication service verification
echo "✅ Test 6: Authentication Service"
if [ -f "vue-frontend/src/services/auth.ts" ] || [ -f "vue-frontend/src/services/auth.js" ]; then
    AUTH_ENDPOINTS=$(grep -c "async.*login\|async.*logout\|async.*validate" vue-frontend/src/services/auth.*)
    if [ $AUTH_ENDPOINTS -gt 2 ]; then
        echo "✅ Authentication service configured with $AUTH_ENDPOINTS endpoints"
    else
        echo "❌ Insufficient auth endpoints"
        exit 1
    fi
else
    echo "❌ Authentication service file not found"
    exit 1
fi

# Test 7: Build verification with new components
echo "✅ Test 7: Build with Components"
cd vue-frontend
npm run build > /dev/null 2>&1
BUILD_SUCCESS=$?
cd ..
if [ $BUILD_SUCCESS -eq 0 ]; then
    echo "✅ Build successful with new components"
else
    echo "❌ Build failed with new components"
    exit 1
fi

echo "🎉 Phase 3: All automated tests passed!"
