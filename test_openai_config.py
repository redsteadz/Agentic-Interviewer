#!/usr/bin/env python3
"""
Test script to verify OpenAI API key configuration functionality
"""
import requests
import json

# API endpoints
BASE_URL = "http://localhost:8000/api"
LOGIN_URL = f"{BASE_URL}/token/"
CONFIG_URL = f"{BASE_URL}/config/"
PROCESS_TRANSCRIPT_URL = f"{BASE_URL}/process-transcript/"

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

def test_config_api():
    """Test the API configuration endpoints"""
    token = get_auth_token()
    if not token:
        print("❌ Failed to get auth token")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("🔧 Testing OpenAI API Key Configuration...")
    
    # Test 1: Get current config
    print("\n1. Getting current configuration...")
    response = requests.get(CONFIG_URL, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        config = response.json()
        print(f"   OpenAI configured: {config.get('openai_configured', False)}")
        print(f"   OpenAI key set: {config.get('openai_api_key_set', False)}")
    else:
        print(f"   Error: {response.text}")
        return False
    
    # Test 2: Set OpenAI API key
    print("\n2. Setting OpenAI API key...")
    config_data = {"openai_api_key": "sk-test-dummy-key-for-testing-123"}
    response = requests.post(CONFIG_URL, json=config_data, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Success: {result.get('success', False)}")
    else:
        print(f"   Error: {response.text}")
    
    # Test 3: Verify config was saved
    print("\n3. Verifying configuration was saved...")
    response = requests.get(CONFIG_URL, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        config = response.json()
        print(f"   OpenAI configured: {config.get('openai_configured', False)}")
        print(f"   OpenAI key set: {config.get('openai_api_key_set', False)}")
        
        if config.get('openai_configured') and config.get('openai_api_key_set'):
            print("   ✅ OpenAI API key successfully configured!")
            return True
        else:
            print("   ❌ OpenAI API key not properly configured")
            return False
    else:
        print(f"   Error: {response.text}")
        return False

def test_transcript_processing():
    """Test transcript processing with configured OpenAI key"""
    token = get_auth_token()
    if not token:
        print("❌ Failed to get auth token")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n🧠 Testing Process Transcript with OpenAI...")
    
    # Test data
    test_data = {
        "transcript": "Interviewer: Let's discuss AI in healthcare. What do you think about machine learning applications? Candidate: I believe AI has great potential in healthcare, especially for diagnostic imaging and personalized treatment plans.",
        "knowledge_text": "=== ARTICLE 1 ===\nAI in Healthcare: Transforming Medical Practice\nArtificial intelligence is revolutionizing healthcare through machine learning applications in diagnostics, treatment planning, and patient care optimization.",
        "call_id": ""
    }
    
    response = requests.post(PROCESS_TRANSCRIPT_URL, json=test_data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Transcript processing successful!")
            print(f"Structured transcript preview: {result.get('structured_transcript', '')[:200]}...")
            return True
        else:
            print("❌ Transcript processing failed - no success field")
            return False
    else:
        print(f"❌ Transcript processing failed: {response.text}")
        return False

def main():
    print("OpenAI Configuration Test Suite")
    print("=" * 40)
    
    # Test configuration API
    config_success = test_config_api()
    
    if config_success:
        # Test transcript processing
        transcript_success = test_transcript_processing()
        
        if transcript_success:
            print("\n🎉 All tests passed! OpenAI integration is working correctly.")
        else:
            print("\n⚠️  Configuration works but transcript processing failed.")
    else:
        print("\n❌ Configuration test failed.")

if __name__ == "__main__":
    main()