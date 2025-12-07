from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from donations.models import Donor, Pantry


# Unregister the default User admin
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Enhanced User admin with role display and organization info"""
    
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'user_role', 'organization_name', 'is_staff', 'is_active', 'date_joined'
    )
    list_filter = BaseUserAdmin.list_filter + ('date_joined',)
    search_fields = BaseUserAdmin.search_fields + (
        'donor__organization_name', 
        'pantry__organization_name'
    )
    ordering = ('-date_joined',)
    list_per_page = 50
    
    def user_role(self, obj):
        """Display user role with color coding"""
        if hasattr(obj, 'donor'):
            return format_html(
                '<span style="color: green; font-weight: bold;">🏢 Donor</span>'
            )
        elif hasattr(obj, 'pantry'):
            return format_html(
                '<span style="color: blue; font-weight: bold;">🏪 Pantry</span>'
            )
        elif obj.is_superuser:
            return format_html(
                '<span style="color: red; font-weight: bold;">👑 Admin</span>'
            )
        elif obj.is_staff:
            return format_html(
                '<span style="color: orange; font-weight: bold;">👤 Staff</span>'
            )
        else:
            return format_html(
                '<span style="color: gray;">👤 Regular User</span>'
            )
    user_role.short_description = 'Role'
    
    def organization_name(self, obj):
        """Display associated organization name"""
        if hasattr(obj, 'donor'):
            return obj.donor.organization_name
        elif hasattr(obj, 'pantry'):
            return obj.pantry.organization_name
        else:
            return "-"
    organization_name.short_description = 'Organization'
    organization_name.admin_order_field = 'donor__organization_name'
    
    def get_queryset(self, request):
        """Optimize queryset with related objects"""
        queryset = super().get_queryset(request)
        return queryset.select_related('donor', 'pantry')
    
    # Add custom fieldsets for better organization
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Information', {
            'fields': ('user_role', 'organization_name'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = BaseUserAdmin.readonly_fields + ('user_role', 'organization_name')


# Customize admin site headers
admin.site.site_header = "CFMP Administration"
admin.site.site_title = "CFMP Admin"
admin.site.index_title = "Community Food Match Platform"
