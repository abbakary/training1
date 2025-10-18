from django.contrib import admin
from .models import Organization, UserRole

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'organization', 'created_at')
    list_filter = ('role', 'organization')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
