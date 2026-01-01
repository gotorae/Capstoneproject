from django.contrib import admin
from .models import Agent, Client,Paypoint, Policy,PremiumReceipt
from django.db import models


class AgentAdminModel(admin.ModelAdmin):
    list_display = ['agent_code', 'agent_name','agent_surname','branch', 'date_joining']
    list_filter = ['agent_code','agent_surname','branch']
    search_fields = ['agent_code','agent_surname','branch']

admin.site.register(Agent, AgentAdminModel)

class ClientAdminModel(admin.ModelAdmin):
    list_display = ['client_code', 'client_name','client_surname','id_number','dob','email','phone_number']
    list_filter = ['client_code', 'client_name','client_surname','id_number','phone_number']
    search_fields = ['client_code', 'client_name','client_surname','id_number','phone_number']

admin.site.register(Client, ClientAdminModel)

class PolicyAdminModel(admin.ModelAdmin):
    list_display = ['contract_id','product_name','product_code','contract_premium','start_date','proposal_sign_date','agent','paypoint','client','total_premium_received','duration','current_month','total_premium_due','total_premium_arrears','months_in_arrears', 'months_paid', 'policy_status']
    list_filter = ['contract_id','product_name','product_code']
    search_fields = ['contract_id','product_name','product_code']

    

admin.site.register(Policy, PolicyAdminModel)


class PaypointAdminModel(admin.ModelAdmin):
    list_display = ['paypoint_code','paypoint_name','date_joined']
    list_filter = ['paypoint_code','paypoint_name']
    search_fields = ['paypoint_code','paypoint_name']

admin.site.register(Paypoint, PaypointAdminModel)

class PremiumReceiptAdminModel(admin.ModelAdmin):
    list_display = ['policy','receipt_number','amount_received','date_received','total_received']
    list_filter = ['policy']
    search_fields= ['policy']

admin.site.register(PremiumReceipt, PremiumReceiptAdminModel)
# Register your models here.
