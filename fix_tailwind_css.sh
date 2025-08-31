#!/bin/bash

# Tailwind CSS Quick Fix Script
# Memo AI Coach - Vue Frontend
# 
# This script automatically fixes common Tailwind CSS configuration issues
# that have been documented multiple times in the implementation changelog.

set -e  # Exit on any error

echo "🔧 Tailwind CSS Quick Fix Script"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "vue-frontend/package.json" ]; then
    echo "❌ Error: This script must be run from the project root directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected: Directory containing vue-frontend/ folder"
    exit 1
fi

cd vue-frontend

echo "📁 Working in: $(pwd)"
echo ""

# Step 1: Check current configuration
echo "🔍 Step 1: Analyzing current configuration..."

# Check package.json for problematic dependencies
if grep -q "@tailwindcss/postcss" package.json; then
    echo "⚠️  Found problematic @tailwindcss/postcss dependency"
    PROBLEMATIC_DEPS=true
else
    echo "✅ No problematic dependencies found"
    PROBLEMATIC_DEPS=false
fi

# Check Tailwind CSS version
TAILWIND_VERSION=$(grep -o '"tailwindcss": "[^"]*"' package.json | cut -d'"' -f4)
echo "📦 Current Tailwind CSS version: $TAILWIND_VERSION"

if [[ "$TAILWIND_VERSION" == *"4."* ]]; then
    echo "⚠️  Found Tailwind CSS v4.x (beta) - this will be fixed"
    VERSION_ISSUE=true
else
    echo "✅ Tailwind CSS version looks good"
    VERSION_ISSUE=false
fi

# Check PostCSS configuration
if grep -q "@tailwindcss/postcss" postcss.config.js; then
    echo "⚠️  Found problematic PostCSS configuration"
    POSTCSS_ISSUE=true
else
    echo "✅ PostCSS configuration looks good"
    POSTCSS_ISSUE=false
fi

echo ""

# Step 2: Apply fixes if needed
if [ "$PROBLEMATIC_DEPS" = true ] || [ "$VERSION_ISSUE" = true ] || [ "$POSTCSS_ISSUE" = true ]; then
    echo "🔧 Step 2: Applying fixes..."
    
    # Remove problematic dependencies
    if [ "$PROBLEMATIC_DEPS" = true ]; then
        echo "   Removing @tailwindcss/postcss..."
        npm uninstall @tailwindcss/postcss 2>/dev/null || true
    fi
    
    # Install correct Tailwind CSS version
    if [ "$VERSION_ISSUE" = true ]; then
        echo "   Installing Tailwind CSS v3.4.17..."
        npm install tailwindcss@^3.4.17
    fi
    
    # Fix PostCSS configuration
    if [ "$POSTCSS_ISSUE" = true ]; then
        echo "   Fixing PostCSS configuration..."
        cat > postcss.config.js << 'EOF'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF
        echo "   ✅ PostCSS configuration updated"
    fi
    
    echo "   ✅ All fixes applied"
else
    echo "✅ No fixes needed - configuration looks good"
fi

echo ""

# Step 3: Test the build
echo "🧪 Step 3: Testing build process..."

# Clean previous build
if [ -d "dist" ]; then
    echo "   Cleaning previous build..."
    rm -rf dist
fi

# Run build
echo "   Running npm run build..."
if npm run build > /dev/null 2>&1; then
    echo "   ✅ Build completed successfully"
else
    echo "   ❌ Build failed"
    echo "   Check the output above for errors"
    exit 1
fi

# Step 4: Check CSS file size
echo ""
echo "📊 Step 4: Checking CSS file size..."

CSS_FILE=$(find dist/assets -name "*.css" 2>/dev/null | head -1)
if [ -n "$CSS_FILE" ]; then
    CSS_SIZE=$(stat -c%s "$CSS_FILE" 2>/dev/null || echo "0")
    echo "   CSS file: $CSS_FILE"
    echo "   File size: $CSS_SIZE bytes"
    
    if [ $CSS_SIZE -gt 20000 ]; then
        echo "   ✅ CSS file size is correct (Tailwind processing)"
        TAILWIND_WORKING=true
    else
        echo "   ❌ CSS file size is too small (Tailwind not processing)"
        TAILWIND_WORKING=false
    fi
else
    echo "   ❌ No CSS file found in dist/assets/"
    TAILWIND_WORKING=false
fi

echo ""

# Step 5: Summary
echo "📋 Step 5: Summary"
echo "=================="

if [ "$TAILWIND_WORKING" = true ]; then
    echo "🎉 SUCCESS: Tailwind CSS is now working correctly!"
    echo ""
    echo "✅ Configuration fixed"
    echo "✅ Build process working"
    echo "✅ CSS file size correct ($CSS_SIZE bytes)"
    echo ""
    echo "🚀 You can now deploy or continue development"
else
    echo "❌ ISSUE: Tailwind CSS still not working properly"
    echo ""
    echo "🔧 Additional troubleshooting steps:"
    echo "   1. Check the build output for errors"
    echo "   2. Verify node_modules is up to date: npm install"
    echo "   3. Check docs/14_Tailwind_CSS_Troubleshooting.md"
    echo "   4. Review vue_implementation_changelog.md for similar issues"
    echo ""
    echo "📞 For help, check the troubleshooting guide:"
    echo "   docs/14_Tailwind_CSS_Troubleshooting.md"
fi

echo ""
echo "📚 Related Documentation:"
echo "   - docs/14_Tailwind_CSS_Troubleshooting.md"
echo "   - docs/04_Configuration_Guide.md (Section 5.1)"
echo "   - docs/08_Development_Guide.md (Section 5.1)"
echo "   - devlog/vue_frontend_implementation_plan.md"
echo "   - vue_implementation_changelog.md"

echo ""
echo "🔧 Fix script completed!"
