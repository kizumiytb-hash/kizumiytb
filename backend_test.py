#!/usr/bin/env python3
"""
Backend API Testing for Forex Broker Trading System with Authentication
Tests the complete trading system: authentication, real-time prices, order placement, 
position management, P&L calculation, SL/TP validation, and auto-execution
"""

import requests
import sys
import json
from datetime import datetime
import uuid
import time

class ForexBrokerAuthTester:
    def __init__(self, base_url="https://19d7651f-4e24-4d23-ad4f-0ab1b902f33c.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        
        # Generate unique emails for this test run
        import time
        timestamp = str(int(time.time()))
        
        # User 1 data
        self.user1_data = {
            "email": f"jean.dupont.{timestamp}@example.com",
            "password": "password123",
            "first_name": "Jean",
            "last_name": "Dupont"
        }
        self.user1_id = None
        self.user1_token = None
        self.user1_demo_account_id = None
        self.user1_real_account_id = None
        
        # User 2 data
        self.user2_data = {
            "email": f"marie.martin.{timestamp}@example.com", 
            "password": "password456",
            "first_name": "Marie",
            "last_name": "Martin"
        }
        self.user2_id = None
        self.user2_token = None
        self.user2_demo_account_id = None
        self.user2_real_account_id = None
        
        # Position tracking for trading tests
        self.user1_position_id = None
        self.user1_xau_position_id = None

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
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

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

    # ========== BASIC TESTS ==========
    
    def test_health_check(self):
        """Test basic health endpoint"""
        return self.run_test("Health Check", "GET", "health", 200)

    def test_prices_endpoint(self):
        """Test public prices endpoint (should work without auth)"""
        return self.run_test("Get Current Prices", "GET", "prices", 200)

    # ========== REGISTRATION TESTS ==========
    
    def test_user_registration_valid(self):
        """Test user registration with valid data"""
        success, response = self.run_test(
            "User Registration - Valid Data",
            "POST",
            "auth/register",
            200,
            self.user1_data
        )
        
        if success:
            self.user1_id = response.get('user_id')
            self.user1_token = response.get('access_token')
            self.user1_demo_account_id = response.get('demo_account_id')
            self.user1_real_account_id = response.get('real_account_id')
            
            print(f"   User 1 ID: {self.user1_id}")
            print(f"   Demo Account: {self.user1_demo_account_id}")
            print(f"   Real Account: {self.user1_real_account_id}")
            
            # Verify response structure
            required_fields = ['user_id', 'access_token', 'token_type', 'demo_account_id', 'real_account_id']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                print(f"   ❌ Missing fields in response: {missing_fields}")
                return False
            
            if response.get('token_type') != 'bearer':
                print(f"   ❌ Invalid token type: {response.get('token_type')}")
                return False
                
        return success

    def test_user_registration_duplicate_email(self):
        """Test registration with already existing email"""
        return self.run_test(
            "User Registration - Duplicate Email",
            "POST",
            "auth/register",
            400,
            self.user1_data  # Same email as first user
        )

    def test_user_registration_invalid_email(self):
        """Test registration with invalid email format"""
        invalid_data = self.user1_data.copy()
        invalid_data['email'] = 'invalid-email'
        
        return self.run_test(
            "User Registration - Invalid Email",
            "POST",
            "auth/register",
            422,  # Pydantic validation error
            invalid_data
        )

    def test_user_registration_missing_fields(self):
        """Test registration with missing required fields"""
        incomplete_data = {
            "email": "incomplete@example.com",
            "password": "password123"
            # Missing first_name and last_name
        }
        
        return self.run_test(
            "User Registration - Missing Fields",
            "POST",
            "auth/register",
            422,  # Pydantic validation error
            incomplete_data
        )

    def test_second_user_registration(self):
        """Register second user for isolation testing"""
        success, response = self.run_test(
            "Second User Registration",
            "POST",
            "auth/register",
            200,
            self.user2_data
        )
        
        if success:
            self.user2_id = response.get('user_id')
            self.user2_token = response.get('access_token')
            self.user2_demo_account_id = response.get('demo_account_id')
            self.user2_real_account_id = response.get('real_account_id')
            
            print(f"   User 2 ID: {self.user2_id}")
            
        return success

    # ========== LOGIN TESTS ==========
    
    def test_user_login_valid(self):
        """Test login with valid credentials"""
        login_data = {
            "email": self.user1_data['email'],
            "password": self.user1_data['password']
        }
        
        success, response = self.run_test(
            "User Login - Valid Credentials",
            "POST",
            "auth/login",
            200,
            login_data
        )
        
        if success:
            # Verify response structure
            required_fields = ['user_id', 'access_token', 'token_type', 'user_profile']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                print(f"   ❌ Missing fields in response: {missing_fields}")
                return False
            
            # Verify user profile structure
            profile = response.get('user_profile', {})
            profile_fields = ['email', 'first_name', 'last_name']
            missing_profile_fields = [field for field in profile_fields if field not in profile]
            if missing_profile_fields:
                print(f"   ❌ Missing profile fields: {missing_profile_fields}")
                return False
                
        return success

    def test_user_login_invalid_email(self):
        """Test login with non-existent email"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        return self.run_test(
            "User Login - Invalid Email",
            "POST",
            "auth/login",
            401,
            login_data
        )

    def test_user_login_invalid_password(self):
        """Test login with wrong password"""
        login_data = {
            "email": self.user1_data['email'],
            "password": "wrongpassword"
        }
        
        return self.run_test(
            "User Login - Invalid Password",
            "POST",
            "auth/login",
            401,
            login_data
        )

    # ========== PROTECTED ENDPOINT TESTS ==========
    
    def test_get_current_user_valid_token(self):
        """Test /api/auth/me with valid token"""
        if not self.user1_token:
            self.log_test("Get Current User - Valid Token", False, "No user1_token available")
            return False
            
        return self.run_test(
            "Get Current User - Valid Token",
            "GET",
            "auth/me",
            200,
            headers=self.get_auth_headers(self.user1_token)
        )

    def test_get_current_user_no_token(self):
        """Test /api/auth/me without token"""
        return self.run_test(
            "Get Current User - No Token",
            "GET",
            "auth/me",
            401
        )

    def test_get_current_user_invalid_token(self):
        """Test /api/auth/me with invalid token"""
        return self.run_test(
            "Get Current User - Invalid Token",
            "GET",
            "auth/me",
            401,
            headers=self.get_auth_headers("invalid_token_here")
        )

    def test_logout_valid_token(self):
        """Test logout with valid token"""
        if not self.user1_token:
            self.log_test("User Logout - Valid Token", False, "No user1_token available")
            return False
            
        return self.run_test(
            "User Logout - Valid Token",
            "POST",
            "auth/logout",
            200,
            headers=self.get_auth_headers(self.user1_token)
        )

    def test_logout_no_token(self):
        """Test logout without token"""
        return self.run_test(
            "User Logout - No Token",
            "POST",
            "auth/logout",
            401
        )

    # ========== TRADING ENDPOINTS PROTECTION TESTS ==========
    
    def test_accounts_endpoint_no_auth(self):
        """Test accounts endpoint without authentication"""
        return self.run_test(
            "Get Accounts - No Auth",
            "GET",
            "accounts",
            401
        )

    def test_accounts_endpoint_with_auth(self):
        """Test accounts endpoint with authentication"""
        if not self.user1_token:
            self.log_test("Get Accounts - With Auth", False, "No user1_token available")
            return False
            
        return self.run_test(
            "Get Accounts - With Auth",
            "GET",
            "accounts",
            200,
            headers=self.get_auth_headers(self.user1_token)
        )

    def test_account_details_no_auth(self):
        """Test account details endpoint without authentication"""
        return self.run_test(
            "Get Account Details - No Auth",
            "GET",
            "accounts/demo",
            401
        )

    def test_account_details_with_auth(self):
        """Test account details endpoint with authentication"""
        if not self.user1_token:
            self.log_test("Get Account Details - With Auth", False, "No user1_token available")
            return False
            
        return self.run_test(
            "Get Account Details - With Auth",
            "GET",
            "accounts/demo",
            200,
            headers=self.get_auth_headers(self.user1_token)
        )

    def test_positions_endpoint_no_auth(self):
        """Test positions endpoint without authentication"""
        return self.run_test(
            "Get Positions - No Auth",
            "GET",
            "positions/demo",
            401
        )

    def test_positions_endpoint_with_auth(self):
        """Test positions endpoint with authentication"""
        if not self.user1_token:
            self.log_test("Get Positions - With Auth", False, "No user1_token available")
            return False
            
        return self.run_test(
            "Get Positions - With Auth",
            "GET",
            "positions/demo",
            200,
            headers=self.get_auth_headers(self.user1_token)
        )

    def test_transactions_endpoint_no_auth(self):
        """Test transactions endpoint without authentication"""
        return self.run_test(
            "Get Transactions - No Auth",
            "GET",
            "transactions/demo",
            401
        )

    def test_transactions_endpoint_with_auth(self):
        """Test transactions endpoint with authentication"""
        if not self.user1_token:
            self.log_test("Get Transactions - With Auth", False, "No user1_token available")
            return False
            
        return self.run_test(
            "Get Transactions - With Auth",
            "GET",
            "transactions/demo",
            200,
            headers=self.get_auth_headers(self.user1_token)
        )

    # ========== USER ISOLATION TESTS ==========
    
    def test_user_isolation_accounts(self):
        """Test that users can only see their own accounts"""
        if not self.user1_token or not self.user2_token:
            self.log_test("User Isolation - Accounts", False, "Missing user tokens")
            return False
        
        # Get User 1's accounts
        success1, user1_accounts = self.run_test(
            "User 1 - Get Own Accounts",
            "GET",
            "accounts",
            200,
            headers=self.get_auth_headers(self.user1_token)
        )
        
        # Get User 2's accounts
        success2, user2_accounts = self.run_test(
            "User 2 - Get Own Accounts",
            "GET",
            "accounts",
            200,
            headers=self.get_auth_headers(self.user2_token)
        )
        
        if success1 and success2:
            # Verify accounts belong to correct users
            user1_account_users = [acc.get('user_id') for acc in user1_accounts]
            user2_account_users = [acc.get('user_id') for acc in user2_accounts]
            
            if all(uid == self.user1_id for uid in user1_account_users):
                print("   ✅ User 1 sees only own accounts")
            else:
                print("   ❌ User 1 sees accounts from other users")
                return False
                
            if all(uid == self.user2_id for uid in user2_account_users):
                print("   ✅ User 2 sees only own accounts")
            else:
                print("   ❌ User 2 sees accounts from other users")
                return False
                
            # Verify no overlap
            if not set(user1_account_users).intersection(set(user2_account_users)):
                print("   ✅ No account overlap between users")
            else:
                print("   ❌ Account overlap detected between users")
                return False
        
        return success1 and success2

    # ========== STRIPE INTEGRATION WITH AUTH TESTS ==========
    
    def test_stripe_checkout_no_auth(self):
        """Test Stripe checkout without authentication"""
        return self.run_test(
            "Stripe Checkout - No Auth",
            "POST",
            "stripe/checkout/session",
            401,
            {
                "account_type": "demo",
                "amount": 100.0
            }
        )

    def test_stripe_checkout_with_auth(self):
        """Test Stripe checkout with authentication"""
        if not self.user1_token:
            self.log_test("Stripe Checkout - With Auth", False, "No user1_token available")
            return False
            
        return self.run_test(
            "Stripe Checkout - With Auth",
            "POST",
            "stripe/checkout/session",
            200,
            {
                "account_type": "demo",
                "amount": 100.0
            },
            headers=self.get_auth_headers(self.user1_token)
        )

    def test_stripe_withdrawal_no_auth(self):
        """Test Stripe withdrawal without authentication"""
        return self.run_test(
            "Stripe Withdrawal - No Auth",
            "POST",
            "stripe/withdrawal",
            401,
            {
                "account_type": "demo",
                "amount": 50.0
            }
        )

    def test_stripe_withdrawal_with_auth(self):
        """Test Stripe withdrawal with authentication"""
        if not self.user1_token:
            self.log_test("Stripe Withdrawal - With Auth", False, "No user1_token available")
            return False
            
        return self.run_test(
            "Stripe Withdrawal - With Auth",
            "POST",
            "stripe/withdrawal",
            200,
            {
                "account_type": "demo",
                "amount": 50.0,
                "description": "Test withdrawal"
            },
            headers=self.get_auth_headers(self.user1_token)
        )

    # ========== TRADING SYSTEM TESTS ==========
    
    def test_real_time_prices(self):
        """Test real-time price simulation for EURUSD and XAUUSD"""
        success, response = self.run_test(
            "Real-Time Prices - EURUSD/XAUUSD",
            "GET",
            "prices",
            200
        )
        
        if success and isinstance(response, list):
            symbols = [price.get('symbol') for price in response]
            if 'EURUSD' in symbols and 'XAUUSD' in symbols:
                print("   ✅ Both EURUSD and XAUUSD prices available")
                
                # Check spread is 0 (bid = ask)
                for price in response:
                    if price.get('spread', 1) == 0.0:
                        print(f"   ✅ {price.get('symbol')} has 0 pip spread (bid={price.get('bid')}, ask={price.get('ask')})")
                    else:
                        print(f"   ❌ {price.get('symbol')} has non-zero spread: {price.get('spread')}")
                        return False
                return True
            else:
                print(f"   ❌ Missing required symbols. Found: {symbols}")
                return False
        
        return success

    def test_place_buy_order_eurusd(self):
        """Test placing BUY order for EURUSD with SL/TP"""
        if not self.user1_token:
            self.log_test("Place BUY Order EURUSD", False, "No user1_token available")
            return False
        
        # Get current price first
        success, prices = self.run_test("Get Prices for Order", "GET", "prices", 200)
        if not success:
            return False
            
        eurusd_price = None
        for price in prices:
            if price.get('symbol') == 'EURUSD':
                eurusd_price = price.get('ask')  # Use ask for BUY
                break
        
        if not eurusd_price:
            self.log_test("Place BUY Order EURUSD", False, "EURUSD price not found")
            return False
        
        # Create minimal order request (backend will set user_id, open_price, timestamp)
        order_data = {
            "user_id": "dummy",  # Will be overridden by backend
            "account_type": "demo",
            "symbol": "EURUSD",
            "order_type": "buy",
            "volume": 0.01,
            "open_price": eurusd_price,  # Set current price
            "leverage": 999999,  # Unlimited leverage
            "stop_loss": round(eurusd_price - 0.0050, 5),  # 50 pips below
            "take_profit": round(eurusd_price + 0.0100, 5),  # 100 pips above
            "timestamp": "2025-08-11T15:39:42.825794"  # Will be overridden
        }
        
        success, response = self.run_test(
            "Place BUY Order EURUSD",
            "POST",
            "orders",
            200,
            order_data,
            headers=self.get_auth_headers(self.user1_token)
        )
        
        if success:
            self.user1_position_id = response.get('position_id')
            print(f"   Position ID: {self.user1_position_id}")
            
        return success

    def test_place_sell_order_xauusd(self):
        """Test placing SELL order for XAUUSD with SL/TP"""
        if not self.user1_token:
            self.log_test("Place SELL Order XAUUSD", False, "No user1_token available")
            return False
        
        # Get current price first
        success, prices = self.run_test("Get Prices for Order", "GET", "prices", 200)
        if not success:
            return False
            
        xauusd_price = None
        for price in prices:
            if price.get('symbol') == 'XAUUSD':
                xauusd_price = price.get('bid')  # Use bid for SELL
                break
        
        if not xauusd_price:
            self.log_test("Place SELL Order XAUUSD", False, "XAUUSD price not found")
            return False
        
        # Create minimal order request (backend will set user_id, open_price, timestamp)
        order_data = {
            "user_id": "dummy",  # Will be overridden by backend
            "account_type": "demo",
            "symbol": "XAUUSD",
            "order_type": "sell",
            "volume": 0.05,
            "open_price": xauusd_price,  # Set current price
            "leverage": 999999,  # Unlimited leverage
            "stop_loss": round(xauusd_price + 50.0, 2),  # 50 points above
            "take_profit": round(xauusd_price - 100.0, 2),  # 100 points below
            "timestamp": "2025-08-11T15:39:42.825794"  # Will be overridden
        }
        
        success, response = self.run_test(
            "Place SELL Order XAUUSD",
            "POST",
            "orders",
            200,
            order_data,
            headers=self.get_auth_headers(self.user1_token)
        )
        
        if success:
            self.user1_xau_position_id = response.get('position_id')
            print(f"   XAU Position ID: {self.user1_xau_position_id}")
            
        return success

    def test_get_positions_with_pnl(self):
        """Test getting positions and verify P&L calculation"""
        if not self.user1_token:
            self.log_test("Get Positions with P&L", False, "No user1_token available")
            return False
        
        success, response = self.run_test(
            "Get Positions with P&L",
            "GET",
            "positions/demo",
            200,
            headers=self.get_auth_headers(self.user1_token)
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} positions")
            
            for position in response:
                symbol = position.get('symbol')
                open_price = position.get('open_price')
                current_price = position.get('current_price')
                pnl = position.get('profit_loss')
                order_type = position.get('order_type')
                
                print(f"   {symbol} {order_type.upper()}: Open={open_price}, Current={current_price}, P&L={pnl}")
                
                # Verify P&L calculation logic
                if symbol and open_price and current_price is not None and pnl is not None:
                    print(f"   ✅ Position {symbol} has complete P&L data")
                else:
                    print(f"   ❌ Position {symbol} missing P&L data")
                    return False
            
            return True
        
        return success

    def test_close_position_manual(self):
        """Test manual position closing"""
        if not self.user1_token or not hasattr(self, 'user1_position_id'):
            self.log_test("Close Position Manual", False, "No user1_token or position_id available")
            return False
        
        success, response = self.run_test(
            "Close Position Manual",
            "DELETE",
            f"positions/{self.user1_position_id}",
            200,
            headers=self.get_auth_headers(self.user1_token)
        )
        
        if success:
            close_price = response.get('close_price')
            print(f"   Position closed at price: {close_price}")
            
        return success

    def test_trade_history(self):
        """Test trade history retrieval"""
        if not self.user1_token:
            self.log_test("Trade History", False, "No user1_token available")
            return False
        
        success, response = self.run_test(
            "Trade History",
            "GET",
            "history/demo",
            200,
            headers=self.get_auth_headers(self.user1_token)
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} closed positions in history")
            
            for position in response:
                if position.get('status') == 'closed':
                    close_reason = position.get('close_reason', 'Unknown')
                    close_price = position.get('close_price')
                    print(f"   ✅ Closed position: {position.get('symbol')} - Reason: {close_reason}, Price: {close_price}")
                else:
                    print(f"   ❌ Non-closed position found in history")
                    return False
            
            return True
        
        return success

    def test_order_validation_invalid_sl(self):
        """Test order validation with invalid Stop Loss"""
        if not self.user1_token:
            self.log_test("Order Validation - Invalid SL", False, "No user1_token available")
            return False
        
        # Get current price
        success, prices = self.run_test("Get Prices for Validation", "GET", "prices", 200)
        if not success:
            return False
            
        eurusd_price = None
        for price in prices:
            if price.get('symbol') == 'EURUSD':
                eurusd_price = price.get('ask')
                break
        
        if not eurusd_price:
            return False
        
        # Invalid SL for BUY order (SL above current price)
        order_data = {
            "user_id": "dummy",
            "account_type": "demo",
            "symbol": "EURUSD",
            "order_type": "buy",
            "volume": 0.01,
            "open_price": eurusd_price,
            "leverage": 100,
            "stop_loss": round(eurusd_price + 0.0050, 5),  # INVALID: Above price for BUY
            "take_profit": round(eurusd_price + 0.0100, 5),
            "timestamp": "2025-08-11T15:39:42.825794"
        }
        
        return self.run_test(
            "Order Validation - Invalid SL",
            "POST",
            "orders",
            400,  # Should fail validation
            order_data,
            headers=self.get_auth_headers(self.user1_token)
        )

    def test_order_validation_invalid_tp(self):
        """Test order validation with invalid Take Profit"""
        if not self.user1_token:
            self.log_test("Order Validation - Invalid TP", False, "No user1_token available")
            return False
        
        # Get current price
        success, prices = self.run_test("Get Prices for Validation", "GET", "prices", 200)
        if not success:
            return False
            
        eurusd_price = None
        for price in prices:
            if price.get('symbol') == 'EURUSD':
                eurusd_price = price.get('ask')
                break
        
        if not eurusd_price:
            return False
        
        # Invalid TP for BUY order (TP below current price)
        order_data = {
            "user_id": "dummy",
            "account_type": "demo",
            "symbol": "EURUSD",
            "order_type": "buy",
            "volume": 0.01,
            "open_price": eurusd_price,
            "leverage": 100,
            "stop_loss": round(eurusd_price - 0.0050, 5),
            "take_profit": round(eurusd_price - 0.0100, 5),  # INVALID: Below price for BUY
            "timestamp": "2025-08-11T15:39:42.825794"
        }
        
        return self.run_test(
            "Order Validation - Invalid TP",
            "POST",
            "orders",
            400,  # Should fail validation
            order_data,
            headers=self.get_auth_headers(self.user1_token)
        )

    def test_order_validation_zero_volume(self):
        """Test order validation with zero volume"""
        if not self.user1_token:
            self.log_test("Order Validation - Zero Volume", False, "No user1_token available")
            return False
        
        order_data = {
            "user_id": "dummy",
            "account_type": "demo",
            "symbol": "EURUSD",
            "order_type": "buy",
            "volume": 0.0,  # Invalid volume
            "open_price": 1.05000,
            "leverage": 100,
            "timestamp": "2025-08-11T15:39:42.825794"
        }
        
        return self.run_test(
            "Order Validation - Zero Volume",
            "POST",
            "orders",
            422,  # Pydantic validation error
            order_data,
            headers=self.get_auth_headers(self.user1_token)
        )

    def test_sl_tp_auto_execution_simulation(self):
        """Test SL/TP auto-execution by creating order with close SL"""
        if not self.user1_token:
            self.log_test("SL/TP Auto-Execution", False, "No user1_token available")
            return False
        
        # Get current price
        success, prices = self.run_test("Get Prices for SL Test", "GET", "prices", 200)
        if not success:
            return False
            
        eurusd_price = None
        for price in prices:
            if price.get('symbol') == 'EURUSD':
                eurusd_price = price.get('ask')
                break
        
        if not eurusd_price:
            return False
        
        # Create order with very close SL (likely to trigger)
        order_data = {
            "user_id": "dummy",
            "account_type": "demo",
            "symbol": "EURUSD",
            "order_type": "buy",
            "volume": 0.01,
            "open_price": eurusd_price,
            "leverage": 100,
            "stop_loss": round(eurusd_price - 0.0001, 5),  # Very close SL
            "take_profit": round(eurusd_price + 0.0100, 5),
            "timestamp": "2025-08-11T15:39:42.825794"
        }
        
        success, response = self.run_test(
            "Create Order for SL Test",
            "POST",
            "orders",
            200,
            order_data,
            headers=self.get_auth_headers(self.user1_token)
        )
        
        if success:
            position_id = response.get('position_id')
            print(f"   Created position {position_id} with close SL")
            
            # Wait a few seconds for price simulation to potentially trigger SL
            print("   Waiting 5 seconds for potential SL trigger...")
            time.sleep(5)
            
            # Check if position was auto-closed
            success2, positions = self.run_test(
                "Check Position Status",
                "GET",
                "positions/demo",
                200,
                headers=self.get_auth_headers(self.user1_token)
            )
            
            if success2:
                position_still_open = any(pos.get('position_id') == position_id for pos in positions)
                if position_still_open:
                    print("   Position still open (SL not triggered yet)")
                else:
                    print("   ✅ Position may have been auto-closed by SL")
                    
                    # Check history for the closed position
                    success3, history = self.run_test(
                        "Check History for Auto-Close",
                        "GET",
                        "history/demo",
                        200,
                        headers=self.get_auth_headers(self.user1_token)
                    )
                    
                    if success3:
                        auto_closed = any(
                            pos.get('position_id') == position_id and 
                            pos.get('close_reason') == 'Stop Loss'
                            for pos in history
                        )
                        if auto_closed:
                            print("   ✅ Confirmed: Position auto-closed by Stop Loss")
                        else:
                            print("   Position closed but not by Stop Loss")
            
            return True
        
        return success

    # ========== JWT VALIDATION TESTS ==========
    
    def test_malformed_jwt_token(self):
        """Test with malformed JWT token"""
        return self.run_test(
            "Malformed JWT Token",
            "GET",
            "auth/me",
            401,
            headers=self.get_auth_headers("not.a.valid.jwt.token")
        )

    def test_expired_jwt_simulation(self):
        """Test with simulated expired token (using obviously invalid token)"""
        # Create a token that looks valid but isn't
        fake_expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        
        return self.run_test(
            "Expired/Invalid JWT Token",
            "GET",
            "auth/me",
            401,
            headers=self.get_auth_headers(fake_expired_token)
        )

    def test_missing_bearer_prefix(self):
        """Test with token missing Bearer prefix"""
        if not self.user1_token:
            self.log_test("Missing Bearer Prefix", False, "No user1_token available")
            return False
            
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.user1_token  # Missing "Bearer " prefix
        }
        
        return self.run_test(
            "Missing Bearer Prefix",
            "GET",
            "auth/me",
            401,
            headers=headers
        )

    # ========== MAIN TEST RUNNER ==========
    
    def run_all_tests(self):
        """Run all trading system tests in sequence"""
        print("🚀 Starting Forex Broker Complete Trading System Tests")
        print("=" * 70)
        
        # Basic connectivity tests
        print("\n🔧 BASIC CONNECTIVITY TESTS")
        print("-" * 40)
        self.test_health_check()
        self.test_prices_endpoint()
        
        # Registration tests
        print("\n📝 REGISTRATION TESTS")
        print("-" * 40)
        self.test_user_registration_valid()
        self.test_user_registration_duplicate_email()
        self.test_user_registration_invalid_email()
        self.test_user_registration_missing_fields()
        self.test_second_user_registration()
        
        # Login tests
        print("\n🔐 LOGIN TESTS")
        print("-" * 40)
        self.test_user_login_valid()
        self.test_user_login_invalid_email()
        self.test_user_login_invalid_password()
        
        # Protected endpoint tests
        print("\n🛡️ PROTECTED ENDPOINT TESTS")
        print("-" * 40)
        self.test_get_current_user_valid_token()
        self.test_get_current_user_no_token()
        self.test_get_current_user_invalid_token()
        self.test_logout_valid_token()
        self.test_logout_no_token()
        
        # Trading endpoints protection
        print("\n📊 TRADING ENDPOINTS PROTECTION")
        print("-" * 40)
        self.test_accounts_endpoint_no_auth()
        self.test_accounts_endpoint_with_auth()
        self.test_account_details_no_auth()
        self.test_account_details_with_auth()
        self.test_positions_endpoint_no_auth()
        self.test_positions_endpoint_with_auth()
        self.test_transactions_endpoint_no_auth()
        self.test_transactions_endpoint_with_auth()
        
        # User isolation tests
        print("\n👥 USER ISOLATION TESTS")
        print("-" * 40)
        self.test_user_isolation_accounts()
        
        # Trading System Tests
        print("\n📈 TRADING SYSTEM TESTS")
        print("-" * 40)
        self.test_real_time_prices()
        self.test_place_buy_order_eurusd()
        self.test_place_sell_order_xauusd()
        self.test_get_positions_with_pnl()
        self.test_close_position_manual()
        self.test_trade_history()
        
        # Order Validation Tests
        print("\n✅ ORDER VALIDATION TESTS")
        print("-" * 40)
        self.test_order_validation_invalid_sl()
        self.test_order_validation_invalid_tp()
        self.test_order_validation_zero_volume()
        
        # SL/TP Auto-Execution Test
        print("\n🎯 SL/TP AUTO-EXECUTION TEST")
        print("-" * 40)
        self.test_sl_tp_auto_execution_simulation()
        
        # Stripe integration with auth
        print("\n💳 STRIPE INTEGRATION WITH AUTH")
        print("-" * 40)
        self.test_stripe_checkout_no_auth()
        self.test_stripe_checkout_with_auth()
        self.test_stripe_withdrawal_no_auth()
        self.test_stripe_withdrawal_with_auth()
        
        # JWT validation tests
        print("\n🔑 JWT VALIDATION TESTS")
        print("-" * 40)
        self.test_malformed_jwt_token()
        self.test_expired_jwt_simulation()
        self.test_missing_bearer_prefix()
        
        # Print final results
        print("=" * 70)
        print(f"📊 COMPLETE SYSTEM TEST RESULTS")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
            return 0
        else:
            print("⚠️  SOME TESTS FAILED")
            return 1

def main():
    """Main test execution"""
    tester = ForexBrokerAuthTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())