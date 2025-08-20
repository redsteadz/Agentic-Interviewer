#!/usr/bin/env python3
"""
Full test script for the Process Transcript endpoint with authentication
"""
import requests
import json
import os

# API endpoints
BASE_URL = "http://localhost:8000/api"
REGISTER_URL = f"{BASE_URL}/register/"
LOGIN_URL = f"{BASE_URL}/token/"
PROCESS_TRANSCRIPT_URL = f"{BASE_URL}/process-transcript/"

# Test credentials
test_user = {
    "username": "test_transcript_user",
    "password": "testpass123",
    "password2": "testpass123"
}

# Test data
test_data = {
    "transcript": "Interviewer: Hello, let's talk about the recent developments in artificial intelligence. What are your thoughts on AI in healthcare? Candidate: I think AI has tremendous potential in healthcare, especially in diagnostics and personalized medicine. The ability to analyze large datasets could help doctors make better decisions. I've worked on projects involving medical image analysis.",
    "knowledge_text": "=== ARTICLE 1 ===\nArtificial Intelligence in Healthcare: Revolutionizing Patient Care\nAI technologies are transforming healthcare by enabling faster diagnoses, personalized treatments, and improved patient outcomes. Machine learning algorithms can analyze medical images, predict disease patterns, and assist in drug discovery.",
    "call_id": ""
}

def register_user():
    """Register a test user"""
    print("Registering test user...")
    response = requests.post(REGISTER_URL, json=test_user)
    print(f"Registration Status: {response.status_code}")
    if response.status_code not in [201, 400]:  # 400 if user already exists
        print(f"Registration Response: {response.text}")
    return response.status_code in [201, 400]

def get_auth_token():
    """Get authentication token"""
    print("Getting authentication token...")
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    
    response = requests.post(LOGIN_URL, json=login_data)
    print(f"Login Status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access")
    else:
        print(f"Login Response: {response.text}")
        return None

def test_process_transcript(token):
    """Test the process transcript endpoint"""
    print("Testing Process Transcript endpoint with authentication...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Check if OpenAI API key is set
    openai_key = os.getenv('OPENAI_API_KEY', '')
    if not openai_key:
        print("⚠ Warning: OPENAI_API_KEY environment variable not set")
        print("The endpoint will likely fail due to missing API key")
    
    response = requests.post(PROCESS_TRANSCRIPT_URL, json=test_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    return response.status_code, response.text

def main():
    print("Process Transcript Endpoint Full Test")
    print("=" * 45)
    
    # Register user (or skip if exists)
    if not register_user():
        print("Failed to register user, exiting...")
        return
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("Failed to get auth token, exiting...")
        return
    
    print(f"✓ Authentication successful")
    
    # Test the endpoint
    status_code, response_text = test_process_transcript(token)
    
    print(f"\nTest Results:")
    print(f"Status Code: {status_code}")
    
    if status_code == 200:
        print("✓ Process Transcript endpoint is working!")
        try:
            response_data = json.loads(response_text)
            if "structured_transcript" in response_data:
                print("✓ GPT processing completed successfully")
                print(f"Articles processed: {response_data.get('articles_processed', 'N/A')}")
            else:
                print("⚠ Unexpected response format")
        except json.JSONDecodeError:
            print("⚠ Response is not valid JSON")
    elif status_code == 500:
        print("⚠ Server error - likely due to missing OpenAI API key")
    else:
        print(f"⚠ Unexpected status code: {status_code}")

if __name__ == "__main__":
    main()