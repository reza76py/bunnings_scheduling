from rest_framework import viewsets

from .models import CountingSession, Supplier
from .serializers import CountingSessionSerializer, SupplierSerializer


class SupplierViewSet(viewsets.ModelViewSet):
	queryset = Supplier.objects.all().order_by('-created_at')
	serializer_class = SupplierSerializer


class CountingSessionViewSet(viewsets.ModelViewSet):
	queryset = CountingSession.objects.select_related('supplier').all().order_by('-created_at')
	serializer_class = CountingSessionSerializer
