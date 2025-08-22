#!/usr/bin/env python3
"""
Test script for VAPI webhook endpoint
"""
import requests
import json
from datetime import datetime

# Test configuration
WEBHOOK_URL = "http://localhost:8000/api/webhook/vapi/"

# Sample webhook payloads for different events
test_payloads = {
    "call.started": {
        "type": "call.started",
        "call": {
            "id": "test-call-123",
            "status": "in-progress",
            "startedAt": datetime.now().isoformat() + "Z",
            "assistantId": "test-assistant-123",
            "phoneNumberId": "test-phone-123",
            "customer": {"number": "+1234567890"}
        }
    },
    "call.ended": {
        "type": "call.ended",
        "call": {
            "id": "test-call-123",
            "status": "ended",
            "startedAt": datetime.now().isoformat() + "Z",
            "endedAt": datetime.now().isoformat() + "Z",
            "duration": 120,
            "cost": 0.05,
            "transcript": [
                {
                    "timestamp": "2024-01-20T14:30:05Z",
                    "role": "assistant",
                    "message": "Hello! How can I help you today?"
                },
                {
                    "timestamp": "2024-01-20T14:30:25Z", 
                    "role": "user",
                    "message": "I'd like to discuss AI applications in healthcare."
                }
            ],
            "recordingUrl": "https://example.com/recording.wav"
        }
    },
    "call.failed": {
        "type": "call.failed",
        "call": {
            "id": "test-call-123",
            "status": "failed",
            "endReason": "no-answer",
            "endedAt": datetime.now().isoformat() + "Z"
        }
    },
    "transcript.updated": {
        "type": "transcript.updated",
        "call": {
            "id": "test-call-123",
            "transcript": [
                {
                    "timestamp": "2024-01-20T14:30:05Z",
                    "role": "assistant", 
                    "message": "Hello! How can I help you today?"
                },
                {
                    "timestamp": "2024-01-20T14:30:25Z",
                    "role": "user",
                    "message": "I'd like to discuss AI applications in healthcare."
                },
                {
                    "timestamp": "2024-01-20T14:30:45Z",
                    "role": "assistant",
                    "message": "That's a fascinating topic! Let's explore that."
                }
            ]
        }
    },
    "recording.ready": {
        "type": "recording.ready",
        "call": {
            "id": "test-call-123",
            "recordingUrl": "https://example.com/recording.wav"
        }
    }
}

def test_webhook_endpoint():
    """Test the webhook endpoint with different event types"""
    print("🧪 Testing VAPI Webhook Endpoint with Logging")
    print("=" * 50)
    
    # Check if webhook endpoint is accessible
    try:
        response = requests.get("http://localhost:8000/api/")
        if response.status_code != 200:
            print("❌ Backend server not running!")
            print("💡 Please run: python manage.py runserver")
            return
    except:
        print("❌ Backend server not accessible!")
        return
    
    results = {}
    
    for event_type, payload in test_payloads.items():
        print(f"\n🔔 Testing {event_type} webhook...")
        
        try:
            response = requests.post(
                WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 200:
                print(f"   ✅ {event_type} webhook successful")
                results[event_type] = "✅ Success"
            elif response.status_code == 404:
                print(f"   ❌ Call not found - this is expected for test data")
                results[event_type] = "⚠️ Expected error (call not found)"
            else:
                print(f"   ❌ {event_type} webhook failed")
                results[event_type] = f"❌ Failed ({response.status_code})"
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[event_type] = f"❌ Error: {e}"
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    for event_type, result in results.items():
        print(f"   {event_type}: {result}")
    
    print(f"\n🌐 Webhook URL: {WEBHOOK_URL}")
    print("\n📝 Next Steps:")
    print("1. Create a test call in your database with vapi_call_id='test-call-123'")
    print("2. Configure VAPI assistant to use this webhook URL")
    print("3. Set webhook secret in environment: VAPI_WEBHOOK_SECRET=your_secret")
    print("\n📁 Webhook Logs:")
    print("Check 'backend/webhook_logs/' folder for saved webhook events")
    print("Each webhook request is now saved as a JSON file for debugging")

if __name__ == "__main__":
    test_webhook_endpoint()