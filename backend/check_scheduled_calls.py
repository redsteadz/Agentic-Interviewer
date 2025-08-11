from api.models import ScheduledCall
from django.utils import timezone

print('All scheduled calls:')
for call in ScheduledCall.objects.all():
    print(f'ID: {call.id}, Time: {call.scheduled_time}, Status: {call.status}, Customer: {call.customer_number}')

print('\nCurrent time:', timezone.now())

print('\nDue calls:')
due_calls = ScheduledCall.objects.filter(
    status='scheduled',
    scheduled_time__lte=timezone.now()
)
for call in due_calls:
    print(f'Due: ID: {call.id}, Time: {call.scheduled_time}, Customer: {call.customer_number}')
