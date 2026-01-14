from django.db import models
from bookings.models import Booking


class Payment(models.Model):
    STATUS_CHOICES = (
        ('INITIATED', 'Initiated'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('EXPIRED', 'Expired'),
    )

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    gateway = models.CharField(max_length=50)
    gateway_order_id = models.CharField(max_length=255, unique=True)
    gateway_payment_id = models.CharField(max_length=255, blank=True, null=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

