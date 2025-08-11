from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    APIConfiguration,
    InterviewAssistant,
    PhoneNumber,
    InterviewCall,
    Campaign,
    ScheduledCall,
)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["username"] = user.username
        token["email"] = user.email
        # ...

        return token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("username", "password", "password2")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def create(self, validated_data):
        user = User.objects.create(username=validated_data["username"])

        user.set_password(validated_data["password"])
        user.save()

        return user


class APIConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIConfiguration
        fields = [
            "twilio_account_sid",
            "twilio_auth_token",
            "vapi_api_key",
            "is_twilio_configured",
            "is_vapi_configured",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "twilio_auth_token": {"write_only": True},
            "vapi_api_key": {"write_only": True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Don't expose sensitive tokens in read operations
        if "twilio_auth_token" in data:
            data["twilio_auth_token"] = bool(instance.twilio_auth_token)
        if "vapi_api_key" in data:
            data["vapi_api_key"] = bool(instance.vapi_api_key)
        return data


class InterviewAssistantSerializer(serializers.ModelSerializer):
    campaign_name = serializers.CharField(source="campaign.name", read_only=True)
    
    class Meta:
        model = InterviewAssistant
        fields = [
            "id",
            "name",
            "vapi_assistant_id",
            "first_message",
            "voice_provider",
            "voice_id",
            "model_provider",
            "model",
            "knowledge_text",
            "knowledge_urls",
            "configuration",
            "campaign",
            "campaign_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "vapi_assistant_id", "created_at", "updated_at"]


class CreateAssistantSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, default="AI Assistant")
    first_message = serializers.CharField(default="Hello! How can I help you today?")
    voice_provider = serializers.CharField(max_length=50, default="openai")
    voice_id = serializers.CharField(max_length=100, default="nova")
    model_provider = serializers.CharField(max_length=50, default="openai")
    model = serializers.CharField(max_length=100, default="gpt-4")
    knowledge_text = serializers.CharField(required=False, allow_blank=True)
    knowledge_urls = serializers.CharField(required=False, allow_blank=True)
    campaign_id = serializers.IntegerField(required=False, allow_null=True)


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            "id",
            "user",
            "name",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CreateCampaignSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Campaign name cannot be empty.")
        return value


class PhoneNumberSerializer(serializers.ModelSerializer):
    campaign_name = serializers.CharField(source="campaign.name", read_only=True)
    
    class Meta:
        model = PhoneNumber
        fields = [
            "id",
            "phone_number",
            "vapi_phone_number_id",
            "twilio_sid",
            "friendly_name",
            "capabilities",
            "is_active",
            "campaign",
            "campaign_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "vapi_phone_number_id", "created_at", "updated_at"]


class RegisterPhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    campaign_id = serializers.IntegerField(required=False, allow_null=True)


class InterviewCallSerializer(serializers.ModelSerializer):
    assistant_name = serializers.CharField(source="assistant.name", read_only=True)
    phone_number_display = serializers.CharField(
        source="phone_number.phone_number", read_only=True
    )
    campaign_name = serializers.CharField(source="campaign.name", read_only=True)
    duration_formatted = serializers.ReadOnlyField()

    class Meta:
        model = InterviewCall
        fields = [
            "id",
            "vapi_call_id",
            "assistant",
            "assistant_name",
            "phone_number",
            "phone_number_display",
            "customer_number",
            "status",
            "outcome_status",
            "outcome_description",
            "campaign",
            "campaign_name",
            "created_at",
            "started_at",
            "ended_at",
            "transcript",
            "transcript_text",
            "cost",
            "cost_breakdown",
            "duration_seconds",
            "duration_formatted",
            "end_reason",
            "raw_call_data",
        ]
        read_only_fields = [
            "id",
            "vapi_call_id",
            "created_at",
            "started_at",
            "ended_at",
            "transcript",
            "transcript_text",
            "cost",
            "cost_breakdown",
            "duration_seconds",
            "end_reason",
            "raw_call_data",
        ]


class MakeCallSerializer(serializers.Serializer):
    customer_number = serializers.CharField(max_length=20)
    twilio_phone_number_id = serializers.CharField(max_length=255)
    vapi_assistant_id = serializers.CharField(max_length=255)


class ScheduledCallSerializer(serializers.ModelSerializer):
    assistant_name = serializers.CharField(source="assistant.name", read_only=True)
    phone_number_display = serializers.CharField(
        source="phone_number.phone_number", read_only=True
    )
    campaign_name = serializers.CharField(source="campaign.name", read_only=True)
    actual_call_id = serializers.CharField(source="actual_call.id", read_only=True)

    class Meta:
        model = ScheduledCall
        fields = [
            "id",
            "assistant",
            "assistant_name",
            "phone_number",
            "phone_number_display",
            "customer_number",
            "scheduled_time",
            "status",
            "call_name",
            "notes",
            "campaign",
            "campaign_name",
            "actual_call",
            "actual_call_id",
            "execution_attempts",
            "last_attempt_at",
            "error_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "actual_call",
            "execution_attempts",
            "last_attempt_at",
            "error_message",
            "created_at",
            "updated_at",
        ]


class CreateScheduledCallSerializer(serializers.Serializer):
    customer_number = serializers.CharField(max_length=20)
    twilio_phone_number_id = serializers.CharField(max_length=255)
    vapi_assistant_id = serializers.CharField(max_length=255)
    scheduled_time = serializers.DateTimeField()
    call_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_scheduled_time(self, value):
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future.")
        return value
