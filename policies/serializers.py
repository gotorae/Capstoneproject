from rest_framework import serializers
from .models import Policy, Upload

# -----------------------------
# Policy Serializer
# -----------------------------
class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = [
            'product_name','proposal_sign_date','beneficiary_name','beneficiary_id',
            'start_date','agent','paypoint','client','frequency','cover',
        ]
        read_only_fields = [
            'contract_id','product_code','current_month','duration',
            'total_premium_due','total_premium_received','contract_premium','created_date','created_by'
        ]


# -----------------------------
# Upload Serializer (normal CRUD)
# -----------------------------
class UploadSerializer(serializers.ModelSerializer):
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)

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
# -----------------------------
class UploadDecisionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    reject_reason = serializers.CharField(required=False, allow_blank=True)
