"""
Celery tasks for scheduled call execution.

To use this in production:
1. Install Celery and Redis: pip install celery redis
2. Start Redis server
3. Start Celery worker: celery -A backend worker --loglevel=info
4. Start Celery beat: celery -A backend beat --loglevel=info

For development, you can run the management command manually:
python manage.py execute_scheduled_calls
"""

import logging
from celery import shared_task
from django.utils import timezone
from api.models import ScheduledCall, InterviewCall, APIConfiguration
import requests

logger = logging.getLogger(__name__)


@shared_task
def execute_due_scheduled_calls():
    """
    Celery task to execute all due scheduled calls.
    This task should be run periodically (e.g., every minute).
    """
    try:
        # Get all due scheduled calls
        due_calls = ScheduledCall.objects.filter(
            status='scheduled',
            scheduled_time__lte=timezone.now()
        ).order_by('scheduled_time')

        if not due_calls.exists():
            logger.info('No scheduled calls are due for execution.')
            return {'status': 'success', 'executed': 0, 'message': 'No calls due'}

        executed_count = 0
        failed_count = 0
        results = []

        for scheduled_call in due_calls:
            try:
                result = execute_single_scheduled_call(scheduled_call)
                results.append(result)
                if result['success']:
                    executed_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                logger.error(f'Error executing scheduled call {scheduled_call.id}: {str(e)}')
                results.append({
                    'scheduled_call_id': scheduled_call.id,
                    'success': False,
                    'error': str(e)
                })

        logger.info(f'Scheduled calls execution complete. {executed_count} executed, {failed_count} failed.')
        
        return {
            'status': 'success',
            'executed': executed_count,
            'failed': failed_count,
            'total_due': len(due_calls),
            'results': results
        }

    except Exception as e:
        logger.error(f'Error in execute_due_scheduled_calls task: {str(e)}')
        return {'status': 'error', 'error': str(e)}


def execute_single_scheduled_call(scheduled_call):
    """Execute a single scheduled call"""
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

        # Prepare call payload
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
            'message': f'Call initiated successfully for {scheduled_call.customer_number}'
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


# You can add this to your settings.py for Celery Beat schedule:
"""
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'execute-scheduled-calls': {
        'task': 'api.tasks.execute_due_scheduled_calls',
        'schedule': crontab(minute='*'),  # Run every minute
    },
}
"""
