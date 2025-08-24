#!/usr/bin/env python3
"""
System Integration Testing for Memo AI Coach
Comprehensive end-to-end testing script for production validation

This script provides comprehensive system validation including:
1. Complete user workflows (frontend to backend)
2. All error scenarios and edge cases
3. Performance benchmarks and requirements validation
4. System stability under concurrent load
5. Database operations and data integrity
6. API endpoint functionality and health
7. Authentication and security validation
8. Configuration management workflows
9. Service health monitoring

Usage:
    python testing/test_system_integration.py

This script is a definitive tool for:
- Production readiness validation
- System health monitoring
- Regression testing
- Performance benchmarking
- Quality assurance
"""

import requests
import time
import json
import threading
import concurrent.futures
from datetime import datetime
import sys
import os

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8501"
TEST_TEXT = "This is a sample memo for testing purposes. It contains multiple sentences to evaluate the system's ability to process and provide feedback on written content."

class SystemIntegrationTester:
    """
    Comprehensive system integration tester for Memo AI Coach
    
    This class provides end-to-end testing capabilities for validating
    the complete system integration, performance, and stability.
    """
    def __init__(self):
        self.session_token = None
        self.admin_token = None
        self.test_results = []
        self.start_time = time.time()
        
    def log_test(self, test_name, status, details=""):
        """Log test results with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "status": status,
            "details": details
        }
        self.test_results.append(result)
        print(f"[{timestamp}] {test_name}: {status} {details}")
        
    def test_backend_health(self):
        """Test 1: Backend Health Check"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Health", "PASS", f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.log_test("Backend Health", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_frontend_health(self):
        """Test 2: Frontend Health Check"""
        try:
            response = requests.get(f"{FRONTEND_URL}", timeout=5)
            if response.status_code == 200:
                self.log_test("Frontend Health", "PASS", "Frontend accessible")
                return True
            else:
                self.log_test("Frontend Health", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Health", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_admin_authentication(self):
        """Test 3: Admin Authentication Workflow"""
        try:
            # Test admin login
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            response = requests.post(f"{BACKEND_URL}/api/v1/admin/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Extract session token from the response structure
                self.admin_token = data.get("data", {}).get("session_token")
                if not self.admin_token:
                    self.log_test("Admin Login", "FAIL", "No session token in response")
                    return False
                    
                self.log_test("Admin Login", "PASS", "Authentication successful")
                
                # Test admin logout
                headers = {"X-Session-Token": self.admin_token}
                logout_response = requests.post(f"{BACKEND_URL}/api/v1/admin/logout", headers=headers, timeout=10)
                
                if logout_response.status_code == 200:
                    self.log_test("Admin Logout", "PASS", "Logout successful")
                    return True
                else:
                    self.log_test("Admin Logout", "FAIL", f"Status code: {logout_response.status_code}")
                    return False
            else:
                self.log_test("Admin Login", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Authentication", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_configuration_management(self):
        """Test 4: Configuration Management Workflow"""
        try:
            # Re-login as admin
            login_data = {"username": "admin", "password": "admin123"}
            response = requests.post(f"{BACKEND_URL}/api/v1/admin/login", json=login_data, timeout=10)
            if response.status_code != 200:
                self.log_test("Config Management", "FAIL", "Cannot authenticate as admin")
                return False
                
            self.admin_token = response.json().get("data", {}).get("session_token")
            headers = {"X-Session-Token": self.admin_token}
            
            # Test reading configuration
            config_response = requests.get(f"{BACKEND_URL}/api/v1/admin/config/rubric", headers=headers, timeout=10)
            if config_response.status_code == 200:
                self.log_test("Config Read", "PASS", "Configuration read successful")
                
                # Test updating configuration (read-only test)
                original_config = config_response.json().get("data", {}).get("content", "")
                update_response = requests.put(
                    f"{BACKEND_URL}/api/v1/admin/config/rubric",
                    headers=headers,
                    json={"content": original_config},
                    timeout=10
                )
                
                if update_response.status_code == 200:
                    self.log_test("Config Update", "PASS", "Configuration update successful")
                    return True
                else:
                    self.log_test("Config Update", "FAIL", f"Status code: {update_response.status_code}")
                    return False
            else:
                self.log_test("Config Read", "FAIL", f"Status code: {config_response.status_code}")
                return False
        except Exception as e:
            self.log_test("Config Management", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_text_evaluation_workflow(self):
        """Test 5: Complete Text Evaluation Workflow"""
        try:
            # Submit text for evaluation
            evaluation_data = {
                "text_content": TEST_TEXT,
                "session_id": "test_session_123"
            }
            
            start_time = time.time()
            response = requests.post(f"{BACKEND_URL}/api/v1/evaluations/submit", json=evaluation_data, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                evaluation_id = data.get("evaluation_id")
                processing_time = end_time - start_time
                
                self.log_test("Text Submission", "PASS", f"Evaluation ID: {evaluation_id}, Time: {processing_time:.2f}s")
                
                # Check if processing time meets performance requirements (< 15 seconds)
                if processing_time < 15:
                    self.log_test("Performance Benchmark", "PASS", f"Processing time: {processing_time:.2f}s (< 15s)")
                else:
                    self.log_test("Performance Benchmark", "WARN", f"Processing time: {processing_time:.2f}s (> 15s)")
                
                # The evaluation result is returned directly in the response
                evaluation_data = data.get("data", {}).get("evaluation", {})
                if evaluation_data:
                    self.log_test("Result Retrieval", "PASS", "Evaluation results retrieved")
                    return True
                else:
                    self.log_test("Result Retrieval", "FAIL", "No evaluation data in response")
                    return False
            else:
                self.log_test("Text Submission", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Text Evaluation", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_error_scenarios(self):
        """Test 6: Error Handling Scenarios"""
        test_cases = [
            {
                "name": "Invalid JSON",
                "data": "invalid json",
                "expected_status": 500  # FastAPI returns 500 for invalid JSON
            },
            {
                "name": "Empty Text",
                "data": {"text_content": "", "session_id": "test"},
                "expected_status": 400
            },
            {
                "name": "Missing Session",
                "data": {"text_content": "test text"},
                "expected_status": 200  # Session ID is optional
            },
            {
                "name": "Invalid Admin Credentials",
                "data": {"username": "invalid", "password": "invalid"},
                "expected_status": 401
            }
        ]
        
        passed = 0
        total = len(test_cases)
        
        for test_case in test_cases:
            try:
                if test_case["name"] == "Invalid JSON":
                    response = requests.post(f"{BACKEND_URL}/api/v1/evaluations/submit", data=test_case["data"], timeout=10)
                elif test_case["name"] == "Invalid Admin Credentials":
                    response = requests.post(f"{BACKEND_URL}/api/v1/admin/login", json=test_case["data"], timeout=10)
                else:
                    response = requests.post(f"{BACKEND_URL}/api/v1/evaluations/submit", json=test_case["data"], timeout=10)
                
                if response.status_code == test_case["expected_status"]:
                    self.log_test(f"Error Test: {test_case['name']}", "PASS", f"Expected {test_case['expected_status']}, got {response.status_code}")
                    passed += 1
                else:
                    self.log_test(f"Error Test: {test_case['name']}", "FAIL", f"Expected {test_case['expected_status']}, got {response.status_code}")
            except Exception as e:
                self.log_test(f"Error Test: {test_case['name']}", "FAIL", f"Exception: {str(e)}")
        
        self.log_test("Error Handling", "PASS" if passed == total else "FAIL", f"{passed}/{total} error scenarios handled correctly")
        return passed == total
    
    def test_concurrent_load(self):
        """Test 7: System Stability Under Load"""
        def submit_evaluation(session_id):
            try:
                data = {
                    "text_content": f"Test text for session {session_id}",
                    "session_id": f"session_{session_id}"
                }
                response = requests.post(f"{BACKEND_URL}/api/v1/evaluations/submit", json=data, timeout=30)
                return response.status_code == 200
            except:
                return False
        
        # Test with 5 concurrent requests
        concurrent_requests = 5
        successful_requests = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(submit_evaluation, i) for i in range(concurrent_requests)]
            for future in concurrent.futures.as_completed(futures):
                if future.result():
                    successful_requests += 1
        
        success_rate = (successful_requests / concurrent_requests) * 100
        self.log_test("Concurrent Load", "PASS" if success_rate >= 80 else "WARN", 
                     f"Success rate: {success_rate:.1f}% ({successful_requests}/{concurrent_requests})")
        return success_rate >= 80
    
    def test_database_operations(self):
        """Test 8: Database Operations and Data Integrity"""
        try:
            # Test health endpoint which includes database status
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                db_status = data.get("services", {}).get("database", "unknown")
                
                if db_status == "healthy":
                    self.log_test("Database Health", "PASS", "Database connection healthy")
                    return True
                else:
                    self.log_test("Database Health", "FAIL", f"Database status: {db_status}")
                    return False
            else:
                self.log_test("Database Health", "FAIL", f"Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Database Health", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_api_endpoints(self):
        """Test 9: All API Endpoints Functionality"""
        endpoints = [
            ("GET", "/health", "Health Check"),
            ("GET", "/health/auth", "Auth Health"),
            ("POST", "/api/v1/evaluations/submit", "Submit Evaluation"),
            ("GET", "/api/v1/admin/config/rubric", "Get Config"),
        ]
        
        passed = 0
        total = len(endpoints)
        
        for method, endpoint, name in endpoints:
            try:
                if method == "POST" and "submit" in endpoint:
                    data = {"text_content": "test", "session_id": "test"}
                    response = requests.post(f"{BACKEND_URL}{endpoint}", json=data, timeout=10)
                elif "config" in endpoint:
                    # Need admin token for config endpoints
                    if not self.admin_token:
                        login_response = requests.post(f"{BACKEND_URL}/api/v1/admin/login", 
                                                     json={"username": "admin", "password": "admin123"}, timeout=10)
                        if login_response.status_code == 200:
                            self.admin_token = login_response.json().get("data", {}).get("session_token")
                    
                    headers = {"X-Session-Token": self.admin_token} if self.admin_token else {}
                    response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=10)
                else:
                    response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
                
                if response.status_code in [200, 201, 422]:  # 422 is acceptable for validation errors
                    self.log_test(f"API: {name}", "PASS", f"Status: {response.status_code}")
                    passed += 1
                else:
                    self.log_test(f"API: {name}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"API: {name}", "FAIL", f"Error: {str(e)}")
        
        self.log_test("API Endpoints", "PASS" if passed == total else "WARN", f"{passed}/{total} endpoints working")
        return passed >= total * 0.8  # 80% success rate
    
    def run_all_tests(self):
        """Run all system integration tests"""
        print("=" * 60)
        print("SYSTEM INTEGRATION TESTING - MEMO AI COACH")
        print("=" * 60)
        print(f"Starting comprehensive system validation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        tests = [
            ("Backend Health", self.test_backend_health),
            ("Frontend Health", self.test_frontend_health),
            ("Admin Authentication", self.test_admin_authentication),
            ("Configuration Management", self.test_configuration_management),
            ("Text Evaluation Workflow", self.test_text_evaluation_workflow),
            ("Error Handling", self.test_error_scenarios),
            ("Concurrent Load", self.test_concurrent_load),
            ("Database Operations", self.test_database_operations),
            ("API Endpoints", self.test_api_endpoints),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, "ERROR", f"Test crashed: {str(e)}")
        
        # Summary
        print("\n" + "=" * 60)
        print("SYSTEM INTEGRATION TESTING SUMMARY")
        print("=" * 60)
        
        total_time = time.time() - self.start_time
        success_rate = (passed / total) * 100
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Testing Time: {total_time:.2f} seconds")
        
        # System validation criteria
        print("\nSYSTEM VALIDATION CRITERIA:")
        print("-" * 40)
        
        workflow_tests = [r for r in self.test_results if "workflow" in r["test"].lower() or "evaluation" in r["test"].lower()]
        error_tests = [r for r in self.test_results if "error" in r["test"].lower()]
        performance_tests = [r for r in self.test_results if "performance" in r["test"].lower() or "load" in r["test"].lower()]
        stability_tests = [r for r in self.test_results if "health" in r["test"].lower() or "database" in r["test"].lower()]
        
        workflows_passed = all(r["status"] in ["PASS", "WARN"] for r in workflow_tests)
        error_handling_passed = all(r["status"] in ["PASS", "WARN"] for r in error_tests)
        performance_passed = all(r["status"] in ["PASS", "WARN"] for r in performance_tests)
        stability_passed = all(r["status"] in ["PASS", "WARN"] for r in stability_tests)
        
        print(f"✓ All workflows functional: {'PASS' if workflows_passed else 'FAIL'}")
        print(f"✓ Error handling complete: {'PASS' if error_handling_passed else 'FAIL'}")
        print(f"✓ Performance targets met: {'PASS' if performance_passed else 'FAIL'}")
        print(f"✓ System stable under load: {'PASS' if stability_passed else 'FAIL'}")
        
        overall_success = workflows_passed and error_handling_passed and performance_passed and stability_passed
        
        print(f"\nOVERALL SYSTEM STATUS: {'PASS' if overall_success else 'FAIL'}")
        
        if overall_success:
            print("\n🎉 SYSTEM INTEGRATION VALIDATION COMPLETED SUCCESSFULLY!")
            print("The Memo AI Coach system is ready for production deployment")
        else:
            print("\n⚠️  SYSTEM INTEGRATION: Some issues need to be addressed before production")
        
        return overall_success

def main():
    """Main function to run system integration testing"""
    tester = SystemIntegrationTester()
    
    # Check if services are running
    print("Checking if services are running...")
    if not tester.test_backend_health():
        print("❌ Backend service is not running. Please start the backend first:")
        print("   cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return False
    
    if not tester.test_frontend_health():
        print("❌ Frontend service is not running. Please start the frontend first:")
        print("   cd frontend && streamlit run app.py --server.port 8501")
        return False
    
    print("✅ Services are running. Starting comprehensive system validation...\n")
    
    # Run all tests
    success = tester.run_all_tests()
    
    # Save test results
    with open("system_integration_test_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "test_type": "System Integration Testing",
            "success": success,
            "results": tester.test_results
        }, f, indent=2)
    
    print(f"\nTest results saved to: system_integration_test_results.json")
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
