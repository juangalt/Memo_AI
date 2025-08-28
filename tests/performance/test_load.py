#!/usr/bin/env python3
"""
Performance and Load Tests
Comprehensive performance testing for production deployment
"""

import os
import sys
import json
import time
import threading
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv
import concurrent.futures

# Load environment variables
load_dotenv()

class PerformanceTester:
    """Tests system performance under various load conditions"""
    
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
            },
            "performance_metrics": {
                "response_times": [],
                "throughput": [],
                "error_rates": [],
                "resource_usage": []
            }
        }
        
        # Test configuration
        self.concurrent_users = 5
        self.test_duration = 30  # seconds
        self.requests_per_user = 10
        
        # Test data
        self.test_texts = [
            "This is a short test message for performance evaluation.",
            "This is a medium-length test message that contains more content for performance testing of the evaluation system.",
            "This is a longer test message that contains significantly more content to test the performance of the text evaluation system under various load conditions."
        ]
    
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
    
    def test_single_evaluation(self, test_text: str) -> Tuple[bool, float, str]:
        """Test a single evaluation and return success, response_time, error"""
        try:
            # Create session
            success, output, error = self.run_docker_command(
                "docker compose exec backend curl -s -X POST http://localhost:8000/api/v1/sessions/create"
            )
            
            if not success or not output.strip():
                return False, 0, f"Session creation failed: {error}"
            
            session_data = json.loads(output)
            session_id = session_data.get("data", {}).get("session_id")
            
            if not session_id:
                return False, 0, "No session ID in response"
            
            # Submit evaluation
            payload = json.dumps({
                "text_content": test_text,
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
                        return True, response_time, ""
                    else:
                        return False, response_time, "No evaluation data in response"
                except json.JSONDecodeError:
                    return False, response_time, "Invalid JSON response"
            else:
                return False, response_time, f"Evaluation failed: {error}"
                
        except Exception as e:
            return False, 0, str(e)
    
    def test_response_time_benchmarks(self) -> bool:
        """Test response time benchmarks"""
        print("\n=== Testing Response Time Benchmarks ===")
        
        response_times = []
        errors = []
        
        # Test with different text lengths
        for i, test_text in enumerate(self.test_texts):
            print(f"Testing text {i+1}/{len(self.test_texts)} (length: {len(test_text)} chars)")
            
            success, response_time, error = self.test_single_evaluation(test_text)
            
            if success:
                response_times.append(response_time)
                self.results["performance_metrics"]["response_times"].append({
                    "text_length": len(test_text),
                    "response_time": response_time
                })
            else:
                errors.append(error)
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            # Check benchmarks
            benchmarks_passed = 0
            total_benchmarks = 3
            
            # API response time benchmark: < 2 seconds for 95% of requests
            if avg_response_time < 2.0:
                self.log_test(
                    "Response Time - Average",
                    "PASS",
                    f"Average response time {avg_response_time:.2f}s meets benchmark (< 2s)",
                    {"average_time": avg_response_time}
                )
                benchmarks_passed += 1
            else:
                self.log_test(
                    "Response Time - Average",
                    "WARN",
                    f"Average response time {avg_response_time:.2f}s exceeds benchmark (2s)",
                    {"average_time": avg_response_time}
                )
            
            # LLM evaluation benchmark: < 15 seconds per evaluation
            if max_response_time < 15.0:
                self.log_test(
                    "Response Time - Maximum",
                    "PASS",
                    f"Maximum response time {max_response_time:.2f}s meets benchmark (< 15s)",
                    {"max_time": max_response_time}
                )
                benchmarks_passed += 1
            else:
                self.log_test(
                    "Response Time - Maximum",
                    "WARN",
                    f"Maximum response time {max_response_time:.2f}s exceeds benchmark (15s)",
                    {"max_time": max_response_time}
                )
            
            # Consistency benchmark: max/min ratio < 3
            if max_response_time > 0:
                ratio = max_response_time / min_response_time
                if ratio < 3.0:
                    self.log_test(
                        "Response Time - Consistency",
                        "PASS",
                        f"Response time consistency good (ratio: {ratio:.2f})",
                        {"max_min_ratio": ratio}
                    )
                    benchmarks_passed += 1
                else:
                    self.log_test(
                        "Response Time - Consistency",
                        "WARN",
                        f"Response time consistency poor (ratio: {ratio:.2f})",
                        {"max_min_ratio": ratio}
                    )
            
            success_rate = (benchmarks_passed / total_benchmarks) * 100
            if success_rate >= 66:  # At least 2/3 benchmarks pass
                return True
            else:
                return False
        else:
            self.log_test(
                "Response Time Benchmarks",
                "FAIL",
                f"No successful evaluations: {len(errors)} errors",
                {"errors": errors}
            )
            return False
    
    def test_concurrent_users(self) -> bool:
        """Test system under concurrent user load"""
        print(f"\n=== Testing Concurrent Users ({self.concurrent_users} users) ===")
        
        def user_workload(user_id: int) -> Tuple[int, List[float], List[str]]:
            """Simulate a user workload"""
            response_times = []
            errors = []
            
            for i in range(self.requests_per_user):
                test_text = self.test_texts[i % len(self.test_texts)]
                success, response_time, error = self.test_single_evaluation(test_text)
                
                if success:
                    response_times.append(response_time)
                else:
                    errors.append(error)
                
                # Small delay between requests
                time.sleep(0.5)
            
            return user_id, response_times, errors
        
        # Run concurrent users
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrent_users) as executor:
            futures = [executor.submit(user_workload, i) for i in range(self.concurrent_users)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # Analyze results
        all_response_times = []
        all_errors = []
        successful_users = 0
        
        for user_id, response_times, errors in results:
            if response_times:
                all_response_times.extend(response_times)
                successful_users += 1
            all_errors.extend(errors)
        
        if all_response_times:
            avg_response_time = sum(all_response_times) / len(all_response_times)
            total_requests = len(all_response_times)
            error_rate = len(all_errors) / (total_requests + len(all_errors)) * 100
            
            # Check concurrent user benchmarks
            benchmarks_passed = 0
            total_benchmarks = 3
            
            # Error rate benchmark: < 5%
            if error_rate < 5.0:
                self.log_test(
                    "Concurrent Users - Error Rate",
                    "PASS",
                    f"Error rate {error_rate:.1f}% meets benchmark (< 5%)",
                    {"error_rate": error_rate, "total_errors": len(all_errors)}
                )
                benchmarks_passed += 1
            else:
                self.log_test(
                    "Concurrent Users - Error Rate",
                    "FAIL",
                    f"Error rate {error_rate:.1f}% exceeds benchmark (5%)",
                    {"error_rate": error_rate, "total_errors": len(all_errors)}
                )
            
            # Response time under load benchmark: < 3 seconds average
            if avg_response_time < 3.0:
                self.log_test(
                    "Concurrent Users - Response Time",
                    "PASS",
                    f"Average response time {avg_response_time:.2f}s meets benchmark (< 3s)",
                    {"average_time": avg_response_time, "total_requests": total_requests}
                )
                benchmarks_passed += 1
            else:
                self.log_test(
                    "Concurrent Users - Response Time",
                    "WARN",
                    f"Average response time {avg_response_time:.2f}s exceeds benchmark (3s)",
                    {"average_time": avg_response_time, "total_requests": total_requests}
                )
            
            # User success rate benchmark: > 80% users successful
            user_success_rate = (successful_users / self.concurrent_users) * 100
            if user_success_rate >= 80.0:
                self.log_test(
                    "Concurrent Users - Success Rate",
                    "PASS",
                    f"User success rate {user_success_rate:.1f}% meets benchmark (> 80%)",
                    {"successful_users": successful_users, "total_users": self.concurrent_users}
                )
                benchmarks_passed += 1
            else:
                self.log_test(
                    "Concurrent Users - Success Rate",
                    "FAIL",
                    f"User success rate {user_success_rate:.1f}% below benchmark (80%)",
                    {"successful_users": successful_users, "total_users": self.concurrent_users}
                )
            
            # Store metrics
            self.results["performance_metrics"]["throughput"].append({
                "concurrent_users": self.concurrent_users,
                "total_requests": total_requests,
                "total_time": total_time,
                "requests_per_second": total_requests / total_time if total_time > 0 else 0
            })
            
            self.results["performance_metrics"]["error_rates"].append({
                "concurrent_users": self.concurrent_users,
                "error_rate": error_rate,
                "total_errors": len(all_errors)
            })
            
            success_rate = (benchmarks_passed / total_benchmarks) * 100
            return success_rate >= 66  # At least 2/3 benchmarks pass
        else:
            self.log_test(
                "Concurrent Users",
                "FAIL",
                f"No successful requests: {len(all_errors)} errors",
                {"errors": all_errors}
            )
            return False
    
    def test_resource_usage(self) -> bool:
        """Test system resource usage under load"""
        print("\n=== Testing Resource Usage ===")
        
        # Get initial resource usage
        success, output, error = self.run_docker_command("docker stats --no-stream --format json")
        if not success:
            self.log_test(
                "Resource Usage",
                "FAIL",
                f"Failed to get initial resource usage: {error}"
            )
            return False
        
        initial_stats = []
        for line in output.strip().split('\n'):
            if line.strip():
                try:
                    initial_stats.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        # Run load test
        print("Running load test for resource monitoring...")
        load_start = time.time()
        
        # Create multiple evaluation requests
        def load_worker():
            for _ in range(5):  # 5 requests per worker
                test_text = self.test_texts[0]
                self.test_single_evaluation(test_text)
                time.sleep(1)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(load_worker) for _ in range(3)]
            concurrent.futures.wait(futures, timeout=30)
        
        load_end = time.time()
        
        # Get final resource usage
        success, output, error = self.run_docker_command("docker stats --no-stream --format json")
        if not success:
            self.log_test(
                "Resource Usage",
                "FAIL",
                f"Failed to get final resource usage: {error}"
            )
            return False
        
        final_stats = []
        for line in output.strip().split('\n'):
            if line.strip():
                try:
                    final_stats.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        # Analyze resource usage
        if initial_stats and final_stats:
            # Calculate memory usage
            initial_memory = sum(float(stat.get('MemUsage', '0MiB').replace('MiB', '')) for stat in initial_stats)
            final_memory = sum(float(stat.get('MemUsage', '0MiB').replace('MiB', '')) for stat in final_stats)
            memory_increase = final_memory - initial_memory
            
            # Calculate CPU usage
            initial_cpu = sum(float(stat.get('CPUPerc', '0%').replace('%', '')) for stat in initial_stats)
            final_cpu = sum(float(stat.get('CPUPerc', '0%').replace('%', '')) for stat in final_stats)
            cpu_increase = final_cpu - initial_cpu
            
            # Store metrics
            self.results["performance_metrics"]["resource_usage"].append({
                "initial_memory_mb": initial_memory,
                "final_memory_mb": final_memory,
                "memory_increase_mb": memory_increase,
                "initial_cpu_percent": initial_cpu,
                "final_cpu_percent": final_cpu,
                "cpu_increase_percent": cpu_increase,
                "load_duration_seconds": load_end - load_start
            })
            
            # Check resource benchmarks
            benchmarks_passed = 0
            total_benchmarks = 2
            
            # Memory usage benchmark: < 200MB total
            if final_memory < 200:
                self.log_test(
                    "Resource Usage - Memory",
                    "PASS",
                    f"Memory usage {final_memory:.1f}MB meets benchmark (< 200MB)",
                    {"memory_mb": final_memory, "increase_mb": memory_increase}
                )
                benchmarks_passed += 1
            else:
                self.log_test(
                    "Resource Usage - Memory",
                    "WARN",
                    f"Memory usage {final_memory:.1f}MB exceeds benchmark (200MB)",
                    {"memory_mb": final_memory, "increase_mb": memory_increase}
                )
            
            # CPU usage benchmark: < 50% total
            if final_cpu < 50:
                self.log_test(
                    "Resource Usage - CPU",
                    "PASS",
                    f"CPU usage {final_cpu:.1f}% meets benchmark (< 50%)",
                    {"cpu_percent": final_cpu, "increase_percent": cpu_increase}
                )
                benchmarks_passed += 1
            else:
                self.log_test(
                    "Resource Usage - CPU",
                    "WARN",
                    f"CPU usage {final_cpu:.1f}% exceeds benchmark (50%)",
                    {"cpu_percent": final_cpu, "increase_percent": cpu_increase}
                )
            
            success_rate = (benchmarks_passed / total_benchmarks) * 100
            return success_rate >= 50  # At least 1/2 benchmarks pass
        else:
            self.log_test(
                "Resource Usage",
                "FAIL",
                "No resource statistics available",
                {"initial_stats_count": len(initial_stats), "final_stats_count": len(final_stats)}
            )
            return False
    
    def run_all_tests(self) -> Dict:
        """Run all performance tests"""
        print("=== Performance and Load Tests ===")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Environment: Local Docker Containers")
        print(f"Concurrent Users: {self.concurrent_users}")
        print(f"Test Duration: {self.test_duration} seconds")
        
        # Run all tests
        tests = [
            self.test_response_time_benchmarks,
            self.test_concurrent_users,
            self.test_resource_usage
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
            print("🎉 Performance tests PASSED - System meets performance requirements!")
        else:
            print("⚠️ Performance tests have issues - Review failed tests")
        
        return self.results

def main():
    """Main function to run performance tests"""
    tester = PerformanceTester()
    results = tester.run_all_tests()
    
    # Save results to file
    output_file = "tests/logs/performance_test_results.json"
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
