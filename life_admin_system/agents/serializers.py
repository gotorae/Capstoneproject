from rest_framework import serializers
from .models import Agent


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['agent_name', 'agent_surname','branch','date_joining']
        read_only_fields = ['agent_code']