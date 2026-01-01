# commissions/models.py
from decimal import Decimal
from django.db import models
from policies.models import Policy
from agents.models import Agent


class CommissionRecord(models.Model):
    """
    One row per (policy, commission_month)
    Commission is auto-calculated from policy premium
    """

    policy = models.ForeignKey(
        Policy,
        on_delete=models.PROTECT,
        related_name="commission_rows",
        editable=False
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.PROTECT,
        related_name="commission_rows",
        editable=False
    )

    commission_month = models.DateField(
        help_text="Use the 1st day of the commission month"
    )

    commission_due = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # Commission rate
    COMMISSION_RATE = Decimal("0.10")

    class Meta:
        unique_together = ("policy", "commission_month")
        ordering = ["policy__contract_id"]

    def __str__(self):
        return f"{self.policy.contract_id} - {self.commission_month:%b %Y}"

    # ---------- Display helpers ----------
    @property
    def client_name(self):
        return str(self.policy.client)

    @property
    def agent_code(self):
        return self.agent.agent_code

    @property
    def agent_name(self):
        return f"{self.agent.agent_name} {self.agent.agent_surname}"

    @property
    def contract_premium(self):
        return self.policy.contract_premium

    # ---------- Core logic ----------
    def _compute_commission_due(self) -> Decimal:
        premium = Decimal(self.policy.contract_premium or 0)
        return (premium * self.COMMISSION_RATE).quantize(Decimal("0.01"))

    def save(self, *args, **kwargs):
        self.commission_due = self._compute_commission_due()
        super().save(*args, **kwargs)

