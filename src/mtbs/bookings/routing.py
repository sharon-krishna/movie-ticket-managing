from django.urls import path
from .consumers import SeatConsumer

websocket_urlpatterns = [
    path('ws/seats/<int:show_id>/', SeatConsumer.as_asgi()),
]
