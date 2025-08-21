#!/usr/bin/env python3
"""
Update VAPI assistants to enable recording
"""
import os
import sys
import django
import requests

# Add the backend directory to Python path
sys.path.insert(0, '/Users/apple/Desktop/Davv/Agentic-Interviewer/backend')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import APIConfiguration, InterviewAssistant
from django.contrib.auth.models import User

def update_vapi_assistant_recording():
    """Update VAPI assistants to enable recording"""
    print("🔄 Updating VAPI Assistants to Enable Recording")
    print("=" * 50)
    
    # Get VAPI API key
    user = User.objects.get(username='Mehroz')
    try:
        config = APIConfiguration.objects.get(user=user)
        if not config.is_vapi_configured:
            print("❌ VAPI not configured")
            return
        vapi_key = config.vapi_api_key
    except APIConfiguration.DoesNotExist:
        print("❌ No API configuration found")
        return
    
    headers = {
        "Authorization": f"Bearer {vapi_key}",
        "Content-Type": "application/json"
    }
    
    # Get all assistants
    assistants = InterviewAssistant.objects.all()
    updated_count = 0
    
    for assistant in assistants:
        print(f"\n🤖 Updating assistant: {assistant.name}")
        print(f"   VAPI ID: {assistant.vapi_assistant_id}")
        
        # Prepare update data
        update_data = assistant.configuration.copy()
        update_data['recordingEnabled'] = True
        
        try:
            # Update assistant via VAPI API
            response = requests.patch(
                f"https://api.vapi.ai/assistant/{assistant.vapi_assistant_id}",
                headers=headers,
                json=update_data,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"   ✅ Successfully enabled recording in VAPI")
                updated_count += 1
            else:
                print(f"   ❌ Failed to update VAPI: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error updating VAPI: {e}")
    
    print(f"\n🎯 Summary: Updated {updated_count} assistants in VAPI")
    print("\n📞 Next Steps:")
    print("   1. Make new test calls")
    print("   2. Recording should now be enabled")
    print("   3. Check dashboard for play buttons")

def main():
    print("VAPI Recording Enablement")
    print("=" * 30)
    update_vapi_assistant_recording()

if __name__ == "__main__":
    main()