from django.core.management.base import BaseCommand
from django.utils import timezone
import logging
import requests
from api.models import ScheduledCall, InterviewCall, APIConfiguration


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Execute scheduled calls that are due'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Execute scheduled calls for a specific user only',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show which calls would be executed without actually executing them',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        dry_run = options.get('dry_run', False)

        # Get all due scheduled calls
        queryset = ScheduledCall.objects.filter(
            status='scheduled',
            scheduled_time__lte=timezone.now()
        )

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        due_calls = queryset.order_by('scheduled_time')

        if not due_calls.exists():
            self.stdout.write(
                self.style.SUCCESS('No scheduled calls are due for execution.')
            )
            return

        self.stdout.write(f'Found {due_calls.count()} scheduled calls due for execution.')

        executed_count = 0
        failed_count = 0

        for scheduled_call in due_calls:
            if dry_run:
                self.stdout.write(
                    f'Would execute: {scheduled_call} (ID: {scheduled_call.id})'
                )
                continue

            try:
                result = self.execute_scheduled_call(scheduled_call)
                if result['success']:
                    executed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully executed scheduled call {scheduled_call.id}: {result["message"]}'
                        )
                    )
                else:
                    failed_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f'Failed to execute scheduled call {scheduled_call.id}: {result["error"]}'
                        )
                    )
            except Exception as e:
                failed_count += 1
                logger.error(f'Error executing scheduled call {scheduled_call.id}: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(
                        f'Error executing scheduled call {scheduled_call.id}: {str(e)}'
                    )
                )

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Execution complete. {executed_count} calls executed, {failed_count} failed.'
                )
            )

    def execute_scheduled_call(self, scheduled_call):
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
                'success': False,
                'error': f"Vapi API error: {str(e)}"
            }

        except Exception as e:
            scheduled_call.status = 'failed'
            scheduled_call.error_message = str(e)
            scheduled_call.save()
            
            return {
                'success': False,
                'error': str(e)
            }
