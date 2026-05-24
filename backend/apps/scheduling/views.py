from rest_framework import viewsets
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import CountingSession, Supplier
from .serializers import CountingSessionSerializer, SupplierSerializer


@method_decorator(csrf_exempt, name='dispatch')
class SupplierViewSet(viewsets.ModelViewSet):
	queryset = Supplier.objects.all().order_by('-created_at')
	serializer_class = SupplierSerializer


@method_decorator(csrf_exempt, name='dispatch')
class CountingSessionViewSet(viewsets.ModelViewSet):
	queryset = CountingSession.objects.select_related('supplier').all().order_by('-created_at')
	serializer_class = CountingSessionSerializer
