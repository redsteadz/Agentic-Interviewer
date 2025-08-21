#!/usr/bin/env python3
"""
Test the download recording feature
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
import requests

def test_download_functionality():
    """Test the download recording functionality"""
    print("📥 Testing Download Recording Feature")
    print("=" * 45)
    
    # Get call with recording
    call = InterviewCall.objects.get(id=2)
    
    print(f"Call ID: {call.id}")
    print(f"Customer: {call.customer_number}")
    print(f"Created: {call.created_at}")
    print(f"Has recording: {call.has_recording}")
    
    if call.has_recording and call.recording_file:
        recording_url = f"http://localhost:8000{call.recording_file.url}"
        print(f"Recording URL: {recording_url}")
        
        # Test if file is downloadable
        try:
            response = requests.head(recording_url, timeout=5)
            print(f"HTTP Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            print(f"Content-Length: {response.headers.get('Content-Length')} bytes")
            print(f"Content-Disposition: {response.headers.get('Content-Disposition', 'Not set')}")
            
            if response.status_code == 200:
                print("✅ File is accessible for download")
                
                # Generate download filename like frontend does
                created_date = call.created_at.strftime('%Y-%m-%d')
                download_filename = f"call_recording_{call.customer_number}_{created_date}.wav"
                print(f"Download filename: {download_filename}")
                
            else:
                print("❌ File not accessible")
                
        except Exception as e:
            print(f"❌ Error testing download: {e}")
    else:
        print("❌ No recording available for this call")

def main():
    test_download_functionality()
    
    print("\n" + "=" * 45)
    print("🎯 Download Feature Details:")
    print("• Download button appears next to Play button")
    print("• Downloads file with descriptive name")
    print("• Format: call_recording_{phone}_{date}.wav")
    print("• Example: call_recording_+923132363332_2025-08-21.wav")
    
    print("\n🌐 How to Test:")
    print("1. Go to http://localhost:5174/")
    print("2. Login as 'Mehroz'")
    print("3. Navigate to Dashboard → Transcripts tab")
    print("4. Find call with recording")
    print("5. Click 'Download' button")
    print("6. File should download to your Downloads folder")
    
    print("\n✨ Features:")
    print("• ▶️  Play button: Stream audio in browser")
    print("• 📥 Download button: Save file to device") 
    print("• 🏷️  Smart naming: Includes phone number and date")
    print("• 🔄 Console logging: Shows download progress")

if __name__ == "__main__":
    main()