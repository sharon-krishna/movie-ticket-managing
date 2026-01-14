from rest_framework.routers import DefaultRouter
from api.v1.theatres.views import TheatreAdminViewSet, ScreenAdminViewSet, SeatAdminViewSet, ShowAdminViewSet


router = DefaultRouter()
router.register('theatres', TheatreAdminViewSet)
router.register('screens', ScreenAdminViewSet)
router.register('seats', SeatAdminViewSet)
router.register('shows', ShowAdminViewSet)

urlpatterns = router.urls
