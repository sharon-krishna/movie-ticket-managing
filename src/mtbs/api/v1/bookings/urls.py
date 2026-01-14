from django.urls import path
from .views import LockSeatsView, CreateBookingView, ReleaseSeatsView

urlpatterns = [
    path('lock/', LockSeatsView.as_view()),
    path('create/', CreateBookingView.as_view()),
    path('release/', ReleaseSeatsView.as_view()),
]
