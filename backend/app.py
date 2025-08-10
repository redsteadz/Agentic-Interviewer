from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
from twilio.rest import Client
import logging
import requests

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

twilio_client = None
vapi_api_key = None

def get_vapi_api_key():
    global vapi_api_key
    api_key = session.get('vapi_api_key') or os.getenv('VAPI_API_KEY')
    if api_key and not api_key.startswith('your_'):
        vapi_api_key = api_key
        return vapi_api_key
    return None

def get_twilio_client():
    global twilio_client
    
    account_sid = session.get('twilio_account_sid') or os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = session.get('twilio_auth_token') or os.getenv('TWILIO_AUTH_TOKEN')
    
    if account_sid and auth_token and not account_sid.startswith('your_'):
        if not twilio_client or getattr(twilio_client, '_account_sid', None) != account_sid:
            twilio_client = Client(account_sid, auth_token)
        return twilio_client
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    if request.method == 'GET':
        return jsonify({
            'twilio_configured': bool(get_twilio_client()),
            'vapi_configured': bool(get_vapi_api_key()),
            'twilio_account_sid': session.get('twilio_account_sid', ''),
            'vapi_api_key_set': bool(session.get('vapi_api_key'))
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        
        if data.get('twilio_account_sid'):
            session['twilio_account_sid'] = data['twilio_account_sid']
        if data.get('twilio_auth_token'):
            session['twilio_auth_token'] = data['twilio_auth_token']
        if data.get('vapi_api_key'):
            session['vapi_api_key'] = data['vapi_api_key']
        
        result = {'success': True, 'errors': []}
        
        twilio_client_test = get_twilio_client()
        if twilio_client_test:
            try:
                account = twilio_client_test.api.account.fetch()
                result['twilio_status'] = f"Connected to Twilio account: {account.friendly_name}"
            except Exception as e:
                result['errors'].append(f"Twilio error: {str(e)}")
                result['success'] = False
        else:
            result['errors'].append("Twilio credentials not provided or invalid")
        
        if get_vapi_api_key():
            result['vapi_status'] = "Vapi API key configured."
        else:
            result['errors'].append("Vapi API key not provided or invalid")
            result['success'] = False
        
        return jsonify(result)

@app.route('/api/clear-config', methods=['POST'])
def clear_config():
    session.pop('twilio_account_sid', None)
    session.pop('twilio_auth_token', None)
    session.pop('vapi_api_key', None)
    return jsonify({'success': True, 'message': 'Configuration cleared'})

@app.route('/api/test-assistant', methods=['POST'])
def test_assistant():
    try:
        data = request.get_json()
        logger.info(f"Test endpoint received: {data}")
        return jsonify({
            'success': True,
            'received_data': data,
            'message': 'Data received successfully'
        })
    except Exception as e:
        logger.error(f"Test endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/create-assistant', methods=['POST'])
def create_assistant():
    try:
        vapi_key = get_vapi_api_key()
        if not vapi_key:
            return jsonify({'error': 'Vapi API key not configured'}), 400
        
        data = request.get_json()
        assistant_name = data.get('name', 'AI Assistant').strip() or 'AI Assistant'
        voice_provider = data.get('voice_provider', 'openai').strip() or 'openai'
        voice_id = data.get('voice_id', 'alloy').strip() or 'alloy'
        model_provider = data.get('model_provider', 'openai').strip() or 'openai'
        model = data.get('model', 'gpt-4').strip() or 'gpt-4'
        first_message = data.get('first_message', 'Hello! How can I help you today?').strip() or 'Hello! How can I help you today?'
        
        logger.info(f"Received data: name='{assistant_name}', voice_provider='{voice_provider}', voice_id='{voice_id}', model_provider='{model_provider}', model='{model}', first_message='{first_message}'")
        
        headers = {
            "Authorization": f"Bearer {vapi_key}",
            "Content-Type": "application/json"
        }
        
        knowledge_text = data.get('knowledge_text', '')
        knowledge_urls = data.get('knowledge_urls', '')
        
        system_message = create_interview_system_message(knowledge_text, knowledge_urls)
        
        professional_first_message = create_professional_first_message(first_message, knowledge_text, knowledge_urls)
        
        payload = {
            "name": assistant_name,
            "firstMessage": professional_first_message,
            "model": {
                "provider": model_provider,
                "model": model
            },
            "voice": {
                "provider": voice_provider,
                "voiceId": voice_id,
                "stability": 0.95,
                "similarityBoost": 0.75,
                "style": 0.0,
                "useSpeakerBoost": False
            },
            "backgroundSound": "none",
            "backgroundDenoisingEnabled": True,
            "silenceTimeoutSeconds": 30,
            "maxDurationSeconds": 1800,
            "voicemailDetection": {
                "enabled": True,
                "machineDetectionTimeout": 30000
            },
            "recordingEnabled": False,
            "endCallOnSilence": False,
            "clientMessages": [],
            "serverMessages": [],
            "audioEncoding": "linear16",
            "sampleRate": 24000
        }
        
        if voice_provider == "openai":
            payload["voice"].update({
                "inputAudioEncoding": "linear16",
                "outputAudioEncoding": "linear16",
                "inputSampleRate": 24000,
                "outputSampleRate": 24000
            })
            payload["transcriber"] = {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "en-US",
                "smartFormat": False,
                "languageDetection": False,
                "profanityFilter": False,
                "redaction": False,
                "punctuation": True,
                "diarization": False,
                "numerals": False,
                "search": False,
                "replace": False,
                "keywords": []
            }
            payload.update({
                "analysisPlan": {
                    "summaryPlan": {
                        "enabled": False
                    },
                    "structuredDataPlan": {
                        "enabled": False
                    }
                }
            })
        
        logger.info(f"Creating assistant with payload: {payload}")
        response = requests.post("https://api.vapi.ai/assistant", headers=headers, json=payload)
        
        logger.info(f"Vapi API response status: {response.status_code}")
        logger.info(f"Vapi API response headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            logger.info(f"Vapi API response body: {response_data}")
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response text: {response.text}")
            return jsonify({'error': f"Invalid JSON response from Vapi API: {response.text}"}), 500
        
        if not response.ok:
            error_message = response_data.get('message', response.text) if response_data else response.text
            logger.error(f"Vapi API error: {response.status_code} - {error_message}")
            return jsonify({'error': f"Vapi API error ({response.status_code}): {error_message}"}), response.status_code
        
        logger.info(f"Assistant created successfully. Response keys: {list(response_data.keys()) if response_data else 'None'}")
        
        return jsonify({
            'success': True,
            'assistant_data': response_data,
            'response_debug': {
                'status': response.status_code,
                'keys': list(response_data.keys()) if response_data else []
            }
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating assistant: {e}")
        return jsonify({'error': f"Vapi API error: {e}"}), 500
    except Exception as e:
        logger.error(f"Error creating assistant: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/phone-numbers', methods=['GET'])
def get_phone_numbers():
    try:
        vapi_key = get_vapi_api_key()
        if not vapi_key:
            return jsonify({'error': 'Vapi API key not configured'}), 400
        
        headers = {
            "Authorization": f"Bearer {vapi_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get("https://api.vapi.ai/phone-number", headers=headers)
        response.raise_for_status()
        
        phone_numbers = response.json()
        
        return jsonify({
            'success': True,
            'phone_numbers': phone_numbers
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching phone numbers: {e}")
        return jsonify({'error': f"Vapi API error: {e}"}), 500
    except Exception as e:
        logger.error(f"Error fetching phone numbers: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/twilio-numbers', methods=['GET'])
def get_twilio_numbers():
    try:
        twilio_client = get_twilio_client()
        if not twilio_client:
            return jsonify({'error': 'Twilio credentials not configured'}), 400
        
        numbers = twilio_client.incoming_phone_numbers.list()
        
        twilio_numbers = []
        for number in numbers:
            twilio_numbers.append({
                'sid': number.sid,
                'phone_number': number.phone_number,
                'friendly_name': number.friendly_name,
                'capabilities': {
                    'voice': number.capabilities['voice'],
                    'sms': number.capabilities['sms'],
                    'mms': number.capabilities['mms'],
                    'fax': number.capabilities['fax']
                }
            })
        
        return jsonify({
            'success': True,
            'twilio_numbers': twilio_numbers
        })
        
    except Exception as e:
        logger.error(f"Error fetching Twilio numbers: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/register-phone-number', methods=['POST'])
def register_phone_number():
    try:
        vapi_key = get_vapi_api_key()
        twilio_client = get_twilio_client()
        
        if not vapi_key:
            return jsonify({'error': 'Vapi API key not configured'}), 400
        if not twilio_client:
            return jsonify({'error': 'Twilio credentials not configured'}), 400
        
        data = request.get_json()
        phone_number = data.get('phone_number')
        
        if not phone_number:
            return jsonify({'error': 'Phone number is required'}), 400
        
        twilio_account_sid = session.get('twilio_account_sid') or os.getenv('TWILIO_ACCOUNT_SID')
        twilio_auth_token = session.get('twilio_auth_token') or os.getenv('TWILIO_AUTH_TOKEN')
        
        headers = {
            "Authorization": f"Bearer {vapi_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "provider": "twilio",
            "number": phone_number,
            "twilioAccountSid": twilio_account_sid,
            "twilioAuthToken": twilio_auth_token
        }
        
        logger.info(f"Registering phone number with Vapi: {payload}")
        response = requests.post("https://api.vapi.ai/phone-number", headers=headers, json=payload)
        
        logger.info(f"Vapi phone number registration response: {response.status_code}")
        
        try:
            response_data = response.json()
            logger.info(f"Vapi phone number response body: {response_data}")
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return jsonify({'error': f"Invalid JSON response from Vapi API: {response.text}"}), 500
        
        if not response.ok:
            error_message = response_data.get('message', response.text) if response_data else response.text
            logger.error(f"Vapi API error: {response.status_code} - {error_message}")
            return jsonify({'error': f"Vapi API error ({response.status_code}): {error_message}"}), response.status_code
        
        logger.info(f"Phone number registered successfully: {response_data.get('id')}")
        
        return jsonify({
            'success': True,
            'vapi_phone_number': response_data
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error registering phone number: {e}")
        return jsonify({'error': f"Vapi API error: {e}"}), 500
    except Exception as e:
        logger.error(f"Error registering phone number: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/make-call', methods=['POST'])
def make_call():
    try:
        vapi_key = get_vapi_api_key()
        if not vapi_key:
            return jsonify({'error': 'Vapi API key not configured. Please set it in the API Configuration section.'}), 400
        
        data = request.get_json()
        customer_number = data.get('customer_number')
        twilio_phone_number_id = data.get('twilio_phone_number_id')
        vapi_assistant_id = data.get('vapi_assistant_id')
        
        if not all([customer_number, twilio_phone_number_id, vapi_assistant_id]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        headers = {
            "Authorization": f"Bearer {vapi_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "phoneNumberId": twilio_phone_number_id,
            "assistantId": vapi_assistant_id,
            "customer": {
                "number": customer_number
            }
        }
        
        logger.info(f"Making call with payload: {payload}")
        response = requests.post("https://api.vapi.ai/call", headers=headers, json=payload)
        
        logger.info(f"Vapi call API response status: {response.status_code}")
        logger.info(f"Vapi call API response headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            logger.info(f"Vapi call API response body: {response_data}")
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response text: {response.text}")
            return jsonify({'error': f"Invalid JSON response from Vapi API: {response.text}"}), 500
        
        if not response.ok:
            error_message = response_data.get('message', response.text) if response_data else response.text
            logger.error(f"Vapi call API error: {response.status_code} - {error_message}")
            return jsonify({'error': f"Vapi call API error ({response.status_code}): {error_message}"}), response.status_code
        
        vapi_call_data = response_data
        
        logger.info(f"Outbound call initiated via Vapi: {vapi_call_data.get('id')}")
        
        return jsonify({
            'success': True,
            'call_id': vapi_call_data.get('id'),
            'status': 'initiated',
            'call_data': vapi_call_data
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making Vapi call: {e}")
        return jsonify({'error': f"Vapi API error: {e}"}), 500
    except Exception as e:
        logger.error(f"Error making call: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-call', methods=['GET'])
def get_call():
    try:
        vapi_key = get_vapi_api_key()
        if not vapi_key:
            return jsonify({'error': 'Vapi API key not configured'}), 400
        
        call_id = request.args.get('call_id')
        if not call_id:
            return jsonify({'error': 'Call ID is required'}), 400
        
        headers = {
            "Authorization": f"Bearer {vapi_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Fetching call details for call ID: {call_id}")
        response = requests.get(f"https://api.vapi.ai/call/{call_id}", headers=headers)
        
        logger.info(f"Vapi get call response status: {response.status_code}")
        
        try:
            call_data = response.json()
            logger.info(f"Vapi call data keys: {list(call_data.keys()) if call_data else 'None'}")
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return jsonify({'error': f"Invalid JSON response from Vapi API: {response.text}"}), 500
        
        if not response.ok:
            error_message = call_data.get('message', response.text) if call_data else response.text
            logger.error(f"Vapi get call API error: {response.status_code} - {error_message}")
            return jsonify({'error': f"Vapi API error ({response.status_code}): {error_message}"}), response.status_code
        
        transcript = None
        transcript_text = ""
        
        if 'transcript' in call_data and call_data['transcript']:
            transcript = call_data['transcript']
            if isinstance(transcript, list):
                transcript_text = "\n".join([
                    f"[{item.get('timestamp', 'Unknown')}] {item.get('role', 'Unknown')}: {item.get('message', '')}"
                    for item in transcript if isinstance(item, dict)
                ])
            else:
                transcript_text = str(transcript)
        
        call_outcome = determine_call_outcome(call_data, transcript)
        
        call_info = {
            'id': call_data.get('id'),
            'status': call_data.get('status'),
            'outcome': call_outcome,
            'type': call_data.get('type'),
            'phoneNumber': call_data.get('phoneNumber', {}).get('number'),
            'customer': call_data.get('customer', {}).get('number'),
            'createdAt': call_data.get('createdAt'),
            'updatedAt': call_data.get('updatedAt'),
            'startedAt': call_data.get('startedAt'),
            'endedAt': call_data.get('endedAt'),
            'cost': call_data.get('cost'),
            'costBreakdown': call_data.get('costBreakdown'),
            'transcript': transcript,
            'transcript_text': transcript_text,
            'duration': call_data.get('endedAt') and call_data.get('startedAt'),
            'assistant': call_data.get('assistant', {}),
            'endReason': call_data.get('endedReason'),
            'messages': call_data.get('messages', [])
        }
        
        if call_data.get('startedAt') and call_data.get('endedAt'):
            from datetime import datetime
            try:
                start_time = datetime.fromisoformat(call_data['startedAt'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(call_data['endedAt'].replace('Z', '+00:00'))
                duration_seconds = (end_time - start_time).total_seconds()
                call_info['duration_seconds'] = duration_seconds
                call_info['duration_formatted'] = f"{int(duration_seconds // 60)}:{int(duration_seconds % 60):02d}"
            except Exception as e:
                logger.warning(f"Could not calculate call duration: {e}")
        
        return jsonify({
            'success': True,
            'call': call_info,
            'raw_data': call_data
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching call details: {e}")
        return jsonify({'error': f"Vapi API error: {e}"}), 500
    except Exception as e:
        logger.error(f"Error fetching call details: {str(e)}")
        return jsonify({'error': str(e)}), 500

def determine_call_outcome(call_data, transcript):
    status = call_data.get('status', '').lower()
    end_reason = call_data.get('endedReason', '').lower() if call_data.get('endedReason') else ''
    started_at = call_data.get('startedAt')
    ended_at = call_data.get('endedAt')
    cost = call_data.get('cost', 0)
    
    logger.info(f"Call outcome analysis - Status: {status}, EndReason: {end_reason}, Cost: {cost}, HasTranscript: {bool(transcript)}")
    
    if status == 'failed':
        if 'busy' in end_reason:
            return {'status': 'busy', 'description': 'Phone was busy'}
        elif 'no-answer' in end_reason or 'timeout' in end_reason:
            return {'status': 'no-answer', 'description': 'No answer - call timed out'}
        elif 'declined' in end_reason or 'rejected' in end_reason:
            return {'status': 'declined', 'description': 'Call was declined'}
        else:
            return {'status': 'failed', 'description': f'Call failed - {end_reason or "Unknown reason"}'}
    
    elif status == 'ended':
        duration_seconds = None
        if started_at and ended_at:
            try:
                from datetime import datetime
                start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(ended_at.replace('Z', '+00:00'))
                duration_seconds = (end_time - start_time).total_seconds()
            except Exception as e:
                logger.warning(f"Could not calculate call duration for outcome: {e}")
        
        if transcript and len(transcript) > 0:
            transcript_text = ""
            has_user_speech = False
            assistant_only = True
            
            if isinstance(transcript, list):
                for item in transcript:
                    if isinstance(item, dict):
                        role = item.get('role', '')
                        message = item.get('message', '').strip().lower()
                        transcript_text += f"{role}: {message} "
                        
                        if role == 'user' and message:
                            has_user_speech = True
                            assistant_only = False
                        elif role == 'assistant' and message:
                            assistant_only = True
            
            voicemail_indicators = [
                'voicemail', 'voice mail', 'leave a message', 'after the beep', 'beep',
                'unavailable', 'cannot take your call', 'please record', 'mailbox',
                'greeting', 'automated message'
            ]
            
            is_likely_voicemail = any(indicator in transcript_text.lower() for indicator in voicemail_indicators)
            
            if assistant_only and not has_user_speech:
                if duration_seconds and duration_seconds < 60:
                    return {'status': 'voicemail', 'description': 'Reached voicemail - message left by assistant'}
                elif is_likely_voicemail:
                    return {'status': 'voicemail', 'description': 'Reached voicemail - automated greeting detected'}
            
            if has_user_speech:
                if duration_seconds and duration_seconds > 30:
                    return {'status': 'answered', 'description': 'Call was answered - conversation recorded'}
                else:
                    return {'status': 'answered-brief', 'description': 'Call answered but ended quickly'}
        
        if duration_seconds is not None:
            if duration_seconds < 5:
                return {'status': 'no-answer', 'description': 'Call ended immediately - likely not answered'}
            elif duration_seconds < 15:
                if cost > 0:
                    return {'status': 'declined', 'description': 'Call was declined quickly'}
                else:
                    return {'status': 'no-answer', 'description': 'Call not answered'}
            elif duration_seconds < 45:
                if end_reason and 'customer-ended-call' in end_reason:
                    return {'status': 'answered-brief', 'description': 'Call answered but customer hung up quickly'}
                else:
                    return {'status': 'voicemail', 'description': 'Likely reached voicemail'}
            else:
                return {'status': 'answered', 'description': 'Call was answered'}
        
        if cost == 0:
            return {'status': 'no-answer', 'description': 'No cost incurred - call not connected'}
        elif cost < 0.01:
            return {'status': 'declined', 'description': 'Call declined - minimal cost'}
        else:
            if 'customer-ended-call' in end_reason:
                return {'status': 'answered', 'description': 'Call completed by customer'}
            else:
                return {'status': 'voicemail', 'description': 'Likely reached voicemail'}
        
        return {'status': 'completed', 'description': 'Call completed'}
    
    elif status in ['queued', 'ringing']:
        return {'status': 'ringing', 'description': 'Call is ringing...'}
    elif status == 'in-progress':
        return {'status': 'in-progress', 'description': 'Call is active'}
    
    else:
        return {'status': 'unknown', 'description': f'Unknown call status: {status}'}

def create_interview_system_message(knowledge_text="", knowledge_urls=""):
    
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
        urls_list = [url.strip() for url in knowledge_urls.split('\n') if url.strip()]
        if urls_list:
            knowledge_section += f"\n\nKNOWLEDGE BASE - REFERENCE URLS:\n" + "\n".join(f"- {url}" for url in urls_list)
            knowledge_section += "\nNote: Use these URLs as reference for topic context, but focus on the interview dialogue."
    
    if not knowledge_section:
        knowledge_section = "\n\nNote: Conduct a general professional interview since no specific knowledge base was provided."

    return base_instructions + knowledge_section

def create_professional_first_message(base_message, knowledge_text="", knowledge_urls=""):
    
    professional_message = base_message
    
    if knowledge_text.strip():
        topics = []
        lines = knowledge_text.split('\n')
        for line in lines:
            if line.strip() and ('?' in line or ':' in line):
                topic = line.split('?')[0].split(':')[0].strip()
                if len(topic) < 50 and topic not in topics:
                    topics.append(topic)
        
        if topics:
            topic_context = f" Today we'll be focusing on {', '.join(topics[:3])}."
            professional_message += topic_context
    
    professional_message += " I'm here to conduct a thorough and professional evaluation. Please feel free to take your time with your responses."
    
    return professional_message

def fetch_url_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        from html import unescape
        import re
        
        text = re.sub(r'<[^>]+>', ' ', response.text)
        text = unescape(text)
        
        text = ' '.join(text.split())
        
        return text[:2000] if len(text) > 2000 else text
        
    except Exception as e:
        logger.warning(f"Could not fetch URL content from {url}: {e}")
        return f"Could not access content from {url}"


if __name__ == '__main__':
    print("Starting Flask app...")
    print("Access the app at:")
    print("- Local: http://localhost:8080")
    print("- Local: http://127.0.0.1:8080")
    print("Press CTRL+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=8080, use_reloader=False)