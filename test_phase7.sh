#!/bin/bash
echo "🔍 Phase 7: Feedback Display Components Testing"

# Test 1: DetailedFeedback component verification
echo "✅ Test 1: DetailedFeedback Component"
if [ -f "vue-frontend/src/views/DetailedFeedback.vue" ]; then
    SEGMENT_FEEDBACK=$(grep -c "segmentFeedback" vue-frontend/src/views/DetailedFeedback.vue)
    SEGMENT_ANALYSIS=$(grep -c "Segment-Level Analysis" vue-frontend/src/views/DetailedFeedback.vue)
    EXPAND_COLLAPSE=$(grep -c "toggleSegment" vue-frontend/src/views/DetailedFeedback.vue)
    
    if [ $SEGMENT_FEEDBACK -gt 0 ] && [ $SEGMENT_ANALYSIS -gt 0 ] && [ $EXPAND_COLLAPSE -gt 0 ]; then
        echo "✅ DetailedFeedback component properly implemented"
    else
        echo "❌ DetailedFeedback component missing required elements"
        exit 1
    fi
else
    echo "❌ DetailedFeedback component not found"
    exit 1
fi

# Test 2: OverallFeedback component enhancement verification
echo "✅ Test 2: OverallFeedback Component Enhancement"
if [ -f "vue-frontend/src/views/OverallFeedback.vue" ]; then
    SCORE_DISPLAY=$(grep -c "overallScore" vue-frontend/src/views/OverallFeedback.vue)
    STRENGTHS_SECTION=$(grep -c "Strengths" vue-frontend/src/views/OverallFeedback.vue)
    OPPORTUNITIES_SECTION=$(grep -c "Opportunities" vue-frontend/src/views/OverallFeedback.vue)
    RUBRIC_SCORES=$(grep -c "RubricScores" vue-frontend/src/views/OverallFeedback.vue)
    
    if [ $SCORE_DISPLAY -gt 0 ] && [ $STRENGTHS_SECTION -gt 0 ] && [ $OPPORTUNITIES_SECTION -gt 0 ] && [ $RUBRIC_SCORES -gt 0 ]; then
        echo "✅ OverallFeedback component properly enhanced"
    else
        echo "❌ OverallFeedback component missing required elements"
        exit 1
    fi
else
    echo "❌ OverallFeedback component not found"
    exit 1
fi

# Test 3: RubricScores component verification
echo "✅ Test 3: RubricScores Component"
if [ -f "vue-frontend/src/components/RubricScores.vue" ]; then
    RUBRIC_DISPLAY=$(grep -c "Detailed Rubric Scores" vue-frontend/src/components/RubricScores.vue)
    SCORE_FORMATTING=$(grep -c "formatCriterionName" vue-frontend/src/components/RubricScores.vue)
    
    if [ $RUBRIC_DISPLAY -gt 0 ] && [ $SCORE_FORMATTING -gt 0 ]; then
        echo "✅ RubricScores component properly implemented"
    else
        echo "❌ RubricScores component missing required elements"
        exit 1
    fi
else
    echo "❌ RubricScores component not found"
    exit 1
fi

# Test 4: Evaluation store interface verification
echo "✅ Test 4: Evaluation Store Interface"
if [ -f "vue-frontend/src/stores/evaluation.ts" ]; then
    SEGMENT_FEEDBACK_INTERFACE=$(grep -c "segment_feedback" vue-frontend/src/stores/evaluation.ts)
    SEGMENT_FEEDBACK_TYPE=$(grep -c "SegmentFeedback" vue-frontend/src/stores/evaluation.ts)
    
    if [ $SEGMENT_FEEDBACK_INTERFACE -gt 0 ] && [ $SEGMENT_FEEDBACK_TYPE -gt 0 ]; then
        echo "✅ Evaluation store interface includes segment feedback"
    else
        echo "❌ Evaluation store interface missing segment feedback"
        exit 1
    fi
else
    echo "❌ Evaluation store not found"
    exit 1
fi

# Test 5: Component navigation verification
echo "✅ Test 5: Component Navigation"
OVERALL_TO_DETAILED=$(grep -c "to=\"/detailed-feedback\"" vue-frontend/src/views/OverallFeedback.vue)
DETAILED_TO_OVERALL=$(grep -c "to=\"/overall-feedback\"" vue-frontend/src/views/DetailedFeedback.vue)
TEXT_INPUT_LINKS=$(grep -c "to=\"/text-input\"" vue-frontend/src/views/DetailedFeedback.vue)

if [ $OVERALL_TO_DETAILED -gt 0 ] && [ $DETAILED_TO_OVERALL -gt 0 ] && [ $TEXT_INPUT_LINKS -gt 0 ]; then
    echo "✅ Component navigation properly implemented"
else
    echo "❌ Component navigation missing required links"
    exit 1
fi

# Test 6: Responsive design verification
echo "✅ Test 6: Responsive Design"
TAILWIND_CLASSES=$(grep -r "class=" vue-frontend/src/views/DetailedFeedback.vue | grep -c "max-w-\|grid-\|md:\|lg:\|sm:")
if [ $TAILWIND_CLASSES -gt 10 ]; then
    echo "✅ Responsive design classes implemented"
else
    echo "❌ Insufficient responsive design classes"
    exit 1
fi

# Test 7: Loading states verification
echo "✅ Test 7: Loading States"
LOADING_STATES=$(grep -c "isLoading" vue-frontend/src/views/DetailedFeedback.vue)
SPINNER_ANIMATION=$(grep -c "animate-spin" vue-frontend/src/views/DetailedFeedback.vue)

if [ $LOADING_STATES -gt 0 ] && [ $SPINNER_ANIMATION -gt 0 ]; then
    echo "✅ Loading states properly implemented"
else
    echo "❌ Loading states missing"
    exit 1
fi

# Test 8: Error handling verification
echo "✅ Test 8: Error Handling"
ERROR_STATES=$(grep -c "v-else" vue-frontend/src/views/DetailedFeedback.vue)
EMPTY_STATES=$(grep -c "No evaluation results" vue-frontend/src/views/DetailedFeedback.vue)

if [ $ERROR_STATES -gt 0 ] && [ $EMPTY_STATES -gt 0 ]; then
    echo "✅ Error handling and empty states implemented"
else
    echo "❌ Error handling or empty states missing"
    exit 1
fi

# Test 9: Accessibility verification
echo "✅ Test 9: Accessibility"
ARIA_LABELS=$(grep -c "aria-\|role=" vue-frontend/src/views/DetailedFeedback.vue 2>/dev/null || echo "0")
SEMANTIC_HTML=$(grep -c "<h[1-6]\|<section\|<article\|<nav" vue-frontend/src/views/DetailedFeedback.vue)

if [ $SEMANTIC_HTML -gt 5 ]; then
    echo "✅ Semantic HTML structure implemented"
else
    echo "❌ Insufficient semantic HTML structure"
    exit 1
fi

# Test 10: Build verification with all components
echo "✅ Test 10: Build with All Components"
cd vue-frontend
npm run build > /dev/null 2>&1
BUILD_SUCCESS=$?
cd ..
if [ $BUILD_SUCCESS -eq 0 ]; then
    echo "✅ Build successful with all Phase 7 components"
else
    echo "❌ Build failed with Phase 7 components"
    exit 1
fi

# Test 11: TypeScript compilation verification
echo "✅ Test 11: TypeScript Compilation"
cd vue-frontend
npx vue-tsc --noEmit > /dev/null 2>&1
TSC_SUCCESS=$?
cd ..
if [ $TSC_SUCCESS -eq 0 ]; then
    echo "✅ TypeScript compilation successful"
else
    echo "❌ TypeScript compilation errors found"
    exit 1
fi

# Test 12: Component integration verification
echo "✅ Test 12: Component Integration"
LAYOUT_IMPORT=$(grep -c "import Layout" vue-frontend/src/views/DetailedFeedback.vue)
EVALUATION_STORE_IMPORT=$(grep -c "useEvaluationStore" vue-frontend/src/views/DetailedFeedback.vue)

if [ $LAYOUT_IMPORT -gt 0 ] && [ $EVALUATION_STORE_IMPORT -gt 0 ]; then
    echo "✅ Component integration properly configured"
else
    echo "❌ Component integration issues"
    exit 1
fi

echo "🎉 Phase 7: All automated tests passed!"
