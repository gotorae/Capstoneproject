
# agents/serializers.py
from rest_framework import serializers
from .models import Agent, Upload

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['agent_name', 'agent_surname', 'branch', 'date_joining']
        read_only_fields = ['agent_code']

class UploadSerializer(serializers.ModelSerializer):
    # Read-only state fields; API callers only POST the file
    uploaded_by = serializers.CharField(source='uploaded_by.username', read_only=True)
    approved_by = serializers.CharField(source='approved_by.username', read_only=True)

    class Meta:
        model = Upload
        fields = [
            'id', 'file', 'uploaded_by', 'uploaded_at',
            'is_approved', 'approved_by', 'approved_at',
            'is_rejected', 'reject_reason', 'created_at'
        ]
        read_only_fields = [
            'uploaded_by', 'uploaded_at',
            'is_approved', 'approved_by', 'approved_at',
            'is_rejected', 'reject_reason', 'created_at'
        ]


class UploadDecisionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    reject_reason = serializers.CharField(
        required=False, allow_blank=True
    )
