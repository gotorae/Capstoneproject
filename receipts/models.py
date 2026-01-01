from decimal import Decimal
from datetime import date
from django.db import models, transaction
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum
from policies.models import Policy
from access.models import Administrator
from django.conf import settings
from auditlog.registry import auditlog




class PremiumReceipt(models.Model):
    policy = models.ForeignKey('policies.Policy', on_delete=models.CASCADE, related_name='receipts')
    receipt_number = models.CharField(max_length=8, unique=True, editable=False )
    amount_received = models.DecimalField(max_digits=7, decimal_places=2)
    date_received = models.DateTimeField(default=timezone.now, editable=False)
    receipted_by = models.ForeignKey(Administrator, on_delete=models.PROTECT, null=True, editable=False)

    # optional default for extra safety
    total_received = models.DecimalField(max_digits=10, decimal_places=2,
                                         default=Decimal('0.00'), editable=False)

    def save(self, *args, **kwargs):
        with transaction.atomic():

            # 🔹 AUTO-GENERATE RECEIPT NUMBER
            if not self.receipt_number:
                last_receipt = PremiumReceipt.objects.order_by('-receipt_number').first()
                if last_receipt:
                    last_number = int(last_receipt.receipt_number.replace('Rec', ''))
                    new_number = last_number + 1
                else:
                    new_number = 1

                self.receipt_number = f"Rec{new_number:06d}"

            # compute cumulative BEFORE insert so NOT NULL is satisfied
            prev_total = (
                PremiumReceipt.objects
                .filter(policy_id=self.policy_id)
                .aggregate(total=Sum('amount_received'))['total']
                or Decimal('0.00')
            )

            self.total_received = prev_total + (self.amount_received or Decimal('0.00'))

            # insert/update this receipt
            super().save(*args, **kwargs)

            # update policy running total WITHOUT invoking Policy.save()
            Policy.objects.filter(pk=self.policy_id).update(
                total_premium_received=self.total_received
            )
    


    def delete(self, *args, **kwargs):
        policy_id = self.policy_id
        with transaction.atomic():
            super().delete(*args, **kwargs)
            new_total = (PremiumReceipt.objects
                         .filter(policy_id=policy_id)
                         .aggregate(total=Sum('amount_received'))['total'] or Decimal('0.00'))
            Policy.objects.filter(pk=policy_id).update(
                total_premium_received=new_total
            )

    def __str__(self):
        return f"{self.receipt_number} • {self.total_received}"
    



from django.conf import settings

class Upload(models.Model):
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='policies_aproved_uploadsss'
    )

    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="policy_approved_uploadssr"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    is_rejected = models.BooleanField(default=False)
    reject_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)







auditlog.register(PremiumReceipt, Upload)






