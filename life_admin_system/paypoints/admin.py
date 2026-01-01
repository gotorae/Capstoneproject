from .models import Paypoint
from django.contrib import admin


class PaypointAdminModel(admin.ModelAdmin):
    list_display = ['paypoint_code','paypoint_name','date_joined']
    list_filter = ['paypoint_code','paypoint_name']
    search_fields = ['paypoint_code','paypoint_name']

admin.site.register(Paypoint, PaypointAdminModel)
