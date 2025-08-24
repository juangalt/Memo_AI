#!/usr/bin/env python3
"""
Test script for API communication layer
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.api_client import test_backend_connection, create_session_with_retry

def test_api_connection():
    """Test basic API connectivity"""
    print("Testing API connection...")
    
    # Test backend connection
    connected, error = test_backend_connection()
    if connected:
        print("✅ Backend connection successful")
        return True
    else:
        print(f"❌ Backend connection failed: {error}")
        return False

def test_session_creation():
    """Test session creation"""
    print("Testing session creation...")
    
    success, session_id, error = create_session_with_retry(max_retries=1)
    if success:
        print(f"✅ Session created successfully: {session_id[:8]}...")
        return True
    else:
        print(f"❌ Session creation failed: {error}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Memo AI Coach Frontend API Communication")
    print("=" * 50)
    
    # Test 1: API Connection
    connection_ok = test_api_connection()
    
    # Test 2: Session Creation (only if connection works)
    session_ok = False
    if connection_ok:
        session_ok = test_session_creation()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"API Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"Session Creation: {'✅ PASS' if session_ok else '❌ FAIL'}")
    
    if connection_ok and session_ok:
        print("\n🎉 All tests passed! Frontend API communication is working.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check backend service status.")
        return 1

if __name__ == "__main__":
    exit(main())
