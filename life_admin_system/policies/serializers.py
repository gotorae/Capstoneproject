from rest_framework import serializers
from .models import Policy

class PolicySerializers(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ['product_name','proposal_sign_date','start_date','agent', 'paypoint','client',
                  'frequency','cover',]
        
        read_only_fields = ['contract_id','product_code', 'current_month',
                            'duration', 'total_premium_due', 'total_premium_received',
                            'total_premium_received','contract_premium', 'created_date', 'created_by']