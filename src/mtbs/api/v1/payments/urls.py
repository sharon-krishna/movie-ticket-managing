from django.urls import path
from .views import CreatePaymentView, payment_webhook

urlpatterns = [
    path('create/', CreatePaymentView.as_view()),
    path('webhook/', payment_webhook),
]
