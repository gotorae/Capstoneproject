from django.contrib import admin, messages
from .models import (
    CancellationRequest,
    PendingCancellationRequest,
    PendingCancellationApproval,
    CancellationStatus,
)

# -------------------------------
# 1️⃣ ALL CANCELLATIONS (AUDIT)
# -------------------------------
@admin.register(CancellationRequest)
class CancellationAdmin(admin.ModelAdmin):
    list_display = (
        "policy",
        "effective_date",
        "requested_by",
        "requested_at",
        "status",
        "approved_by",
        "approved_at",
    )
    list_filter = ("status",)
    search_fields = ("policy__contract_id",)

    def has_add_permission(self, request):
        return True


# ------------------------------------
# 2️⃣ PENDING CANCELLATION REQUESTS
# ------------------------------------
@admin.register(PendingCancellationRequest)
class PendingCancellationRequestAdmin(admin.ModelAdmin):
    list_display = (
        "policy",
        "effective_date",
        "requested_by",
        "requested_at",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            status=CancellationStatus.REQUESTED
        )

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


# ------------------------------------
# 3️⃣ PENDING CANCELLATION APPROVALS
# ------------------------------------
@admin.register(PendingCancellationApproval)
class PendingCancellationApprovalAdmin(admin.ModelAdmin):
    list_display = (
        "policy",
        "effective_date",
        "requested_by",
        "requested_at",
    )

    actions = ["approve_cancellation"]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            status=CancellationStatus.REQUESTED
        )

    def approve_cancellation(self, request, queryset):
        for cancellation in queryset:
            cancellation.approve(approver=request.user)

        messages.success(
            request,
            "Cancellation approved successfully."
        )

    approve_cancellation.short_description = "Approve cancellation"

    def has_add_permission(self, request):
        return False
