
# billing/serializers.py
from rest_framework import serializers
from billing.models import BillingRecord

class BillingRecordSerializer(serializers.ModelSerializer):
    policy_status = serializers.CharField(source="policy.overall_policy_status", read_only=True)
    contract_id = serializers.CharField(source="policy.contract_id", read_only=True)
    client_name = serializers.CharField(source="policy.client", read_only=True)

    class Meta:
        model = BillingRecord
        fields = ["id", "billing_month", "contract_id", "client_name", "policy_status"]
