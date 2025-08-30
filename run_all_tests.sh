#!/bin/bash
echo "🚀 Vue Frontend Implementation - Complete Test Suite"

# Make all scripts executable
chmod +x test_phase*.sh

# Test execution order
phases=("1" "2" "3" "4" "5" "9" "10")
failed_phases=()

for phase in "${phases[@]}"; do
    echo ""
    echo "=========================================="
    echo "📋 Phase $phase: Starting automated tests"
    echo "=========================================="

    if [ -f "test_phase${phase}.sh" ]; then
        ./test_phase${phase}.sh
        if [ $? -ne 0 ]; then
            failed_phases+=("$phase")
            echo "❌ Phase $phase tests FAILED"
        else
            echo "✅ Phase $phase tests PASSED"
        fi
    else
        echo "⚠️  Test script for Phase $phase not found"
    fi
done

echo ""
echo "=========================================="
echo "📊 Test Results Summary"
echo "=========================================="

if [ ${#failed_phases[@]} -eq 0 ]; then
    echo "🎉 ALL PHASES PASSED! Vue frontend implementation is ready."
else
    echo "❌ FAILED PHASES: ${failed_phases[*]}"
    echo "🔧 Please fix the issues in the failed phases before proceeding."
    exit 1
fi
