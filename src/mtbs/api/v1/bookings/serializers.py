from rest_framework import serializers


class SeatLockSerializer(serializers.Serializer):
    show_id = serializers.IntegerField()
    seat_ids = serializers.ListField(
        child=serializers.IntegerField()
    )

class CreateBookingSerializer(serializers.Serializer):
    show_id = serializers.IntegerField()
    seat_ids = serializers.ListField(
        child=serializers.IntegerField()
    )
