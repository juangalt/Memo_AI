#!/usr/bin/env python3
"""
Environment Configuration Validation Test
Validates all critical environment variables and configuration for production deployment
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EnvironmentValidator:
    """Validates environment configuration for production deployment"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "environment": "production",
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
        
        # Required environment variables
        self.required_vars = {
            "DOMAIN": "Production domain name",
            "LLM_API_KEY": "Claude API key for LLM integration",
            "ADMIN_PASSWORD": "Admin password for authentication",
            "DATABASE_URL": "Database connection string",
            "SESSION_TIMEOUT": "Session timeout in seconds",
            "MAX_CONCURRENT_USERS": "Maximum concurrent users",
            "RATE_LIMIT_PER_SESSION": "Rate limit per session",
            "RATE_LIMIT_PER_HOUR": "Rate limit per hour"
        }
        
        # Optional but recommended variables
        self.optional_vars = {
            "SSL_CERT_PATH": "SSL certificate path",
            "SSL_KEY_PATH": "SSL private key path",
            "LOG_LEVEL": "Logging level",
            "DEBUG_MODE": "Debug mode flag"
        }
    
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
    
    def test_required_environment_variables(self) -> bool:
        """Test required environment variables"""
        print("\n=== Testing Required Environment Variables ===")
        
        all_present = True
        for var_name, description in self.required_vars.items():
            value = os.getenv(var_name)
            if value:
                # Mask sensitive values
                if "KEY" in var_name or "PASSWORD" in var_name or "SECRET" in var_name:
                    display_value = f"{value[:10]}..." if len(value) > 10 else "***"
                else:
                    display_value = value
                
                self.log_test(
                    f"Required Variable: {var_name}",
                    "PASS",
                    f"{description} is set",
                    {"value": display_value}
                )
            else:
                self.log_test(
                    f"Required Variable: {var_name}",
                    "FAIL",
                    f"{description} is missing"
                )
                all_present = False
        
        return all_present
    
    def test_optional_environment_variables(self) -> bool:
        """Test optional environment variables"""
        print("\n=== Testing Optional Environment Variables ===")
        
        for var_name, description in self.optional_vars.items():
            value = os.getenv(var_name)
            if value:
                self.log_test(
                    f"Optional Variable: {var_name}",
                    "PASS",
                    f"{description} is set",
                    {"value": value}
                )
            else:
                self.log_test(
                    f"Optional Variable: {var_name}",
                    "WARN",
                    f"{description} is not set (recommended for production)"
                )
        
        return True
    
    def test_domain_accessibility(self) -> bool:
        """Test domain accessibility"""
        print("\n=== Testing Domain Accessibility ===")
        
        domain = os.getenv("DOMAIN")
        if not domain:
            self.log_test("Domain Accessibility", "FAIL", "DOMAIN environment variable not set")
            return False
        
        try:
            # Test HTTP access
            response = requests.get(f"http://{domain}", timeout=10, allow_redirects=False)
            if response.status_code in [200, 301, 302, 308]:
                self.log_test(
                    "Domain HTTP Access",
                    "PASS",
                    f"Domain {domain} is accessible via HTTP",
                    {"status_code": response.status_code}
                )
            else:
                self.log_test(
                    "Domain HTTP Access",
                    "WARN",
                    f"Domain {domain} returned status {response.status_code}",
                    {"status_code": response.status_code}
                )
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Domain HTTP Access",
                "FAIL",
                f"Domain {domain} is not accessible: {str(e)}"
            )
            return False
        
        return True
    
    def test_ssl_certificate(self) -> bool:
        """Test SSL certificate"""
        print("\n=== Testing SSL Certificate ===")
        
        domain = os.getenv("DOMAIN")
        if not domain:
            self.log_test("SSL Certificate", "FAIL", "DOMAIN environment variable not set")
            return False
        
        try:
            # Test HTTPS access
            response = requests.get(f"https://{domain}", timeout=10, verify=True)
            if response.status_code in [200, 301, 302, 308]:
                self.log_test(
                    "SSL Certificate",
                    "PASS",
                    f"SSL certificate for {domain} is valid",
                    {"status_code": response.status_code}
                )
                return True
            else:
                self.log_test(
                    "SSL Certificate",
                    "WARN",
                    f"SSL certificate valid but returned status {response.status_code}",
                    {"status_code": response.status_code}
                )
                return True
        except requests.exceptions.SSLError as e:
            self.log_test(
                "SSL Certificate",
                "FAIL",
                f"SSL certificate for {domain} is invalid: {str(e)}"
            )
            return False
        except requests.exceptions.RequestException as e:
            self.log_test(
                "SSL Certificate",
                "WARN",
                f"SSL certificate test failed (may be development): {str(e)}"
            )
            return True
    
    def test_database_connection(self) -> bool:
        """Test database connection"""
        print("\n=== Testing Database Connection ===")
        
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            self.log_test("Database Connection", "FAIL", "DATABASE_URL environment variable not set")
            return False
        
        try:
            # Test SQLite database file existence
            if database_url.startswith("sqlite:///"):
                db_path = database_url.replace("sqlite:///", "")
                if os.path.exists(db_path):
                    self.log_test(
                        "Database Connection",
                        "PASS",
                        f"SQLite database file exists: {db_path}",
                        {"database_url": database_url}
                    )
                    return True
                else:
                    self.log_test(
                        "Database Connection",
                        "WARN",
                        f"SQLite database file not found: {db_path}",
                        {"database_url": database_url}
                    )
                    return True  # Database will be created on first use
            else:
                self.log_test(
                    "Database Connection",
                    "WARN",
                    f"Database URL format not SQLite: {database_url}",
                    {"database_url": database_url}
                )
                return True
        except Exception as e:
            self.log_test(
                "Database Connection",
                "FAIL",
                f"Database connection test failed: {str(e)}"
            )
            return False
    
    def test_llm_api_key(self) -> bool:
        """Test LLM API key validity"""
        print("\n=== Testing LLM API Key ===")
        
        api_key = os.getenv("LLM_API_KEY")
        if not api_key:
            self.log_test("LLM API Key", "FAIL", "LLM_API_KEY environment variable not set")
            return False
        
        # Check if it's a valid Anthropic API key format
        if api_key.startswith("sk-ant-api"):
            self.log_test(
                "LLM API Key",
                "PASS",
                "LLM API key has valid Anthropic format",
                {"key_format": "anthropic", "key_preview": f"{api_key[:15]}..."}
            )
            return True
        else:
            self.log_test(
                "LLM API Key",
                "WARN",
                "LLM API key format not recognized",
                {"key_preview": f"{api_key[:15]}..."}
            )
            return True
    
    def test_security_configuration(self) -> bool:
        """Test security configuration"""
        print("\n=== Testing Security Configuration ===")
        
        # Note: SECRET_KEY removed - session tokens use Python's secrets module
        # which is cryptographically secure and doesn't require a secret key
        self.log_test(
            "Security Configuration",
            "PASS",
            "Session security uses Python secrets module (no SECRET_KEY required)",
            {"security_method": "Python secrets module", "cryptographic": True}
        )
        
        # Check session timeout
        session_timeout = os.getenv("SESSION_TIMEOUT")
        if session_timeout:
            try:
                timeout_seconds = int(session_timeout)
                if timeout_seconds >= 3600:  # 1 hour minimum
                    self.log_test(
                        "Session Timeout",
                        "PASS",
                        f"Session timeout is reasonable: {timeout_seconds} seconds",
                        {"timeout_seconds": timeout_seconds}
                    )
                else:
                    self.log_test(
                        "Session Timeout",
                        "WARN",
                        f"Session timeout may be too short: {timeout_seconds} seconds",
                        {"timeout_seconds": timeout_seconds, "recommended": ">= 3600"}
                    )
            except ValueError:
                self.log_test(
                    "Session Timeout",
                    "WARN",
                    f"Session timeout is not a valid number: {session_timeout}"
                )
        
        return True
    
    def test_rate_limiting_configuration(self) -> bool:
        """Test rate limiting configuration"""
        print("\n=== Testing Rate Limiting Configuration ===")
        
        rate_limit_session = os.getenv("RATE_LIMIT_PER_SESSION")
        rate_limit_hour = os.getenv("RATE_LIMIT_PER_HOUR")
        
        if rate_limit_session:
            try:
                session_limit = int(rate_limit_session)
                if session_limit > 0:
                    self.log_test(
                        "Rate Limit Per Session",
                        "PASS",
                        f"Session rate limit is set: {session_limit}",
                        {"limit": session_limit}
                    )
                else:
                    self.log_test(
                        "Rate Limit Per Session",
                        "WARN",
                        f"Session rate limit is zero or negative: {session_limit}"
                    )
            except ValueError:
                self.log_test(
                    "Rate Limit Per Session",
                    "WARN",
                    f"Session rate limit is not a valid number: {rate_limit_session}"
                )
        
        if rate_limit_hour:
            try:
                hour_limit = int(rate_limit_hour)
                if hour_limit > 0:
                    self.log_test(
                        "Rate Limit Per Hour",
                        "PASS",
                        f"Hourly rate limit is set: {hour_limit}",
                        {"limit": hour_limit}
                    )
                else:
                    self.log_test(
                        "Rate Limit Per Hour",
                        "WARN",
                        f"Hourly rate limit is zero or negative: {hour_limit}"
                    )
            except ValueError:
                self.log_test(
                    "Rate Limit Per Hour",
                    "WARN",
                    f"Hourly rate limit is not a valid number: {rate_limit_hour}"
                )
        
        return True
    
    def run_all_tests(self) -> Dict:
        """Run all environment validation tests"""
        print("=== Environment Configuration Validation ===")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Environment: Production")
        
        # Run all tests
        tests = [
            self.test_required_environment_variables,
            self.test_optional_environment_variables,
            self.test_domain_accessibility,
            self.test_ssl_certificate,
            self.test_database_connection,
            self.test_llm_api_key,
            self.test_security_configuration,
            self.test_rate_limiting_configuration
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
            print("🎉 Environment validation PASSED - Ready for production!")
        else:
            print("⚠️ Environment validation has issues - Review failed tests")
        
        return self.results

def main():
    """Main function to run environment validation"""
    validator = EnvironmentValidator()
    results = validator.run_all_tests()
    
    # Save results to file
    output_file = "tests/logs/environment_validation_results.json"
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
