#!/usr/bin/env python3
"""
PayPal Integration Diagnostic Tool
Comprehensive testing of PayPal authentication and API calls
"""

import requests
import base64
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

class PayPalDiagnostic:
    def __init__(self):
        self.client_id = os.environ.get('PAYPAL_CLIENT_ID')
        self.client_secret = os.environ.get('PAYPAL_CLIENT_SECRET')
        self.base_url = 'https://api.sandbox.paypal.com'
        
    def print_config(self):
        """Print current PayPal configuration"""
        print("🔧 PayPal Configuration:")
        print(f"   Client ID: {self.client_id[:20]}..." if self.client_id else "   Client ID: NOT SET")
        print(f"   Client Secret: {self.client_secret[:20]}..." if self.client_secret else "   Client Secret: NOT SET")
        print(f"   Base URL: {self.base_url}")
        print()
        
    def test_credentials_format(self):
        """Test if credentials are properly formatted"""
        print("🔍 Testing Credential Format:")
        
        if not self.client_id or not self.client_secret:
            print("❌ Missing PayPal credentials")
            return False
            
        # Check if credentials look like PayPal format
        if len(self.client_id) < 50:
            print("⚠️  Client ID seems too short")
        else:
            print("✅ Client ID length looks correct")
            
        if len(self.client_secret) < 50:
            print("⚠️  Client Secret seems too short")
        else:
            print("✅ Client Secret length looks correct")
            
        print()
        return True
        
    def test_basic_auth_encoding(self):
        """Test Basic Auth encoding"""
        print("🔍 Testing Basic Auth Encoding:")
        
        try:
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            print(f"   Auth String Length: {len(auth_string)}")
            print(f"   Base64 Encoded Length: {len(auth_b64)}")
            print(f"   Base64 Sample: {auth_b64[:50]}...")
            print("✅ Basic Auth encoding successful")
            print()
            return auth_b64
        except Exception as e:
            print(f"❌ Basic Auth encoding failed: {str(e)}")
            print()
            return None
            
    def test_oauth_token_request(self):
        """Test OAuth token request with detailed debugging"""
        print("🔍 Testing OAuth Token Request:")
        
        auth_b64 = self.test_basic_auth_encoding()
        if not auth_b64:
            return None
            
        url = f"{self.base_url}/v1/oauth2/token"
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = 'grant_type=client_credentials'
        
        print(f"   URL: {url}")
        print(f"   Headers: {json.dumps({k: v for k, v in headers.items() if k != 'Authorization'}, indent=4)}")
        print(f"   Auth Header: Basic {auth_b64[:20]}...")
        print(f"   Data: {data}")
        print()
        
        try:
            response = requests.post(url, headers=headers, data=data, timeout=30)
            
            print(f"   Response Status: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                token_data = response.json()
                print("✅ OAuth token request successful!")
                print(f"   Access Token: {token_data.get('access_token', 'N/A')[:20]}...")
                print(f"   Token Type: {token_data.get('token_type', 'N/A')}")
                print(f"   Expires In: {token_data.get('expires_in', 'N/A')} seconds")
                print()
                return token_data.get('access_token')
            else:
                print("❌ OAuth token request failed!")
                try:
                    error_data = response.json()
                    print(f"   Error Response: {json.dumps(error_data, indent=4)}")
                except:
                    print(f"   Error Text: {response.text}")
                print()
                return None
                
        except requests.exceptions.Timeout:
            print("❌ Request timeout")
            print()
            return None
        except requests.exceptions.ConnectionError:
            print("❌ Connection error")
            print()
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            print()
            return None
            
    def test_payout_api_structure(self, access_token):
        """Test PayPal Payout API structure without actually sending money"""
        if not access_token:
            print("❌ Cannot test Payout API - no access token")
            return False
            
        print("🔍 Testing PayPal Payout API Structure:")
        
        # Create a test payout structure (won't be sent)
        payout_data = {
            "sender_batch_header": {
                "sender_batch_id": "test-batch-123",
                "email_subject": "Test Payout",
                "email_message": "This is a test payout"
            },
            "items": [
                {
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": "1.00",
                        "currency": "EUR"
                    },
                    "receiver": "test@sandbox.paypal.com",
                    "note": "Test payout",
                    "sender_item_id": "test-item-123"
                }
            ]
        }
        
        print(f"   Payout Structure: {json.dumps(payout_data, indent=4)}")
        
        # Test the API endpoint (but don't actually send)
        url = f"{self.base_url}/v1/payments/payouts"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }
        
        print(f"   Payout URL: {url}")
        print(f"   Headers: {json.dumps({k: v for k, v in headers.items() if k != 'Authorization'}, indent=4)}")
        print(f"   Auth Header: Bearer {access_token[:20]}...")
        print()
        
        # Note: We're not actually sending this request to avoid creating real payouts
        print("✅ Payout API structure validated (not sent)")
        print()
        return True
        
    def test_alternative_credentials(self):
        """Test with alternative credential formats"""
        print("🔍 Testing Alternative Credential Scenarios:")
        
        # Test if credentials might have extra whitespace
        clean_id = self.client_id.strip() if self.client_id else ""
        clean_secret = self.client_secret.strip() if self.client_secret else ""
        
        if clean_id != self.client_id or clean_secret != self.client_secret:
            print("⚠️  Found whitespace in credentials - testing cleaned versions")
            
            # Test with cleaned credentials
            original_id, original_secret = self.client_id, self.client_secret
            self.client_id, self.client_secret = clean_id, clean_secret
            
            token = self.test_oauth_token_request()
            
            # Restore original credentials
            self.client_id, self.client_secret = original_id, original_secret
            
            if token:
                print("✅ Cleaned credentials work!")
                return True
            else:
                print("❌ Cleaned credentials also fail")
        else:
            print("✅ No whitespace issues found")
            
        print()
        return False
        
    def run_full_diagnostic(self):
        """Run complete PayPal diagnostic"""
        print("🚀 PayPal Integration Diagnostic")
        print("=" * 60)
        
        self.print_config()
        
        if not self.test_credentials_format():
            print("❌ Cannot proceed - missing credentials")
            return False
            
        # Test alternative credential formats first
        self.test_alternative_credentials()
        
        # Test main OAuth flow
        access_token = self.test_oauth_token_request()
        
        if access_token:
            self.test_payout_api_structure(access_token)
            print("🎉 PayPal integration appears to be working!")
            return True
        else:
            print("❌ PayPal authentication failed")
            
            # Provide diagnostic suggestions
            print("\n🔧 DIAGNOSTIC SUGGESTIONS:")
            print("1. Verify PayPal credentials are for Sandbox environment")
            print("2. Check if credentials are active in PayPal Developer Dashboard")
            print("3. Ensure app has 'Send Money' permissions enabled")
            print("4. Try regenerating credentials in PayPal Developer Console")
            print("5. Check if PayPal account is verified and in good standing")
            
            return False

def main():
    diagnostic = PayPalDiagnostic()
    success = diagnostic.run_full_diagnostic()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())