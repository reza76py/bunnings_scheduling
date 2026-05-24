from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import CountingSession, SessionParticipant, Supplier
from .serializers import CountingSessionSerializer, SessionParticipantSerializer, SupplierSerializer


@method_decorator(csrf_exempt, name='dispatch')
class SupplierViewSet(viewsets.ModelViewSet):
	queryset = Supplier.objects.all().order_by('-created_at')
	serializer_class = SupplierSerializer


@method_decorator(csrf_exempt, name='dispatch')
class CountingSessionViewSet(viewsets.ModelViewSet):
	queryset = CountingSession.objects.select_related('supplier').all().order_by('-created_at')
	serializer_class = CountingSessionSerializer

	def create(self, request, *args, **kwargs):
		payload = request.data.copy()
		session_id = payload.pop('session_id', None)
		if session_id:
			try:
				session = self.get_queryset().get(pk=session_id)
			except CountingSession.DoesNotExist:
				return Response({'detail': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)

			serializer = self.get_serializer(session, data=payload, partial=True)
			serializer.is_valid(raise_exception=True)
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)

		serializer = self.get_serializer(data=payload)
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

	@action(detail=False, methods=['post'])
	def start(self, request):
		payload = {
			'supplier': request.data.get('supplier'),
			'value': request.data.get('value'),
			'people_working': request.data.get('people_working'),
			'start_time': timezone.now(),
		}
		serializer = self.get_serializer(data=payload)
		serializer.is_valid(raise_exception=True)
		session = serializer.save()
		return Response({'session_id': session.id}, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class SessionParticipantViewSet(viewsets.GenericViewSet):
	queryset = SessionParticipant.objects.select_related('session').all()
	serializer_class = SessionParticipantSerializer

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

	def perform_create(self, serializer):
		serializer.save()

	def get_success_headers(self, data):
		try:
			return {'Location': str(data['id'])}
		except (TypeError, KeyError):
			return {}

	@action(detail=True, methods=['patch'])
	def leave(self, request, pk=None):
		participant = self.get_object()
		participant.left_at = timezone.now()
		participant.save(update_fields=['left_at'])
		serializer = self.get_serializer(participant)
		return Response(serializer.data)

	@action(detail=True, methods=['patch'])
	def rejoin(self, request, pk=None):
		participant = self.get_object()
		rejoined = SessionParticipant.objects.create(
			session=participant.session,
			name=participant.name,
			joined_at=timezone.now(),
		)
		serializer = self.get_serializer(rejoined)
		return Response(serializer.data, status=status.HTTP_201_CREATED)
