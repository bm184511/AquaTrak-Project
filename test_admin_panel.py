#!/usr/bin/env python3
"""
Admin Panel Test Script
Tests the comprehensive admin panel functionality
"""

import requests
import json
import time
from datetime import datetime
import sys
import os

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@aquatrak.com"
ADMIN_PASSWORD = "admin123"

class AdminPanelTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_login(self):
        """Test admin login"""
        try:
            self.log("Testing admin login...")
            response = self.session.post(f"{BASE_URL}/api/v1/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                if self.access_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                    self.log("Admin login successful", "SUCCESS")
                    return True
                else:
                    self.log("No access token received", "ERROR")
                    return False
            else:
                self.log(f"Login failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Login test failed: {str(e)}", "ERROR")
            return False
    
    def test_admin_dashboard(self):
        """Test admin dashboard endpoint"""
        try:
            self.log("Testing admin dashboard...")
            response = self.session.get(f"{BASE_URL}/api/v1/admin/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    dashboard_data = data.get("data", {})
                    
                    # Check required fields
                    required_fields = ["users", "organizations", "analyses", "alerts", "system", "modules"]
                    missing_fields = [field for field in required_fields if field not in dashboard_data]
                    
                    if not missing_fields:
                        self.log("Admin dashboard test passed", "SUCCESS")
                        self.log(f"Dashboard data: {json.dumps(dashboard_data, indent=2)}")
                        return True
                    else:
                        self.log(f"Missing dashboard fields: {missing_fields}", "ERROR")
                        return False
                else:
                    self.log(f"Dashboard returned error status: {data.get('message')}", "ERROR")
                    return False
            else:
                self.log(f"Dashboard request failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Dashboard test failed: {str(e)}", "ERROR")
            return False
    
    def test_user_management(self):
        """Test user management endpoints"""
        try:
            self.log("Testing user management...")
            
            # Test get users
            response = self.session.get(f"{BASE_URL}/api/v1/admin/users")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log("Get users test passed", "SUCCESS")
                else:
                    self.log(f"Get users failed: {data.get('message')}", "ERROR")
                    return False
            else:
                self.log(f"Get users request failed: {response.status_code}", "ERROR")
                return False
            
            # Test create user
            new_user_data = {
                "username": "testuser",
                "email": "testuser@example.com",
                "password": "testpass123",
                "full_name": "Test User",
                "roles": ["analyst"],
                "country_code": "US",
                "language": "en"
            }
            
            response = self.session.post(f"{BASE_URL}/api/v1/admin/users", json=new_user_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log("Create user test passed", "SUCCESS")
                    user_id = data.get("data", {}).get("id")
                    
                    # Test update user
                    update_data = {"full_name": "Updated Test User"}
                    response = self.session.put(f"{BASE_URL}/api/v1/admin/users/{user_id}", json=update_data)
                    if response.status_code == 200:
                        self.log("Update user test passed", "SUCCESS")
                    else:
                        self.log(f"Update user failed: {response.status_code}", "ERROR")
                    
                    # Test delete user
                    response = self.session.delete(f"{BASE_URL}/api/v1/admin/users/{user_id}")
                    if response.status_code == 200:
                        self.log("Delete user test passed", "SUCCESS")
                    else:
                        self.log(f"Delete user failed: {response.status_code}", "ERROR")
                        
                else:
                    self.log(f"Create user failed: {data.get('message')}", "ERROR")
                    return False
            else:
                self.log(f"Create user request failed: {response.status_code}", "ERROR")
                return False
                
            return True
            
        except Exception as e:
            self.log(f"User management test failed: {str(e)}", "ERROR")
            return False
    
    def test_system_monitoring(self):
        """Test system monitoring endpoints"""
        try:
            self.log("Testing system monitoring...")
            
            # Test system status
            response = self.session.get(f"{BASE_URL}/api/v1/admin/system/status")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log("System status test passed", "SUCCESS")
                else:
                    self.log(f"System status failed: {data.get('message')}", "ERROR")
                    return False
            else:
                self.log(f"System status request failed: {response.status_code}", "ERROR")
                return False
            
            # Test system performance
            response = self.session.get(f"{BASE_URL}/api/v1/admin/system/performance")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log("System performance test passed", "SUCCESS")
                else:
                    self.log(f"System performance failed: {data.get('message')}", "ERROR")
                    return False
            else:
                self.log(f"System performance request failed: {response.status_code}", "ERROR")
                return False
            
            # Test system logs
            response = self.session.get(f"{BASE_URL}/api/v1/admin/system/logs")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log("System logs test passed", "SUCCESS")
                else:
                    self.log(f"System logs failed: {data.get('message')}", "ERROR")
                    return False
            else:
                self.log(f"System logs request failed: {response.status_code}", "ERROR")
                return False
                
            return True
            
        except Exception as e:
            self.log(f"System monitoring test failed: {str(e)}", "ERROR")
            return False
    
    def test_data_management(self):
        """Test data management endpoints"""
        try:
            self.log("Testing data management...")
            
            # Test data sources
            response = self.session.get(f"{BASE_URL}/api/v1/admin/data/sources")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log("Data sources test passed", "SUCCESS")
                else:
                    self.log(f"Data sources failed: {data.get('message')}", "ERROR")
                    return False
            else:
                self.log(f"Data sources request failed: {response.status_code}", "ERROR")
                return False
            
            # Test file uploads
            response = self.session.get(f"{BASE_URL}/api/v1/admin/data/uploads")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log("File uploads test passed", "SUCCESS")
                else:
                    self.log(f"File uploads failed: {data.get('message')}", "ERROR")
                    return False
            else:
                self.log(f"File uploads request failed: {response.status_code}", "ERROR")
                return False
                
            return True
            
        except Exception as e:
            self.log(f"Data management test failed: {str(e)}", "ERROR")
            return False
    
    def test_analytics(self):
        """Test analytics endpoints"""
        try:
            self.log("Testing analytics...")
            
            # Test usage analytics
            response = self.session.get(f"{BASE_URL}/api/v1/admin/analytics/usage?period=7d")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log("Usage analytics test passed", "SUCCESS")
                else:
                    self.log(f"Usage analytics failed: {data.get('message')}", "ERROR")
                    return False
            else:
                self.log(f"Usage analytics request failed: {response.status_code}", "ERROR")
                return False
            
            # Test module analytics
            response = self.session.get(f"{BASE_URL}/api/v1/admin/analytics/modules")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log("Module analytics test passed", "SUCCESS")
                else:
                    self.log(f"Module analytics failed: {data.get('message')}", "ERROR")
                    return False
            else:
                self.log(f"Module analytics request failed: {response.status_code}", "ERROR")
                return False
                
            return True
            
        except Exception as e:
            self.log(f"Analytics test failed: {str(e)}", "ERROR")
            return False
    
    def test_organizations(self):
        """Test organization management endpoints"""
        try:
            self.log("Testing organization management...")
            
            response = self.session.get(f"{BASE_URL}/api/v1/admin/organizations")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log("Organization management test passed", "SUCCESS")
                    return True
                else:
                    self.log(f"Organization management failed: {data.get('message')}", "ERROR")
                    return False
            else:
                self.log(f"Organization management request failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Organization management test failed: {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all admin panel tests"""
        self.log("Starting Admin Panel Tests", "INFO")
        self.log("=" * 50)
        
        tests = [
            ("Admin Login", self.test_login),
            ("Admin Dashboard", self.test_admin_dashboard),
            ("User Management", self.test_user_management),
            ("System Monitoring", self.test_system_monitoring),
            ("Data Management", self.test_data_management),
            ("Analytics", self.test_analytics),
            ("Organization Management", self.test_organizations),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            self.log(f"\nRunning {test_name} test...")
            try:
                if test_func():
                    self.log(f"✅ {test_name} test PASSED", "SUCCESS")
                    passed += 1
                else:
                    self.log(f"❌ {test_name} test FAILED", "ERROR")
                    failed += 1
            except Exception as e:
                self.log(f"❌ {test_name} test FAILED with exception: {str(e)}", "ERROR")
                failed += 1
        
        # Summary
        self.log("\n" + "=" * 50)
        self.log("ADMIN PANEL TEST SUMMARY", "INFO")
        self.log("=" * 50)
        self.log(f"Total Tests: {len(tests)}")
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {failed}")
        self.log(f"Success Rate: {(passed/len(tests)*100):.1f}%")
        
        if failed == 0:
            self.log("🎉 All admin panel tests passed!", "SUCCESS")
            return True
        else:
            self.log(f"⚠️ {failed} test(s) failed. Please check the logs above.", "WARNING")
            return False

def main():
    """Main function"""
    print("🛡️ AquaTrak Admin Panel Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding properly")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Please ensure the server is running on http://localhost:8000")
        sys.exit(1)
    
    # Run tests
    tester = AdminPanelTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Admin Panel is fully functional!")
        sys.exit(0)
    else:
        print("\n❌ Admin Panel has issues that need to be addressed.")
        sys.exit(1)

if __name__ == "__main__":
    main() 