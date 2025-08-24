#!/usr/bin/env python3
"""
Comprehensive Test Runner for Memo AI Coach
Handles both development and production environments
"""

import os
import sys
import subprocess
from datetime import datetime

def run_test_script(script_name, description):
    """Run a test script and report results"""
    print(f"\n--- Running {description} ---")
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to run {script_name}: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Memo AI Coach - Comprehensive Test Suite ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Environment: {os.getenv('APP_ENV', 'development')}")
    
    # Import test configuration to show current settings
    try:
        import test_config
        print(f"Backend URL: {test_config.BACKEND_URL}")
        print(f"Frontend URL: {test_config.FRONTEND_URL}")
        print(f"Log Directory: {test_config.LOG_DIR}")
    except ImportError:
        print("Warning: test_config.py not found")
    
    tests = [
        ("test_system.py", "System Integration Tests"),
        ("test_security_dev.py", "Security Tests (Development)"),
        ("monitor_production_dev.py", "Production Monitoring"),
    ]
    
    passed = 0
    total = len(tests)
    
    for script, description in tests:
        if run_test_script(script, description):
            passed += 1
    
    print(f"\n=== Test Summary ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit(main())
