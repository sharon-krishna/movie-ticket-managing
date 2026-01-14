from rest_framework import serializers


class CreatePaymentSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField()
