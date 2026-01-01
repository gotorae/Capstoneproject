from django.contrib import admin
from django.utils import timezone
from .models import Agent, Upload
from .services import process_upload   # 🔥 THIS IMPORT


class AgentAdminModel(admin.ModelAdmin):
    readonly_fields = ('agent_code',)
    list_display = ['agent_code', 'agent_name', 'agent_surname', 'branch', 'date_joining']
    list_filter = ['agent_code', 'agent_surname', 'branch']
    search_fields = ['agent_code', 'agent_surname', 'branch']

    


admin.site.register(Agent, AgentAdminModel)


@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = ("id", "uploaded_by", "is_approved", "is_rejected", "uploaded_at")
    list_filter = ("is_approved", "is_rejected")
    actions = ["approve_uploads", "reject_uploads"]

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ("is_approved", "approved_by", "approved_at", "is_rejected", "reject_reason")
        return ()
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.uploaded_by = request.user
            obj.approved_by = request.user
        super().save_model(request, obj, form, change)


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
