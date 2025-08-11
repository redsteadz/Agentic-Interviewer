from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.http import JsonResponse
from api.serializer import (
    CampaignSerializer,
    CreateCampaignSerializer,
    MyTokenObtainPairSerializer,
    RegisterSerializer,
    APIConfigurationSerializer,
    InterviewAssistantSerializer,
    CreateAssistantSerializer,
    PhoneNumberSerializer,
    RegisterPhoneNumberSerializer,
    InterviewCallSerializer,
    MakeCallSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import (
    APIConfiguration,
    Campaign,
    InterviewAssistant,
    PhoneNumber,
    InterviewCall,
)
import json
import logging
import requests
import os
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime

load_dotenv()
logger = logging.getLogger(__name__)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


@api_view(["GET"])
def getRoutes(request):
    routes = [
        "/api/token/",
        "/api/register/",
        "/api/token/refresh/",
        "/api/test/",
        "/api/config/",
        "/api/clear-config/",
        "/api/create-assistant/",
        "/api/assistants/",
        "/api/phone-numbers/",
        "/api/twilio-numbers/",
        "/api/register-phone-number/",
        "/api/make-call/",
        "/api/calls/",
        "/api/call/<call_id>/",
        "/api/campaign/",
    ]
    return Response(routes)


# Campaign view
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def campaignView(request):
    if request.method == "GET":
        campaigns = Campaign.objects.filter(user=request.user)
        serializer = CampaignSerializer(campaigns, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == "POST":
        serializer = CreateCampaignSerializer(data=request.data)
        print(f"Received campaign data: {serializer}")
        if serializer.is_valid():
            campaign = Campaign.objects.create(
                user=request.user,
                name=request.data.get("name"),
                description=request.data.get("description", ""),
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def testEndPoint(request):
    if request.method == "GET":
        data = f"Congratulation {request.user}, your API just responded to GET request"
        return Response({"response": data}, status=status.HTTP_200_OK)
    elif request.method == "POST":
        try:
            body = request.body.decode("utf-8")
            data = json.loads(body)
            if "text" not in data:
                return Response("Invalid JSON data", status.HTTP_400_BAD_REQUEST)
            text = data.get("text")
            data = f"Congratulation your API just responded to POST request with text: {text}"
            return Response({"response": data}, status=status.HTTP_200_OK)
        except json.JSONDecodeError:
            return Response("Invalid JSON data", status.HTTP_400_BAD_REQUEST)
    return Response("Invalid JSON data", status.HTTP_400_BAD_REQUEST)


class APIConfigurationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            config = APIConfiguration.objects.get(user=request.user)
            serializer = APIConfigurationSerializer(config)
            return Response(
                {
                    "twilio_configured": config.is_twilio_configured,
                    "vapi_configured": config.is_vapi_configured,
                    "twilio_account_sid": config.twilio_account_sid or "",
                    "vapi_api_key_set": bool(config.vapi_api_key),
                    **serializer.data,
                }
            )
        except APIConfiguration.DoesNotExist:
            return Response(
                {
                    "twilio_configured": False,
                    "vapi_configured": False,
                    "twilio_account_sid": "",
                    "vapi_api_key_set": False,
                }
            )

    def post(self, request):
        try:
            config, created = APIConfiguration.objects.get_or_create(user=request.user)

            # Update fields if provided
            if "twilio_account_sid" in request.data:
                config.twilio_account_sid = request.data["twilio_account_sid"]
            if "twilio_auth_token" in request.data:
                config.twilio_auth_token = request.data["twilio_auth_token"]
            if "vapi_api_key" in request.data:
                config.vapi_api_key = request.data["vapi_api_key"]

            config.save()

            result = {"success": True, "errors": []}

            # Test Twilio configuration
            if config.is_twilio_configured:
                try:
                    twilio_client = Client(
                        config.twilio_account_sid, config.twilio_auth_token
                    )
                    account = twilio_client.api.account.fetch()
                    result["twilio_status"] = (
                        f"Connected to Twilio account: {account.friendly_name}"
                    )
                except Exception as e:
                    result["errors"].append(f"Twilio error: {str(e)}")
                    result["success"] = False
            else:
                result["errors"].append("Twilio credentials not provided or invalid")

            # Test Vapi configuration
            if config.is_vapi_configured:
                result["vapi_status"] = "Vapi API key configured."
            else:
                result["errors"].append("Vapi API key not provided or invalid")
                result["success"] = False

            return Response(result)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def clear_config(request):
    try:
        APIConfiguration.objects.filter(user=request.user).delete()
        return Response({"success": True, "message": "Configuration cleared"})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateAssistantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get user's API configuration
            try:
                config = APIConfiguration.objects.get(user=request.user)
                if not config.is_vapi_configured:
                    return Response(
                        {"error": "Vapi API key not configured"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                vapi_key = config.vapi_api_key
            except APIConfiguration.DoesNotExist:
                return Response(
                    {"error": "Vapi API key not configured"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = CreateAssistantSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            data = serializer.validated_data
            print(f"Received data: {data}")
            assistant_name = data.get("name", "AI Assistant").strip() or "AI Assistant"
            voice_provider = data.get("voice_provider", "openai").strip() or "openai"
            voice_id = data.get("voice_id", "nova").strip() or "nova"
            model_provider = data.get("model_provider", "openai").strip() or "openai"
            model = data.get("model", "gpt-4").strip() or "gpt-4"
            first_message = (
                data.get("first_message", "Hello! How can I help you today?").strip()
                or "Hello! How can I help you today?"
            )
            knowledge_text = data.get("knowledge_text", "")
            knowledge_urls = data.get("knowledge_urls", "")
            campaign_id = data.get("campaign_id")

            # Get campaign if provided
            campaign = None
            if campaign_id:
                try:
                    campaign = Campaign.objects.get(id=campaign_id, user=request.user)
                except Campaign.DoesNotExist:
                    return Response(
                        {"error": "Campaign not found or does not belong to user"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            logger.info(
                f"Received data: name='{assistant_name}', voice_provider='{voice_provider}', voice_id='{voice_id}', model_provider='{model_provider}', model='{model}', first_message='{first_message}'"
            )

            headers = {
                "Authorization": f"Bearer {vapi_key}",
                "Content-Type": "application/json",
            }

            system_message = self.create_interview_system_message(
                knowledge_text, knowledge_urls
            )
            professional_first_message = self.create_professional_first_message(
                first_message, knowledge_text, knowledge_urls
            )

            payload = {
                "name": assistant_name,
                "firstMessage": professional_first_message,
                "model": {
                    "provider": model_provider,
                    "model": model,
                },
                "voice": {"provider": voice_provider, "voiceId": voice_id},
                "backgroundSound": "off",
                "backgroundDenoisingEnabled": True,
                "silenceTimeoutSeconds": 30,
                "maxDurationSeconds": 1800,
                "voicemailDetection": {"provider": "vapi"},
                "recordingEnabled": False,
                "clientMessages": [],
                "serverMessages": [],
            }

            if voice_provider == "openai":
                payload["transcriber"] = {
                    "provider": "deepgram",
                    "model": "nova-2",
                    "language": "en-US",
                }
                payload.update(
                    {
                        "analysisPlan": {
                            "summaryPlan": {"enabled": False},
                            "structuredDataPlan": {"enabled": False},
                        }
                    }
                )

            logger.info(f"Creating assistant with payload: {payload}")
            response = requests.post(
                "https://api.vapi.ai/assistant", headers=headers, json=payload
            )

            logger.info(f"Vapi API response status: {response.status_code}")

            try:
                response_data = response.json()
                logger.info(f"Vapi API response body: {response_data}")
            except ValueError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response text: {response.text}")
                return Response(
                    {"error": f"Invalid JSON response from Vapi API: {response.text}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            if not response.ok:
                error_message = (
                    response_data.get("message", response.text)
                    if response_data
                    else response.text
                )
                logger.error(
                    f"Vapi API error: {response.status_code} - {error_message}"
                )
                return Response(
                    {
                        "error": f"Vapi API error ({response.status_code}): {error_message}"
                    },
                    status=response.status_code,
                )

            # Save assistant to database
            assistant = InterviewAssistant.objects.create(
                user=request.user,
                campaign=campaign,
                name=assistant_name,
                vapi_assistant_id=response_data.get("id"),
                first_message=first_message,
                voice_provider=voice_provider,
                voice_id=voice_id,
                model_provider=model_provider,
                model=model,
                knowledge_text=knowledge_text,
                knowledge_urls=knowledge_urls,
                configuration=payload,
            )

            logger.info(
                f"Assistant created successfully. Response keys: {list(response_data.keys()) if response_data else 'None'}"
            )

            return Response(
                {
                    "success": True,
                    "assistant_data": response_data,
                    "assistant": InterviewAssistantSerializer(assistant).data,
                    "response_debug": {
                        "status": response.status_code,
                        "keys": list(response_data.keys()) if response_data else [],
                    },
                }
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating assistant: {e}")
            return Response(
                {"error": f"Vapi API error: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.error(f"Error creating assistant: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create_interview_system_message(self, knowledge_text="", knowledge_urls=""):
        base_instructions = """You are a professional interviewer conducting a formal interview. Your role is to:

1. NEVER mention that you are an AI, artificial intelligence, or automated system
2. Speak in a professional, serious, and human-like manner
3. ASK QUESTIONS - DO NOT teach or explain concepts
4. Listen to answers and ask follow-up questions based on responses
5. Evaluate the candidate's knowledge through questioning
6. Keep your responses brief and focused on asking the next question
7. Maintain a respectful but professional tone throughout
8. End calls gracefully when the interview is complete

CRITICAL INTERVIEWER BEHAVIOR:
- Your job is to ASK QUESTIONS, not provide answers or explanations
- When the candidate gives an incomplete answer, ask "Can you elaborate on that?"
- When the candidate seems unsure, ask "What's your understanding of [topic]?"
- After each answer, ask a related follow-up question
- DO NOT teach, explain, or provide correct answers
- Focus on evaluating their knowledge, not educating them
- Ask one question at a time and wait for their response
- If they ask you a question, redirect: "I'm here to learn about your knowledge. Can you tell me..."

Interview Flow:
- Start with introductory questions
- Progress to more detailed technical questions
- Ask follow-up questions based on their answers
- Probe areas where they seem weak or strong
- End with summary questions about their experience"""

        knowledge_section = ""
        if knowledge_text.strip():
            knowledge_section += f"\n\nKNOWLEDGE BASE - TEXT:\n{knowledge_text.strip()}"

        if knowledge_urls.strip():
            urls_list = [
                url.strip() for url in knowledge_urls.split("\n") if url.strip()
            ]
            if urls_list:
                knowledge_section += (
                    f"\n\nKNOWLEDGE BASE - REFERENCE URLS:\n"
                    + "\n".join(f"- {url}" for url in urls_list)
                )
                knowledge_section += "\nNote: Use these URLs as reference for topic context, but focus on the interview dialogue."

        if not knowledge_section:
            knowledge_section = "\n\nNote: Conduct a general professional interview since no specific knowledge base was provided."

        return base_instructions + knowledge_section

    def create_professional_first_message(
        self, base_message, knowledge_text="", knowledge_urls=""
    ):
        professional_message = base_message

        if knowledge_text.strip():
            topics = []
            lines = knowledge_text.split("\n")
            for line in lines:
                if line.strip() and ("?" in line or ":" in line):
                    topic = line.split("?")[0].split(":")[0].strip()
                    if len(topic) < 50 and topic not in topics:
                        topics.append(topic)

            if topics:
                topic_context = f" Today we'll be focusing on {', '.join(topics[:3])}."
                professional_message += topic_context

        professional_message += " I'm here to conduct a thorough and professional evaluation. Please feel free to take your time with your responses."

        return professional_message


class AssistantListView(generics.ListAPIView):
    serializer_class = InterviewAssistantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = InterviewAssistant.objects.filter(user=self.request.user)
        campaign_id = self.request.query_params.get('campaign_id')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        return queryset


class VapiPhoneNumbersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get user's API configuration
            try:
                config = APIConfiguration.objects.get(user=request.user)
                if not config.is_vapi_configured:
                    return Response(
                        {"error": "Vapi API key not configured"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                vapi_key = config.vapi_api_key
            except APIConfiguration.DoesNotExist:
                return Response(
                    {"error": "Vapi API key not configured"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            headers = {
                "Authorization": f"Bearer {vapi_key}",
                "Content-Type": "application/json",
            }

            response = requests.get("https://api.vapi.ai/phone-number", headers=headers)
            response.raise_for_status()

            phone_numbers = response.json()

            return Response({"success": True, "phone_numbers": phone_numbers})

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching phone numbers: {e}")
            return Response(
                {"error": f"Vapi API error: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.error(f"Error fetching phone numbers: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TwilioPhoneNumbersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get user's API configuration
            try:
                config = APIConfiguration.objects.get(user=request.user)
                if not config.is_twilio_configured:
                    return Response(
                        {"error": "Twilio credentials not configured"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                twilio_client = Client(
                    config.twilio_account_sid, config.twilio_auth_token
                )
            except APIConfiguration.DoesNotExist:
                return Response(
                    {"error": "Twilio credentials not configured"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            numbers = twilio_client.incoming_phone_numbers.list()

            twilio_numbers = []
            for number in numbers:
                twilio_numbers.append(
                    {
                        "sid": number.sid,
                        "phone_number": number.phone_number,
                        "friendly_name": number.friendly_name,
                        "capabilities": {
                            "voice": number.capabilities["voice"],
                            "sms": number.capabilities["sms"],
                            "mms": number.capabilities["mms"],
                            "fax": number.capabilities["fax"],
                        },
                    }
                )

            return Response({"success": True, "twilio_numbers": twilio_numbers})

        except Exception as e:
            logger.error(f"Error fetching Twilio numbers: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RegisterPhoneNumberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get user's API configuration
            try:
                config = APIConfiguration.objects.get(user=request.user)
                if not config.is_vapi_configured or not config.is_twilio_configured:
                    return Response(
                        {
                            "error": "Both Vapi API key and Twilio credentials must be configured"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                vapi_key = config.vapi_api_key
                twilio_client = Client(
                    config.twilio_account_sid, config.twilio_auth_token
                )
            except APIConfiguration.DoesNotExist:
                return Response(
                    {"error": "API configuration not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = RegisterPhoneNumberSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            phone_number = serializer.validated_data["phone_number"]
            campaign_id = serializer.validated_data.get("campaign_id")

            # Get campaign if provided
            campaign = None
            if campaign_id:
                try:
                    campaign = Campaign.objects.get(id=campaign_id, user=request.user)
                except Campaign.DoesNotExist:
                    return Response(
                        {"error": "Campaign not found or does not belong to user"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            headers = {
                "Authorization": f"Bearer {vapi_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "provider": "twilio",
                "number": phone_number,
                "twilioAccountSid": config.twilio_account_sid,
                "twilioAuthToken": config.twilio_auth_token,
            }

            logger.info(f"Registering phone number with Vapi: {payload}")
            response = requests.post(
                "https://api.vapi.ai/phone-number", headers=headers, json=payload
            )

            logger.info(
                f"Vapi phone number registration response: {response.status_code}"
            )

            try:
                response_data = response.json()
                logger.info(f"Vapi phone number response body: {response_data}")
            except ValueError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                return Response(
                    {"error": f"Invalid JSON response from Vapi API: {response.text}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            if not response.ok:
                error_message = (
                    response_data.get("message", response.text)
                    if response_data
                    else response.text
                )
                logger.error(
                    f"Vapi API error: {response.status_code} - {error_message}"
                )
                return Response(
                    {
                        "error": f"Vapi API error ({response.status_code}): {error_message}"
                    },
                    status=response.status_code,
                )

            # Save phone number to database
            phone_number_obj = PhoneNumber.objects.create(
                user=request.user,
                campaign=campaign,
                phone_number=phone_number,
                vapi_phone_number_id=response_data.get("id"),
                friendly_name=response_data.get("name", phone_number),
            )

            logger.info(
                f"Phone number registered successfully: {response_data.get('id')}"
            )

            return Response(
                {
                    "success": True,
                    "vapi_phone_number": response_data,
                    "phone_number": PhoneNumberSerializer(phone_number_obj).data,
                }
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Error registering phone number: {e}")
            return Response(
                {"error": f"Vapi API error: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.error(f"Error registering phone number: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PhoneNumberListView(generics.ListAPIView):
    serializer_class = PhoneNumberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = PhoneNumber.objects.filter(user=self.request.user, is_active=True)
        campaign_id = self.request.query_params.get('campaign_id')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        return queryset


class MakeCallView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get user's API configuration
            try:
                config = APIConfiguration.objects.get(user=request.user)
                if not config.is_vapi_configured:
                    return Response(
                        {
                            "error": "Vapi API key not configured. Please set it in the API Configuration section."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                vapi_key = config.vapi_api_key
            except APIConfiguration.DoesNotExist:
                return Response(
                    {"error": "Vapi API key not configured"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = MakeCallSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            data = serializer.validated_data
            customer_number = data["customer_number"]
            twilio_phone_number_id = data["twilio_phone_number_id"]
            vapi_assistant_id = data["vapi_assistant_id"]

            # Verify assistant and phone number belong to user
            try:
                assistant = InterviewAssistant.objects.get(
                    user=request.user, vapi_assistant_id=vapi_assistant_id
                )
                phone_number = PhoneNumber.objects.get(
                    user=request.user, vapi_phone_number_id=twilio_phone_number_id
                )
            except (InterviewAssistant.DoesNotExist, PhoneNumber.DoesNotExist):
                return Response(
                    {
                        "error": "Assistant or phone number not found or does not belong to user"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            headers = {
                "Authorization": f"Bearer {vapi_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "phoneNumberId": twilio_phone_number_id,
                "assistantId": vapi_assistant_id,
                "customer": {"number": customer_number},
            }

            logger.info(f"Making call with payload: {payload}")
            response = requests.post(
                "https://api.vapi.ai/call", headers=headers, json=payload
            )

            logger.info(f"Vapi call API response status: {response.status_code}")

            try:
                response_data = response.json()
                logger.info(f"Vapi call API response body: {response_data}")
            except ValueError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response text: {response.text}")
                return Response(
                    {"error": f"Invalid JSON response from Vapi API: {response.text}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            if not response.ok:
                error_message = (
                    response_data.get("message", response.text)
                    if response_data
                    else response.text
                )
                logger.error(
                    f"Vapi call API error: {response.status_code} - {error_message}"
                )
                return Response(
                    {
                        "error": f"Vapi call API error ({response.status_code}): {error_message}"
                    },
                    status=response.status_code,
                )

            # Save call to database
            # Use campaign from assistant or phone number (prefer assistant)
            campaign = assistant.campaign or phone_number.campaign
            call = InterviewCall.objects.create(
                user=request.user,
                campaign=campaign,
                vapi_call_id=response_data.get("id"),
                assistant=assistant,
                phone_number=phone_number,
                customer_number=customer_number,
                status=response_data.get("status", "queued"),
                raw_call_data=response_data,
            )

            logger.info(f"Outbound call initiated via Vapi: {response_data.get('id')}")

            return Response(
                {
                    "success": True,
                    "call_id": response_data.get("id"),
                    "status": "initiated",
                    "call_data": response_data,
                    "call": InterviewCallSerializer(call).data,
                }
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Error making Vapi call: {e}")
            return Response(
                {"error": f"Vapi API error: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.error(f"Error making call: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CallDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, call_id):
        try:
            # Get user's API configuration
            try:
                config = APIConfiguration.objects.get(user=request.user)
                if not config.is_vapi_configured:
                    return Response(
                        {"error": "Vapi API key not configured"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                vapi_key = config.vapi_api_key
            except APIConfiguration.DoesNotExist:
                return Response(
                    {"error": "Vapi API key not configured"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            headers = {
                "Authorization": f"Bearer {vapi_key}",
                "Content-Type": "application/json",
            }

            logger.info(f"Fetching call details for call ID: {call_id}")
            response = requests.get(
                f"https://api.vapi.ai/call/{call_id}", headers=headers
            )

            logger.info(f"Vapi get call response status: {response.status_code}")

            try:
                call_data = response.json()
                logger.info(
                    f"Vapi call data keys: {list(call_data.keys()) if call_data else 'None'}"
                )
            except ValueError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                return Response(
                    {"error": f"Invalid JSON response from Vapi API: {response.text}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            if not response.ok:
                error_message = (
                    call_data.get("message", response.text)
                    if call_data
                    else response.text
                )
                logger.error(
                    f"Vapi get call API error: {response.status_code} - {error_message}"
                )
                return Response(
                    {
                        "error": f"Vapi API error ({response.status_code}): {error_message}"
                    },
                    status=response.status_code,
                )

            # Update local call record
            try:
                call = InterviewCall.objects.get(
                    vapi_call_id=call_id, user=request.user
                )
                call = self.update_call_from_vapi_data(call, call_data)
            except InterviewCall.DoesNotExist:
                call = None

            call_outcome = self.determine_call_outcome(call_data)

            call_info = self.format_call_info(call_data, call_outcome)

            response_data = {"success": True, "call": call_info, "raw_data": call_data}

            if call:
                response_data["call_db"] = InterviewCallSerializer(call).data

            return Response(response_data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching call details: {e}")
            return Response(
                {"error": f"Vapi API error: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.error(f"Error fetching call details: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update_call_from_vapi_data(self, call, call_data):
        """Update local call record with data from Vapi API"""
        call.status = call_data.get("status", call.status)
        call.raw_call_data = call_data

        if call_data.get("startedAt"):
            try:
                call.started_at = datetime.fromisoformat(
                    call_data["startedAt"].replace("Z", "+00:00")
                )
            except:
                pass

        if call_data.get("endedAt"):
            try:
                call.ended_at = datetime.fromisoformat(
                    call_data["endedAt"].replace("Z", "+00:00")
                )
            except:
                pass

        if call_data.get("transcript"):
            call.transcript = call_data["transcript"]
            if isinstance(call_data["transcript"], list):
                call.transcript_text = "\n".join(
                    [
                        f"[{item.get('timestamp', 'Unknown')}] {item.get('role', 'Unknown')}: {item.get('message', '')}"
                        for item in call_data["transcript"]
                        if isinstance(item, dict)
                    ]
                )

        if call_data.get("cost"):
            call.cost = call_data["cost"]

        if call_data.get("costBreakdown"):
            call.cost_breakdown = call_data["costBreakdown"]

        if call_data.get("endedReason"):
            call.end_reason = call_data["endedReason"]

        # Calculate duration
        if call.started_at and call.ended_at:
            duration = call.ended_at - call.started_at
            call.duration_seconds = int(duration.total_seconds())

        # Determine outcome
        call_outcome = self.determine_call_outcome(call_data)
        call.outcome_status = call_outcome["status"]
        call.outcome_description = call_outcome["description"]

        call.save()
        return call

    def determine_call_outcome(self, call_data):
        """Determine call outcome based on Vapi data"""
        status = call_data.get("status", "").lower()
        end_reason = (
            call_data.get("endedReason", "").lower()
            if call_data.get("endedReason")
            else ""
        )
        started_at = call_data.get("startedAt")
        ended_at = call_data.get("endedAt")
        cost = call_data.get("cost", 0)
        transcript = call_data.get("transcript")

        logger.info(
            f"Call outcome analysis - Status: {status}, EndReason: {end_reason}, Cost: {cost}, HasTranscript: {bool(transcript)}"
        )

        if status == "failed":
            if "busy" in end_reason:
                return {"status": "busy", "description": "Phone was busy"}
            elif "no-answer" in end_reason or "timeout" in end_reason:
                return {
                    "status": "no-answer",
                    "description": "No answer - call timed out",
                }
            elif "declined" in end_reason or "rejected" in end_reason:
                return {"status": "declined", "description": "Call was declined"}
            else:
                return {
                    "status": "failed",
                    "description": f'Call failed - {end_reason or "Unknown reason"}',
                }

        elif status == "ended":
            duration_seconds = None
            if started_at and ended_at:
                try:
                    start_time = datetime.fromisoformat(
                        started_at.replace("Z", "+00:00")
                    )
                    end_time = datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
                    duration_seconds = (end_time - start_time).total_seconds()
                except Exception as e:
                    logger.warning(
                        f"Could not calculate call duration for outcome: {e}"
                    )

            if transcript and len(transcript) > 0:
                transcript_text = ""
                has_user_speech = False
                assistant_only = True

                if isinstance(transcript, list):
                    for item in transcript:
                        if isinstance(item, dict):
                            role = item.get("role", "")
                            message = item.get("message", "").strip().lower()
                            transcript_text += f"{role}: {message} "

                            if role == "user" and message:
                                has_user_speech = True
                                assistant_only = False
                            elif role == "assistant" and message:
                                assistant_only = True

                voicemail_indicators = [
                    "voicemail",
                    "voice mail",
                    "leave a message",
                    "after the beep",
                    "beep",
                    "unavailable",
                    "cannot take your call",
                    "please record",
                    "mailbox",
                    "greeting",
                    "automated message",
                ]

                is_likely_voicemail = any(
                    indicator in transcript_text.lower()
                    for indicator in voicemail_indicators
                )

                if assistant_only and not has_user_speech:
                    if duration_seconds and duration_seconds < 60:
                        return {
                            "status": "voicemail",
                            "description": "Reached voicemail - message left by assistant",
                        }
                    elif is_likely_voicemail:
                        return {
                            "status": "voicemail",
                            "description": "Reached voicemail - automated greeting detected",
                        }

                if has_user_speech:
                    if duration_seconds and duration_seconds > 30:
                        return {
                            "status": "answered",
                            "description": "Call was answered - conversation recorded",
                        }
                    else:
                        return {
                            "status": "answered-brief",
                            "description": "Call answered but ended quickly",
                        }

            if duration_seconds is not None:
                if duration_seconds < 5:
                    return {
                        "status": "no-answer",
                        "description": "Call ended immediately - likely not answered",
                    }
                elif duration_seconds < 15:
                    if cost > 0:
                        return {
                            "status": "declined",
                            "description": "Call was declined quickly",
                        }
                    else:
                        return {
                            "status": "no-answer",
                            "description": "Call not answered",
                        }
                elif duration_seconds < 45:
                    if end_reason and "customer-ended-call" in end_reason:
                        return {
                            "status": "answered-brief",
                            "description": "Call answered but customer hung up quickly",
                        }
                    else:
                        return {
                            "status": "voicemail",
                            "description": "Likely reached voicemail",
                        }
                else:
                    return {"status": "answered", "description": "Call was answered"}

            if cost == 0:
                return {
                    "status": "no-answer",
                    "description": "No cost incurred - call not connected",
                }
            elif cost < 0.01:
                return {
                    "status": "declined",
                    "description": "Call declined - minimal cost",
                }
            else:
                if "customer-ended-call" in end_reason:
                    return {
                        "status": "answered",
                        "description": "Call completed by customer",
                    }
                else:
                    return {
                        "status": "voicemail",
                        "description": "Likely reached voicemail",
                    }

            return {"status": "completed", "description": "Call completed"}

        elif status in ["queued", "ringing"]:
            return {"status": "ringing", "description": "Call is ringing..."}
        elif status == "in-progress":
            return {"status": "in-progress", "description": "Call is active"}

        else:
            return {
                "status": "unknown",
                "description": f"Unknown call status: {status}",
            }

    def format_call_info(self, call_data, call_outcome):
        """Format call info for frontend"""
        transcript = None
        transcript_text = ""

        if "transcript" in call_data and call_data["transcript"]:
            transcript = call_data["transcript"]
            if isinstance(transcript, list):
                transcript_text = "\n".join(
                    [
                        f"[{item.get('timestamp', 'Unknown')}] {item.get('role', 'Unknown')}: {item.get('message', '')}"
                        for item in transcript
                        if isinstance(item, dict)
                    ]
                )
            else:
                transcript_text = str(transcript)

        call_info = {
            "id": call_data.get("id"),
            "status": call_data.get("status"),
            "outcome": call_outcome,
            "type": call_data.get("type"),
            "phoneNumber": call_data.get("phoneNumber", {}).get("number"),
            "customer": call_data.get("customer", {}).get("number"),
            "createdAt": call_data.get("createdAt"),
            "updatedAt": call_data.get("updatedAt"),
            "startedAt": call_data.get("startedAt"),
            "endedAt": call_data.get("endedAt"),
            "cost": call_data.get("cost"),
            "costBreakdown": call_data.get("costBreakdown"),
            "transcript": transcript,
            "transcript_text": transcript_text,
            "duration": call_data.get("endedAt") and call_data.get("startedAt"),
            "assistant": call_data.get("assistant", {}),
            "endReason": call_data.get("endedReason"),
            "messages": call_data.get("messages", []),
        }

        if call_data.get("startedAt") and call_data.get("endedAt"):
            try:
                start_time = datetime.fromisoformat(
                    call_data["startedAt"].replace("Z", "+00:00")
                )
                end_time = datetime.fromisoformat(
                    call_data["endedAt"].replace("Z", "+00:00")
                )
                duration_seconds = (end_time - start_time).total_seconds()
                call_info["duration_seconds"] = duration_seconds
                call_info["duration_formatted"] = (
                    f"{int(duration_seconds // 60)}:{int(duration_seconds % 60):02d}"
                )
            except Exception as e:
                logger.warning(f"Could not calculate call duration: {e}")

        return call_info


class CallListView(generics.ListAPIView):
    serializer_class = InterviewCallSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = InterviewCall.objects.filter(user=self.request.user)
        campaign_id = self.request.query_params.get('campaign_id')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        return queryset
