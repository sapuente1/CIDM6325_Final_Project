import csv
from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html
from .models import Donation, Donor, Pantry


def mark_expired(modeladmin, request, queryset):
    """Mark selected donations as expired"""
    count = queryset.filter(status='available').update(
        status='expired',
        updated_at=timezone.now()
    )
    modeladmin.message_user(
        request,
        f"Successfully marked {count} donations as expired.",
        level=messages.SUCCESS
    )
mark_expired.short_description = "Mark selected donations as expired"


def export_csv(modeladmin, request, queryset):
    """Export selected donations to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="donations.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Donor', 'Food Type', 'Quantity', 'Expiry Date', 
        'Status', 'Location', 'Claimed By', 'Created At'
    ])
    
    for donation in queryset.select_related('donor__user', 'claimed_by__user'):
        writer.writerow([
            donation.id,
            donation.donor.organization_name,
            donation.food_type,
            donation.quantity,
            donation.expiry_date.strftime('%Y-%m-%d %H:%M') if donation.expiry_date else '',
            donation.status,
            donation.location,
            donation.claimed_by.organization_name if donation.claimed_by else '',
            donation.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    return response
export_csv.short_description = "Export selected donations to CSV"


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'food_type', 'donor_name', 'quantity', 
        'status', 'expiry_date', 'days_until_expiry', 'created_at'
    )
    list_filter = (
        'status', 
        ('expiry_date', admin.DateFieldListFilter),
        ('created_at', admin.DateFieldListFilter),
        'food_type',
        'location'
    )
    search_fields = (
        'donor__organization_name', 
        'food_type', 
        'location',
        'description',
        'claimed_by__organization_name'
    )
    readonly_fields = ('created_at', 'updated_at', 'claimed_at')
    actions = [mark_expired, export_csv]
    date_hierarchy = 'expiry_date'
    ordering = ('-created_at',)
    list_per_page = 50
    list_max_show_all = 200
    
    # Custom display methods
    def donor_name(self, obj):
        return obj.donor.organization_name
    donor_name.short_description = 'Donor'
    donor_name.admin_order_field = 'donor__organization_name'
    
    def days_until_expiry(self, obj):
        """Display expiry status with color coding"""
        if obj.expiry_date:
            delta = obj.expiry_date - timezone.now().date()
            days = delta.days
            if days < 0:
                return format_html(
                    '<span style="color: red; font-weight: bold;">Expired ({} days ago)</span>', 
                    abs(days)
                )
            elif days == 0:
                return format_html(
                    '<span style="color: orange; font-weight: bold;">Expires today</span>'
                )
            elif days <= 2:
                return format_html(
                    '<span style="color: orange;">{} days</span>', days
                )
            elif days <= 7:
                return format_html(
                    '<span style="color: blue;">{} days</span>', days
                )
            else:
                return f"{days} days"
        return "-"
    days_until_expiry.short_description = 'Days Until Expiry'
    
    # Customize queryset for performance
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'donor__user', 
            'claimed_by__user'
        )
    
    # Add fieldsets for better organization
    fieldsets = (
        ('Donation Information', {
            'fields': ('food_type', 'description', 'quantity', 'expiry_date')
        }),
        ('Location and Status', {
            'fields': ('location', 'status')
        }),
        ('Relationships', {
            'fields': ('donor', 'claimed_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'claimed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = (
        'organization_name', 'user_email', 'user_full_name', 
        'location', 'total_donations', 'active_donations', 'created_at'
    )
    list_filter = (
        'location', 
        ('created_at', admin.DateFieldListFilter),
        'contact_phone'
    )
    search_fields = (
        'organization_name', 
        'user__email', 
        'user__first_name', 
        'user__last_name',
        'location'
    )
    readonly_fields = ('created_at', 'total_donations', 'active_donations')
    ordering = ('-created_at',)
    list_per_page = 50
    
    # Custom display methods
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
    
    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_full_name.short_description = 'Contact Name'
    user_full_name.admin_order_field = 'user__first_name'
    
    def total_donations(self, obj):
        return obj.donations.count()
    total_donations.short_description = 'Total Donations'
    
    def active_donations(self, obj):
        count = obj.donations.filter(status='available').count()
        if count > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>', 
                count
            )
        return count
    active_donations.short_description = 'Active Donations'
    
    # Optimize queryset
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user').prefetch_related('donations')
    
    # Fieldsets for organization
    fieldsets = (
        ('Organization Information', {
            'fields': ('organization_name', 'location')
        }),
        ('Contact Information', {
            'fields': ('user', 'contact_phone')
        }),
        ('Statistics', {
            'fields': ('total_donations', 'active_donations'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Pantry)
class PantryAdmin(admin.ModelAdmin):
    list_display = (
        'organization_name', 'user_email', 'user_full_name',
        'location', 'service_area', 'capacity', 'total_claims', 'created_at'
    )
    list_filter = (
        'location', 
        'service_area',
        'capacity',
        ('created_at', admin.DateFieldListFilter)
    )
    search_fields = (
        'organization_name', 
        'user__email', 
        'user__first_name', 
        'user__last_name',
        'location', 
        'service_area'
    )
    readonly_fields = ('created_at', 'total_claims')
    ordering = ('-created_at',)
    list_per_page = 50
    
    # Custom display methods
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
    
    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_full_name.short_description = 'Contact Name'
    user_full_name.admin_order_field = 'user__first_name'
    
    def total_claims(self, obj):
        count = obj.claimed_donations.count()
        if count > 0:
            return format_html(
                '<span style="color: blue; font-weight: bold;">{}</span>', 
                count
            )
        return count
    total_claims.short_description = 'Total Claims'
    
    # Optimize queryset
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user').prefetch_related('claimed_donations')
    
    # Fieldsets for organization
    fieldsets = (
        ('Organization Information', {
            'fields': ('organization_name', 'location', 'service_area', 'capacity')
        }),
        ('Contact Information', {
            'fields': ('user', 'contact_phone')
        }),
        ('Statistics', {
            'fields': ('total_claims',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# Apply customizations to default admin site
admin.site.site_header = "CFMP Administration"
admin.site.site_title = "CFMP Admin"
admin.site.index_title = "Community Food Match Platform"
