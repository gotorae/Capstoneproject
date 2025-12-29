from rest_framework import serializers
from claims.models import Claim


class ClaimCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = (
            "policy",
            "account_number",
            "burial_order",
            "death_certificate",
            "claim_form",
        )

    def validate(self, attrs):
        if not attrs.get("burial_order") and not attrs.get("death_certificate"):
            raise serializers.ValidationError(
                "Burial order or death certificate is required."
            )
        return attrs


class ClaimApprovalSerializer(serializers.Serializer):
    approve = serializers.BooleanField(default=True)
