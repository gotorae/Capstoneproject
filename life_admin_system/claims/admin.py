from django.contrib import admin, messages
from .models import (
    Claim,
    PendingClaimRequest,
    PendingClaimApproval,
    ClaimStatus
)
from django.core.mail import send_mail
from django.conf import settings



class ClaimAdmin(admin.ModelAdmin):
    list_disply = ['policy', 'claimant', 'account_number', 'burial order','death_certificate',
                       'claim_form', 'requested_at', 'approved_at', 'approved_by']
    list_filter = ['policy']
    search_fields = ['policy']

admin.site.register(Claim, ClaimAdmin)
        


@admin.register(PendingClaimRequest)
class ClaimRequestAdmin(admin.ModelAdmin):
    list_display = (
        "policy",
        "claimant",
        "account_number",
        "requested_at",
        "status",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            status=ClaimStatus.REQUESTED
        )

    def has_view_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(PendingClaimApproval)
class ClaimApprovalAdmin(admin.ModelAdmin):
    list_display = (
        "policy",
        "claimant",
        "account_number",
        "requested_at",
    )

    actions = ["approve_claim"]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            status=ClaimStatus.REQUESTED
        )

    def approve_claim(self, request, queryset):
        for claim in queryset:
            claim.approve(approver=request.user)

            # 📧 Payment requisition email
            send_mail(
                subject="Payment Requisition – Claim Approved",
                message=(
                    f"Claim for policy {claim.policy.contract_id} "
                    f"has been approved.\n"
                    f"Account Number: {claim.account_number}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=["finance@company.com"],
            )

        messages.success(request, "Claim approved and payment requisition sent.")

    approve_claim.short_description = "Approve claim and send payment requisition"

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return False

