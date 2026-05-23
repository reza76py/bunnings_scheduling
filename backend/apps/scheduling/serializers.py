from rest_framework import serializers

from .models import CountingSession, Supplier


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


class CountingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountingSession
        fields = [
            'id',
            'supplier',
            'value',
            'people_working',
            'start_time',
            'end_time',
            'duration_minutes',
            'created_at',
        ]
        read_only_fields = ['id', 'duration_minutes', 'created_at']
