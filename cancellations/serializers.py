from rest_framework import serializers
from .models import CancellationRequest, CancellationStatus


class CancellationRequestSerializer(serializers.ModelSerializer):
    policy_contract_id = serializers.CharField(
        source="policy.contract_id", read_only=True
    )
    requested_by_username = serializers.CharField(
        source="requested_by.username", read_only=True
    )
    approved_by_username = serializers.CharField(
        source="approved_by.username", read_only=True
    )

    class Meta:
        model = CancellationRequest
        fields = [
            "id",
            "policy",
            "policy_contract_id",
            "requested_by",
            "requested_by_username",
            "requested_at",
            "effective_date",
            "status",
            "approved_by",
            "approved_by_username",
            "approved_at",
        ]
        read_only_fields = [
            "requested_by",
            "requested_at",
            "status",
            "approved_by",
            "approved_at",
        ]


class CancellationApprovalSerializer(serializers.Serializer):
    """
    Used only for approving a cancellation
    """
    approve = serializers.BooleanField()
