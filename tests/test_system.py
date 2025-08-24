#!/usr/bin/env python3
"""
Simple System Test for Memo AI Coach
"""

import requests
import json
from datetime import datetime

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Health: {data['status']}")
            print(f"   Services: {data['services']}")
            return True
        else:
            print(f"❌ Backend Health: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Health: {str(e)}")
        return False

def test_backend_root():
    """Test backend root endpoint"""
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Root: {data['message']} v{data['version']}")
            return True
        else:
            print(f"❌ Backend Root: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Root: {str(e)}")
        return False

def test_database_health():
    """Test database health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health/database", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Database Health: {data['status']}")
            return True
        else:
            print(f"❌ Database Health: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Database Health: {str(e)}")
        return False

def test_llm_health():
    """Test LLM health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health/llm", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ LLM Health: {data['status']}")
            return True
        else:
            print(f"❌ LLM Health: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ LLM Health: {str(e)}")
        return False

def test_auth_health():
    """Test auth health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health/auth", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Auth Health: {data['status']}")
            return True
        else:
            print(f"❌ Auth Health: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Auth Health: {str(e)}")
        return False

def test_session_creation():
    """Test session creation"""
    try:
        response = requests.post("http://localhost:8000/api/v1/sessions/create", timeout=10)
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('data', {}).get('session_id')
            print(f"✅ Session Creation: Session ID {session_id[:8]}...")
            return True
        else:
            print(f"❌ Session Creation: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Session Creation: {str(e)}")
        return False

def test_container_status():
    """Test container status"""
    import subprocess
    try:
        result = subprocess.run(['docker', 'compose', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Container Status:")
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                if line.strip():
                    print(f"   {line}")
            return True
        else:
            print(f"❌ Container Status: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Container Status: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=== Memo AI Coach System Test ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    tests = [
        ("Container Status", test_container_status),
        ("Backend Root", test_backend_root),
        ("Backend Health", test_backend_health),
        ("Database Health", test_database_health),
        ("LLM Health", test_llm_health),
        ("Auth Health", test_auth_health),
        ("Session Creation", test_session_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the system configuration.")
        return 1

if __name__ == "__main__":
    exit(main())
