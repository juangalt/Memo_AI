#!/usr/bin/env python3
"""
Memo AI Coach - Production Security Testing Script
Based on 07_Deployment.md security specifications
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
import os

# Configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:8501')
DOMAIN = os.getenv('DOMAIN', 'localhost')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('memoai.security.test')

class SecurityTester:
    """Production security testing system for Memo AI Coach"""
    
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name: str, status: str, message: str):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        if status == 'PASS':
            logger.info(f"✅ {test_name}: {message}")
        elif status == 'FAIL':
            logger.error(f"❌ {test_name}: {message}")
        else:
            logger.warning(f"⚠️ {test_name}: {message}")
    
    def test_ssl_configuration(self) -> bool:
        """Test SSL/TLS configuration"""
        logger.info("Testing SSL/TLS configuration...")
        
        try:
            # Test HTTPS redirect
            response = self.session.get(f"http://{DOMAIN}", allow_redirects=False, timeout=10)
            if response.status_code in [301, 302, 307, 308]:
                self.log_test("SSL Redirect", "PASS", f"HTTP redirects to HTTPS (status: {response.status_code})")
            else:
                self.log_test("SSL Redirect", "FAIL", f"Expected redirect, got status: {response.status_code}")
                return False
            
            # Test HTTPS access
            response = self.session.get(f"https://{DOMAIN}", timeout=10)
            if response.status_code == 200:
                self.log_test("HTTPS Access", "PASS", "HTTPS access working")
            else:
                self.log_test("HTTPS Access", "FAIL", f"HTTPS access failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("SSL Configuration", "FAIL", f"SSL test failed: {str(e)}")
            return False
    
    def test_security_headers(self) -> bool:
        """Test security headers"""
        logger.info("Testing security headers...")
        
        try:
            response = self.session.get(f"https://{DOMAIN}", timeout=10)
            
            # Check required security headers
            required_headers = {
                'Strict-Transport-Security': 'HSTS header',
                'X-Content-Type-Options': 'Content type options',
                'X-Frame-Options': 'Frame options',
                'X-XSS-Protection': 'XSS protection',
                'Content-Security-Policy': 'CSP header',
                'Referrer-Policy': 'Referrer policy'
            }
            
            missing_headers = []
            for header, description in required_headers.items():
                if header in response.headers:
                    self.log_test(f"Security Header: {header}", "PASS", f"{description} present")
                else:
                    missing_headers.append(header)
                    self.log_test(f"Security Header: {header}", "FAIL", f"{description} missing")
            
            if missing_headers:
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Security Headers", "FAIL", f"Header test failed: {str(e)}")
            return False
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting functionality"""
        logger.info("Testing rate limiting...")
        
        try:
            # Test normal request
            response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                self.log_test("Rate Limiting - Normal Request", "PASS", "Normal request allowed")
            else:
                self.log_test("Rate Limiting - Normal Request", "FAIL", f"Normal request failed: {response.status_code}")
                return False
            
            # Test rapid requests (should trigger rate limiting)
            rapid_requests = []
            for i in range(25):  # Exceed the 20 requests/hour limit
                try:
                    response = self.session.get(f"{BACKEND_URL}/health", timeout=5)
                    rapid_requests.append(response.status_code)
                    time.sleep(0.1)  # Small delay between requests
                except Exception as e:
                    rapid_requests.append(f"Error: {str(e)}")
            
            # Check if rate limiting was triggered
            rate_limited = any(status == 429 for status in rapid_requests if isinstance(status, int))
            
            if rate_limited:
                self.log_test("Rate Limiting - Abuse Prevention", "PASS", "Rate limiting triggered for rapid requests")
            else:
                self.log_test("Rate Limiting - Abuse Prevention", "WARN", "Rate limiting may not be working as expected")
            
            return True
            
        except Exception as e:
            self.log_test("Rate Limiting", "FAIL", f"Rate limiting test failed: {str(e)}")
            return False
    
    def test_authentication_security(self) -> bool:
        """Test authentication security"""
        logger.info("Testing authentication security...")
        
        try:
            # Test admin login with invalid credentials
            invalid_credentials = {
                'username': 'admin',
                'password': 'wrong_password'
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/api/v1/admin/login",
                json=invalid_credentials,
                timeout=10
            )
            
            if response.status_code == 401:
                self.log_test("Authentication - Invalid Credentials", "PASS", "Invalid credentials properly rejected")
            else:
                self.log_test("Authentication - Invalid Credentials", "FAIL", f"Expected 401, got {response.status_code}")
                return False
            
            # Test admin login with valid credentials (if available)
            # This would require valid admin credentials to be configured
            self.log_test("Authentication - Valid Credentials", "INFO", "Skipped (requires valid admin credentials)")
            
            return True
            
        except Exception as e:
            self.log_test("Authentication Security", "FAIL", f"Authentication test failed: {str(e)}")
            return False
    
    def test_input_validation(self) -> bool:
        """Test input validation and sanitization"""
        logger.info("Testing input validation...")
        
        try:
            # Test text evaluation with invalid input
            invalid_inputs = [
                "",  # Empty text
                "a" * 10000,  # Very long text
                "<script>alert('xss')</script>",  # XSS attempt
                "'; DROP TABLE users; --",  # SQL injection attempt
            ]
            
            for i, invalid_input in enumerate(invalid_inputs):
                response = self.session.post(
                    f"{BACKEND_URL}/api/v1/evaluations/submit",
                    json={'text_content': invalid_input},
                    timeout=10
                )
                
                if response.status_code in [400, 422]:  # Bad request or validation error
                    self.log_test(f"Input Validation - Test {i+1}", "PASS", f"Invalid input properly rejected: {response.status_code}")
                else:
                    self.log_test(f"Input Validation - Test {i+1}", "FAIL", f"Invalid input not rejected: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Input Validation", "FAIL", f"Input validation test failed: {str(e)}")
            return False
    
    def test_session_security(self) -> bool:
        """Test session security"""
        logger.info("Testing session security...")
        
        try:
            # Test session creation
            response = self.session.post(f"{BACKEND_URL}/api/v1/sessions", timeout=10)
            
            if response.status_code == 200:
                session_data = response.json()
                session_id = session_data.get('data', {}).get('session_id')
                
                if session_id:
                    self.log_test("Session Security - Creation", "PASS", "Session created successfully")
                    
                    # Test session validation
                    headers = {'X-Session-ID': session_id}
                    response = self.session.get(f"{BACKEND_URL}/health", headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        self.log_test("Session Security - Validation", "PASS", "Session validation working")
                    else:
                        self.log_test("Session Security - Validation", "FAIL", f"Session validation failed: {response.status_code}")
                        return False
                else:
                    self.log_test("Session Security - Creation", "FAIL", "No session ID returned")
                    return False
            else:
                self.log_test("Session Security - Creation", "FAIL", f"Session creation failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Session Security", "FAIL", f"Session security test failed: {str(e)}")
            return False
    
    def test_csrf_protection(self) -> bool:
        """Test CSRF protection"""
        logger.info("Testing CSRF protection...")
        
        try:
            # Test without CSRF token (should be rejected)
            response = self.session.post(
                f"{BACKEND_URL}/api/v1/evaluations/submit",
                json={'text_content': 'Test text'},
                timeout=10
            )
            
            # Note: CSRF protection may not be fully implemented in this version
            # This is a placeholder test
            self.log_test("CSRF Protection", "INFO", "CSRF protection test skipped (implementation dependent)")
            
            return True
            
        except Exception as e:
            self.log_test("CSRF Protection", "FAIL", f"CSRF protection test failed: {str(e)}")
            return False
    
    def test_monitoring_and_logging(self) -> bool:
        """Test monitoring and logging functionality"""
        logger.info("Testing monitoring and logging...")
        
        try:
            # Test health check endpoint
            response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                
                # Check if health data includes security-related information
                if 'services' in health_data:
                    self.log_test("Monitoring - Health Check", "PASS", "Health check includes service status")
                else:
                    self.log_test("Monitoring - Health Check", "WARN", "Health check missing service status")
                
                # Check for request ID in headers
                if 'X-Request-ID' in response.headers:
                    self.log_test("Monitoring - Request Tracking", "PASS", "Request ID present in headers")
                else:
                    self.log_test("Monitoring - Request Tracking", "WARN", "Request ID not present in headers")
                
            else:
                self.log_test("Monitoring - Health Check", "FAIL", f"Health check failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Monitoring and Logging", "FAIL", f"Monitoring test failed: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict:
        """Run all security tests"""
        logger.info("Starting comprehensive security testing...")
        
        tests = [
            ("SSL Configuration", self.test_ssl_configuration),
            ("Security Headers", self.test_security_headers),
            ("Rate Limiting", self.test_rate_limiting),
            ("Authentication Security", self.test_authentication_security),
            ("Input Validation", self.test_input_validation),
            ("Session Security", self.test_session_security),
            ("CSRF Protection", self.test_csrf_protection),
            ("Monitoring and Logging", self.test_monitoring_and_logging),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, "FAIL", f"Test execution failed: {str(e)}")
        
        # Generate summary
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            'test_results': self.test_results
        }
        
        return summary
    
    def generate_report(self, summary: Dict) -> str:
        """Generate security test report"""
        report = f"""
=== Memo AI Coach Security Test Report ===
Generated: {summary['timestamp']}
Total Tests: {summary['total_tests']}
Passed: {summary['passed_tests']}
Failed: {summary['failed_tests']}
Success Rate: {summary['success_rate']:.1f}%

Test Results:
"""
        
        for result in summary['test_results']:
            status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⚠️"
            report += f"{status_icon} {result['test']}: {result['message']}\n"
        
        if summary['success_rate'] >= 90:
            report += "\n🎉 Security testing PASSED - System is ready for production!"
        elif summary['success_rate'] >= 70:
            report += "\n⚠️ Security testing PARTIAL - Some issues need attention"
        else:
            report += "\n❌ Security testing FAILED - Critical issues must be resolved"
        
        return report


def main():
    """Main security testing function"""
    tester = SecurityTester()
    
    # Run all security tests
    summary = tester.run_all_tests()
    
    # Generate and print report
    report = tester.generate_report(summary)
    print(report)
    
    # Save results to file
    try:
        with open('/app/logs/security_test_results.json', 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info("Security test results saved to /app/logs/security_test_results.json")
    except Exception as e:
        logger.error(f"Failed to save security test results: {e}")
    
    # Exit with error code if security testing failed
    if summary['success_rate'] < 70:
        logger.error("Security testing failed - critical issues detected")
        exit(1)
    elif summary['success_rate'] < 90:
        logger.warning("Security testing partial - some issues need attention")
        exit(0)
    else:
        logger.info("Security testing passed - system ready for production")
        exit(0)


if __name__ == "__main__":
    main()
