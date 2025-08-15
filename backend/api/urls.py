from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    # Authentication endpoints
    path("token/", views.MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", views.RegisterView.as_view(), name="auth_register"),
    path("test/", views.testEndPoint, name="test"),
    # Campaign endpoints
    path("campaign/", views.campaignView, name="campaign"),
    # Interview system endpoints
    path("config/", views.APIConfigurationView.as_view(), name="api_config"),
    path("clear-config/", views.clear_config, name="clear_config"),
    # Assistant endpoints
    path(
        "create-assistant/",
        views.CreateAssistantView.as_view(),
        name="create_assistant",
    ),
    path("assistants/", views.AssistantListView.as_view(), name="assistant_list"),
    # Phone number endpoints
    path(
        "phone-numbers/",
        views.VapiPhoneNumbersView.as_view(),
        name="vapi_phone_numbers",
    ),
    path(
        "twilio-numbers/",
        views.TwilioPhoneNumbersView.as_view(),
        name="twilio_phone_numbers",
    ),
    path(
        "register-phone-number/",
        views.RegisterPhoneNumberView.as_view(),
        name="register_phone_number",
    ),
    path(
        "my-phone-numbers/",
        views.PhoneNumberListView.as_view(),
        name="my_phone_numbers",
    ),
    # Call endpoints
    path("make-call/", views.MakeCallView.as_view(), name="make_call"),
    path("call/<str:call_id>/", views.CallDetailView.as_view(), name="call_detail"),
    path("calls/", views.CallListView.as_view(), name="call_list"),
    # Scheduled call endpoints
    path("schedule-call/", views.ScheduleCallView.as_view(), name="schedule_call"),
    path("scheduled-calls/", views.ScheduledCallListView.as_view(), name="scheduled_call_list"),
    path("scheduled-call/<int:call_id>/", views.ScheduledCallDetailView.as_view(), name="scheduled_call_detail"),
    path("execute-scheduled-calls/", views.ExecuteScheduledCallsView.as_view(), name="execute_scheduled_calls"),
    # Website analysis endpoint
    path("analyze-website/", views.AnalyzeWebsiteView.as_view(), name="analyze_website"),
    # ElevenLabs voices endpoint
    path("elevenlabs-voices/", views.ElevenLabsVoicesView.as_view(), name="elevenlabs_voices"),
    # Transcript processing endpoint
    path("process-transcript/", views.ProcessTranscriptView.as_view(), name="process_transcript"),
    # Routes listing
    path("", views.getRoutes, name="routes"),
]
