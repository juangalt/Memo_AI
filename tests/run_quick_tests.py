#!/usr/bin/env python3
"""
Quick Production Test Runner for Memo AI Coach
Runs Phase 8 production tests (excluding performance) for faster validation
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Tuple

class QuickTestRunner:
    """Runs production tests quickly (excluding performance tests)"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "environment": "production",
            "test_suites": [],
            "summary": {
                "total_suites": 0,
                "passed_suites": 0,
                "failed_suites": 0,
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "warnings": 0
            }
        }
        
        # Test suite definitions (excluding performance)
        self.test_suites = [
            {
                "name": "Environment Configuration Validation",
                "script": "tests/config/test_environment.py",
                "description": "Validates all environment variables, domain accessibility, SSL certificates, database connections, and LLM API keys",
                "phase": "8.2"
            },
            {
                "name": "Critical System Tests",
                "script": "tests/integration/test_critical_system_local.py",
                "description": "Tests container status, API health endpoints, session management, text evaluation workflow, database operations, LLM integration, and error handling",
                "phase": "8.3"
            },
            {
                "name": "Production Readiness Verification",
                "script": "tests/integration/test_production_readiness.py",
                "description": "Tests system accessibility, security measures, complete functionality, monitoring, backup/recovery, and performance under load",
                "phase": "8.5"
            }
        ]
    
    def run_test_suite(self, suite: Dict) -> Dict:
        """Run a single test suite and capture results"""
        print(f"\n{'='*80}")
        print(f"🧪 Running {suite['name']} (Phase {suite['phase']})")
        print(f"📝 {suite['description']}")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        try:
            # Run the test script
            result = subprocess.run(
                [sys.executable, suite['script']],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per suite
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Parse the output to extract test results
            output_lines = result.stdout.split('\n')
            test_results = self.parse_test_output(output_lines)
            
            suite_result = {
                "name": suite['name'],
                "phase": suite['phase'],
                "script": suite['script'],
                "execution_time": execution_time,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "test_results": test_results,
                "status": "PASS" if result.returncode == 0 else "FAIL"
            }
            
            # Print summary
            if result.returncode == 0:
                print(f"✅ {suite['name']} - PASSED ({execution_time:.2f}s)")
                if test_results:
                    print(f"   Tests: {test_results.get('passed', 0)} passed, {test_results.get('failed', 0)} failed, {test_results.get('warnings', 0)} warnings")
            else:
                print(f"❌ {suite['name']} - FAILED ({execution_time:.2f}s)")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")
            
            return suite_result
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {suite['name']} - TIMEOUT (exceeded 5 minutes)")
            return {
                "name": suite['name'],
                "phase": suite['phase'],
                "script": suite['script'],
                "execution_time": 300,
                "return_code": -1,
                "stdout": "",
                "stderr": "Test suite timed out after 5 minutes",
                "test_results": {},
                "status": "TIMEOUT"
            }
        except Exception as e:
            print(f"💥 {suite['name']} - ERROR: {str(e)}")
            return {
                "name": suite['name'],
                "phase": suite['phase'],
                "script": suite['script'],
                "execution_time": 0,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "test_results": {},
                "status": "ERROR"
            }
    
    def parse_test_output(self, output_lines: List[str]) -> Dict:
        """Parse test output to extract test counts and results"""
        test_results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "success_rate": 0.0
        }
        
        for line in output_lines:
            line = line.strip()
            
            # Look for test summary patterns
            if "Total Tests:" in line:
                try:
                    test_results["total"] = int(line.split(":")[1].strip())
                except (ValueError, IndexError):
                    pass
            elif "Passed:" in line:
                try:
                    test_results["passed"] = int(line.split(":")[1].strip())
                except (ValueError, IndexError):
                    pass
            elif "Failed:" in line:
                try:
                    test_results["failed"] = int(line.split(":")[1].strip())
                except (ValueError, IndexError):
                    pass
            elif "Warnings:" in line:
                try:
                    test_results["warnings"] = int(line.split(":")[1].strip())
                except (ValueError, IndexError):
                    pass
            elif "Success Rate:" in line:
                try:
                    test_results["success_rate"] = float(line.split(":")[1].strip().replace("%", ""))
                except (ValueError, IndexError):
                    pass
        
        return test_results
    
    def run_all_tests(self) -> Dict:
        """Run all quick test suites"""
        print("🚀 Memo AI Coach - Quick Production Test Suite")
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Running Phase 8 Production Tests (Quick Mode - No Performance)")
        print(f"{'='*80}")
        
        total_start_time = time.time()
        
        for suite in self.test_suites:
            suite_result = self.run_test_suite(suite)
            self.results["test_suites"].append(suite_result)
            
            # Update summary
            self.results["summary"]["total_suites"] += 1
            if suite_result["status"] == "PASS":
                self.results["summary"]["passed_suites"] += 1
            else:
                self.results["summary"]["failed_suites"] += 1
            
            # Update test counts
            test_results = suite_result["test_results"]
            self.results["summary"]["total_tests"] += test_results.get("total", 0)
            self.results["summary"]["passed_tests"] += test_results.get("passed", 0)
            self.results["summary"]["failed_tests"] += test_results.get("failed", 0)
            self.results["summary"]["warnings"] += test_results.get("warnings", 0)
        
        total_execution_time = time.time() - total_start_time
        
        # Generate final summary
        self.print_final_summary(total_execution_time)
        
        # Save results
        self.save_results()
        
        return self.results
    
    def print_final_summary(self, total_time: float):
        """Print comprehensive final summary"""
        print(f"\n{'='*80}")
        print("📊 QUICK PRODUCTION TEST SUITE SUMMARY")
        print(f"{'='*80}")
        
        summary = self.results["summary"]
        
        # Suite summary
        print(f"🧪 Test Suites:")
        print(f"   Total: {summary['total_suites']}")
        print(f"   Passed: {summary['passed_suites']}")
        print(f"   Failed: {summary['failed_suites']}")
        print(f"   Success Rate: {(summary['passed_suites']/summary['total_suites']*100):.1f}%")
        
        # Test summary
        print(f"\n🔍 Individual Tests:")
        print(f"   Total: {summary['total_tests']}")
        print(f"   Passed: {summary['passed_tests']}")
        print(f"   Failed: {summary['failed_tests']}")
        print(f"   Warnings: {summary['warnings']}")
        if summary['total_tests'] > 0:
            print(f"   Success Rate: {(summary['passed_tests']/summary['total_tests']*100):.1f}%")
        
        # Timing
        print(f"\n⏱️  Execution Time: {total_time:.2f} seconds")
        
        # Overall status
        if summary['failed_suites'] == 0 and summary['failed_tests'] == 0:
            print(f"\n🎉 ALL TESTS PASSED - System is production ready!")
            print(f"✅ Phase 8 Quick Validation: COMPLETE")
            print(f"💡 Note: Performance tests skipped for speed. Run full suite for complete validation.")
        elif summary['failed_suites'] == 0:
            print(f"\n⚠️  All test suites passed but some individual tests failed")
            print(f"🔍 Review failed tests for details")
        else:
            print(f"\n❌ Some test suites failed")
            print(f"🔍 Review failed suites for details")
        
        print(f"{'='*80}")
    
    def save_results(self):
        """Save test results to JSON file"""
        output_file = "tests/logs/quick_production_test_results.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📁 Results saved to: {output_file}")

def main():
    """Main entry point"""
    runner = QuickTestRunner()
    results = runner.run_all_tests()
    
    # Return appropriate exit code
    if results["summary"]["failed_suites"] == 0 and results["summary"]["failed_tests"] == 0:
        print("\n✅ Quick production test suite completed successfully!")
        return 0
    else:
        print("\n❌ Quick production test suite completed with failures!")
        return 1

if __name__ == "__main__":
    exit(main())
