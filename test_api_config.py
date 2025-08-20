#!/usr/bin/env python3
"""
Test API configuration for current user
"""
import os
import sys
import django

# Add the backend directory to Python path  
sys.path.insert(0, '/Users/apple/Desktop/Davv/Agentic-Interviewer/backend')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import APIConfiguration
from django.contrib.auth.models import User

def main():
    print("🔍 API Configuration Debug")
    print("=" * 30)
    
    # List all users and their configurations
    users = User.objects.all()
    print(f"Found {len(users)} users:")
    
    for user in users:
        print(f"\n👤 User: {user.username}")
        try:
            config = APIConfiguration.objects.get(user=user)
            
            print(f"   Twilio SID: {config.twilio_account_sid[:10] + '...' if config.twilio_account_sid else 'None'}")
            print(f"   Twilio Configured: {config.is_twilio_configured}")
            
            print(f"   VAPI Key: {config.vapi_api_key[:10] + '...' if config.vapi_api_key else 'None'}")  
            print(f"   VAPI Configured: {config.is_vapi_configured}")
            
            print(f"   OpenAI Key: {config.openai_api_key[:10] + '...' if config.openai_api_key else 'None'}")
            print(f"   OpenAI Configured: {config.is_openai_configured}")
            
            # Debug the OpenAI configuration logic
            if config.openai_api_key:
                starts_with_your = config.openai_api_key.startswith("your_")
                print(f"   Debug: Key starts with 'your_': {starts_with_your}")
                print(f"   Debug: Key length: {len(config.openai_api_key)}")
                print(f"   Debug: First 20 chars: {config.openai_api_key[:20]}")
            
        except APIConfiguration.DoesNotExist:
            print("   ❌ No API configuration found")
    
    print("\n💡 Troubleshooting:")
    print("   • Make sure you're logged in as the correct user")
    print("   • The OpenAI API key should start with 'sk-' not 'your_'")
    print("   • Configuration is user-specific")

if __name__ == "__main__":
    main()