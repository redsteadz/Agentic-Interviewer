#!/usr/bin/env python3
"""
Test script for the Process Transcript endpoint
"""
import requests
import json

# Test data
test_data = {
    "transcript": "Interviewer: Hello, let's talk about the recent developments in artificial intelligence. What are your thoughts on AI in healthcare? Candidate: I think AI has tremendous potential in healthcare, especially in diagnostics and personalized medicine. The ability to analyze large datasets could help doctors make better decisions.",
    "knowledge_text": "=== ARTICLE 1 ===\nArtificial Intelligence in Healthcare: Revolutionizing Patient Care\nAI technologies are transforming healthcare by enabling faster diagnoses, personalized treatments, and improved patient outcomes. Machine learning algorithms can analyze medical images, predict disease patterns, and assist in drug discovery.",
    "call_id": ""
}

# API endpoints
BASE_URL = "http://localhost:8000/api"
LOGIN_URL = f"{BASE_URL}/token/"
PROCESS_TRANSCRIPT_URL = f"{BASE_URL}/process-transcript/"

def test_endpoint_without_auth():
    """Test the endpoint without authentication"""
    print("Testing Process Transcript endpoint without authentication...")
    
    response = requests.post(PROCESS_TRANSCRIPT_URL, json=test_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    return response.status_code

def test_endpoint_with_dummy_auth():
    """Test the endpoint with dummy authentication"""
    print("\nTesting Process Transcript endpoint with dummy auth headers...")
    
    headers = {
        "Authorization": "Bearer dummy_token",
        "Content-Type": "application/json"
    }
    
    response = requests.post(PROCESS_TRANSCRIPT_URL, json=test_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    return response.status_code

if __name__ == "__main__":
    print("Process Transcript Endpoint Test")
    print("=" * 40)
    
    # Test without authentication
    status1 = test_endpoint_without_auth()
    
    # Test with dummy authentication 
    status2 = test_endpoint_with_dummy_auth()
    
    print(f"\nTest Summary:")
    print(f"Without auth: {status1}")
    print(f"With dummy auth: {status2}")
    
    if status1 == 401:
        print("✓ Endpoint properly requires authentication")
    else:
        print("⚠ Endpoint may not be properly secured")