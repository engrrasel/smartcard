from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, UserProfile


class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ('email', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    ordering = ('-date_joined',)
    search_fields = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'activation_date')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'job_title', 'company_name', 'updated_at')
    search_fields = ('user__email', 'full_name', 'company_name', 'username')
    prepopulated_fields = {'username': ('full_name',)}  # Auto slug fill
    ordering = ('-updated_at',)


admin.site.register(CustomUser, CustomUserAdmin)
