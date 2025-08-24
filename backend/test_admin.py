#!/usr/bin/env python3
"""
Test script for Phase 5: Administrative Functions
Tests admin authentication and configuration management
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services import get_auth_service, get_config_manager, authenticate_admin_user, validate_admin_session

def test_auth_service_initialization():
    """Test authentication service initialization"""
    print("🔧 Testing Auth Service Initialization...")
    
    try:
        auth_service = get_auth_service()
        health = auth_service.health_check()
        
        if health["status"] == "healthy":
            print("✅ Auth service initialized successfully")
            print(f"   - Config loaded: {health.get('config_loaded', False)}")
            print(f"   - Active sessions: {health.get('active_sessions', 0)}")
            print(f"   - Brute force protection: {health.get('brute_force_protection', False)}")
            return True
        else:
            print(f"❌ Auth service unhealthy: {health.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Auth service initialization failed: {e}")
        return False

def test_admin_authentication():
    """Test admin authentication"""
    print("\n🔐 Testing Admin Authentication...")
    
    try:
        # Test successful authentication
        success, session_token, error = authenticate_admin_user("admin", "admin123")
        
        if success and session_token:
            print("✅ Admin authentication successful")
            print(f"   - Session token: {session_token[:8]}...")
            
            # Test session validation
            valid, session_data, validation_error = validate_admin_session(session_token)
            
            if valid and session_data:
                print("✅ Session validation successful")
                print(f"   - Username: {session_data.get('username')}")
                print(f"   - Is admin: {session_data.get('is_admin')}")
                print(f"   - Permissions: {session_data.get('permissions', [])}")
                return True
            else:
                print(f"❌ Session validation failed: {validation_error}")
                return False
        else:
            print(f"❌ Admin authentication failed: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Admin authentication test failed: {e}")
        return False

def test_config_manager_initialization():
    """Test configuration manager initialization"""
    print("\n⚙️ Testing Config Manager Initialization...")
    
    try:
        config_manager = get_config_manager()
        health = config_manager.health_check()
        
        if health["status"] == "healthy":
            print("✅ Config manager initialized successfully")
            print(f"   - Config files: {list(health.get('config_files', {}).keys())}")
            print(f"   - Backup directory: {health.get('backup_dir', 'N/A')}")
            return True
        else:
            print(f"❌ Config manager unhealthy: {health.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Config manager initialization failed: {e}")
        return False

def test_config_file_operations():
    """Test configuration file operations"""
    print("\n📁 Testing Config File Operations...")
    
    try:
        config_manager = get_config_manager()
        
        # Test reading rubric config
        success, content, error = config_manager.read_config_file('rubric')
        
        if success and content:
            print("✅ Rubric config read successfully")
            print(f"   - Content length: {len(content)} characters")
            
            # Test YAML validation
            valid_yaml, parsed_data, yaml_error = config_manager.validate_yaml(content)
            
            if valid_yaml and parsed_data:
                print("✅ YAML validation successful")
                print(f"   - Has rubric section: {'rubric' in parsed_data}")
                print(f"   - Has criteria: {'criteria' in parsed_data.get('rubric', {})}")
                return True
            else:
                print(f"❌ YAML validation failed: {yaml_error}")
                return False
        else:
            print(f"❌ Rubric config read failed: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Config file operations test failed: {e}")
        return False

def test_backend_api_endpoints():
    """Test backend API endpoints"""
    print("\n🌐 Testing Backend API Endpoints...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health endpoint working")
            print(f"   - Overall status: {health_data.get('status')}")
            print(f"   - Services: {health_data.get('services', {})}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test auth health endpoint
        response = requests.get(f"{base_url}/health/auth", timeout=5)
        if response.status_code == 200:
            auth_health = response.json()
            print("✅ Auth health endpoint working")
            print(f"   - Auth status: {auth_health.get('status')}")
        else:
            print(f"❌ Auth health endpoint failed: {response.status_code}")
            return False
        
        # Test admin login endpoint
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{base_url}/api/v1/admin/login", json=login_data, timeout=5)
        
        if response.status_code == 200:
            login_response = response.json()
            session_token = login_response.get('data', {}).get('session_token')
            print("✅ Admin login endpoint working")
            print(f"   - Session token received: {bool(session_token)}")
            
            if session_token:
                # Test config get endpoint
                headers = {"X-Session-Token": session_token}
                response = requests.get(f"{base_url}/api/v1/admin/config/rubric", headers=headers, timeout=5)
                
                if response.status_code == 200:
                    config_response = response.json()
                    print("✅ Config get endpoint working")
                    print(f"   - Config content received: {bool(config_response.get('data', {}).get('content'))}")
                    return True
                else:
                    print(f"❌ Config get endpoint failed: {response.status_code}")
                    return False
            else:
                print("❌ No session token received")
                return False
        else:
            print(f"❌ Admin login endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend - make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Backend API test failed: {e}")
        return False

def main():
    """Run all Phase 5 tests"""
    print("🧪 Phase 5: Administrative Functions - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Auth Service Initialization", test_auth_service_initialization),
        ("Admin Authentication", test_admin_authentication),
        ("Config Manager Initialization", test_config_manager_initialization),
        ("Config File Operations", test_config_file_operations),
        ("Backend API Endpoints", test_backend_api_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 5 tests passed! Admin functions are working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit(main())
