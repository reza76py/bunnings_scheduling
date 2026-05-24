from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import CountingSessionViewSet, SessionParticipantViewSet, SupplierViewSet

router = DefaultRouter()
router.register('sessions', CountingSessionViewSet, basename='sessions')
router.register('suppliers', SupplierViewSet, basename='suppliers')

participant_create = SessionParticipantViewSet.as_view({'post': 'create'})
participant_leave = SessionParticipantViewSet.as_view({'patch': 'leave'})
participant_rejoin = SessionParticipantViewSet.as_view({'patch': 'rejoin'})

urlpatterns = [
	*router.urls,
	path('participants/', participant_create, name='participants-create'),
	path('participants/<int:pk>/leave/', participant_leave, name='participants-leave'),
	path('participants/<int:pk>/rejoin/', participant_rejoin, name='participants-rejoin'),
]
