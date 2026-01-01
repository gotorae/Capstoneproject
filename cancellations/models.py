from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from policies.models import Policy
from django.conf import settings


class CancellationStatus(models.TextChoices):
    REQUESTED = "REQUESTED", "Requested"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"


class CancellationRequest(models.Model):
    policy = models.OneToOneField(
        Policy,
        on_delete=models.PROTECT,
        related_name="cancellation_request"
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="cancellation_requests"
    )

    requested_at = models.DateTimeField(auto_now_add=True)

    effective_date = models.DateField(null=True,
        help_text="Date when cancellation becomes effective"
    )

    status = models.CharField(
        max_length=20,
        choices=CancellationStatus.choices,
        default=CancellationStatus.REQUESTED
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="approved_cancellations"
    )

    approved_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.policy.policy_status != "Policy Active":
            raise ValidationError("Only ACTIVE policies can be cancelled.")

        if self.effective_date < timezone.localdate():
            raise ValidationError(
                {"effective_date": "Effective date cannot be in the past."}
            )

        if CancellationRequest.objects.filter(
            policy=self.policy,
            status=CancellationStatus.APPROVED
        ).exists():
            raise ValidationError("Policy is already cancelled.")

    def approve(self, *, approver):
        if self.status != CancellationStatus.REQUESTED:
            raise ValidationError("Cancellation is not pending approval.")

        self.status = CancellationStatus.APPROVED
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.policy.contract_id} – Cancellation"


class PendingCancellationRequest(CancellationRequest):
    class Meta:
        proxy = True
        verbose_name = "Pending Cancellation Request"
        verbose_name_plural = "Pending Cancellation Requests"


class PendingCancellationApproval(CancellationRequest):
    class Meta:
        proxy = True
        verbose_name = "Pending Cancellation Approval"
        verbose_name_plural = "Pending Cancellation Approvals"
