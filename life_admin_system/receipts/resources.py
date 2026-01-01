from import_export import resources
from .models import PremiumReceipt

class PremiumReceiptResource(resources.ModelResource):
    class Meta:
        model = PremiumReceipt
        fields = (
            'policy',
            'amount_received',
            
        )

