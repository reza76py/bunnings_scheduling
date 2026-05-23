from rest_framework.routers import DefaultRouter

from .views import CountingSessionViewSet, SupplierViewSet

router = DefaultRouter()
router.register('sessions', CountingSessionViewSet, basename='sessions')
router.register('suppliers', SupplierViewSet, basename='suppliers')

urlpatterns = router.urls
