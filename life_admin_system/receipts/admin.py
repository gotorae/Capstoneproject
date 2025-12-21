from django.contrib import admin
from .models import PremiumReceipt
from django.db import models




class PremiumReceiptAdminModel(admin.ModelAdmin):
    list_display = ['policy','receipt_number','amount_received','date_received','total_received', 'receipted_by']
    list_filter = ['policy']
    search_fields= ['policy']

admin.site.register(PremiumReceipt, PremiumReceiptAdminModel)
# Register your models here.
