from django.urls import path
from .views import LockSeatsView, CreateBookingView, ReleaseSeatsView, SeatAvailabilityView

urlpatterns = [
    path('lock/', LockSeatsView.as_view()),
    path('create/', CreateBookingView.as_view()),
    path('release/', ReleaseSeatsView.as_view()),
    path('availability/<int:show_id>/',SeatAvailabilityView.as_view()),
]
