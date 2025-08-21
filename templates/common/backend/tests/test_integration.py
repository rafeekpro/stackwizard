"""
Integration tests for CORS, API endpoints, and static files.
These tests ensure proper frontend-backend communication.
"""

import requests
import time
from typing import Dict, Any
import sys

# Configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_test_header(test_name: str):
    """Print a formatted test header."""
    print(f"\n{BOLD}Testing: {test_name}{RESET}")
    print("-" * 50)

def print_result(passed: bool, message: str):
    """Print a colored test result."""
    if passed:
        print(f"{GREEN}✓ {message}{RESET}")
    else:
        print(f"{RED}✗ {message}{RESET}")

class TestCORS:
    """Test CORS configuration."""
    
    def test_cors_preflight(self):
        """Test CORS preflight requests."""
        print_test_header("CORS Preflight Requests")
        
        endpoints = ["/api/v1/users/me", "/api/health", "/health"]
        all_passed = True
        
        for endpoint in endpoints:
            try:
                response = requests.options(
                    f"{BASE_URL}{endpoint}",
                    headers={
                        "Origin": FRONTEND_URL,
                        "Access-Control-Request-Method": "GET",
                        "Access-Control-Request-Headers": "content-type"
                    }
                )
                
                has_cors = "access-control-allow-origin" in response.headers
                status_ok = response.status_code in [200, 204]
                
                if has_cors and status_ok:
                    print_result(True, f"Preflight {endpoint}: Status {response.status_code}, CORS headers present")
                else:
                    print_result(False, f"Preflight {endpoint}: Status {response.status_code}, CORS: {has_cors}")
                    all_passed = False
                    
            except Exception as e:
                print_result(False, f"Preflight {endpoint}: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_cors_actual_request(self):
        """Test actual CORS requests."""
        print_test_header("CORS Actual Requests")
        
        endpoints = ["/health", "/api/health"]
        all_passed = True
        
        for endpoint in endpoints:
            try:
                response = requests.get(
                    f"{BASE_URL}{endpoint}",
                    headers={"Origin": FRONTEND_URL}
                )
                
                has_cors = "access-control-allow-origin" in response.headers
                cors_value = response.headers.get("access-control-allow-origin", "")
                status_ok = response.status_code == 200
                
                if has_cors and status_ok:
                    print_result(True, f"GET {endpoint}: Status {response.status_code}, CORS: {cors_value}")
                else:
                    print_result(False, f"GET {endpoint}: Status {response.status_code}, CORS: {cors_value or 'Missing'}")
                    all_passed = False
                    
            except Exception as e:
                print_result(False, f"GET {endpoint}: {str(e)}")
                all_passed = False
        
        return all_passed

class TestAPIEndpoints:
    """Test API endpoint availability."""
    
    def test_health_endpoints(self):
        """Test health check endpoints."""
        print_test_header("Health Check Endpoints")
        
        endpoints = [
            ("/health", ["status", "service", "version"]),
            ("/api/health", ["status", "service", "version"])
        ]
        
        all_passed = True
        
        for endpoint, required_fields in endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    missing_fields = [f for f in required_fields if f not in data]
                    
                    if not missing_fields:
                        print_result(True, f"{endpoint}: Status 200, All fields present")
                    else:
                        print_result(False, f"{endpoint}: Missing fields: {missing_fields}")
                        all_passed = False
                else:
                    print_result(False, f"{endpoint}: Status {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                print_result(False, f"{endpoint}: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_api_docs(self):
        """Test API documentation endpoints."""
        print_test_header("API Documentation")
        
        endpoints = ["/docs", "/redoc"]
        all_passed = True
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}")
                
                if response.status_code == 200:
                    print_result(True, f"{endpoint}: Available (Status 200)")
                else:
                    print_result(False, f"{endpoint}: Status {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                print_result(False, f"{endpoint}: {str(e)}")
                all_passed = False
        
        return all_passed

class TestStaticFiles:
    """Test static file handling."""
    
    def test_favicon(self):
        """Test favicon endpoint."""
        print_test_header("Static Files")
        
        try:
            response = requests.get(f"{BASE_URL}/favicon.ico")
            
            if response.status_code == 200:
                print_result(True, f"/favicon.ico: Available (Status 200)")
                return True
            else:
                print_result(False, f"/favicon.ico: Status {response.status_code}")
                return False
                
        except Exception as e:
            print_result(False, f"/favicon.ico: {str(e)}")
            return False

def wait_for_backend():
    """Wait for backend to be ready."""
    print(f"{YELLOW}Waiting for backend to start...{RESET}")
    
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print(f"{GREEN}Backend is ready!{RESET}")
                return True
        except:
            pass
        
        if i < max_attempts - 1:
            time.sleep(1)
            sys.stdout.write(".")
            sys.stdout.flush()
    
    print(f"\n{RED}Backend failed to start after {max_attempts} seconds{RESET}")
    return False

def main():
    """Run all integration tests."""
    print(f"\n{BOLD}=== Integration Tests ==={RESET}")
    print(f"Backend URL: {BASE_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")
    
    # Wait for backend
    if not wait_for_backend():
        sys.exit(1)
    
    # Run tests
    test_results = []
    
    # CORS tests
    cors_tests = TestCORS()
    test_results.append(("CORS Preflight", cors_tests.test_cors_preflight()))
    test_results.append(("CORS Actual", cors_tests.test_cors_actual_request()))
    
    # API tests
    api_tests = TestAPIEndpoints()
    test_results.append(("Health Endpoints", api_tests.test_health_endpoints()))
    test_results.append(("API Documentation", api_tests.test_api_docs()))
    
    # Static file tests
    static_tests = TestStaticFiles()
    test_results.append(("Static Files", static_tests.test_favicon()))
    
    # Summary
    print(f"\n{BOLD}=== Test Summary ==={RESET}")
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = f"{GREEN}PASSED{RESET}" if result else f"{RED}FAILED{RESET}"
        print(f"{test_name}: {status}")
    
    print(f"\n{BOLD}Total: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        print(f"{GREEN}All tests passed! ✨{RESET}")
        sys.exit(0)
    else:
        print(f"{RED}Some tests failed. Please check the errors above.{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()