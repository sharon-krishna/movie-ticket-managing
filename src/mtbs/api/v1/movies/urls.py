from rest_framework.routers import DefaultRouter
from .views import MovieAdminViewSet


router = DefaultRouter()
router.register('movies', MovieAdminViewSet, basename='movies')

urlpatterns = router.urls
