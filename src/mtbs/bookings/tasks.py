from celery import shared_task
from django.utils import timezone
from .models import SeatLock
from .models import Booking


@shared_task
def expire_seat_locks():
    expired = SeatLock.objects.filter(
        expires_at__lt=timezone.now()
    )
    count = expired.count()
    expired.delete()
    return f"{count} seat locks expired"

@shared_task
def expire_pending_bookings():
    expired = Booking.objects.filter(
        status='PENDING',
        created_at__lt=timezone.now() - timezone.timedelta(minutes=10)
    )
    count = expired.count()
    expired.update(status='EXPIRED')
    return f"{count} bookings expired"
