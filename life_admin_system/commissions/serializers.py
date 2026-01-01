
# commissions/serializers.py
from rest_framework import serializers
from commissions.models import CommissionRecord

class CommissionRecordSerializer(serializers.ModelSerializer):
    contract_id = serializers.CharField(source="policy.contract_id", read_only=True)
    client_name = serializers.CharField(source="policy.client", read_only=True)
    agent_code = serializers.CharField(source="agent.agent_code", read_only=True)
    agent_name = serializers.SerializerMethodField()
    contract_premium = serializers.DecimalField(source="policy.contract_premium",
                                                max_digits=12, decimal_places=2, read_only=True)

    def get_agent_name(self, obj):
        return f"{obj.agent.agent_name} {obj.agent.agent_surname}"

    class Meta:
        model = CommissionRecord
        fields = [
            "id", "commission_month", "contract_id", "client_name",
            "agent_code", "agent_name", "contract_premium", "commission_due",
        ]
