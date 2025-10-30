from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "account_type", "is_active", "is_staff", "date_joined")
    list_filter = ("account_type", "is_active", "is_staff")
    ordering = ("-date_joined",)
    search_fields = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Account Info", {"fields": ("account_type", "is_active", "is_staff", "is_superuser")}),
        ("Permissions", {"fields": ("groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "account_type", "is_active"),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "username", "company_name", "updated_at")
    search_fields = ("user__email", "full_name", "username", "company_name")
    list_filter = ("updated_at",)
    readonly_fields = ("updated_at",)

    # ✅ username locked after first set
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.username:  # আগে username থাকলে
            return self.readonly_fields + ("username",)
        return self.readonly_fields
