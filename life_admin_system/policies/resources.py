

        

from import_export import resources
from .models import Policy

class PolicyResource(resources.ModelResource):
    class Meta:
        model = Policy
        fields = (
            'contract_id',
            'product_name',
            'product_code',
            'start_date',
            'proposal_sign_date',
            'beneficiary_name',
            'beneficiary_id',
            'agent__agent_name',
            'agent__agent_surname',
            'paypoint__paypoint_name',
            'client__client_name',
            'client__client_surname',
            'frequency',
            'cover',
            'contract_premium',
            'total_premium_due',
            'total_premium_received',
            'total_premium_arrears',
            'duration',
            'current_month',
            'overall_policy_status',
            'created_date',
        )

