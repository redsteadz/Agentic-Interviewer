#!/usr/bin/env python3
"""
Test the automatic transcript processing workflow
"""
import os
import sys
import django

# Add the backend directory to Python path
sys.path.insert(0, '/Users/apple/Desktop/Davv/Agentic-Interviewer/backend')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import InterviewCall, InterviewAssistant, Campaign, PhoneNumber
from django.contrib.auth.models import User
import json

def simulate_vapi_call_completion():
    """Simulate a complete VAPI call with automatic processing"""
    print("🔄 Simulating Complete VAPI Call with Automatic Processing")
    print("=" * 60)
    
    try:
        # Get user and existing assistant
        user = User.objects.get(username='Mehroz')
        assistant = InterviewAssistant.objects.filter(user=user).first()
        phone_number = PhoneNumber.objects.filter(user=user).first()
        
        if not assistant or not phone_number:
            print("❌ No assistant or phone number found")
            return
        
        print(f"✅ Using assistant: {assistant.name}")
        print(f"✅ Using phone: {phone_number.phone_number}")
        
        # Create realistic VAPI call data with recording
        vapi_call_data = {
            "id": "test-call-auto-process-123",
            "assistantId": assistant.vapi_assistant_id,
            "phoneNumberId": phone_number.vapi_phone_number_id,
            "type": "outboundPhoneCall",
            "startedAt": "2024-08-21T16:00:00.000Z",
            "endedAt": "2024-08-21T16:05:30.000Z",
            "status": "ended",
            "endedReason": "customer-ended-call",
            "customer": {"number": "+1234567890"},
            "cost": 0.25,
            "transcript": """AI: Good afternoon! I'm here to conduct your interview about artificial intelligence and technology innovation. Let's begin by discussing your experience with AI technologies. Could you share your background in artificial intelligence?

User: Thank you for the opportunity. I have over 6 years of experience in AI development, primarily focusing on machine learning applications in healthcare. I've worked on projects involving computer vision for medical imaging, natural language processing for clinical documentation, and predictive analytics for patient outcomes.

AI: That's impressive experience. Can you elaborate on the computer vision applications you've developed for medical imaging?

User: Certainly. My main project involved developing a convolutional neural network for detecting early-stage diabetic retinopathy in retinal photographs. We achieved 94% accuracy in identifying referable cases, which helped ophthalmologists prioritize urgent cases. The system processes thousands of images daily and has reduced diagnosis time from weeks to minutes.

AI: Excellent results. How do you approach the challenge of ensuring AI fairness and reducing bias in healthcare applications?

User: Bias mitigation is crucial in healthcare AI. We ensure diverse training datasets that represent different demographics, ages, and disease presentations. We also implement fairness metrics during model evaluation and continuously monitor performance across different patient populations. Regular audits help identify and correct any emerging biases.

AI: Very thoughtful approach. What about the integration of AI with existing healthcare systems? What challenges have you encountered?

User: Integration is indeed challenging. Legacy healthcare systems often have outdated APIs and data formats. We've had to develop custom connectors and data transformation pipelines. Change management is equally important - training medical staff to trust and effectively use AI recommendations requires careful planning and ongoing support.""",
            "artifact": {
                "recording": {
                    "mono": {
                        "combinedUrl": "https://storage.vapi.ai/test-call-auto-process-123-mono.wav"
                    }
                }
            }
        }
        
        print("\n📞 Step 1: Creating Call Record")
        print("-" * 30)
        
        # Create the call record
        call = InterviewCall.objects.create(
            user=user,
            vapi_call_id=vapi_call_data["id"],
            assistant=assistant,
            phone_number=phone_number,
            customer_number=vapi_call_data["customer"]["number"],
            status="ended",
            raw_call_data=vapi_call_data
        )
        
        print(f"✅ Call created with ID: {call.id}")
        
        print("\n🔄 Step 2: Simulating VAPI Data Update")
        print("-" * 35)
        
        # Import the view class to access the method
        from api.views import CallDetailView
        
        # Create view instance and process the call data
        call_view = CallDetailView()
        updated_call = call_view.update_call_from_vapi_data(call, vapi_call_data)
        
        print(f"✅ Call data updated")
        print(f"   Transcript length: {len(updated_call.transcript_text) if updated_call.transcript_text else 0} chars")
        print(f"   Recording URL: {updated_call.recording_url[:50] + '...' if updated_call.recording_url else 'None'}")
        print(f"   Processing status: {'Processed' if updated_call.processed_transcript else 'Not processed'}")
        
        print("\n📊 Step 3: Checking Automatic Processing Results")
        print("-" * 45)
        
        # Refresh from database to get latest data
        updated_call.refresh_from_db()
        
        if updated_call.processed_transcript:
            print("✅ Automatic transcript processing SUCCESSFUL!")
            print("\n📋 AI Processing Results:")
            print("=" * 30)
            print(updated_call.processed_transcript[:500] + "..." if len(updated_call.processed_transcript) > 500 else updated_call.processed_transcript)
        else:
            print("❌ Automatic processing did not complete")
            print("   This might be due to:")
            print("   • Missing knowledge base in assistant")
            print("   • OpenAI API issues")
            print("   • Processing conditions not met")
        
        print("\n🎯 Step 4: Verification Summary")
        print("-" * 30)
        
        print(f"Call ID: {updated_call.id}")
        print(f"Status: {updated_call.status}")
        print(f"Duration: {updated_call.duration_formatted or 'N/A'}")
        print(f"Cost: ${updated_call.cost or 0}")
        print(f"Has transcript: {'Yes' if updated_call.transcript_text else 'No'}")
        print(f"Has recording: {'Yes' if updated_call.recording_url else 'No'}")
        print(f"AI processed: {'Yes' if updated_call.processed_transcript else 'No'}")
        
        return updated_call
        
    except Exception as e:
        print(f"❌ Error in automatic workflow test: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_dashboard_integration(call):
    """Test how the call appears in dashboard"""
    if not call:
        return
        
    print("\n\n🌐 Step 5: Dashboard Integration Test")
    print("-" * 40)
    
    from api.serializer import InterviewCallSerializer
    from django.http import HttpRequest
    
    # Create mock request for serializer
    request = HttpRequest()
    request.META['HTTP_HOST'] = 'localhost:8000'
    request.META['wsgi.url_scheme'] = 'http'
    
    # Serialize the call data as it would appear in dashboard
    serializer = InterviewCallSerializer(call, context={'request': request})
    data = serializer.data
    
    print(f"📊 Dashboard Data for Call {call.id}:")
    print(f"   Customer: {data.get('customer_number')}")
    print(f"   Duration: {data.get('duration_formatted', 'N/A')}")
    print(f"   Has recording: {data.get('has_recording')}")
    print(f"   Recording URL: {'Available' if data.get('recording_file_url') else 'None'}")
    print(f"   Transcript length: {len(data.get('transcript_text', ''))}")
    print(f"   AI processed: {'Yes' if data.get('processed_transcript') else 'No'}")
    
    # Check if this call would appear in transcripts tab
    has_transcript = bool(data.get('transcript_text', '').strip())
    would_show_in_transcripts = has_transcript
    
    print(f"\n🎯 Frontend Display:")
    print(f"   Shows in 'Calls' tab: Yes")
    print(f"   Shows in 'Transcripts' tab: {'Yes' if would_show_in_transcripts else 'No'}")
    print(f"   Play button visible: {'Yes' if data.get('has_recording') and data.get('recording_file_url') else 'No'}")
    print(f"   Download button visible: {'Yes' if data.get('has_recording') and data.get('recording_file_url') else 'No'}")

def main():
    print("Automatic Transcript Processing Workflow Test")
    print("=" * 50)
    
    # Simulate the complete workflow
    call = simulate_vapi_call_completion()
    
    # Test dashboard integration
    test_dashboard_integration(call)
    
    print("\n\n🎉 Workflow Test Complete!")
    print("=" * 30)
    
    if call and call.processed_transcript:
        print("✅ FULL WORKFLOW SUCCESS!")
        print("\n🔄 This demonstrates the complete production workflow:")
        print("   1. VAPI call completes")
        print("   2. System fetches call data")
        print("   3. Transcript and recording are processed")
        print("   4. AI automatically analyzes transcript")
        print("   5. Results appear in dashboard")
        print("   6. Users can play/download recordings")
        print("   7. Users can view AI analysis")
    else:
        print("⚠️  PARTIAL SUCCESS - Manual processing may be needed")
    
    print(f"\n🌐 View results at: http://localhost:5174/")
    print(f"   Login as 'Mehroz' and check the Dashboard")

if __name__ == "__main__":
    main()