from django.db import models
from django.contrib.auth.models import User
import json


class Campaign(models.Model):
    """Store campaign details for interview calls"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="campaigns")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (User: {self.user.username})"

    class Meta:
        ordering = ["-created_at"]


class APIConfiguration(models.Model):
    """Store user's API configuration for Twilio and Vapi"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="api_config"
    )
    twilio_account_sid = models.CharField(max_length=255, blank=True, null=True)
    twilio_auth_token = models.CharField(max_length=255, blank=True, null=True)
    vapi_api_key = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"API Config for {self.user.username}"

    @property
    def is_twilio_configured(self):
        return bool(
            self.twilio_account_sid
            and self.twilio_auth_token
            and not self.twilio_account_sid.startswith("your_")
        )

    @property
    def is_vapi_configured(self):
        return bool(self.vapi_api_key and not self.vapi_api_key.startswith("your_"))


class InterviewAssistant(models.Model):
    """Store created interview assistants"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assistants")
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="assistants",
        blank=True,
        null=True,
    )

    name = models.CharField(max_length=255)
    vapi_assistant_id = models.CharField(max_length=255, unique=True)
    first_message = models.TextField()
    voice_provider = models.CharField(max_length=50, default="openai")
    voice_id = models.CharField(max_length=100, default="nova")
    model_provider = models.CharField(max_length=50, default="openai")
    model = models.CharField(max_length=100, default="gpt-4")
    knowledge_text = models.TextField(blank=True, null=True)
    knowledge_urls = models.TextField(blank=True, null=True)
    configuration = models.JSONField(
        default=dict, blank=True
    )  # Store full Vapi configuration
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (User: {self.user.username})"

    class Meta:
        ordering = ["-created_at"]


class PhoneNumber(models.Model):
    """Store registered phone numbers"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="phone_numbers"
    )
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="phone_numbers",
        blank=True,
        null=True,
    )

    phone_number = models.CharField(max_length=20)
    vapi_phone_number_id = models.CharField(max_length=255, unique=True)
    twilio_sid = models.CharField(max_length=255, blank=True, null=True)
    friendly_name = models.CharField(max_length=255, blank=True, null=True)
    capabilities = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone_number} (User: {self.user.username})"

    class Meta:
        ordering = ["-created_at"]


class InterviewCall(models.Model):
    """Store call records and outcomes"""

    CALL_STATUS_CHOICES = [
        ("queued", "Queued"),
        ("ringing", "Ringing"),
        ("in-progress", "In Progress"),
        ("ended", "Ended"),
        ("failed", "Failed"),
    ]

    OUTCOME_STATUS_CHOICES = [
        ("answered", "Answered"),
        ("answered-brief", "Answered (Brief)"),
        ("voicemail", "Voicemail"),
        ("no-answer", "No Answer"),
        ("busy", "Busy"),
        ("declined", "Declined"),
        ("failed", "Failed"),
        ("in-progress", "In Progress"),
        ("ringing", "Ringing"),
        ("completed", "Completed"),
        ("unknown", "Unknown"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="calls")
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="calls",
        blank=True,
        null=True,
    )

    vapi_call_id = models.CharField(max_length=255, unique=True)
    assistant = models.ForeignKey(
        InterviewAssistant, on_delete=models.CASCADE, related_name="calls"
    )
    phone_number = models.ForeignKey(
        PhoneNumber, on_delete=models.CASCADE, related_name="calls"
    )
    customer_number = models.CharField(max_length=20)

    # Call details
    status = models.CharField(
        max_length=20, choices=CALL_STATUS_CHOICES, default="queued"
    )
    outcome_status = models.CharField(
        max_length=20, choices=OUTCOME_STATUS_CHOICES, blank=True, null=True
    )
    outcome_description = models.TextField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    # Call results
    transcript = models.JSONField(default=list, blank=True)
    transcript_text = models.TextField(blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    cost_breakdown = models.JSONField(default=dict, blank=True)
    duration_seconds = models.IntegerField(blank=True, null=True)
    end_reason = models.CharField(max_length=255, blank=True, null=True)

    # Raw data from Vapi
    raw_call_data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Call to {self.customer_number} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def duration_formatted(self):
        if self.duration_seconds:
            minutes = self.duration_seconds // 60
            seconds = self.duration_seconds % 60
            return f"{minutes}:{seconds:02d}"
        return None

    class Meta:
        ordering = ["-created_at"]


class ScheduledCall(models.Model):
    """Store scheduled call information"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scheduled_calls")
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="scheduled_calls",
        blank=True,
        null=True,
    )

    # Call configuration
    assistant = models.ForeignKey(
        InterviewAssistant, on_delete=models.CASCADE, related_name="scheduled_calls"
    )
    phone_number = models.ForeignKey(
        PhoneNumber, on_delete=models.CASCADE, related_name="scheduled_calls"
    )
    customer_number = models.CharField(max_length=20)
    
    # Scheduling information
    scheduled_time = models.DateTimeField()
    timezone = models.CharField(max_length=50, blank=True, null=True)  # Store the timezone used for scheduling
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    
    # Optional call metadata
    call_name = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Execution tracking
    actual_call = models.OneToOneField(
        InterviewCall, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name="scheduled_call"
    )
    execution_attempts = models.IntegerField(default=0)
    last_attempt_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Scheduled call to {self.customer_number} at {self.scheduled_time}"

    @property
    def is_due(self):
        """Check if the scheduled call is due for execution"""
        from django.utils import timezone
        return self.status == "scheduled" and self.scheduled_time <= timezone.now()

    class Meta:
        ordering = ["scheduled_time"]
