
# agents/resources.py
from import_export import resources
from .models import Agent

class AgentResource(resources.ModelResource):
       class Meta:
        model = Agent
        fields = ('id', 'agent_code', 'agent_name', 'agent_surname', 'branch', 'date_joining')
