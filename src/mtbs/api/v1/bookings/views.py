from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from theatres.models import Show, Seat

from bookings.models import SeatLock, Booking
from .serializers import SeatLockSerializer, CreateBookingSerializer
from django.conf import settings


class LockSeatsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SeatLockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        show_id = serializer.validated_data['show_id']
        seat_ids = serializer.validated_data['seat_ids']

        expires_at = timezone.now() + timedelta(minutes=settings.SEAT_LOCK_MINUTES)

        with transaction.atomic():
            for seat_id in seat_ids:
                SeatLock.objects.create(
                    show_id=show_id,
                    seat_id=seat_id,
                    user=request.user,
                    expires_at=expires_at
                )

        return Response({"message": "Seats locked"},status=status.HTTP_201_CREATED)


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
            return Response(
                {"error": "Seats not locked by user"},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_price = 0  # calculate later (fixed price for now)

        booking = Booking.objects.create(user=request.user,show_id=show_id,status='PENDING',total_amount=total_price)

        return Response({"booking_id": booking.id},status=status.HTTP_201_CREATED)


class ReleaseSeatsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        SeatLock.objects.filter(
            user=request.user
        ).delete()

        return Response({"message": "Locks released"})
