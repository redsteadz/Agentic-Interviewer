from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication

# Custom authentication class that disables CSRF for webhooks
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening
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
    ScheduledCallSerializer,
    CreateScheduledCallSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import (
    APIConfiguration,
    Campaign,
    InterviewAssistant,
    PhoneNumber,
    InterviewCall,
    ScheduledCall,
)
import json
import logging
import requests
import os
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime
import logging
import requests
import json
import hmac
import hashlib
import time
from django.conf import settings

load_dotenv()
logger = logging.getLogger(__name__)

# Server URL configuration - can be overridden via environment variables
VAPI_SERVER_URL = os.getenv('VAPI_SERVER_URL', 'https://your-domain.com/api/webhook/vapi/')
VAPI_SERVER_URL_SECRET = os.getenv('VAPI_SERVER_URL_SECRET')

# Webhook logging configuration
WEBHOOK_LOG_FOLDER = os.path.join(settings.BASE_DIR, 'webhook_logs')
if not os.path.exists(WEBHOOK_LOG_FOLDER):
    os.makedirs(WEBHOOK_LOG_FOLDER, exist_ok=True)


def save_webhook_event(event_type, event):
    """
    Save webhook event data to a JSON file for debugging and auditing
    """
    try:
        os.makedirs(WEBHOOK_LOG_FOLDER, exist_ok=True)
        
        # Use event id or timestamp to create a unique filename
        event_name = event_type.replace('.', '_')
        event_id = event.get('id', 'no_event_id')
        
        # Add timestamp to make the filename even more unique
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # Construct filename
        filename = f"{event_name}_{event_id}_{timestamp}.json"
        filepath = os.path.join(WEBHOOK_LOG_FOLDER, filename)
        
        # Write the event data to the file
        with open(filepath, 'w') as f:
            json.dump(event, f, indent=4)

        logger.info(f"Webhook event saved to: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Failed to save webhook event: {str(e)}")
        return None


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
        "/api/schedule-call/",
        "/api/scheduled-calls/",
        "/api/scheduled-call/<call_id>/",
        "/api/execute-scheduled-calls/",
        "/api/analyze-website/",
        "/api/elevenlabs-voices/",
        "/api/process-transcript/",
        "/api/webhook/vapi/",
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
                    "openai_configured": config.is_openai_configured,
                    "twilio_account_sid": config.twilio_account_sid or "",
                    "vapi_api_key_set": bool(config.vapi_api_key),
                    "openai_api_key_set": bool(config.openai_api_key),
                    **serializer.data,
                }
            )
        except APIConfiguration.DoesNotExist:
            return Response(
                {
                    "twilio_configured": False,
                    "vapi_configured": False,
                    "openai_configured": False,
                    "twilio_account_sid": "",
                    "vapi_api_key_set": False,
                    "openai_api_key_set": False,
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
            if "openai_api_key" in request.data:
                config.openai_api_key = request.data["openai_api_key"]

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
            system_prompt = data.get("system_prompt", "")
            end_call_phrases = data.get("end_call_phrases", [])

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

            # Use custom system prompt if provided, otherwise use default
            if system_prompt.strip():
                system_message = system_prompt
                # Append structured knowledge if available
                if knowledge_text.strip():
                    formatted_articles = self.format_articles_for_interview(knowledge_text)
                    system_message += f"\n\n📚 KNOWLEDGE BASE - ARTICLES TO PROCESS:\n{formatted_articles}"
                if knowledge_urls.strip():
                    system_message += f"\n\nREFERENCE URLS:\n{knowledge_urls}"
            else:
                system_message = self.create_interview_system_message(
                    knowledge_text, knowledge_urls
                )
                # If knowledge is provided, add structured articles
                if knowledge_text.strip():
                    formatted_articles = self.format_articles_for_interview(knowledge_text)
                    system_message += f"\n\n📚 KNOWLEDGE BASE - ARTICLES TO PROCESS:\n{formatted_articles}"
            professional_first_message = self.create_professional_first_message(
                first_message, knowledge_text, knowledge_urls
            )

            payload = {
                "name": assistant_name,
                "firstMessage": professional_first_message,
                "model": {
                    "provider": model_provider,
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": system_message
                        }
                    ]
                },
                "voice": {"provider": voice_provider, "voiceId": voice_id},
                "backgroundSound": "off",
                "backgroundDenoisingEnabled": True,
                "silenceTimeoutSeconds": 30,
                "maxDurationSeconds": 1800,
                "voicemailDetection": {"provider": "vapi"},
                "recordingEnabled": True,
                "clientMessages": [],
                "serverMessages": [],
                "serverUrl": VAPI_SERVER_URL,
                "serverUrlSecret": VAPI_SERVER_URL_SECRET
            }

            # Add end call phrases if provided
            if end_call_phrases and len(end_call_phrases) > 0:
                payload["endCallPhrases"] = end_call_phrases

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

    def format_articles_for_interview(self, knowledge_text):
        """Format knowledge text into numbered articles for sequential processing"""
        if not knowledge_text.strip():
            return ""
        
        # Split knowledge by common delimiters (double newlines, article markers, etc.)
        articles = []
        
        # Try to detect if articles are already separated
        if "\n\n" in knowledge_text:
            potential_articles = knowledge_text.split("\n\n")
        elif "Article" in knowledge_text and knowledge_text.count("Article") > 1:
            # Split by "Article" keyword
            parts = knowledge_text.split("Article")
            potential_articles = [("Article" + part).strip() for part in parts[1:]]
        else:
            # Split by sentences and group into articles (every 3-5 sentences)
            sentences = knowledge_text.split(". ")
            chunk_size = 4
            potential_articles = [
                ". ".join(sentences[i:i+chunk_size]) + "."
                for i in range(0, len(sentences), chunk_size)
            ]
        
        # Clean and number the articles
        article_number = 1
        for article in potential_articles:
            cleaned_article = article.strip()
            if len(cleaned_article) > 50:  # Only include substantial content
                articles.append(f"\n=== ARTICLE {article_number} ===\n{cleaned_article}\n")
                article_number += 1
        
        # If no clear articles found, treat entire text as one article
        if not articles:
            articles.append(f"\n=== ARTICLE 1 ===\n{knowledge_text.strip()}\n")
        
        return "\n".join(articles)

    def extract_article_titles(self, knowledge_text):
        """Extract article titles from knowledge text"""
        titles = []
        
        # Look for different title patterns in the knowledge text
        lines = knowledge_text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Pattern 1: "=== ARTICLE X ===" followed by title
            if line.startswith('=== ARTICLE') and line.endswith('==='):
                # Check if next line is the title
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith('==='):
                        titles.append(next_line)
            
            # Pattern 2: Direct article headers like "Article 1: Title"
            elif line.startswith('Article ') and ':' in line:
                title_part = line.split(':', 1)[1].strip()
                if title_part:
                    titles.append(title_part)
            
            # Pattern 3: Look for prominent headings (lines that are short and seem like titles)
            elif len(line) > 10 and len(line) < 100 and not line.endswith('.'):
                # Check if this looks like a title (no periods, capitalized, etc.)
                if line[0].isupper() and '.' not in line and len(line.split()) <= 10:
                    titles.append(line)
        
        # If no titles found, try to extract from article content
        if not titles:
            articles = knowledge_text.split('=== ARTICLE')
            for i, article in enumerate(articles[1:], 1):  # Skip first empty part
                lines_in_article = article.split('\n')
                for line in lines_in_article:
                    line = line.strip()
                    if line and not line.startswith('===') and len(line) > 5:
                        titles.append(f"Article {i}")
                        break
        
        # Format titles for the prompt
        if titles:
            numbered_titles = []
            for i, title in enumerate(titles, 1):
                numbered_titles.append(f"Article {i}: {title}")
            return '\n'.join(numbered_titles)
        else:
            return "No specific article titles found - use content-based titles"

    def process_transcript_with_articles(self, transcript_text, knowledge_text, user=None):
        """Process transcript using OpenAI to extract structured article information"""
        if not transcript_text or not knowledge_text:
            return {"error": "Missing transcript or knowledge text"}
        
        # Get user's OpenAI API key if user is provided
        openai_api_key = None
        if user:
            try:
                config = APIConfiguration.objects.get(user=user)
                if config.is_openai_configured:
                    openai_api_key = config.openai_api_key
                else:
                    return {"error": "OpenAI API key not configured for this user"}
            except APIConfiguration.DoesNotExist:
                return {"error": "API configuration not found for this user"}
        else:
            # Fallback to global settings
            from django.conf import settings
            openai_api_key = settings.OPENAI_API_KEY
        
        if not openai_api_key:
            return {"error": "OpenAI API key not available"}
        
        # Format articles for processing and extract titles
        formatted_articles = self.format_articles_for_interview(knowledge_text)
        article_titles = self.extract_article_titles(knowledge_text)
        
        # Create OpenAI prompt for transcript processing
        processing_prompt = f"""
You are a transcript analysis agent. You have been provided with:
1. A complete interview transcript
2. The articles that were discussed during the interview

Your task is to analyze the transcript and extract structured information for each article that was discussed.

📚 ARTICLES THAT WERE AVAILABLE:
{formatted_articles}

📝 INTERVIEW TRANSCRIPT:
{transcript_text}

For each article that was discussed in the transcript, provide the following structured output (use EXACT titles provided):

Article [Number]:
Article [Number] Title: [Use the exact title from the knowledge base - do not modify]
Article [Number] Summary: [Provide a concise 2-3 sentence summary of the article's main points]
Article [Number] Keyword Phrase: [Identify 1-3 key phrases or terms from the article]
Article [Number] Transcript: [Document the candidate's responses, insights, and discussion about this specific article]

AVAILABLE ARTICLE TITLES:
{article_titles}

CRITICAL NUMBERING INSTRUCTIONS:
- Number articles sequentially starting from 1 (Article 1, Article 2, Article 3, etc.)
- Do NOT use the original article numbers from the knowledge base
- Use consecutive numbering based on the order discussed in the interview
- If only 2 articles are discussed, use "Article 1" and "Article 2" (not Article 1 and Article 3)

IMPORTANT INSTRUCTIONS:
- Use the EXACT article titles provided in the "AVAILABLE ARTICLE TITLES" section
- Only include articles that were actually discussed in the transcript
- If an article was not discussed, do not include it in your output
- Extract the candidate's actual responses and insights from the transcript
- Use plain text format with colons (NO bold formatting)
- If no articles were discussed, state "No articles were discussed in this interview"
"""

        try:
            # Use OpenAI to process the transcript (v1.0+ API)
            import openai
            
            # Create client with explicit parameters only
            client = openai.OpenAI(
                api_key=openai_api_key,
                timeout=30.0
            )
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional transcript analysis agent."},
                    {"role": "user", "content": processing_prompt}
                ],
                temperature=0.3
            )
            
            return {
                "success": True,
                "structured_output": response.choices[0].message.content,
                "articles_processed": formatted_articles
            }
            
        except Exception as e:
            return {
                "error": f"Failed to process transcript: {str(e)}"
            }

    def create_interview_system_message(self, knowledge_text="", knowledge_urls=""):
        base_instructions = """🎤 YOU ARE ON A LIVE VOICE CALL INTERVIEW 🎤
You are conducting a REAL-TIME PHONE CONVERSATION with a candidate. This is NOT text messaging or chat.

📞 VOICE CALL REQUIREMENTS:
- SPEAK naturally as if talking on the phone
- Use verbal communication style (not written text style)
- Keep responses conversational and engaging for voice
- Use phone etiquette throughout the call
- Remember: the candidate can HEAR you, not read you

📰 STRICT SEQUENTIAL ARTICLE PROCESSING:
If a knowledge base with articles is provided, you MUST process articles in this EXACT order:

🔒 **CRITICAL RULE: ONE ARTICLE AT A TIME**
- Start with Article 1 ONLY
- Do NOT mention or reference any other articles until Article 1 is COMPLETELY finished
- Only move to Article 2 after Article 1 discussion is 100% complete
- Continue this pattern for ALL articles in sequence

📋 **ARTICLE COMPLETION PROCESS:**
For EACH article, follow these steps IN ORDER:

1. **Introduce Current Article**: "Let's discuss the first article..." (or second, third, etc.)
2. **Explore the Topic**: Thoroughly discuss the article's content with the candidate
3. **Gather Complete Responses**: Ask follow-up questions until you have comprehensive insights
4. **Complete Discussion**: Ensure you have covered all important aspects of the article
5. **Move to Next**: ONLY then proceed to the next numbered article

📝 **DISCUSSION FOCUS:**
- Ask about the candidate's thoughts on the article's main points
- Explore their experience related to the article's topics
- Assess their understanding and opinions
- Gather detailed responses about the subject matter
- Keep discussion focused on the current article only

CORE INTERVIEW PRINCIPLES:
1. NEVER mention that you are an AI, artificial intelligence, or automated system
2. Speak in a professional, articulate, and human-like manner appropriate for phone conversations
3. WAIT for the candidate to speak first after your initial greeting
4. ASK THOUGHTFUL QUESTIONS - DO NOT teach or explain concepts
5. Listen carefully to answers and ask insightful follow-up questions
6. Evaluate the candidate's knowledge, experience, and capabilities
7. Keep your responses concise and focused on questioning
8. Maintain a respectful but authoritative professional tone
9. Work through all articles systematically ONE AT A TIME if knowledge base is provided
10. Focus on gathering comprehensive candidate responses for each article
11. End calls gracefully when the interview is complete

CRITICAL VOICE CALL INTERVIEWER BEHAVIOR:
- This is a LIVE PHONE INTERVIEW - respond as if you are speaking to them in real-time
- When they ask "Can you hear me?" respond "Yes, I can hear you clearly"
- Use phone conversation etiquette and natural speech patterns
- Begin with a professional greeting and WAIT for the candidate to respond
- Your primary job is to ASK QUESTIONS, not provide answers or explanations
- When the candidate gives an incomplete answer, ask "Could you elaborate on that point?"
- When the candidate seems uncertain, ask "What's your experience with [topic]?"
- After each answer, ask a thoughtful follow-up question based on their response
- DO NOT teach, explain, or provide correct answers - you are evaluating, not educating
- Focus on assessing their knowledge, skills, and experience
- Ask one clear question at a time and wait for their complete response
- If they ask you a question, professionally redirect: "I'd like to focus on learning about your background and experience. Could you tell me..."
- Use the business and industry information provided to ask relevant, targeted questions

Professional Voice Interview Flow:
1. Professional phone greeting and wait for candidate response
2. Ask introductory questions about their background
3. Progress to specific questions about their experience and skills
4. Ask behavioral and situational questions
5. Probe deeper into areas relevant to the business/role
6. Ask follow-up questions based on their responses
7. End with professional closing questions about their experience and goals

TONE: Authoritative but respectful, like a senior executive conducting an important phone interview. Remember: this is a LIVE VOICE CONVERSATION, not text messaging."""

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

            # Create or update PhoneNumber objects for the user
            for number_data in phone_numbers:
                phone_number_obj, created = PhoneNumber.objects.get_or_create(
                    user=request.user,
                    vapi_phone_number_id=number_data.get("id"),
                    defaults={
                        "phone_number": number_data.get("number", ""),
                        "friendly_name": number_data.get("name", ""),
                        "capabilities": number_data,
                        "is_active": True,
                    }
                )
                # Update existing records if needed
                if not created:
                    phone_number_obj.phone_number = number_data.get("number", "")
                    phone_number_obj.friendly_name = number_data.get("name", "")
                    phone_number_obj.capabilities = number_data
                    phone_number_obj.is_active = True
                    phone_number_obj.save()

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
            elif isinstance(call_data["transcript"], str):
                # Handle string format transcripts from VAPI
                call.transcript_text = call_data["transcript"]

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

        # Store recording URL from VAPI (check multiple possible locations)
        recording_url = None
        
        # Check for direct recording URL
        if call_data.get("recordingUrl"):
            recording_url = call_data["recordingUrl"]
        
        # Check for artifact.recording structure
        elif call_data.get("artifact", {}).get("recording"):
            artifact_recording = call_data["artifact"]["recording"]
            # Check for mono recording
            if artifact_recording.get("mono", {}).get("recordingUrl"):
                recording_url = artifact_recording["mono"]["recordingUrl"]
            # Check for stereo recording
            elif artifact_recording.get("stereo", {}).get("recordingUrl"):
                recording_url = artifact_recording["stereo"]["recordingUrl"]
            # Check for any recording URL in the artifact
            elif isinstance(artifact_recording, dict):
                for key, value in artifact_recording.items():
                    if isinstance(value, dict) and value.get("recordingUrl"):
                        recording_url = value["recordingUrl"]
                        break
        
        if recording_url:
            call.recording_url = recording_url
            
        call.save()
        
        # Download recording file if URL is provided and not already downloaded
        if call_data.get("recordingUrl") and not call.recording_file:
            self.download_call_recording(call, call_data["recordingUrl"])
        
        # Automatically process transcript with OpenAI if transcript was updated and not already processed
        if (call_data.get("transcript") and call.transcript_text and 
            not call.processed_transcript):
            self.auto_process_transcript(call)
        
        return call

    def auto_process_transcript(self, call):
        """Automatically process transcript with OpenAI in the background"""
        try:
            # Get the assistant's knowledge text for processing
            knowledge_text = ""
            if call.assistant and call.assistant.knowledge_text:
                knowledge_text = call.assistant.knowledge_text
            
            # Only process if we have knowledge text to work with
            if knowledge_text and call.transcript_text:
                # Create an instance to access the method
                assistant_creator = CreateAssistantView()
                
                # Process the transcript with user's API key
                result = assistant_creator.process_transcript_with_articles(
                    call.transcript_text, knowledge_text, user=call.user
                )
                
                # If processing was successful, save the result
                if result.get("success") and "structured_output" in result:
                    call.processed_transcript = result["structured_output"]
                    call.save()
                    logger.info(f"Successfully auto-processed transcript for call {call.id}")
                else:
                    # Log the error but don't fail the call update
                    error_msg = result.get("error", "Unknown error")
                    logger.warning(f"Auto-processing failed for call {call.id}: {error_msg}")
            else:
                logger.debug(f"Skipping auto-processing for call {call.id}: missing knowledge_text or transcript_text")
                
        except Exception as e:
            # Log the error but don't fail the call update
            logger.error(f"Exception during auto-processing for call {call.id}: {str(e)}")

    def download_call_recording(self, call, recording_url):
        """Download call recording from VAPI URL and store it locally"""
        import requests
        import os
        from django.core.files.base import ContentFile
        from urllib.parse import urlparse
        
        try:
            logger.info(f"Downloading recording for call {call.id} from {recording_url}")
            
            # Make request to download the recording
            response = requests.get(recording_url, timeout=30)
            response.raise_for_status()
            
            # Get file extension from URL or use .mp3 as default
            parsed_url = urlparse(recording_url)
            file_extension = os.path.splitext(parsed_url.path)[1] or '.mp3'
            
            # Generate filename: call_<id>_<timestamp><extension>
            from django.utils import timezone
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            filename = f"call_{call.id}_{timestamp}{file_extension}"
            
            # Save the file
            file_content = ContentFile(response.content, name=filename)
            call.recording_file.save(filename, file_content)
            call.save()
            
            logger.info(f"Successfully downloaded recording for call {call.id}: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to download recording for call {call.id}: {str(e)}")

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


class ScheduleCallView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            print(f"ScheduleCallView: POST request received")
            print(f"User: {request.user}")
            print(f"Is authenticated: {request.user.is_authenticated}")
            print(f"Request headers: {dict(request.headers)}")
            print(f"Received schedule call data: {request.data}")
            serializer = CreateScheduledCallSerializer(data=request.data)
            if not serializer.is_valid():
                print(f"Serializer validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            data = serializer.validated_data

            # Get assistant and phone number objects
            try:
                assistant = InterviewAssistant.objects.get(
                    vapi_assistant_id=data['vapi_assistant_id'],
                    user=request.user
                )
            except InterviewAssistant.DoesNotExist:
                return Response(
                    {"error": "Assistant not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                phone_number = PhoneNumber.objects.get(
                    vapi_phone_number_id=data['twilio_phone_number_id'],
                    user=request.user,
                    is_active=True
                )
            except PhoneNumber.DoesNotExist:
                return Response(
                    {"error": "Phone number not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Determine campaign from assistant or phone number
            campaign = assistant.campaign or phone_number.campaign

            # Create scheduled call
            scheduled_call = ScheduledCall.objects.create(
                user=request.user,
                campaign=campaign,
                assistant=assistant,
                phone_number=phone_number,
                customer_number=data['customer_number'],
                scheduled_time=data['scheduled_time'],
                timezone=data.get('timezone', ''),
                call_name=data.get('call_name', ''),
                notes=data.get('notes', ''),
                status='scheduled'
            )

            return Response(
                {
                    "success": True,
                    "scheduled_call": ScheduledCallSerializer(scheduled_call).data,
                    "message": f"Call scheduled for {scheduled_call.scheduled_time}"
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Error scheduling call: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ScheduledCallListView(generics.ListAPIView):
    serializer_class = ScheduledCallSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ScheduledCall.objects.filter(user=self.request.user)
        campaign_id = self.request.query_params.get('campaign_id')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        return queryset


class ScheduledCallDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, call_id):
        try:
            scheduled_call = ScheduledCall.objects.get(
                id=call_id, user=request.user
            )
            return Response(ScheduledCallSerializer(scheduled_call).data)
        except ScheduledCall.DoesNotExist:
            return Response(
                {"error": "Scheduled call not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request, call_id):
        try:
            scheduled_call = ScheduledCall.objects.get(
                id=call_id, user=request.user
            )
            
            # Only allow certain status updates
            if 'status' in request.data:
                if request.data['status'] in ['cancelled']:
                    scheduled_call.status = request.data['status']
                    scheduled_call.save()
                    return Response(ScheduledCallSerializer(scheduled_call).data)
                else:
                    return Response(
                        {"error": "Invalid status update"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            return Response(
                {"error": "No valid updates provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ScheduledCall.DoesNotExist:
            return Response(
                {"error": "Scheduled call not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, call_id):
        try:
            scheduled_call = ScheduledCall.objects.get(
                id=call_id, user=request.user
            )
            scheduled_call.delete()
            return Response({"success": True, "message": "Scheduled call deleted"})
        except ScheduledCall.DoesNotExist:
            return Response(
                {"error": "Scheduled call not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class ExecuteScheduledCallsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Manually trigger execution of due scheduled calls (for testing/manual trigger)"""
        try:
            from django.utils import timezone
            
            # Get all due scheduled calls for this user
            due_calls = ScheduledCall.objects.filter(
                user=request.user,
                status='scheduled',
                scheduled_time__lte=timezone.now()
            )

            executed_count = 0
            results = []

            for scheduled_call in due_calls:
                try:
                    result = self.execute_scheduled_call(scheduled_call)
                    results.append(result)
                    if result['success']:
                        executed_count += 1
                except Exception as e:
                    logger.error(f"Error executing scheduled call {scheduled_call.id}: {str(e)}")
                    results.append({
                        'scheduled_call_id': scheduled_call.id,
                        'success': False,
                        'error': str(e)
                    })

            return Response({
                "success": True,
                "executed_count": executed_count,
                "total_due": len(due_calls),
                "results": results
            })

        except Exception as e:
            logger.error(f"Error executing scheduled calls: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def execute_scheduled_call(self, scheduled_call):
        """Execute a single scheduled call"""
        from django.utils import timezone
        
        try:
            # Update status and attempt tracking
            scheduled_call.status = 'in_progress'
            scheduled_call.execution_attempts += 1
            scheduled_call.last_attempt_at = timezone.now()
            scheduled_call.save()

            # Get user's API configuration
            try:
                api_config = APIConfiguration.objects.get(user=scheduled_call.user)
                vapi_key = api_config.vapi_api_key
            except APIConfiguration.DoesNotExist:
                raise Exception("API configuration not found")

            if not api_config.is_vapi_configured:
                raise Exception("Vapi API not configured")

            # Prepare call payload (similar to MakeCallView)
            headers = {
                "Authorization": f"Bearer {vapi_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "assistantId": scheduled_call.assistant.vapi_assistant_id,
                "phoneNumberId": scheduled_call.phone_number.vapi_phone_number_id,
                "customer": {"number": scheduled_call.customer_number},
            }

            # Make the call via Vapi API
            response = requests.post(
                "https://api.vapi.ai/call", headers=headers, json=payload
            )

            response.raise_for_status()
            call_data = response.json()

            # Create InterviewCall record
            interview_call = InterviewCall.objects.create(
                user=scheduled_call.user,
                campaign=scheduled_call.campaign,
                vapi_call_id=call_data.get("id"),
                assistant=scheduled_call.assistant,
                phone_number=scheduled_call.phone_number,
                customer_number=scheduled_call.customer_number,
                status="queued",
                raw_call_data=call_data,
            )

            # Link the scheduled call to the actual call
            scheduled_call.actual_call = interview_call
            scheduled_call.status = 'completed'
            scheduled_call.save()

            return {
                'scheduled_call_id': scheduled_call.id,
                'success': True,
                'call_id': interview_call.id,
                'vapi_call_id': call_data.get("id"),
                'message': 'Call initiated successfully'
            }

        except requests.exceptions.RequestException as e:
            scheduled_call.status = 'failed'
            scheduled_call.error_message = f"Vapi API error: {str(e)}"
            scheduled_call.save()
            
            return {
                'scheduled_call_id': scheduled_call.id,
                'success': False,
                'error': f"Vapi API error: {str(e)}"
            }

        except Exception as e:
            scheduled_call.status = 'failed'
            scheduled_call.error_message = str(e)
            scheduled_call.save()
            
            return {
                'scheduled_call_id': scheduled_call.id,
                'success': False,
                'error': str(e)
            }


class AnalyzeWebsiteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Analyze a website URL using OpenAI to extract business summary, topics, and keywords"""
        try:
            website_url = request.data.get('website_url', '').strip()
            if not website_url:
                return Response(
                    {"error": "Website URL is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate URL format
            if not website_url.startswith(('http://', 'https://')):
                website_url = 'https://' + website_url

            logger.info(f"Analyzing website: {website_url}")
            
            # For testing, return mock data first
            if website_url == "https://example.com":
                mock_analysis = {
                    "summary": "Example.com is a domain name used in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.",
                    "company_details": {
                        "name": "Example Domain",
                        "industry": "Internet Services",
                        "location": "United States"
                    },
                    "article_topics": [
                        "Domain Name Management",
                        "Internet Infrastructure", 
                        "Web Development Examples",
                        "Technical Documentation",
                        "Reserved Domain Names",
                        "Internet Standards",
                        "Web Hosting Services",
                        "DNS Management"
                    ],
                    "keywords": [
                        "domain name", "example", "illustrative", "documents", 
                        "internet", "web development", "DNS", "hosting", 
                        "reserved domain", "IANA", "standards", "documentation",
                        "web services", "domain management", "technical examples"
                    ]
                }
                
                return Response({
                    "success": True,
                    "analysis": mock_analysis,
                    "website_url": website_url
                })
            
            # Scrape website content
            website_content = self.scrape_website_content(website_url)
            if not website_content:
                return Response(
                    {"error": "Unable to extract content from the website"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Analyze with OpenAI
            analysis_result = self.analyze_with_openai(website_content, website_url)
            
            return Response({
                "success": True,
                "analysis": analysis_result,
                "website_url": website_url
            })

        except Exception as e:
            logger.error(f"Error analyzing website: {str(e)}")
            return Response(
                {"error": f"Website analysis failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def scrape_website_content(self, url):
        """Scrape content from website and follow internal links for comprehensive analysis"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Get the base domain for filtering internal links
            from urllib.parse import urljoin, urlparse
            base_domain = urlparse(url).netloc
            
            all_content = []
            visited_urls = set()
            urls_to_visit = [url]
            max_pages = 5  # Limit to 5 pages to avoid too long processing
            
            logger.info(f"Starting comprehensive website crawling for: {url}")
            
            for i, current_url in enumerate(urls_to_visit[:max_pages]):
                if current_url in visited_urls:
                    continue
                    
                try:
                    logger.info(f"Crawling page {i+1}: {current_url}")
                    response = requests.get(current_url, headers=headers, timeout=10)
                    response.raise_for_status()
                    visited_urls.add(current_url)
                    
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract page title
                    title = soup.find('title')
                    if title:
                        all_content.append(f"PAGE TITLE: {title.get_text().strip()}")
                    
                    # Extract meta description
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    if meta_desc and meta_desc.get('content'):
                        all_content.append(f"META DESCRIPTION: {meta_desc.get('content').strip()}")
                    
                    # Extract main content areas
                    main_content_selectors = [
                        'main', 'article', '.content', '#content', '.main-content',
                        'h1', 'h2', 'h3', 'p', '.about', '.services', '.description'
                    ]
                    
                    for selector in main_content_selectors:
                        elements = soup.select(selector)
                        for element in elements[:3]:  # Limit per selector
                            text = element.get_text().strip()
                            if len(text) > 20:  # Only meaningful content
                                all_content.append(text)
                    
                    # Find internal links for further crawling (only on first page)
                    if i == 0:  # Only get links from the main page
                        for link in soup.find_all('a', href=True)[:20]:  # Limit link checking
                            href = link['href']
                            full_url = urljoin(current_url, href)
                            link_domain = urlparse(full_url).netloc
                            
                            # Only follow internal links
                            if link_domain == base_domain and full_url not in visited_urls:
                                # Prioritize important pages
                                link_text = link.get_text().lower()
                                important_keywords = ['about', 'service', 'contact', 'company', 'team', 'product']
                                
                                if any(keyword in link_text for keyword in important_keywords) or \
                                   any(keyword in href.lower() for keyword in important_keywords):
                                    urls_to_visit.append(full_url)
                                    if len(urls_to_visit) >= max_pages:
                                        break
                
                except Exception as e:
                    logger.warning(f"Error crawling {current_url}: {str(e)}")
                    continue
            
            # Combine all content
            combined_content = '\n\n'.join(all_content)
            
            # Remove script and style content
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(combined_content, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Clean up the text
            text = soup.get_text() if hasattr(soup, 'get_text') else combined_content
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit content length for API processing but keep more content
            if len(content) > 12000:
                content = content[:12000] + "..."
                
            logger.info(f"Successfully crawled {len(visited_urls)} pages, extracted {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"Error in comprehensive website scraping {url}: {str(e)}")
            return None

    def analyze_with_openai(self, content, url):
        """Analyze website content using enhanced content extraction"""
        try:
            logger.info(f"Starting enhanced content analysis for {url}")
            logger.info(f"Content length: {len(content)} characters")
            
            # Enhanced content analysis using the crawled data
            company_name = self.extract_company_name(content, url)
            industry = self.extract_industry(content, url)
            location = self.extract_location(content)
            services = self.extract_services(content)
            
            # Create comprehensive business summary
            summary = self.create_business_summary(company_name, industry, services, content)
            
            # Generate relevant article topics based on actual content
            article_topics = self.generate_article_topics(industry, services, content)
            
            # Generate targeted keywords from content
            keywords = self.generate_keywords(company_name, industry, services, content)
            
            return {
                "summary": summary,
                "company_details": {
                    "name": company_name,
                    "industry": industry,
                    "location": location
                },
                "article_topics": article_topics,
                "keywords": keywords
            }
            
        except Exception as e:
            logger.error(f"Error with enhanced content analysis: {str(e)}")
            # Return basic fallback
            return self.get_fallback_analysis()

    def extract_company_name(self, content, url):
        """Extract company name from content and URL"""
        # Look for common company name patterns in content
        import re
        
        # Check page titles first
        title_patterns = [
            r'PAGE TITLE:\s*([^|\n]+)',
            r'<title[^>]*>([^<]+)</title>',
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                title = matches[0].strip()
                # Clean up common title suffixes
                title = re.sub(r'\s*[-|]\s*(Home|Welcome|Official|Site|Website).*$', '', title, flags=re.IGNORECASE)
                if len(title) > 3 and len(title) < 50:
                    return title
        
        # Look for "About [Company]" or "[Company] is" patterns
        about_patterns = [
            r'About\s+([A-Z][a-zA-Z\s&]+?)(?:\s+is|\s+was|\.|,)',
            r'([A-Z][a-zA-Z\s&]+?)\s+is\s+a\s+(?:leading|professional|premier)',
            r'Welcome\s+to\s+([A-Z][a-zA-Z\s&]+?)(?:\.|!|,)',
        ]
        
        for pattern in about_patterns:
            matches = re.findall(pattern, content)
            if matches:
                name = matches[0].strip()
                if len(name) > 3 and len(name) < 50:
                    return name
        
        # Extract from URL as fallback
        domain = url.split('//')[1].split('/')[0].split('.')[0]
        if domain and len(domain) > 2:
            return domain.replace('-', ' ').title()
        
        return "Unknown Company"

    def extract_industry(self, content, url):
        """Extract industry from content"""
        content_lower = content.lower()
        
        # Define industry keywords
        industries = {
            "junk removal": ["junk", "removal", "cleanup", "cleanout", "hauling", "debris"],
            "web development": ["web", "website", "development", "coding", "programming"],
            "healthcare": ["medical", "health", "doctor", "clinic", "hospital", "patient"],
            "restaurant": ["restaurant", "food", "dining", "menu", "kitchen", "chef"],
            "real estate": ["real estate", "property", "homes", "buying", "selling", "agent"],
            "legal services": ["law", "legal", "attorney", "lawyer", "court", "legal advice"],
            "construction": ["construction", "building", "contractor", "renovation", "remodeling"],
            "consulting": ["consulting", "consultant", "advisory", "strategy", "business consulting"],
            "marketing": ["marketing", "advertising", "digital marketing", "seo", "social media"],
            "education": ["education", "school", "training", "learning", "course", "teaching"],
            "fitness": ["fitness", "gym", "personal training", "workout", "exercise", "health"],
            "automotive": ["automotive", "car", "auto", "vehicle", "repair", "maintenance"],
            "financial services": ["financial", "finance", "investment", "banking", "money", "loan"],
            "retail": ["retail", "store", "shop", "shopping", "products", "merchandise"],
            "technology": ["technology", "software", "tech", "IT", "computer", "digital"],
        }
        
        for industry, keywords in industries.items():
            if sum(content_lower.count(keyword) for keyword in keywords) >= 3:
                return industry.title()
        
        return "Professional Services"

    def extract_location(self, content):
        """Extract location from content"""
        import re
        
        # Look for location patterns
        location_patterns = [
            r'(?:located in|based in|serving|in)\s+([A-Z][a-zA-Z\s,]+?)(?:\.|,|\s+and|\s+area)',
            r'([A-Z][a-zA-Z\s]+),\s+([A-Z]{2})\s+\d{5}',  # City, State ZIP
            r'([A-Z][a-zA-Z\s]+),?\s+(Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming|AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)',
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                location = matches[0] if isinstance(matches[0], str) else ' '.join(matches[0])
                if len(location.strip()) > 2:
                    return location.strip()
        
        return "Service Area"

    def extract_services(self, content):
        """Extract services from content"""
        content_lower = content.lower()
        services = []
        
        # Look for service-related keywords
        service_patterns = [
            r'(?:we offer|our services|services include|we provide|we specialize in)\s+([^.]+)',
            r'services:\s*([^.]+)',
        ]
        
        import re
        for pattern in service_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                services.extend([s.strip() for s in matches[0].split(',')])
        
        return services[:5]  # Limit to 5 services

    def create_business_summary(self, company_name, industry, services, content):
        """Create comprehensive business summary"""
        if company_name == "Unknown Company":
            company_name = "This business"
        
        summary = f"{company_name} is a professional {industry.lower()} company"
        
        if services:
            summary += f" that specializes in {', '.join(services[:3])}"
        
        # Add content-based insights
        content_lower = content.lower()
        if "customer satisfaction" in content_lower:
            summary += ". They prioritize customer satisfaction"
        if "experience" in content_lower and "years" in content_lower:
            summary += " and bring years of experience to their work"
        if "quality" in content_lower:
            summary += ". The company is committed to delivering quality services"
        if "local" in content_lower or "community" in content_lower:
            summary += " to their local community"
        
        summary += ". Their professional approach and dedication to excellence make them a trusted choice in their industry."
        
        return summary

    def generate_article_topics(self, industry, services, content):
        """Generate relevant article topics based on industry and content"""
        base_topics = []
        
        # Industry-specific topics
        if "junk removal" in industry.lower():
            base_topics = [
                "Professional Junk Removal Benefits",
                "Eco-Friendly Disposal Practices", 
                "Home Decluttering Tips",
                "Commercial Cleanout Services",
                "Moving and Estate Cleanouts"
            ]
        elif "web" in industry.lower():
            base_topics = [
                "Modern Web Design Trends",
                "SEO Best Practices",
                "User Experience Optimization",
                "Mobile-First Development",
                "Website Security Essentials"
            ]
        elif "healthcare" in industry.lower():
            base_topics = [
                "Patient Care Excellence",
                "Healthcare Technology Advances",
                "Preventive Medicine Importance",
                "Healthcare Accessibility",
                "Medical Best Practices"
            ]
        else:
            # Generic professional topics
            base_topics = [
                f"{industry} Best Practices",
                "Customer Service Excellence", 
                "Industry Trends and Insights",
                "Professional Service Delivery",
                "Quality Assurance Standards"
            ]
        
        # Add 3-5 more general business topics
        general_topics = [
            "Business Growth Strategies",
            "Customer Satisfaction Methods", 
            "Industry Innovation Approaches",
            "Service Quality Improvement",
            "Professional Development Tips"
        ]
        
        return (base_topics + general_topics)[:10]

    def generate_keywords(self, company_name, industry, services, content):
        """Generate targeted keywords from actual content"""
        keywords = set()
        
        # Add company and industry keywords
        if company_name != "Unknown Company":
            keywords.add(company_name.lower())
        keywords.add(industry.lower())
        
        # Add service keywords
        for service in services:
            keywords.add(service.lower())
        
        # Extract common business keywords from content
        content_lower = content.lower()
        business_keywords = [
            "professional", "services", "quality", "customer", "business",
            "experienced", "reliable", "trusted", "expert", "solutions",
            "local", "community", "satisfaction", "excellence", "dedicated"
        ]
        
        for keyword in business_keywords:
            if keyword in content_lower:
                keywords.add(keyword)
        
        # Industry-specific keyword expansion
        if "junk removal" in industry.lower():
            keywords.update([
                "cleanup", "hauling", "debris removal", "decluttering",
                "waste disposal", "residential", "commercial"
            ])
        
        return list(keywords)[:20]

    def get_fallback_analysis(self):
        """Fallback analysis structure"""
        return {
            "summary": "Professional business services with focus on customer satisfaction and quality delivery.",
            "company_details": {
                "name": "Business Services",
                "industry": "Professional Services", 
                "location": "Service Area"
            },
            "article_topics": [
                "Business Overview", "Service Excellence", "Customer Focus",
                "Industry Expertise", "Quality Standards", "Professional Approach"
            ],
            "keywords": [
                "professional", "business", "services", "quality",
                "customer", "expertise", "reliable", "solutions"
            ]
        }

    def parse_openai_response_fallback(self, text):
        """Fallback parser for when JSON parsing fails"""
        return {
            "summary": "Website analysis completed. Please check the raw response for detailed information.",
            "company_details": {
                "name": "To be determined",
                "industry": "Various"
            },
            "article_topics": [
                "Business Overview",
                "Industry Analysis", 
                "Market Research",
                "Company Profile",
                "Services Review",
                "Product Analysis"
            ],
            "keywords": [
                "business", "company", "services", "products", 
                "industry", "market", "analysis", "overview"
            ]
        }


class ElevenLabsVoicesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Fetch available ElevenLabs voice models"""
        try:
            # ElevenLabs popular voice models with their IDs
            # These are the most commonly used voices from ElevenLabs
            elevenlabs_voices = [
                {
                    "voice_id": "21m00Tcm4TlvDq8ikWAM",
                    "name": "Rachel",
                    "description": "Young American Female, Calm"
                },
                {
                    "voice_id": "AZnzlk1XvdvUeBnXmlld", 
                    "name": "Domi",
                    "description": "Young American Female, Strong"
                },
                {
                    "voice_id": "EXAVITQu4vr4xnSDxMaL",
                    "name": "Bella",
                    "description": "Young American Female, Sweet"
                },
                {
                    "voice_id": "ErXwobaYiN019PkySvjV",
                    "name": "Antoni",
                    "description": "Young American Male, Well-rounded"
                },
                {
                    "voice_id": "VR6AewLTigWG4xSOukaG",
                    "name": "Arnold",
                    "description": "American Male, Crisp"
                },
                {
                    "voice_id": "pNInz6obpgDQGcFmaJgB",
                    "name": "Adam",
                    "description": "American Male, Deep"
                },
                {
                    "voice_id": "yoZ06aMxZJJ28mfd3POQ",
                    "name": "Sam",
                    "description": "American Male, Raspy"
                },
                {
                    "voice_id": "TxGEqnHWrfWFTfGW9XjX",
                    "name": "Josh",
                    "description": "American Male, Deep"
                },
                {
                    "voice_id": "jsCqWAovK2LkecY7zXl4",
                    "name": "Serena",
                    "description": "American Female, Pleasant"
                },
                {
                    "voice_id": "jBpfuIE2acCO8z3wKNLl",
                    "name": "Gigi",
                    "description": "American Female, Childlish"
                },
                {
                    "voice_id": "XB0fDUnXU5powFXDhCwa",
                    "name": "Charlotte",
                    "description": "English Female, Seductive"
                },
                {
                    "voice_id": "IKne3meq5aSn9XLyUdCD",
                    "name": "Matilda",
                    "description": "American Female, Warm"
                },
                {
                    "voice_id": "flq6f7yk4E4fJM5XTYuZ",
                    "name": "Michael",
                    "description": "American Male, Old"
                },
                {
                    "voice_id": "piTKgcLEGmPE4e6mEKli",
                    "name": "Nicole",
                    "description": "American Female, Whisper"
                }
            ]
            
            return Response({
                "success": True,
                "voices": elevenlabs_voices
            })
            
        except Exception as e:
            logger.error(f"Error fetching ElevenLabs voices: {str(e)}")
            return Response(
                {"error": "Failed to fetch ElevenLabs voices"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProcessTranscriptView(APIView):
    """Process interview transcript with article-aware analysis"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            transcript_text = data.get('transcript', '')
            knowledge_text = data.get('knowledge_text', '')
            call_id = data.get('call_id', '')

            if not transcript_text:
                return Response(
                    {"error": "Transcript text is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create an instance to access the method
            assistant_creator = CreateAssistantView()
            
            # Process the transcript with user's API key
            result = assistant_creator.process_transcript_with_articles(
                transcript_text, knowledge_text, user=request.user
            )

            if "error" in result:
                return Response(
                    {"error": result["error"]}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # If call_id is provided, try to update the call record
            if call_id:
                try:
                    call = InterviewCall.objects.get(id=call_id, user=request.user)
                    # Store the processed transcript in a new field or update existing
                    call.processed_transcript = result["structured_output"]
                    call.save()
                except InterviewCall.DoesNotExist:
                    pass  # Call not found, continue anyway

            return Response({
                "success": True,
                "structured_transcript": result["structured_output"],
                "articles_processed": result["articles_processed"],
                "call_id": call_id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error processing transcript: {str(e)}")
            return Response(
                {"error": f"Failed to process transcript: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




@csrf_exempt
def vapi_webhook_view(request):
    """
    Handle VAPI webhook events according to the new message format:
    {
      "message": {
        "type": "<server-message-type>",
        "call": { /* Call Object */ },
        /* other fields depending on type */
      }
    }
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
        
    try:
        # Validate webhook signature using serverUrlSecret
        if not validate_webhook_signature(request):
            logger.warning("Invalid webhook signature")
            return JsonResponse({"error": "Invalid signature"}, status=401)
        
        # Log the entire request for debugging
        logger.info(f"=== WEBHOOK REQUEST DEBUG ===")
        logger.info(f"Method: {request.method}")
        logger.info(f"Path: {request.path}")
        logger.info(f"Headers: {dict(request.META)}")
        logger.info(f"Raw Body: {request.body.decode('utf-8', errors='ignore')}")
        logger.info(f"Content Type: {request.content_type}")
        logger.info(f"=== END WEBHOOK REQUEST DEBUG ===")
        # print(f"=== WEBHOOK REQUEST DEBUG ===")
        # print(f"Method: {request.method}")
        # print(f"Path: {request.path}")
        # print(f"Headers: {dict(request.META)}")
        # print(f"Raw Body: {request.body.decode('utf-8', errors='ignore')}")
        # print(f"Content Type: {request.content_type}")
        # print(f"=== END WEBHOOK REQUEST DEBUG ===")

        # Parse JSON body
        try:
            webhook_data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            logger.error("Invalid JSON in webhook payload")
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        
        # Extract message from webhook payload
        message = webhook_data.get('message', {})
        
        if not message:
            logger.warning("Webhook received without message field")
            return JsonResponse({"error": "Missing message field"}, status=400)
        
        event_type = message.get('type')
        call_data = message.get('call', {})
        vapi_call_id = call_data.get('id')
        
        logger.info(f"Received VAPI webhook: {event_type} for call {vapi_call_id}")
        
        # Save webhook event to file for debugging and auditing
        save_webhook_event(event_type or 'unknown_event', webhook_data)
        
        # Handle events that don't require a call lookup
        if event_type in ['assistant-request', 'tool-calls', 'transfer-destination-request', 'knowledge-base-request']:
            return handle_special_events(event_type, message)
        
        # For other events, we need a call ID
        if not vapi_call_id:
            logger.warning("Webhook received without call ID")
            return JsonResponse({"error": "Missing call ID"}, status=400)
        
        # Find the call in our database with security validation
        try:
            call = InterviewCall.objects.select_related('user', 'assistant').get(
                vapi_call_id=vapi_call_id
            )
            
            # Security validation: Verify call ownership and assistant relationship
            if not validate_call_ownership(call, call_data):
                logger.error(f"Security violation: Invalid call ownership for {vapi_call_id}")
                return JsonResponse({"error": "Unauthorized"}, status=401)
                
        except InterviewCall.DoesNotExist:
            logger.warning(f"Call {vapi_call_id} not found in database")
            return JsonResponse({"error": "Call not found"}, status=404)
        
        # Handle different webhook events
        if event_type == 'status-update':
            handle_status_update(call, message)
        elif event_type == 'end-of-call-report':
            handle_end_of_call_report(call, message)
        elif event_type == 'transcript':
            handle_transcript(call, message)
        elif event_type == 'conversation-update':
            handle_conversation_update(call, message)
        elif event_type == 'hang':
            handle_hang(call, message)
        elif event_type == 'speech-update':
            handle_speech_update(call, message)
        elif event_type == 'model-output':
            handle_model_output(call, message)
        elif event_type == 'transfer-update':
            handle_transfer_update(call, message)
        elif event_type == 'user-interrupted':
            handle_user_interrupted(call, message)
        elif event_type == 'language-change-detected':
            handle_language_change_detected(call, message)
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")
        
        return JsonResponse({"status": "success"}, status=200)
        
    except Exception as e:
        logger.error(f"Error processing VAPI webhook: {str(e)}")
        return JsonResponse(
            {"error": "Webhook processing failed"}, 
            status=500
        )

def handle_special_events(event_type, message):
    """Handle special events that don't require a call lookup"""
    if event_type == 'assistant-request':
        return handle_assistant_request(message)
    elif event_type == 'tool-calls':
        return handle_tool_calls(message)
    elif event_type == 'transfer-destination-request':
        return handle_transfer_destination_request(message)
    elif event_type == 'knowledge-base-request':
        return handle_knowledge_base_request(message)
    else:
        logger.info(f"Unhandled special event type: {event_type}")
        return JsonResponse({"status": "success"}, status=200)

def handle_assistant_request(message):
    """Handle assistant-request webhook event"""
    logger.info("Assistant request received")
    # Return error message to be spoken to caller
    return JsonResponse({
        "error": "Sorry, no assistant is available at this time. Please call back later."
    }, status=200)

def handle_tool_calls(message):
    """Handle tool-calls webhook event"""
    logger.info("Tool calls received")
    tool_calls = message.get('toolCallList', [])
    results = []
    
    for tool_call in tool_calls:
        tool_name = tool_call.get('name')
        tool_id = tool_call.get('id')
        parameters = tool_call.get('parameters', {})
        
        logger.info(f"Processing tool call: {tool_name} with ID: {tool_id}")
        
        # Add your tool handling logic here
        # For now, return a generic success response
        results.append({
            "name": tool_name,
            "toolCallId": tool_id,
            "result": json.dumps({"status": "completed", "message": f"Tool {tool_name} executed successfully"})
        })
    
    return JsonResponse({"results": results}, status=200)

def handle_transfer_destination_request(message):
    """Handle transfer-destination-request webhook event"""
    logger.info("Transfer destination request received")
    # Return a default transfer destination or error
    return JsonResponse({
        "error": "No transfer destination available at this time."
    }, status=200)

def handle_knowledge_base_request(message):
    """Handle knowledge-base-request webhook event"""
    logger.info("Knowledge base request received")
    messages = message.get('messages', [])
    
    # Return empty documents for now - implement your knowledge base logic here
    return JsonResponse({
        "documents": []
    }, status=200)
    
def handle_status_update(call, message):
    """Handle status-update webhook event"""
    status_value = message.get('status')
    call_data = message.get('call', {})
    
    logger.info(f"Call {call.vapi_call_id} status update: {status_value}")
    
    if status_value == "scheduled":
        call.status = "scheduled"
    elif status_value == "queued":
        call.status = "queued"
    elif status_value == "ringing":
        call.status = "ringing"
    elif status_value == "in-progress":
        call.status = "in-progress"
        if call_data.get("startedAt"):
            try:
                call.started_at = datetime.fromisoformat(
                    call_data["startedAt"].replace("Z", "+00:00")
                )
            except:
                pass
    elif status_value == "forwarding":
        call.status = "forwarding"
    elif status_value == "ended":
        call.status = "ended"
        if call_data.get("endedAt"):
            try:
                call.ended_at = datetime.fromisoformat(
                    call_data["endedAt"].replace("Z", "+00:00")
                )
            except:
                pass
    
    call.raw_call_data = call_data
    call.save()

def handle_end_of_call_report(call, message):
    """Handle end-of-call-report webhook event"""
    logger.info(f"End of call report for call {call.vapi_call_id}")
    
    call_data = message.get('call', {})
    artifact = message.get('artifact', {})
    ended_reason = message.get('endedReason')
    
    # Use existing method to update call data
    call_detail_view = CallDetailView()
    call = call_detail_view.update_call_from_vapi_data(call, call_data)
    
    # Update with artifact data
    if artifact.get('transcript'):
        call.transcript_text = artifact['transcript']
    
    if artifact.get('recording'):
        recording_data = artifact['recording']
        if recording_data.get('mono', {}).get('recordingUrl'):
            call.recording_url = recording_data['mono']['recordingUrl']
        elif recording_data.get('stereo', {}).get('recordingUrl'):
            call.recording_url = recording_data['stereo']['recordingUrl']
    
    if artifact.get('messages'):
        call.transcript = artifact['messages']
    
    if ended_reason:
        call.end_reason = ended_reason
    
    call.save()
    
    # Trigger automatic transcript processing if conditions are met
    if (call.transcript_text and 
        call.assistant and 
        call.assistant.knowledge_text and
        not call.processed_transcript):
        call_detail_view.auto_process_transcript(call)

def handle_transcript(call, message):
    """Handle transcript webhook event"""
    role = message.get('role')
    transcript_type = message.get('transcriptType')
    transcript_text = message.get('transcript')
    
    logger.info(f"Transcript update for call {call.vapi_call_id}: {role} - {transcript_type}")
    
    # Only process final transcripts to avoid too many updates
    if transcript_type == 'final' and transcript_text:
        # Append to existing transcript or create new
        if call.transcript_text:
            call.transcript_text += f"\n{role}: {transcript_text}"
        else:
            call.transcript_text = f"{role}: {transcript_text}"
        
        call.save()

def handle_conversation_update(call, message):
    """Handle conversation-update webhook event"""
    messages = message.get('messages', [])
    logger.info(f"Conversation update for call {call.vapi_call_id}: {len(messages)} messages")
    
    if messages:
        call.transcript = messages
        # Also update transcript_text for easier reading
        call.transcript_text = "\n".join([
            f"{msg.get('role', 'unknown')}: {msg.get('message', '')}"
            for msg in messages
        ])
        call.save()

def handle_hang(call, message):
    """Handle hang webhook event"""
    logger.info(f"Hang detected for call {call.vapi_call_id}")
    # This is an informational event, you might want to log it or notify your team
    # No specific action required

def handle_speech_update(call, message):
    """Handle speech-update webhook event"""
    status_value = message.get('status')
    role = message.get('role')
    turn = message.get('turn')
    
    logger.info(f"Speech update for call {call.vapi_call_id}: {role} - {status_value} (turn {turn})")
    # This is informational - you can use it for real-time UI updates if needed

def handle_model_output(call, message):
    """Handle model-output webhook event"""
    output = message.get('output', {})
    logger.info(f"Model output for call {call.vapi_call_id}")
    # This contains token-level outputs - useful for real-time streaming if needed

def handle_transfer_update(call, message):
    """Handle transfer-update webhook event"""
    destination = message.get('destination', {})
    logger.info(f"Transfer update for call {call.vapi_call_id} to {destination.get('type')}")
    
    # Update call status to indicate transfer
    call.status = "transferred"
    call.raw_call_data.update({"transfer_destination": destination})
    call.save()

def handle_user_interrupted(call, message):
    """Handle user-interrupted webhook event"""
    logger.info(f"User interrupted for call {call.vapi_call_id}")
    # Informational event - user interrupted the assistant

def handle_language_change_detected(call, message):
    """Handle language-change-detected webhook event"""
    language = message.get('language')
    logger.info(f"Language change detected for call {call.vapi_call_id}: {language}")
    # Update call with detected language if needed
    
def validate_webhook_signature(request):
    """
    Validate VAPI webhook signature for security using serverUrlSecret
    VAPI sends the secret directly, not an HMAC hash
    Returns True if signature is valid or no secret is configured
    """
    # Use the SERVER_URL_SECRET from configuration
    webhook_secret = VAPI_SERVER_URL_SECRET
    if not webhook_secret:
        # If no secret is configured, skip validation (for development)
        logger.info("No VAPI server URL secret configured, skipping signature validation")
        return True
    
    # Get signature from headers - VAPI sends the raw secret, not HMAC
    signature = request.META.get('HTTP_X_VAPI_SECRET')
    if not signature:
        logger.warning("No X-Vapi-Secret header found")
        return False
    
    # VAPI sends the serverUrlSecret directly, so we just compare it
    is_valid = hmac.compare_digest(signature, webhook_secret)
    
    if is_valid:
        logger.info("Webhook signature validated successfully")
    else:
        logger.error(f"Webhook signature validation failed. Expected secret: {webhook_secret}, Got: {signature}")
    
    return is_valid

def validate_call_ownership(call, call_data):
    """
    Validate that the webhook call data matches our database call
    This prevents cross-user data leakage and ensures call integrity
    """
    try:
        # Extract VAPI data from webhook
        vapi_assistant_id = call_data.get('assistantId')
        vapi_phone_number_id = call_data.get('phoneNumberId')
        
        # Security Check 1: Verify assistant belongs to the same user as the call
        if call.assistant.vapi_assistant_id != vapi_assistant_id:
            logger.error(f"Assistant ID mismatch: DB={call.assistant.vapi_assistant_id}, VAPI={vapi_assistant_id}")
            return False
        
        # Security Check 2: Verify assistant belongs to the call's user  
        if call.assistant.user_id != call.user_id:
            logger.error(f"User mismatch: Call user={call.user_id}, Assistant user={call.assistant.user_id}")
            return False
        
        # Security Check 3: Verify phone number ownership (if provided)
        if vapi_phone_number_id and call.phone_number.vapi_phone_number_id != vapi_phone_number_id:
            logger.error(f"Phone number mismatch: DB={call.phone_number.vapi_phone_number_id}, VAPI={vapi_phone_number_id}")
            return False
        
        # Security Check 4: Verify phone number belongs to same user
        if call.phone_number.user_id != call.user_id:
            logger.error(f"Phone user mismatch: Call user={call.user_id}, Phone user={call.phone_number.user_id}")
            return False
        
        # All checks passed
        logger.info(f"Call ownership validated for user {call.user.username} (ID: {call.user_id})")
        return True
        
    except Exception as e:
        logger.error(f"Error validating call ownership: {str(e)}")
        return False
