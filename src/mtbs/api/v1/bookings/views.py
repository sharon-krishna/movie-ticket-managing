from django.db import transaction
from django.db.utils import IntegrityError
from django.utils import timezone
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from bookings.models import SeatLock, Booking
from theatres.models import Seat
from .serializers import SeatLockSerializer, CreateBookingSerializer
from django.conf import settings

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class LockSeatsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SeatLockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        show_id = serializer.validated_data["show_id"]
        seat_ids = serializer.validated_data["seat_ids"]

        expires_at = timezone.now() + timedelta(
            minutes=settings.SEAT_LOCK_MINUTES
        )

        channel_layer = get_channel_layer()

        try:
            with transaction.atomic():
                for seat_id in seat_ids:
                    SeatLock.objects.create(
                        show_id=show_id,
                        seat_id=seat_id,
                        user=request.user,
                        expires_at=expires_at,
                    )

        except IntegrityError:
            return Response({"error": "One or more seats are already locked"},status=status.HTTP_400_BAD_REQUEST,)

        async_to_sync(channel_layer.group_send)(
            f"show_{show_id}",
            {
                "type": "seat_event",
                "data": {
                    "event": "SEAT_LOCKED",
                    "seat_ids": seat_ids,
                    "user_id": request.user.id,
                },
            },
        )

        return Response({"message": "Seats locked successfully"},status=status.HTTP_201_CREATED,)


class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        show_id = serializer.validated_data['show_id']
        seat_ids = serializer.validated_data['seat_ids']

        locks = SeatLock.objects.filter(
            show_id=show_id,
            seat_id__in=seat_ids,
            user=request.user
        )

        if locks.count() != len(seat_ids):
            return Response({"error": "Seats not locked by user"},status=status.HTTP_400_BAD_REQUEST)

        total_price = 0  # TODO: calculate from show price

        booking = Booking.objects.create(
            user=request.user,
            show_id=show_id,
            status='PENDING',
            total_amount=total_price
        )

        return Response({"booking_id": booking.id},status=status.HTTP_201_CREATED)


class ReleaseSeatsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        locks = SeatLock.objects.filter(user=request.user)

        if not locks.exists():
            return Response({"message": "No locks to release"},status=status.HTTP_200_OK)

        show_id = locks.first().show_id
        seat_ids = list(locks.values_list('seat_id', flat=True))

        locks.delete()

        channel_layer = get_channel_layer()

        #WebSocket broadcast
        async_to_sync(channel_layer.group_send)(
            f"show_{show_id}",
            {
                "type": "seat_event",
                "data": {
                    "event": "SEAT_RELEASED",
                    "seat_ids": seat_ids,
                    "user_id": request.user.id
                }
            }
        )

        return Response({"message": "Locks released"},status=status.HTTP_200_OK)


class SeatAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, show_id):
        now = timezone.now()

        # All seats for the show’s screen
        seats = Seat.objects.filter(
            screen__shows__id=show_id
        ).distinct()

        #Locked seats (not expired)
        locked_seats = set(
            SeatLock.objects.filter(
                show_id=show_id,
                expires_at__gt=now
            ).values_list('seat_id', flat=True)
        )

        #Booked seats (CONFIRMED bookings)
        booked_seats = set(
            Booking.objects.filter(
                show_id=show_id,
                status='CONFIRMED'
            ).values_list('bookingseat__seat_id', flat=True)
        )

        response = []

        for seat in seats:
            if seat.id in booked_seats:
                status = 'BOOKED'
            elif seat.id in locked_seats:
                status = 'LOCKED'
            else:
                status = 'AVAILABLE'

            response.append({
                "seat_id": seat.id,
                "row_label": seat.row_label,
                "seat_number": seat.seat_number,
                "status": status
            })

        return Response(response)
