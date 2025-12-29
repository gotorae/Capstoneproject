from django.contrib import admin
from .models import Policy
from django.db import models


class PolicyAdminModel(admin.ModelAdmin):
    
    list_display = [
        'contract_id',
        'product_name',
        'product_code',
        'contract_premium',
        'start_date',
        'proposal_sign_date',
        'agent',
        'paypoint',
        'client',

        # FINANCIALS
        'total_premium_received',
        'duration',
        'current_month',
        'total_premium_due',
        'total_premium_arrears',
        'months_in_arrears',
        'months_paid',

        # CLAIM & CANCELLATION
        'claim_status',
        'claim_effective_date',
        'cancellation_status',
        'cancellation_effective_date',

        # OVERALL STATUS
        'overall_policy_status',

        'policy_status',
        'created_date',
        'created_by',
    ]


    list_filter = ['contract_id','product_name','product_code', 'created_by', 'created_date']
    search_fields = ['contract_id','product_name','product_code', 'created_by', 'created_date']

    

admin.site.register(Policy, PolicyAdminModel)




