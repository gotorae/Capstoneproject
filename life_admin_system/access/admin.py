
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Administrator


@admin.register(Administrator)
class AdministratorAdmin(UserAdmin):
    model = Administrator

    # --- List page (what you see in the table) ---
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")

    # --- Make UserAdmin work with email instead of username ---
    ordering = ("email",)
    search_fields = ("email", "first_name", "last_name")

    # --- Fields shown on the change (edit) page ---
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ( "first_name", "last_name", "dob", "profile_photo")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_created")}),
    )

    # --- Fields shown on the add page (create user) ---
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "first_name", "last_name", "dob", "profile_photo",
                       "is_active", "is_staff", "is_superuser"),
        }),
    )

    # If your model has these    # If your model has these as auto fields / from AbstractBaseUser:
