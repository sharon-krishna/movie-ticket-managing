from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminUserRole
from api.v1.theatres.serializers import TheatreSerializer, ScreenSerializer, SeatSerializer, ShowSerializer
from theatres.models import Theatre, Screen, Seat, Show


class TheatreAdminViewSet(ModelViewSet):
    queryset = Theatre.objects.all()
    serializer_class = TheatreSerializer
    permission_classes = [IsAuthenticated, IsAdminUserRole]


class ScreenAdminViewSet(ModelViewSet):
    queryset = Screen.objects.all()
    serializer_class = ScreenSerializer
    permission_classes = [IsAuthenticated, IsAdminUserRole]


class SeatAdminViewSet(ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [IsAuthenticated, IsAdminUserRole]


class ShowAdminViewSet(ModelViewSet):
    queryset = Show.objects.all()
    serializer_class = ShowSerializer
    permission_classes = [IsAuthenticated, IsAdminUserRole]
