from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from bookings.models import Booking
from payments.models import Payment
from .serializers import CreatePaymentSerializer
import uuid
from django.db import transaction
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes


class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = Booking.objects.get(
            id=serializer.validated_data['booking_id'],
            user=request.user,
            status='PENDING'
        )

        # simulate gateway order creation
        gateway_order_id = str(uuid.uuid4())

        payment = Payment.objects.create(
            booking=booking,
            gateway='DUMMY',
            gateway_order_id=gateway_order_id,
            amount=booking.total_amount,
            status='INITIATED'
        )

        return Response({
            'gateway_order_id': gateway_order_id,
            'amount': payment.amount
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def payment_webhook(request):
    payload = request.data

    gateway_order_id = payload.get('order_id')
    payment_id = payload.get('payment_id')
    status_flag = payload.get('status')  # SUCCESS / FAILED

    try:
        with transaction.atomic():
            payment = Payment.objects.select_for_update().get(
                gateway_order_id=gateway_order_id
            )

            if status_flag == 'SUCCESS':
                payment.status = 'SUCCESS'
                payment.gateway_payment_id = payment_id
                payment.save()

                booking = payment.booking
                booking.status = 'CONFIRMED'
                booking.save()

            else:
                payment.status = 'FAILED'
                payment.save()

                booking = payment.booking
                booking.status = 'CANCELLED'
                booking.save()

    except Payment.DoesNotExist:
        return Response(
            {"error": "Invalid order"},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({"message": "Webhook processed"})
