#!/usr/bin/env python3
"""
Test script to verify how website analysis works
"""
import requests
import json

# API endpoints
BASE_URL = "http://localhost:8000/api"
LOGIN_URL = f"{BASE_URL}/token/"
ANALYZE_WEBSITE_URL = f"{BASE_URL}/analyze-website/"

# Test credentials (from our previous test)
test_user = {
    "username": "test_transcript_user", 
    "password": "testpass123"
}

def get_auth_token():
    """Get authentication token"""
    response = requests.post(LOGIN_URL, json=test_user)
    if response.status_code == 200:
        return response.json().get("access")
    return None

def test_website_analysis():
    """Test website analysis endpoint"""
    token = get_auth_token()
    if not token:
        print("Failed to get auth token")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test with a real website (not example.com to avoid mock data)
    test_data = {"website_url": "https://google.com"}
    
    print("Testing website analysis...")
    response = requests.post(ANALYZE_WEBSITE_URL, json=test_data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_website_analysis()