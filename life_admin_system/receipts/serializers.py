from rest_framework import serializers
from .models import PremiumReceipt, Upload
from django.utils import timezone


# -----------------------------
# Premium Receipt Serializer
# -----------------------------

class PremiumReceiptSerializer(serializers.ModelSerializer):
    policy_contract_id = serializers.CharField(
        source='policy.contract_id', read_only=True
    )
    receipted_by_username = serializers.CharField(
        source='receipted_by.username', read_only=True
    )

    class Meta:
        model = PremiumReceipt
        fields = [
            'id',
            'policy',
            'policy_contract_id',
            'receipt_number',
            'amount_received',
            'date_received',
            'total_received',
            'receipted_by',
            'receipted_by_username',
        ]
        read_only_fields = [
            'receipt_number',
            'total_received',
            'receipted_by',
            'date_received',
        ]


# -----------------------------
# Upload Serializer (normal CRUD)
# -----------------------------

class UploadSerializer(serializers.ModelSerializer):
    uploaded_by_username = serializers.CharField(
        source='uploaded_by.username', read_only=True
    )

    class Meta:
        model = Upload
        fields = [
            'id',
            'uploaded_by',
            'uploaded_by_username',
            'file',
            'uploaded_at',
            'is_approved',
            'approved_by',
            'approved_at',
            'is_rejected',
            'reject_reason',
        ]
        read_only_fields = [
            'uploaded_by',
            'uploaded_at',
            'approved_by',
            'approved_at',
            'is_approved',
            'is_rejected',
        ]


# -----------------------------
# Approval / Rejection Serializer
# (THIS is what makes the form appear)
# -----------------------------

class UploadDecisionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    reject_reason = serializers.CharField(
        required=False, allow_blank=True
    )
