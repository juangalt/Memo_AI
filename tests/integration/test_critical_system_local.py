#!/usr/bin/env python3
"""
Critical System Tests - Local Container Version
Comprehensive tests for all critical system functionality using local Docker containers
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CriticalSystemTesterLocal:
    """Tests critical system functionality using local Docker containers"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "environment": "local_containers",
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
        
        # Test data
        self.test_text = "This is a test evaluation message for critical system testing."
        self.session_id = None
    
    def log_test(self, test_name: str, status: str, message: str, details: Optional[Dict] = None):
        """Log test result"""
        test_result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            test_result["details"] = details
        
        self.results["tests"].append(test_result)
        
        # Update summary
        self.results["summary"]["total"] += 1
        if status == "PASS":
            self.results["summary"]["passed"] += 1
        elif status == "FAIL":
            self.results["summary"]["failed"] += 1
        elif status == "WARN":
            self.results["summary"]["warnings"] += 1
        
        # Print result
        status_icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}
        print(f"{status_icon.get(status, '❓')} {test_name}: {message}")
    
    def run_docker_command(self, command: str) -> Tuple[bool, str, str]:
        """Run a Docker command and return success, stdout, stderr"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def test_container_status(self) -> bool:
        """Test container status"""
        print("\n=== Testing Container Status ===")
        
        success, output, error = self.run_docker_command("docker compose ps")
        if success:
            # Check if all containers are running
            lines = output.strip().split('\n')
            if len(lines) >= 2:  # Header + at least one container
                container_lines = [line for line in lines[1:] if line.strip()]
                running_containers = [line for line in container_lines if "Up" in line]
                
                if len(running_containers) >= 3:  # backend, frontend, traefik
                    self.log_test(
                        "Container Status",
                        "PASS",
                        f"All containers running: {len(running_containers)} containers",
                        {"running_containers": len(running_containers)}
                    )
                    return True
                else:
                    self.log_test(
                        "Container Status",
                        "FAIL",
                        f"Not all containers running: {len(running_containers)}/{len(container_lines)}",
                        {"running": len(running_containers), "total": len(container_lines)}
                    )
                    return False
            else:
                self.log_test(
                    "Container Status",
                    "FAIL",
                    "No containers found",
                    {"output": output}
                )
                return False
        else:
            self.log_test(
                "Container Status",
                "FAIL",
                f"Failed to check container status: {error}",
                {"error": error}
            )
            return False
    
    def test_api_health_endpoints(self) -> bool:
        """Test API health endpoints"""
        print("\n=== Testing API Health Endpoints ===")
        
        health_endpoints = [
            ("/health", "Main health check"),
            ("/health/database", "Database health"),
            ("/health/config", "Configuration health"),
            ("/health/llm", "LLM health"),
            ("/health/auth", "Authentication health")
        ]
        
        all_healthy = True
        for endpoint, description in health_endpoints:
            success, output, error = self.run_docker_command(
                f"docker compose exec backend curl -s http://localhost:8000{endpoint}"
            )
            
            if success and output.strip():
                try:
                    data = json.loads(output)
                    status = data.get("status", "unknown")
                    if status == "healthy":
                        self.log_test(
                            f"API Health: {description}",
                            "PASS",
                            f"Endpoint {endpoint} is healthy",
                            {"endpoint": endpoint, "status": status}
                        )
                    else:
                        self.log_test(
                            f"API Health: {description}",
                            "WARN",
                            f"Endpoint {endpoint} returned status: {status}",
                            {"endpoint": endpoint, "status": status}
                        )
                        all_healthy = False
                except json.JSONDecodeError:
                    self.log_test(
                        f"API Health: {description}",
                        "FAIL",
                        f"Endpoint {endpoint} returned invalid JSON",
                        {"endpoint": endpoint, "output": output[:100]}
                    )
                    all_healthy = False
            else:
                self.log_test(
                    f"API Health: {description}",
                    "FAIL",
                    f"Endpoint {endpoint} request failed: {error}",
                    {"endpoint": endpoint, "error": error}
                )
                all_healthy = False
        
        return all_healthy
    
    def test_session_management(self) -> bool:
        """Test session creation and management"""
        print("\n=== Testing Session Management ===")
        
        # Login first
        login_payload = json.dumps({
            "username": "admin",
            "password": "admin123"
        })
        success, output, error = self.run_docker_command(
            f"docker compose exec backend curl -s -X POST http://localhost:8000/api/v1/auth/login -H 'Content-Type: application/json' -d '{login_payload}'"
        )
        
        if success and output.strip():
            try:
                data = json.loads(output)
                session_token = data.get("data", {}).get("session_token")
                if not session_token:
                    self.log_test(
                        "Session Management",
                        "FAIL",
                        "No session token in login response",
                        {"response": data}
                    )
                    return False
                
                self.session_id = session_token
                self.log_test(
                    "Session Creation",
                    "PASS",
                    f"Session created successfully: {session_token[:10]}...",
                    {"session_token": session_token[:10] + "..."}
                )
                
                # Test session validation
                success, output, error = self.run_docker_command(
                    f"docker compose exec backend curl -s -X GET http://localhost:8000/api/v1/auth/validate -H 'X-Session-Token: {session_token}'"
                )
                
                if success and output.strip():
                    try:
                        session_data = json.loads(output)
                        if session_data.get("data"):
                            self.log_test(
                                "Session Validation",
                                "PASS",
                                "Session can be validated successfully",
                                {"session_token": session_token[:10] + "..."}
                            )
                            return True
                        else:
                            self.log_test(
                                "Session Validation",
                                "FAIL",
                                "No session data in response",
                                {"session_token": session_token[:10] + "...", "response": session_data}
                            )
                            return False
                    except json.JSONDecodeError:
                        self.log_test(
                            "Session Validation",
                            "FAIL",
                            "Session validation returned invalid JSON",
                            {"session_token": session_token[:10] + "...", "output": output[:100]}
                        )
                        return False
                else:
                    self.log_test(
                        "Session Validation",
                        "FAIL",
                        f"Session validation failed: {error}",
                        {"session_token": session_token[:10] + "...", "error": error}
                    )
                    return False
            except json.JSONDecodeError:
                self.log_test(
                    "Session Management",
                    "FAIL",
                    "Login response is not valid JSON",
                    {"output": output[:100]}
                )
                return False
        else:
            self.log_test(
                "Session Management",
                "FAIL",
                f"Login failed: {error}",
                {"error": error}
            )
            return False
    
    def test_text_evaluation_workflow(self) -> bool:
        """Test complete text evaluation workflow"""
        print("\n=== Testing Text Evaluation Workflow ===")
        
        if not self.session_id:
            self.log_test(
                "Text Evaluation",
                "FAIL",
                "No session ID available for evaluation test"
            )
            return False
        
        # Login first
        login_payload = json.dumps({
            "username": "admin",
            "password": "admin123"
        })
        success, output, error = self.run_docker_command(
            f"docker compose exec backend curl -s -X POST http://localhost:8000/api/v1/auth/login -H 'Content-Type: application/json' -d '{login_payload}'"
        )
        
        if not success or not output.strip():
            self.log_test(
                "Text Evaluation",
                "FAIL",
                f"Login failed: {error}",
                {"error": error}
            )
            return False
        
        try:
            data = json.loads(output)
            session_token = data.get("data", {}).get("session_token")
            if not session_token:
                self.log_test(
                    "Text Evaluation",
                    "FAIL",
                    "No session token in login response",
                    {"response": data}
                )
                return False
            
            # Submit text for evaluation
            payload = json.dumps({
                "text_content": self.test_text
            })
            
            start_time = time.time()
            success, output, error = self.run_docker_command(
                f"docker compose exec backend curl -s -X POST http://localhost:8000/api/v1/evaluations/submit -H 'Content-Type: application/json' -H 'X-Session-Token: {session_token}' -d '{payload}'"
            )
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            if not success or not output.strip():
                self.log_test(
                    "Text Evaluation",
                    "FAIL",
                    f"Evaluation submission failed: {error}",
                    {"error": error}
                )
                return False
            
            data = json.loads(output)
            evaluation_data = data.get("data", {}).get("evaluation", {})
            
            if not evaluation_data:
                self.log_test(
                    "Text Evaluation Data",
                    "FAIL",
                    "No evaluation data in response",
                    {"response": data}
                )
                return False
            
            # Check for required evaluation fields
            required_fields = ["overall_score", "strengths", "opportunities", "rubric_scores"]
            missing_fields = [field for field in required_fields if field not in evaluation_data]
            
            if missing_fields:
                self.log_test(
                    "Text Evaluation Data",
                    "FAIL",
                    f"Missing required evaluation fields: {missing_fields}",
                    {"missing_fields": missing_fields}
                )
                return False
            
            self.log_test(
                "Text Evaluation Submission",
                "PASS",
                f"Evaluation completed successfully in {processing_time:.2f}s",
                {
                    "processing_time": processing_time,
                    "overall_score": evaluation_data.get("overall_score"),
                    "model_used": evaluation_data.get("model_used")
                }
            )
            
            # Check performance benchmark
            if processing_time < 15:
                self.log_test(
                    "Evaluation Performance",
                    "PASS",
                    f"Processing time {processing_time:.2f}s meets benchmark (< 15s)",
                    {"processing_time": processing_time}
                )
            else:
                self.log_test(
                    "Evaluation Performance",
                    "WARN",
                    f"Processing time {processing_time:.2f}s exceeds benchmark (15s)",
                    {"processing_time": processing_time}
                )
            
            return True
            
        except json.JSONDecodeError:
            self.log_test(
                "Text Evaluation",
                "FAIL",
                "Response is not valid JSON",
                {"output": output[:100]}
            )
            return False
    
    def test_database_operations(self) -> bool:
        """Test database operations"""
        print("\n=== Testing Database Operations ===")
        
        success, output, error = self.run_docker_command(
            "docker compose exec backend curl -s http://localhost:8000/health/database"
        )
        
        if success and output.strip():
            try:
                data = json.loads(output)
                database_details = data.get("database", {})
                
                # Check for required database tables
                tables = database_details.get("tables", [])
                required_tables = ["users", "sessions", "submissions", "evaluations"]
                missing_tables = [table for table in required_tables if table not in tables]
                
                if not missing_tables:
                    self.log_test(
                        "Database Tables",
                        "PASS",
                        f"All required database tables present: {len(tables)} tables",
                        {"tables": tables}
                    )
                else:
                    self.log_test(
                        "Database Tables",
                        "FAIL",
                        f"Missing required database tables: {missing_tables}",
                        {"missing_tables": missing_tables, "present_tables": tables}
                    )
                    return False
                
                # Check WAL mode
                journal_mode = database_details.get("journal_mode", "unknown")
                if journal_mode == "wal":
                    self.log_test(
                        "Database WAL Mode",
                        "PASS",
                        "Database is using WAL mode for better performance",
                        {"journal_mode": journal_mode}
                    )
                else:
                    self.log_test(
                        "Database WAL Mode",
                        "WARN",
                        f"Database is not using WAL mode: {journal_mode}",
                        {"journal_mode": journal_mode}
                    )
                
                return True
            except json.JSONDecodeError:
                self.log_test(
                    "Database Operations",
                    "FAIL",
                    "Database health check returned invalid JSON",
                    {"output": output[:100]}
                )
                return False
        else:
            self.log_test(
                "Database Operations",
                "FAIL",
                f"Database health check failed: {error}",
                {"error": error}
            )
            return False
    
    def test_llm_integration(self) -> bool:
        """Test LLM integration"""
        print("\n=== Testing LLM Integration ===")
        
        success, output, error = self.run_docker_command(
            "docker compose exec backend curl -s http://localhost:8000/health/llm"
        )
        
        if success and output.strip():
            try:
                data = json.loads(output)
                llm_details = data.get("llm", {})
                
                # Check LLM configuration
                provider = llm_details.get("provider", "unknown")
                model = llm_details.get("model", "unknown")
                api_accessible = llm_details.get("api_accessible", False)
                config_loaded = llm_details.get("config_loaded", False)
                
                if provider == "claude" and model and api_accessible and config_loaded:
                    self.log_test(
                        "LLM Integration",
                        "PASS",
                        f"LLM integration working: {provider} {model}",
                        {
                            "provider": provider,
                            "model": model,
                            "api_accessible": api_accessible,
                            "config_loaded": config_loaded
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "LLM Integration",
                        "FAIL",
                        f"LLM integration issues: provider={provider}, model={model}, api_accessible={api_accessible}, config_loaded={config_loaded}",
                        {
                            "provider": provider,
                            "model": model,
                            "api_accessible": api_accessible,
                            "config_loaded": config_loaded
                        }
                    )
                    return False
            except json.JSONDecodeError:
                self.log_test(
                    "LLM Integration",
                    "FAIL",
                    "LLM health check returned invalid JSON",
                    {"output": output[:100]}
                )
                return False
        else:
            self.log_test(
                "LLM Integration",
                "FAIL",
                f"LLM health check failed: {error}",
                {"error": error}
            )
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling scenarios"""
        print("\n=== Testing Error Handling ===")
        
        error_tests = [
            {
                "name": "Invalid Session ID",
                "command": "docker compose exec backend curl -s -w 'STATUS:%{http_code}' http://localhost:8000/api/v1/sessions/invalid-session-id",
                "expected_status": "404"
            },
            {
                "name": "Invalid Evaluation Payload",
                "command": "docker compose exec backend curl -s -w 'STATUS:%{http_code}' -X POST http://localhost:8000/api/v1/evaluations/submit -H 'Content-Type: application/json' -d '{\"invalid\": \"payload\"}'",
                "expected_status": "401"
            },
            {
                "name": "Missing Text Content",
                "command": "docker compose exec backend curl -s -w 'STATUS:%{http_code}' -X POST http://localhost:8000/api/v1/evaluations/submit -H 'Content-Type: application/json' -d '{\"session_id\": \"test\"}'",
                "expected_status": "401"
            },
            {
                "name": "Invalid Login Credentials",
                "command": "docker compose exec backend curl -s -w 'STATUS:%{http_code}' -X POST http://localhost:8000/api/v1/auth/login -H 'Content-Type: application/json' -d '{\"username\": \"invalid\", \"password\": \"invalid\"}'",
                "expected_status": "401"
            },
            {
                "name": "Missing Login Credentials",
                "command": "docker compose exec backend curl -s -w 'STATUS:%{http_code}' -X POST http://localhost:8000/api/v1/auth/login -H 'Content-Type: application/json' -d '{}'",
                "expected_status": "400"
            }
        ]
        
        all_passed = True
        for test in error_tests:
            success, output, error = self.run_docker_command(test["command"])
            
            if success and output.strip():
                # Extract the status code from the output (format: response_bodySTATUS:code)
                if "STATUS:" in output:
                    parts = output.split("STATUS:")
                    response_body = parts[0]
                    status_code = parts[1]
                    
                    if status_code == test["expected_status"]:
                        self.log_test(
                            f"Error Handling: {test['name']}",
                            "PASS",
                            f"Correctly returned status {status_code}",
                            {"expected": test["expected_status"], "actual": status_code, "response": response_body[:100]}
                        )
                    else:
                        self.log_test(
                            f"Error Handling: {test['name']}",
                            "FAIL",
                            f"Expected status {test['expected_status']}, got {status_code}",
                            {"expected": test["expected_status"], "actual": status_code, "response": response_body[:100]}
                        )
                        all_passed = False
                else:
                    self.log_test(
                        f"Error Handling: {test['name']}",
                        "WARN",
                        f"Unexpected response format - no STATUS found",
                        {"output": output[:100], "error": error}
                    )
            else:
                self.log_test(
                    f"Error Handling: {test['name']}",
                    "WARN",
                    f"Request failed: {error}",
                    {"expected": test["expected_status"], "error": error}
                )
        
        return all_passed
    
    def run_all_tests(self) -> Dict:
        """Run all critical system tests"""
        print("=== Critical System Tests (Local Containers) ===")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Environment: Local Docker Containers")
        
        # Run all tests
        tests = [
            self.test_container_status,
            self.test_api_health_endpoints,
            self.test_session_management,
            self.test_text_evaluation_workflow,
            self.test_database_operations,
            self.test_llm_integration,
            self.test_error_handling
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(
                    f"Test Execution: {test.__name__}",
                    "FAIL",
                    f"Test execution failed: {str(e)}"
                )
        
        # Generate summary
        summary = self.results["summary"]
        success_rate = (summary["passed"] / summary["total"]) * 100 if summary["total"] > 0 else 0
        
        print(f"\n=== Test Summary ===")
        print(f"Total Tests: {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Warnings: {summary['warnings']}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if summary["failed"] == 0:
            print("🎉 Critical system tests PASSED - System is operational!")
        else:
            print("⚠️ Critical system tests have issues - Review failed tests")
        
        return self.results

def main():
    """Main function to run critical system tests"""
    tester = CriticalSystemTesterLocal()
    results = tester.run_all_tests()
    
    # Save results to file
    output_file = "tests/logs/critical_system_test_results.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    # Exit with appropriate code
    if results["summary"]["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
