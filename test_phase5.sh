#!/bin/bash
echo "🔍 Phase 5: Automated Testing"

# Test 1: Vue component structure verification
echo "✅ Test 1: Component Structure"
COMPONENT_COUNT=$(find vue-frontend/src -name "*.vue" | wc -l)
if [ $COMPONENT_COUNT -gt 5 ]; then
    echo "✅ Found $COMPONENT_COUNT Vue components"
else
    echo "❌ Insufficient Vue components found"
    exit 1
fi

# Test 2: Login component verification
echo "✅ Test 2: Login Component"
if [ -f "vue-frontend/src/views/Login.vue" ]; then
    if grep -q "v-model.*username" vue-frontend/src/views/Login.vue && grep -q "v-model.*password" vue-frontend/src/views/Login.vue; then
        echo "✅ Login component has username/password fields"
    else
        echo "❌ Login component missing form fields"
        exit 1
    fi
else
    echo "❌ Login component not found"
    exit 1
fi

# Test 3: Layout component verification
echo "✅ Test 3: Layout Component"
if [ -f "vue-frontend/src/components/Layout.vue" ]; then
    if grep -q "router-link" vue-frontend/src/components/Layout.vue; then
        echo "✅ Layout component has navigation links"
    else
        echo "❌ Layout component missing navigation"
        exit 1
    fi
else
    echo "❌ Layout component not found"
    exit 1
fi

# Test 4: Text input component verification
echo "✅ Test 4: Text Input Component"
if [ -f "vue-frontend/src/views/TextInput.vue" ]; then
    if grep -q "textarea" vue-frontend/src/views/TextInput.vue && grep -q "CharacterCounter" vue-frontend/src/views/TextInput.vue; then
        echo "✅ Text input component has textarea and character counter"
    else
        echo "❌ Text input component missing required elements"
        exit 1
    fi
else
    echo "❌ Text input component not found"
    exit 1
fi

# Test 5: Feedback component verification
echo "✅ Test 5: Feedback Component"
if [ -f "vue-frontend/src/views/OverallFeedback.vue" ]; then
    if grep -q "overallScore" vue-frontend/src/views/OverallFeedback.vue && grep -q "RubricScores" vue-frontend/src/views/OverallFeedback.vue; then
        echo "✅ Feedback component displays overall score and rubric scores"
    else
        echo "❌ Feedback component missing score display"
        exit 1
    fi
else
    echo "❌ Feedback component not found"
    exit 1
fi

# Test 6: AuthStatus component verification
echo "✅ Test 6: AuthStatus Component"
if [ -f "vue-frontend/src/components/AuthStatus.vue" ]; then
    if grep -q "isAuthenticated" vue-frontend/src/components/AuthStatus.vue; then
        echo "✅ AuthStatus component has authentication status"
    else
        echo "❌ AuthStatus component missing authentication status"
        exit 1
    fi
else
    echo "❌ AuthStatus component not found"
    exit 1
fi

# Test 7: CharacterCounter component verification
echo "✅ Test 7: CharacterCounter Component"
if [ -f "vue-frontend/src/components/CharacterCounter.vue" ]; then
    if grep -q "characterCount" vue-frontend/src/components/CharacterCounter.vue; then
        echo "✅ CharacterCounter component has character counting"
    else
        echo "❌ CharacterCounter component missing character counting"
        exit 1
    fi
else
    echo "❌ CharacterCounter component not found"
    exit 1
fi

# Test 8: ProgressBar component verification
echo "✅ Test 8: ProgressBar Component"
if [ -f "vue-frontend/src/components/ProgressBar.vue" ]; then
    if grep -q "progress" vue-frontend/src/components/ProgressBar.vue && grep -q "status" vue-frontend/src/components/ProgressBar.vue; then
        echo "✅ ProgressBar component has progress and status"
    else
        echo "❌ ProgressBar component missing progress or status"
        exit 1
    fi
else
    echo "❌ ProgressBar component not found"
    exit 1
fi

# Test 9: RubricScores component verification
echo "✅ Test 9: RubricScores Component"
if [ -f "vue-frontend/src/components/RubricScores.vue" ]; then
    if grep -q "scores" vue-frontend/src/components/RubricScores.vue; then
        echo "✅ RubricScores component displays scores"
    else
        echo "❌ RubricScores component missing scores display"
        exit 1
    fi
else
    echo "❌ RubricScores component not found"
    exit 1
fi

# Test 10: Build verification with all components
echo "✅ Test 10: Build with All Components"
cd vue-frontend
npm run build > /dev/null 2>&1
BUILD_SUCCESS=$?
cd ..
if [ $BUILD_SUCCESS -eq 0 ]; then
    echo "✅ Build successful with all UI components"
else
    echo "❌ Build failed with UI components"
    exit 1
fi

echo "🎉 Phase 5: All automated tests passed!"
