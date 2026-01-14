from rest_framework import serializers
from theatres.models import Theatre, Show, Seat, Screen
from django.db.models import Q
from rest_framework.exceptions import ValidationError


class TheatreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theatre
        fields = '__all__'


class ScreenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screen
        fields = '__all__'


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = '__all__'


class ShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Show
        fields = '__all__'

    def validate(self, data):
        screen = data['screen']
        start = data['start_time']
        end = data['end_time']

        conflict = Show.objects.filter(
            screen=screen
        ).filter(
            Q(start_time__lt=end) &
            Q(end_time__gt=start)
        )

        if self.instance:
            conflict = conflict.exclude(id=self.instance.id)

        if conflict.exists():
            raise ValidationError("Show timing overlaps with another show.")

        return data
