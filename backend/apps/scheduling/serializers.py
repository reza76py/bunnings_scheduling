from rest_framework import serializers

from .models import CountingSession, SessionParticipant, Supplier


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


class SessionParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionParticipant
        fields = ['id', 'session', 'name', 'joined_at', 'left_at']
        read_only_fields = ['id']


class CountingSessionSerializer(serializers.ModelSerializer):
    participants = SessionParticipantSerializer(many=True, read_only=True)

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
            'participants',
        ]
        read_only_fields = ['id', 'duration_minutes', 'created_at']
