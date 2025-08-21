#!/usr/bin/env python3
"""
Test what the frontend should see for recordings
"""
import os
import sys
import django

# Add the backend directory to Python path
sys.path.insert(0, '/Users/apple/Desktop/Davv/Agentic-Interviewer/backend')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import InterviewCall
from api.serializer import InterviewCallSerializer
from django.http import HttpRequest

def test_frontend_data():
    """Test what data the frontend should receive"""
    print("🎵 Frontend Recording Data Test")
    print("=" * 40)
    
    # Get all calls
    calls = InterviewCall.objects.all().order_by('-created_at')
    
    # Create mock request
    request = HttpRequest()
    request.META['HTTP_HOST'] = 'localhost:8000'
    request.META['wsgi.url_scheme'] = 'http'
    
    print(f"Total calls in database: {len(calls)}")
    
    for call in calls:
        print(f"\n📞 Call {call.id}:")
        print(f"   Customer: {call.customer_number}")
        print(f"   Created: {call.created_at}")
        
        # Serialize like API would
        serializer = InterviewCallSerializer(call, context={'request': request})
        data = serializer.data
        
        print(f"   has_recording: {data.get('has_recording')}")
        print(f"   recording_file_url: {data.get('recording_file_url')}")
        
        # Check what frontend condition would be
        has_recording = data.get('has_recording')
        recording_url = data.get('recording_file_url')
        
        should_show_button = has_recording and recording_url
        print(f"   Should show play button: {should_show_button}")
        
        if should_show_button:
            print(f"   🎵 PLAY BUTTON SHOULD BE VISIBLE!")
        else:
            print(f"   ❌ Play button hidden")
            
        # Check transcript availability
        has_transcript = bool(data.get('transcript_text'))
        print(f"   Has transcript: {has_transcript}")

def main():
    test_frontend_data()
    
    print("\n" + "=" * 40)
    print("🌐 Frontend Instructions:")
    print("1. Go to http://localhost:5174/")
    print("2. Login as 'Mehroz'")  
    print("3. Go to Dashboard")
    print("4. Click 'Transcripts' tab")
    print("5. Look for call +923132363332")
    print("6. Play button should be visible next to transcript")
    
    print("\n🔧 If play button not visible:")
    print("   • Try refreshing the page (F5)")
    print("   • Check browser console for errors")
    print("   • Verify you're in 'Transcripts' tab")
    print("   • Make sure you're logged in as 'Mehroz'")

if __name__ == "__main__":
    main()