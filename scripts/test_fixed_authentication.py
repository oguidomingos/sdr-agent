#!/usr/bin/env python3
"""
Comprehensive authentication test suite for fixed implementation
"""
import requests
import json
import time
import sys

class AuthenticationTester:
    def __init__(self, api_url):
        self.api_url = api_url.rstrip('/')
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'details': details
        })
        
        if details and not success:
            print(f"   Details: {details}")
    
    def test_health_endpoint(self):
        """Test health endpoint and environment validation"""
        print("\n🔍 Testing Health Endpoint...")
        
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check basic health
                if data.get('status') == 'healthy':
                    self.log_test("Health Check", True, "API is healthy")
                else:
                    self.log_test("Health Check", False, f"API status: {data.get('status')}")
                
                # Check Supabase connection
                supabase_status = data.get('supabase', 'unknown')
                if supabase_status == 'connected':
                    self.log_test("Supabase Connection", True, "Connected successfully")
                else:
                    self.log_test("Supabase Connection", False, f"Status: {supabase_status}")
                
                # Check environment variables
                env_vars = data.get('environment_vars', {})
                for var, status in env_vars.items():
                    self.log_test(f"Env Var {var}", status == "✅", f"Status: {status}")
                
            else:
                self.log_test("Health Endpoint", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Health Endpoint", False, f"Request failed: {e}")
    
    def test_user_login(self, email, password):
        """Test user login with real credentials"""
        print(f"\n🔐 Testing Login for {email}...")
        
        try:
            login_data = {
                "email": email,
                "password": password
            }
            
            response = requests.post(f"{self.api_url}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Validate token response format
                required_fields = ['access_token', 'token_type', 'expires_in', 'user_id', 'email']
                missing_fields = [field for field in required_fields if field not in token_data]
                
                if not missing_fields:
                    self.log_test("Login Response Format", True, "All required fields present")
                    
                    # Validate email matches
                    if token_data.get('email') == email:
                        self.log_test("Login Email Match", True, f"Email: {email}")
                    else:
                        self.log_test("Login Email Match", False, f"Expected {email}, got {token_data.get('email')}")
                    
                    return token_data.get('access_token')
                else:
                    self.log_test("Login Response Format", False, f"Missing fields: {missing_fields}")
                    
            elif response.status_code == 401:
                self.log_test("Login Authentication", False, "Invalid credentials")
            else:
                self.log_test("Login Request", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Login Request", False, f"Request failed: {e}")
        
        return None
    
    def test_get_user_data(self, token, expected_email, expected_first_name, expected_last_name):
        """Test /auth/me endpoint with real user data validation"""
        print(f"\n👤 Testing User Data Retrieval...")
        
        if not token:
            self.log_test("User Data", False, "No token available")
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Validate user data format
                required_fields = ['id', 'email', 'first_name', 'last_name', 'status', 'plan']
                missing_fields = [field for field in required_fields if field not in user_data]
                
                if not missing_fields:
                    self.log_test("User Data Format", True, "All required fields present")
                else:
                    self.log_test("User Data Format", False, f"Missing fields: {missing_fields}")
                
                # Validate email (most critical test)
                actual_email = user_data.get('email')
                if actual_email == expected_email:
                    self.log_test("Real Email Data", True, f"Email: {actual_email}")
                else:
                    self.log_test("Real Email Data", False, f"Expected {expected_email}, got {actual_email}")
                
                # Check for mock data indicators
                if actual_email == 'user@example.com':
                    self.log_test("Mock Data Check", False, "Still returning mock email")
                else:
                    self.log_test("Mock Data Check", True, "No mock email detected")
                
                # Validate first name
                actual_first_name = user_data.get('first_name')
                if actual_first_name == expected_first_name:
                    self.log_test("Real First Name", True, f"Name: {actual_first_name}")
                else:
                    self.log_test("Real First Name", False, f"Expected {expected_first_name}, got {actual_first_name}")
                
                # Check for mock name indicators
                if actual_first_name == 'Demo':
                    self.log_test("Mock Name Check", False, "Still returning 'Demo' as first name")
                else:
                    self.log_test("Mock Name Check", True, "No mock name detected")
                
                # Validate last name
                actual_last_name = user_data.get('last_name')
                if actual_last_name == expected_last_name:
                    self.log_test("Real Last Name", True, f"Last name: {actual_last_name}")
                else:
                    self.log_test("Real Last Name", False, f"Expected {expected_last_name}, got {actual_last_name}")
                
                return user_data
                
            elif response.status_code == 401:
                self.log_test("User Data Auth", False, "Token invalid or expired")
            elif response.status_code == 404:
                self.log_test("User Data", False, "User not found in database")
            else:
                self.log_test("User Data Request", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("User Data Request", False, f"Request failed: {e}")
        
        return None
    
    def test_clients_endpoint(self, token):
        """Test clients endpoint with authentication"""
        print(f"\n🏢 Testing Clients Endpoint...")
        
        if not token:
            self.log_test("Clients Endpoint", False, "No token available")
            return
        
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.api_url}/clients/", headers=headers, timeout=10)
            
            if response.status_code == 200:
                clients_data = response.json()
                
                # Validate response format
                if 'items' in clients_data and 'total' in clients_data:
                    self.log_test("Clients Response Format", True, "Correct format")
                    
                    total_clients = clients_data.get('total', 0)
                    self.log_test("Clients Count", True, f"Total clients: {total_clients}")
                    
                    # List clients
                    for client in clients_data.get('items', []):
                        client_name = client.get('name', 'Unknown')
                        client_domain = client.get('domain', 'Unknown')
                        print(f"   - {client_name} ({client_domain})")
                        
                else:
                    self.log_test("Clients Response Format", False, "Invalid response format")
                    
            elif response.status_code == 401:
                self.log_test("Clients Auth", False, "Authentication required")
            else:
                self.log_test("Clients Request", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Clients Request", False, f"Request failed: {e}")
    
    def run_comprehensive_test(self, email, password, expected_first_name, expected_last_name):
        """Run complete authentication test suite"""
        print("🚀 Starting Comprehensive Authentication Test")
        print("=" * 60)
        print(f"API URL: {self.api_url}")
        print(f"Test User: {email}")
        print(f"Expected Name: {expected_first_name} {expected_last_name}")
        
        # Test 1: Health check
        self.test_health_endpoint()
        
        # Test 2: User login
        token = self.test_user_login(email, password)
        
        # Test 3: Get user data
        user_data = self.test_get_user_data(token, email, expected_first_name, expected_last_name)
        
        # Test 4: Test clients endpoint
        self.test_clients_endpoint(token)
        
        # Summary
        self.print_summary()
        
        return self.is_all_tests_passed()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        # List failed tests
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['message']}")
        else:
            print(f"\n🎉 All tests passed!")
    
    def is_all_tests_passed(self):
        """Check if all tests passed"""
        return all(result['success'] for result in self.test_results)

def main():
    """Main test function"""
    # Test configuration
    api_urls = [
        "https://sdr-agent-five.vercel.app/api",  # Current working API
        "http://localhost:8000/api",  # Local development
    ]
    
    test_user = {
        "email": "oguigodomingos@gmail.com",
        "password": "180121430",
        "expected_first_name": "Guigo",
        "expected_last_name": "Domingos"
    }
    
    print("🧪 Fixed Authentication Test Suite")
    print("=" * 70)
    
    for api_url in api_urls:
        print(f"\n🌐 Testing API: {api_url}")
        print("-" * 50)
        
        tester = AuthenticationTester(api_url)
        
        try:
            success = tester.run_comprehensive_test(
                test_user["email"],
                test_user["password"],
                test_user["expected_first_name"],
                test_user["expected_last_name"]
            )
            
            if success:
                print(f"\n🎯 API {api_url} - ALL TESTS PASSED!")
                print("✅ Authentication is working correctly with real data")
                return True
            else:
                print(f"\n⚠️  API {api_url} - Some tests failed")
                
        except Exception as e:
            print(f"\n❌ API {api_url} - Test suite failed: {e}")
    
    print(f"\n❌ No API passed all tests")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)