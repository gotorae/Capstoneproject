from django.contrib import admin
from .models import Agent
from django.db import models


class AgentAdminModel(admin.ModelAdmin):
    readonly_fields = ('agent_code',)
    list_display = ['agent_code', 'agent_name','agent_surname','branch', 'date_joining']
    list_filter = ['agent_code','agent_surname','branch']
    search_fields = ['agent_code','agent_surname','branch']

admin.site.register(Agent, AgentAdminModel)
