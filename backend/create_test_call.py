from api.models import ScheduledCall, InterviewAssistant, PhoneNumber, Campaign
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Find a user with assistants and phone numbers
user = User.objects.first()
print(f"Using user: {user}")

# Find an assistant and phone number
assistant = InterviewAssistant.objects.filter(user=user).first()
phone_number = PhoneNumber.objects.filter(user=user).first()

if assistant and phone_number:
    # Create a scheduled call for 5 minutes ago (should be due)
    past_time = timezone.now() - timedelta(minutes=5)
    
    scheduled_call = ScheduledCall.objects.create(
        user=user,
        campaign=assistant.campaign,
        assistant=assistant,
        phone_number=phone_number,
        customer_number="+1234567890",  # Test number
        scheduled_time=past_time,
        call_name="Test Past Call",
        notes="This is a test call scheduled in the past",
        status='scheduled'
    )
    
    print(f"Created test scheduled call ID: {scheduled_call.id}")
    print(f"Scheduled for: {scheduled_call.scheduled_time}")
    print(f"Current time: {timezone.now()}")
    print(f"Should be due: {scheduled_call.is_due}")
else:
    print("Need an assistant and phone number to create test call")
    print(f"Assistants: {InterviewAssistant.objects.filter(user=user).count()}")
    print(f"Phone numbers: {PhoneNumber.objects.filter(user=user).count()}")
