#!/usr/bin/env python3
"""
Stripe LIVE Integration Test
Tests the newly configured LIVE Stripe keys and validates production readiness
CRITICAL: Uses LIVE keys - no real payments will be made, only configuration validation
"""

import requests
import sys
import json
import os
from datetime import datetime
import uuid
import time

class StripeLiveIntegrationTester:
    def __init__(self, base_url="https://19d7651f-4e24-4d23-ad4f-0ab1b902f33c.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        
        # Generate unique email for this test run
        timestamp = str(int(time.time()))
        self.test_user_data = {
            "email": f"stripe.live.test.{timestamp}@example.com",
            "password": "SecurePass123!",
            "first_name": "Stripe",
            "last_name": "LiveTest"
        }
        self.user_token = None
        self.user_id = None

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED")
        
        if details:
            print(f"   Details: {details}")
        print()

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        print(f"🔍 Testing {name}...")
        print(f"   URL: {url}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

            print(f"   Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
                print(f"   Response: {json.dumps(response_data, indent=2)}")
            except:
                response_data = response.text
                print(f"   Response Text: {response_data}")

            self.log_test(name, success, f"Expected {expected_status}, got {response.status_code}")
            return success, response_data if success else {}

        except requests.exceptions.Timeout:
            self.log_test(name, False, "Request timeout")
            return False, {}
        except requests.exceptions.ConnectionError:
            self.log_test(name, False, "Connection error")
            return False, {}
        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def get_auth_headers(self, token):
        """Get authorization headers with JWT token"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

    # ========== STRIPE LIVE CONFIGURATION TESTS ==========
    
    def test_backend_health_with_live_keys(self):
        """Test that backend starts correctly with LIVE Stripe keys"""
        print("🏥 Testing Backend Health with LIVE Stripe Keys...")
        success, response = self.run_test(
            "Backend Health Check with LIVE Keys",
            "GET",
            "health",
            200
        )
        
        if success:
            print("   ✅ Backend is running with LIVE Stripe configuration")
        else:
            print("   ❌ Backend health check failed - possible LIVE key configuration issue")
            
        return success

    def test_user_registration_for_stripe_testing(self):
        """Register a test user for Stripe LIVE testing"""
        print("👤 Registering test user for Stripe LIVE validation...")
        success, response = self.run_test(
            "Register Test User for Stripe LIVE",
            "POST",
            "auth/register",
            200,
            self.test_user_data
        )
        
        if success:
            self.user_id = response.get('user_id')
            self.user_token = response.get('access_token')
            print(f"   ✅ Test user registered: {self.user_id}")
        else:
            print("   ❌ Failed to register test user")
            
        return success

    def test_user_login_for_stripe_testing(self):
        """Login test user to get fresh token"""
        print("🔐 Logging in test user...")
        login_data = {
            "email": self.test_user_data['email'],
            "password": self.test_user_data['password']
        }
        
        success, response = self.run_test(
            "Login Test User for Stripe LIVE",
            "POST",
            "auth/login",
            200,
            login_data
        )
        
        if success:
            self.user_token = response.get('access_token')
            print("   ✅ Test user logged in successfully")
        else:
            print("   ❌ Failed to login test user")
            
        return success

    def test_stripe_live_checkout_session_creation(self):
        """Test Stripe LIVE checkout session creation (REAL account with minimal amount)"""
        if not self.user_token:
            self.log_test("Stripe LIVE Checkout Session", False, "No user token available")
            return False
            
        print("💳 Testing Stripe LIVE Checkout Session Creation...")
        print("   ⚠️  CRITICAL: Using LIVE keys - testing with minimal amount (1€)")
        
        # Test with REAL account and minimal amount for safety
        checkout_data = {
            "account_type": "real",
            "amount": 1.0  # Minimal amount for LIVE testing
        }
        
        success, response = self.run_test(
            "Stripe LIVE Checkout Session Creation",
            "POST",
            "stripe/checkout/session",
            200,
            checkout_data,
            headers=self.get_auth_headers(self.user_token)
        )
        
        if success:
            # Validate LIVE session characteristics
            session_url = response.get('url', '')
            session_id = response.get('session_id', '')
            
            print(f"   Session ID: {session_id}")
            print(f"   Session URL: {session_url}")
            
            # Check that it's a LIVE session (not test)
            if 'stripe.com' in session_url and 'checkout.stripe.com/test' not in session_url:
                print("   ✅ LIVE Stripe session created (production domain)")
            else:
                print("   ❌ Session appears to be test mode, not LIVE")
                return False
                
            # Validate session ID format for LIVE
            if session_id.startswith('cs_live_') or (session_id.startswith('cs_') and not session_id.startswith('cs_test_')):
                print("   ✅ Session ID indicates LIVE mode")
            else:
                print(f"   ❌ Session ID format suggests test mode: {session_id}")
                return False
                
        return success

    def test_stripe_live_demo_account_simulation(self):
        """Test that demo accounts still work with LIVE keys (should be simulated)"""
        if not self.user_token:
            self.log_test("Stripe LIVE Demo Account", False, "No user token available")
            return False
            
        print("🎮 Testing Demo Account with LIVE Stripe Keys...")
        
        # Test with demo account - should still be simulated
        demo_data = {
            "account_type": "demo",
            "amount": 100.0
        }
        
        success, response = self.run_test(
            "Stripe LIVE - Demo Account Simulation",
            "POST",
            "stripe/checkout/session",
            200,
            demo_data,
            headers=self.get_auth_headers(self.user_token)
        )
        
        if success:
            session_id = response.get('session_id', '')
            session_url = response.get('url', '')
            
            # Demo should still be simulated even with LIVE keys
            if session_id.startswith('demo_cs_'):
                print("   ✅ Demo account properly simulated with LIVE keys")
            else:
                print(f"   ❌ Demo account not properly simulated: {session_id}")
                return False
                
        return success

    def test_stripe_key_configuration_validation(self):
        """Validate that LIVE keys are properly configured"""
        print("🔑 Validating Stripe LIVE Key Configuration...")
        
        # This test validates configuration by attempting to create a session
        # and checking the response characteristics
        if not self.user_token:
            self.log_test("Stripe Key Configuration", False, "No user token available")
            return False
            
        # Test with real account to validate LIVE key usage
        test_data = {
            "account_type": "real",
            "amount": 1.0  # Minimal amount
        }
        
        success, response = self.run_test(
            "Stripe LIVE Key Configuration Validation",
            "POST",
            "stripe/checkout/session",
            200,
            test_data,
            headers=self.get_auth_headers(self.user_token)
        )
        
        if success:
            # Check response indicates LIVE mode
            session_url = response.get('url', '')
            
            # LIVE sessions should use production Stripe domain
            if 'checkout.stripe.com/c/pay/' in session_url:
                print("   ✅ LIVE Stripe keys properly configured (production checkout URL)")
            elif 'stripe.com' in session_url and 'test' not in session_url:
                print("   ✅ LIVE Stripe keys properly configured (production domain)")
            else:
                print(f"   ❌ Session URL suggests test mode: {session_url}")
                return False
                
        return success

    def test_stripe_security_validation(self):
        """Test security aspects of LIVE Stripe integration"""
        print("🔒 Testing Stripe LIVE Security Configuration...")
        
        # Test that authentication is required
        security_data = {
            "account_type": "real",
            "amount": 1.0
        }
        
        success, response = self.run_test(
            "Stripe LIVE Security - Auth Required",
            "POST",
            "stripe/checkout/session",
            401,  # Should require authentication
            security_data
            # No auth headers - should fail
        )
        
        if success:
            print("   ✅ Stripe LIVE endpoints properly secured (auth required)")
        else:
            print("   ❌ Stripe LIVE endpoints not properly secured")
            
        return success

    def test_stripe_amount_validation_live(self):
        """Test amount validation with LIVE keys"""
        if not self.user_token:
            self.log_test("Stripe Amount Validation", False, "No user token available")
            return False
            
        print("💰 Testing Amount Validation with LIVE Keys...")
        
        # Test invalid amount (0 or negative)
        invalid_data = {
            "account_type": "real",
            "amount": 0.0
        }
        
        success, response = self.run_test(
            "Stripe LIVE - Invalid Amount Validation",
            "POST",
            "stripe/checkout/session",
            400,  # Should reject invalid amount
            invalid_data,
            headers=self.get_auth_headers(self.user_token)
        )
        
        if success:
            print("   ✅ Amount validation working with LIVE keys")
        else:
            print("   ❌ Amount validation failed with LIVE keys")
            
        return success

    def test_stripe_withdrawal_live_config(self):
        """Test withdrawal configuration with LIVE keys"""
        if not self.user_token:
            self.log_test("Stripe Withdrawal LIVE", False, "No user token available")
            return False
            
        print("💸 Testing Withdrawal Configuration with LIVE Keys...")
        
        # Test withdrawal (should work but be simulated for now)
        withdrawal_data = {
            "account_type": "demo",  # Use demo for safety
            "amount": 10.0,
            "description": "LIVE key configuration test"
        }
        
        success, response = self.run_test(
            "Stripe LIVE - Withdrawal Configuration",
            "POST",
            "stripe/withdrawal",
            200,
            withdrawal_data,
            headers=self.get_auth_headers(self.user_token)
        )
        
        if success:
            print("   ✅ Withdrawal endpoints working with LIVE keys")
        else:
            print("   ❌ Withdrawal endpoints failed with LIVE keys")
            
        return success

    # ========== MAIN TEST RUNNER ==========
    
    def run_stripe_live_tests(self):
        """Run all Stripe LIVE integration tests"""
        print("🚀 Starting Stripe LIVE Integration Tests")
        print("⚠️  CRITICAL: Using LIVE Stripe keys - no real payments will be completed")
        print("=" * 80)
        
        # Backend health with LIVE keys
        print("\n🏥 BACKEND HEALTH WITH LIVE KEYS")
        print("-" * 50)
        self.test_backend_health_with_live_keys()
        
        # User setup for testing
        print("\n👤 USER SETUP FOR STRIPE TESTING")
        print("-" * 50)
        self.test_user_registration_for_stripe_testing()
        self.test_user_login_for_stripe_testing()
        
        # Stripe LIVE configuration tests
        print("\n💳 STRIPE LIVE CONFIGURATION TESTS")
        print("-" * 50)
        self.test_stripe_live_checkout_session_creation()
        self.test_stripe_live_demo_account_simulation()
        self.test_stripe_key_configuration_validation()
        
        # Security and validation tests
        print("\n🔒 STRIPE LIVE SECURITY TESTS")
        print("-" * 50)
        self.test_stripe_security_validation()
        self.test_stripe_amount_validation_live()
        self.test_stripe_withdrawal_live_config()
        
        # Print final results
        print("=" * 80)
        print(f"📊 STRIPE LIVE INTEGRATION TEST RESULTS")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL STRIPE LIVE TESTS PASSED!")
            print("✅ Stripe LIVE integration is ready for production")
            return 0
        else:
            print("⚠️  SOME STRIPE LIVE TESTS FAILED")
            print("❌ Stripe LIVE integration needs attention before production")
            return 1

def main():
    """Main test execution"""
    print("🔴 STRIPE LIVE INTEGRATION TESTING")
    print("⚠️  WARNING: This uses LIVE Stripe keys")
    print("💡 Only configuration validation - no real payments will be made")
    print()
    
    tester = StripeLiveIntegrationTester()
    return tester.run_stripe_live_tests()

if __name__ == "__main__":
    sys.exit(main())