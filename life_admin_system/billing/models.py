from django.db import models
from policies.models import Policy


class BillingRecord(models.Model):
    policy = models.ForeignKey(
        Policy,
        on_delete=models.PROTECT,
        related_name="billings"
    )

    billing_month = models.DateField(
        help_text="Billing month (1st day of month)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("policy", "billing_month")
        ordering = ["policy__contract_id"]

    def __str__(self):
        return f"{self.policy.contract_id} - {self.billing_month:%B %Y}"

    # 🔹 Derived values (NO duplication)
    @property
    def client_name(self):
        return str(self.policy.client)

    @property
    def contract_premium(self):
        return self.policy.contract_premium

    @property
    def cover(self):
        return self.policy.cover


