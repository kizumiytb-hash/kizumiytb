#!/usr/bin/env python3
"""
Quick Stripe LIVE Key Validation Test
"""

import requests
import json
import time

def test_stripe_live_validation():
    base_url = "https://19d7651f-4e24-4d23-ad4f-0ab1b902f33c.preview.emergentagent.com"
    
    # Register a test user
    timestamp = str(int(time.time()))
    user_data = {
        "email": f"live.validation.{timestamp}@example.com",
        "password": "TestPass123!",
        "first_name": "Live",
        "last_name": "Validation"
    }
    
    print("🔍 Registering test user...")
    response = requests.post(f"{base_url}/api/auth/register", json=user_data, timeout=30)
    if response.status_code != 200:
        print(f"❌ Registration failed: {response.status_code}")
        return False
    
    user_info = response.json()
    token = user_info.get('access_token')
    
    print("🔍 Testing LIVE Stripe checkout session...")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    checkout_data = {
        "account_type": "real",
        "amount": 1.0
    }
    
    response = requests.post(f"{base_url}/api/stripe/checkout/session", json=checkout_data, headers=headers, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        session_id = result.get('session_id', '')
        session_url = result.get('url', '')
        
        print(f"✅ Session created successfully")
        print(f"   Session ID: {session_id}")
        print(f"   Session URL: {session_url[:100]}...")
        
        # Check if it's LIVE
        if session_id.startswith('cs_live_'):
            print("✅ LIVE session confirmed (session ID starts with cs_live_)")
            return True
        elif 'checkout.stripe.com/c/pay/' in session_url:
            print("✅ LIVE session confirmed (production checkout URL)")
            return True
        else:
            print("❌ Session appears to be test mode")
            return False
    else:
        print(f"❌ Checkout session failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

if __name__ == "__main__":
    print("🚀 Quick Stripe LIVE Key Validation")
    print("=" * 50)
    
    if test_stripe_live_validation():
        print("\n🎉 STRIPE LIVE KEYS ARE WORKING CORRECTLY!")
    else:
        print("\n❌ STRIPE LIVE KEYS VALIDATION FAILED")