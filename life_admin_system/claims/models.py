from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

from policies.models import Policy


class ClaimStatus(models.TextChoices):
    REQUESTED = "REQUESTED", "Requested"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    PAID = "PAID", "Paid"



class Claim(models.Model):
    policy = models.ForeignKey(
        Policy,
        on_delete=models.PROTECT,
        related_name="claims"
    )

    claimant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="claims"
    )

    account_number = models.CharField(max_length=30)

    burial_order = models.FileField(
        upload_to="claims/burial_orders/",
        null=True,
        blank=True
    )

    death_certificate = models.FileField(
        upload_to="claims/death_certificates/",
        null=True,
        blank=True
    )

    claim_form = models.FileField(
        upload_to="claims/claim_forms/"
    )

    status = models.CharField(
        max_length=20,
        choices=ClaimStatus.choices,
        default=ClaimStatus.REQUESTED,
        db_index=True
    )

    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="approved_claims"
    )

    # -------------------------
    # VALIDATION
    # -------------------------
    def clean(self):
        # Only ACTIVE policies can claim
        if self.policy.policy_status != "Policy Active":
            raise ValidationError(
                "Claims can only be submitted for ACTIVE policies."
            )

        # At least one supporting document is required
        if not self.burial_order and not self.death_certificate:
            raise ValidationError(
                "Burial order or death certificate is required."
            )


    # -------------------------
    # WORKFLOW
    # -------------------------
    def approve(self, *, approver):
        if self.status != ClaimStatus.REQUESTED:
            raise ValidationError("Claim is not pending approval.")

        self.status = ClaimStatus.APPROVED
        self.approved_at = timezone.now()
        self.approved_by = approver
        self.save()

    def __str__(self):
        return f"Claim #{self.id} - {self.policy.contract_id}"
    


class PendingClaimRequest(Claim):
    class Meta:
        proxy = True
        verbose_name = "Claim Request"
        verbose_name_plural = "Claim Requests"


class PendingClaimApproval(Claim):
    class Meta:
        proxy = True
        verbose_name = "Claim Approval"
        verbose_name_plural = "Claim Approvals"


