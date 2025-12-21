from .models import PremiumReceipt
from rest_framework import serializers

class PremiumReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = PremiumReceipt
        fields = ['policy', 'amount_received', 'date_received']
        read_only_fields = ['receipt_number', 'date_received', 'receipted_by']