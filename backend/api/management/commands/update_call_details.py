from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import InterviewCall, APIConfiguration
import requests
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update call details and transcripts from Vapi API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--call-id',
            type=str,
            help='Specific call ID to update (optional)'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Update calls from the last N hours (default: 24)'
        )

    def handle(self, *args, **options):
        self.stdout.write("🔄 Starting call details update...")
        
        # Get API configuration
        config = APIConfiguration.objects.first()
        if not config or not config.vapi_api_key:
            self.stdout.write(self.style.ERROR("❌ No Vapi API key configured"))
            return

        headers = {
            'Authorization': f'Bearer {config.vapi_api_key}',
            'Content-Type': 'application/json'
        }

        # Get calls to update
        if options['call_id']:
            calls = InterviewCall.objects.filter(vapi_call_id=options['call_id'])
        else:
            # Get calls from last N hours that might need updating
            cutoff_time = timezone.now() - timezone.timedelta(hours=options['hours'])
            calls = InterviewCall.objects.filter(
                created_at__gte=cutoff_time,
                vapi_call_id__isnull=False
            ).exclude(status='ended')

        updated_count = 0
        failed_count = 0

        for call in calls:
            try:
                self.stdout.write(f"📞 Updating call {call.vapi_call_id}...")
                result = self.update_call_details(call, headers)
                
                if result['success']:
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Updated call {call.id}: {result['message']}")
                    )
                else:
                    failed_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"❌ Failed to update call {call.id}: {result['error']}")
                    )
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error updating call {call.id}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f"❌ Error updating call {call.id}: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"🎉 Update complete: {updated_count} updated, {failed_count} failed"
            )
        )

    def update_call_details(self, call, headers):
        """Update a single call with details from Vapi API"""
        try:
            # Get call details from Vapi
            url = f'https://api.vapi.ai/call/{call.vapi_call_id}'
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Vapi API error: {response.status_code} - {response.text}'
                }

            call_data = response.json()
            
            # Update call fields
            call.status = call_data.get('status', call.status)
            call.raw_call_data = call_data
            
            # Update timestamps
            from dateutil import parser as date_parser
            if call_data.get('startedAt'):
                call.started_at = date_parser.parse(call_data['startedAt'])
            if call_data.get('endedAt'):
                call.ended_at = date_parser.parse(call_data['endedAt'])
            
            # Update duration
            if call_data.get('duration'):
                call.duration_seconds = call_data['duration']
            elif call.started_at and call.ended_at:
                duration = (call.ended_at - call.started_at).total_seconds()
                call.duration_seconds = int(duration)
            
            # Update cost
            if call_data.get('cost'):
                call.cost = call_data['cost']
                call.cost_breakdown = call_data.get('costBreakdown', {})
            
            # Update transcript
            transcript = call_data.get('transcript')
            if transcript:
                if isinstance(transcript, list):
                    # Convert transcript array to text
                    transcript_text = ""
                    for item in transcript:
                        if isinstance(item, dict):
                            role = item.get('role', 'unknown')
                            message = item.get('message', '')
                            transcript_text += f"{role}: {message}\n"
                        else:
                            transcript_text += str(item) + "\n"
                    call.transcript_text = transcript_text
                    call.transcript = transcript
                else:
                    call.transcript_text = str(transcript)
            
            # Update outcome
            call.outcome_status = self.determine_call_outcome(call_data)
            if call_data.get('endReason'):
                call.end_reason = call_data['endReason']
            
            call.save()
            
            return {
                'success': True,
                'message': f'Status: {call.status}, Duration: {call.duration_seconds}s, Cost: ${call.cost}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def determine_call_outcome(self, call_data):
        """Determine call outcome based on Vapi data"""
        status = call_data.get('status', '')
        end_reason = call_data.get('endReason', '')
        duration = call_data.get('duration', 0)
        
        if status == 'ended':
            if 'no-answer' in end_reason.lower() or 'declined' in end_reason.lower():
                return 'no-answer'
            elif 'voicemail' in end_reason.lower():
                return 'voicemail'
            elif duration and duration > 10:
                return 'answered'
            elif duration and duration <= 10:
                return 'answered-brief'
            else:
                return 'completed'
        
        return status