from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from bookings.models import Booking, SeatLock
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

        return Response({'gateway_order_id': gateway_order_id,'amount': payment.amount}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def payment_webhook(request):
    payload = request.data

    gateway_order_id = payload.get('order_id')
    payment_id = payload.get('payment_id')
    status_flag = payload.get('status')  # SUCCESS / FAILED

    if not gateway_order_id or not status_flag:
        return Response({"error": "Invalid payload"},status=status.HTTP_400_BAD_REQUEST)

    channel_layer = get_channel_layer()

    try:
        with transaction.atomic():
            payment = Payment.objects.select_for_update().get(
                gateway_order_id=gateway_order_id
            )

            # Idempotency guard
            if payment.status == 'SUCCESS':
                return Response({"message": "Already processed"},status=status.HTTP_200_OK)

            booking = payment.booking

            if status_flag == 'SUCCESS':
                payment.status = 'SUCCESS'
                payment.gateway_payment_id = payment_id
                payment.save()

                booking.status = 'CONFIRMED'
                booking.save()

                # fetch locked seats BEFORE deleting locks
                seat_ids = list(
                    SeatLock.objects.filter(
                        show=booking.show,
                        user=booking.user
                    ).values_list('seat_id', flat=True)
                )

                # remove locks permanently
                SeatLock.objects.filter(
                    show=booking.show,
                    user=booking.user
                ).delete()

            else:
                payment.status = 'FAILED'
                payment.save()

                booking.status = 'CANCELLED'
                booking.save()

                seat_ids = list(
                    SeatLock.objects.filter(
                        show=booking.show,
                        user=booking.user
                    ).values_list('seat_id', flat=True)
                )

                SeatLock.objects.filter(
                    show=booking.show,
                    user=booking.user
                ).delete()

        #WebSocket broadcast AFTER transaction commit
        async_to_sync(channel_layer.group_send)(
            f"show_{booking.show_id}",
            {
                "type": "seat_event",
                "data": {
                    "event": "SEAT_BOOKED" if status_flag == 'SUCCESS' else "SEAT_RELEASED",
                    "seat_ids": seat_ids,
                    "booking_id": booking.id
                }
            }
        )

    except Payment.DoesNotExist:
        return Response({"error": "Invalid order ID"},status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Webhook processed"}, status=status.HTTP_200_OK)
