from django.contrib import admin
from .models import Policy, Upload
from django.db import models
from django.utils import timezone
from .services import process_upload
from import_export.admin import ExportMixin
from .resources import PolicyResource


class PolicyAdminModel(ExportMixin, admin.ModelAdmin):
    resource_class = PolicyResource





    
    list_display = [
        'contract_id',
        'product_name',
        'product_code',
        'contract_premium',
        'start_date',
        'proposal_sign_date',
        'beneficiary_name',
        'beneficiary_id',
        'agent',
        'paypoint',
        'client',

        # FINANCIALS
        'total_premium_received',
        'duration',
        'current_month',
        'total_premium_due',
        'total_premium_arrears',
        'months_in_arrears',
        'months_paid',

        # CLAIM & CANCELLATION
        'claim_status',
        'claim_effective_date',
        'cancellation_status',
        'cancellation_effective_date',

        # OVERALL STATUS
        'overall_policy_status',

        'policy_status',
        'created_date',
        'created_by',
    ]


    list_filter = ['contract_id','product_name','product_code', 'created_by', 'created_date']
    search_fields = ['contract_id','product_name','product_code', 'created_by', 'created_date']
    readonly_fields = ['contract_id','product_code','contract_premium','total_premium_received',
                       'duration','current_month','total_premium_due','total_premium_arrears',
                       'months_in_arrears','months_paid','claim_status','claim_effective_date',
                       'cancellation_status','cancellation_effective_date','overall_policy_status',
                       'policy_status','created_date','created_by']

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    

admin.site.register(Policy, PolicyAdminModel)




@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = ("id", "uploaded_by", "is_approved", "is_rejected", "uploaded_at")
    list_filter = ("is_approved", "is_rejected")
    actions = ["approve_uploads", "reject_uploads"]

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ("is_approved", "approved_by", "approved_at", "is_rejected", "reject_reason")
        return ()

    @admin.action(description="Approve selected uploads")
    def approve_uploads(self, request, queryset):
        if not request.user.is_superuser:
            self.message_user(request, "Only superusers can approve uploads.", level="error")
            return

        for upload in queryset:
            if upload.is_approved:
                continue

            upload.is_approved = True
            upload.approved_by = request.user
            upload.approved_at = timezone.now()
            upload.save()

            errors = process_upload(upload)

            if errors:
                self.message_user(
                    request,
                    f"Upload {upload.id} imported with errors:\n" + "\n".join(errors),
                    level="warning"
                )

        self.message_user(request, "Uploads approved and processed.")

    @admin.action(description="Reject selected uploads")
    def reject_uploads(self, request, queryset):
        for upload in queryset:
            upload.is_rejected = True
            upload.is_approved = False
            upload.reject_reason = "Rejected by admin"
            upload.save()

        self.message_user(request, "Selected uploads rejected.")










