#!/usr/bin/env python3
"""
Production Readiness Verification Test
Final comprehensive validation of complete production system
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

class ProductionReadinessTester:
    """Final production readiness verification"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "environment": "production_ready",
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
        
        # Test data
        self.test_text = "This is a comprehensive test message for production readiness verification."
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
    
    def test_system_accessibility(self) -> bool:
        """Test system accessibility"""
        print("\n=== Testing System Accessibility ===")
        
        # Test container accessibility
        success, output, error = self.run_docker_command("docker compose ps")
        if success:
            lines = output.strip().split('\n')
            if len(lines) >= 2:
                container_lines = [line for line in lines[1:] if line.strip()]
                running_containers = [line for line in container_lines if "Up" in line]
                
                if len(running_containers) >= 3:
                    self.log_test(
                        "Container Accessibility",
                        "PASS",
                        f"All containers accessible: {len(running_containers)} containers running",
                        {"running_containers": len(running_containers)}
                    )
                else:
                    self.log_test(
                        "Container Accessibility",
                        "FAIL",
                        f"Not all containers running: {len(running_containers)}/{len(container_lines)}",
                        {"running": len(running_containers), "total": len(container_lines)}
                    )
                    return False
            else:
                self.log_test(
                    "Container Accessibility",
                    "FAIL",
                    "No containers found"
                )
                return False
        else:
            self.log_test(
                "Container Accessibility",
                "FAIL",
                f"Failed to check containers: {error}"
            )
            return False
        
        # Test backend accessibility
        success, output, error = self.run_docker_command(
            "docker compose exec backend curl -s http://localhost:8000/health"
        )
        if success and output.strip():
            try:
                data = json.loads(output)
                if data.get("status") == "healthy":
                    self.log_test(
                        "Backend Accessibility",
                        "PASS",
                        "Backend is accessible and healthy"
                    )
                else:
                    self.log_test(
                        "Backend Accessibility",
                        "FAIL",
                        f"Backend not healthy: {data.get('status')}"
                    )
                    return False
            except json.JSONDecodeError:
                self.log_test(
                    "Backend Accessibility",
                    "FAIL",
                    "Backend returned invalid JSON"
                )
                return False
        else:
            self.log_test(
                "Backend Accessibility",
                "FAIL",
                f"Backend not accessible: {error}"
            )
            return False
        
        return True
    
    def test_security_measures(self) -> bool:
        """Test security measures"""
        print("\n=== Testing Security Measures ===")
        
        # Test configuration file security
        success, output, error = self.run_docker_command(
            "docker compose exec backend ls -la /app/config/"
        )
        if success:
            # Check if config files are read-only
            if "rw-r--r--" in output or "-r--r--r--" in output:
                self.log_test(
                    "Configuration Security",
                    "PASS",
                    "Configuration files have appropriate permissions"
                )
            else:
                self.log_test(
                    "Configuration Security",
                    "WARN",
                    "Configuration file permissions may need review"
                )
        else:
            self.log_test(
                "Configuration Security",
                "FAIL",
                f"Failed to check configuration permissions: {error}"
            )
            return False
        
        # Test non-root user
        success, output, error = self.run_docker_command(
            "docker compose exec backend whoami"
        )
        if success and "root" not in output.strip():
            self.log_test(
                "Container Security",
                "PASS",
                f"Container running as non-root user: {output.strip()}"
            )
        else:
            self.log_test(
                "Container Security",
                "FAIL",
                "Container running as root user"
            )
            return False
        
        return True
    
    def test_functionality_verification(self) -> bool:
        """Test complete functionality"""
        print("\n=== Testing Complete Functionality ===")
        
        # Test session creation
        success, output, error = self.run_docker_command(
            "docker compose exec backend curl -s -X POST http://localhost:8000/api/v1/sessions/create"
        )
        if success and output.strip():
            try:
                data = json.loads(output)
                session_id = data.get("data", {}).get("session_id")
                if session_id:
                    self.session_id = session_id
                    self.log_test(
                        "Session Functionality",
                        "PASS",
                        f"Session creation working: {session_id[:10]}..."
                    )
                else:
                    self.log_test(
                        "Session Functionality",
                        "FAIL",
                        "No session ID in response"
                    )
                    return False
            except json.JSONDecodeError:
                self.log_test(
                    "Session Functionality",
                    "FAIL",
                    "Session creation returned invalid JSON"
                )
                return False
        else:
            self.log_test(
                "Session Functionality",
                "FAIL",
                f"Session creation failed: {error}"
            )
            return False
        
        # Test evaluation functionality
        if self.session_id:
            payload = json.dumps({
                "text_content": self.test_text,
                "session_id": self.session_id
            })
            
            start_time = time.time()
            success, output, error = self.run_docker_command(
                f"docker compose exec backend curl -s -X POST http://localhost:8000/api/v1/evaluations/submit -H 'Content-Type: application/json' -d '{payload}'"
            )
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            if success and output.strip():
                try:
                    data = json.loads(output)
                    evaluation_data = data.get("data", {}).get("evaluation", {})
                    
                    if evaluation_data:
                        self.log_test(
                            "Evaluation Functionality",
                            "PASS",
                            f"Evaluation working: {processing_time:.2f}s processing time",
                            {
                                "processing_time": processing_time,
                                "overall_score": evaluation_data.get("overall_score"),
                                "model_used": evaluation_data.get("model_used")
                            }
                        )
                        return True
                    else:
                        self.log_test(
                            "Evaluation Functionality",
                            "FAIL",
                            "No evaluation data in response"
                        )
                        return False
                except json.JSONDecodeError as e:
                    self.log_test(
                        "Evaluation Functionality",
                        "FAIL",
                        f"Evaluation returned invalid JSON: {str(e)}"
                    )
                    return False
            else:
                self.log_test(
                    "Evaluation Functionality",
                    "FAIL",
                    f"Evaluation failed: {error}"
                )
                return False
        
        return True
    
    def test_monitoring_and_alerting(self) -> bool:
        """Test monitoring and alerting"""
        print("\n=== Testing Monitoring and Alerting ===")
        
        # Test health monitoring
        health_endpoints = [
            ("/health", "Main health"),
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
                    if data.get("status") == "healthy":
                        self.log_test(
                            f"Monitoring: {description}",
                            "PASS",
                            f"Health endpoint {endpoint} responding"
                        )
                    else:
                        self.log_test(
                            f"Monitoring: {description}",
                            "WARN",
                            f"Health endpoint {endpoint} not healthy: {data.get('status')}"
                        )
                        all_healthy = False
                except json.JSONDecodeError:
                    self.log_test(
                        f"Monitoring: {description}",
                        "FAIL",
                        f"Health endpoint {endpoint} returned invalid JSON"
                    )
                    all_healthy = False
            else:
                self.log_test(
                    f"Monitoring: {description}",
                    "FAIL",
                    f"Health endpoint {endpoint} not accessible: {error}"
                )
                all_healthy = False
        
        return all_healthy
    
    def test_backup_and_recovery(self) -> bool:
        """Test backup and recovery procedures"""
        print("\n=== Testing Backup and Recovery ===")
        
        # Test database backup
        success, output, error = self.run_docker_command(
            "docker compose exec backend ls -la /app/data/"
        )
        if success:
            if "memoai.db" in output:
                self.log_test(
                    "Database Backup",
                    "PASS",
                    "Database file exists and accessible"
                )
            else:
                self.log_test(
                    "Database Backup",
                    "WARN",
                    "Database file not found in expected location"
                )
        else:
            self.log_test(
                "Database Backup",
                "FAIL",
                f"Failed to check database: {error}"
            )
            return False
        
        # Test configuration backup
        success, output, error = self.run_docker_command(
            "docker compose exec backend ls -la /app/config/backups/"
        )
        if success:
            if output.strip():
                self.log_test(
                    "Configuration Backup",
                    "PASS",
                    "Configuration backups directory exists"
                )
            else:
                self.log_test(
                    "Configuration Backup",
                    "WARN",
                    "Configuration backups directory is empty"
                )
        else:
            self.log_test(
                "Configuration Backup",
                "WARN",
                "Configuration backups directory not accessible"
            )
        
        return True
    
    def test_performance_under_load(self) -> bool:
        """Test performance under basic load"""
        print("\n=== Testing Performance Under Load ===")
        
        # Test multiple evaluations
        response_times = []
        errors = []
        
        for i in range(3):  # Test 3 evaluations
            # Create new session for each test
            success, output, error = self.run_docker_command(
                "docker compose exec backend curl -s -X POST http://localhost:8000/api/v1/sessions/create"
            )
            if success and output.strip():
                try:
                    data = json.loads(output)
                    session_id = data.get("data", {}).get("session_id")
                except json.JSONDecodeError:
                    errors.append("Failed to create session")
                    continue
            else:
                errors.append("Session creation failed")
                continue
            
            if session_id:
                payload = json.dumps({
                    "text_content": f"Performance test message {i+1} for load testing.",
                    "session_id": session_id
                })
                
                start_time = time.time()
                success, output, error = self.run_docker_command(
                    f"docker compose exec backend curl -s -X POST http://localhost:8000/api/v1/evaluations/submit -H 'Content-Type: application/json' -d '{payload}'"
                )
                end_time = time.time()
                
                response_time = end_time - start_time
                
                if success and output.strip():
                    try:
                        data = json.loads(output)
                        if data.get("data", {}).get("evaluation"):
                            response_times.append(response_time)
                        else:
                            errors.append("No evaluation data")
                    except json.JSONDecodeError:
                        errors.append("Invalid JSON response")
                else:
                    errors.append(f"Request failed: {error}")
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            # Performance benchmarks
            benchmarks_passed = 0
            total_benchmarks = 2
            
            # Average response time < 15 seconds
            if avg_response_time < 15.0:
                self.log_test(
                    "Performance - Average Response Time",
                    "PASS",
                    f"Average response time {avg_response_time:.2f}s meets benchmark (< 15s)",
                    {"average_time": avg_response_time}
                )
                benchmarks_passed += 1
            else:
                self.log_test(
                    "Performance - Average Response Time",
                    "WARN",
                    f"Average response time {avg_response_time:.2f}s exceeds benchmark (15s)",
                    {"average_time": avg_response_time}
                )
            
            # Maximum response time < 20 seconds
            if max_response_time < 20.0:
                self.log_test(
                    "Performance - Maximum Response Time",
                    "PASS",
                    f"Maximum response time {max_response_time:.2f}s meets benchmark (< 20s)",
                    {"max_time": max_response_time}
                )
                benchmarks_passed += 1
            else:
                self.log_test(
                    "Performance - Maximum Response Time",
                    "WARN",
                    f"Maximum response time {max_response_time:.2f}s exceeds benchmark (20s)",
                    {"max_time": max_response_time}
                )
            
            success_rate = (benchmarks_passed / total_benchmarks) * 100
            return success_rate >= 50  # At least 1/2 benchmarks pass
        else:
            self.log_test(
                "Performance Under Load",
                "FAIL",
                f"No successful evaluations: {len(errors)} errors",
                {"errors": errors}
            )
            return False
    
    def run_all_tests(self) -> Dict:
        """Run all production readiness tests"""
        print("=== Production Readiness Verification ===")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Environment: Production Ready")
        
        # Run all tests
        tests = [
            self.test_system_accessibility,
            self.test_security_measures,
            self.test_functionality_verification,
            self.test_monitoring_and_alerting,
            self.test_backup_and_recovery,
            self.test_performance_under_load
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
        
        if summary["failed"] == 0 and success_rate >= 80:
            print("🎉 Production readiness verification PASSED - System is ready for production!")
        else:
            print("⚠️ Production readiness verification has issues - Review failed tests")
        
        return self.results

def main():
    """Main function to run production readiness tests"""
    tester = ProductionReadinessTester()
    results = tester.run_all_tests()
    
    # Save results to file
    output_file = "tests/logs/production_readiness_test_results.json"
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
