# ADR-004: Django Admin Interface Strategy

**Date**: 2025-12-07  
**Status**: Proposed  
**Related PRD**: Section 6 (FR-004), Section 4 (Django Admin), Section 10 (Administration)

## Context

CFMP requires a comprehensive admin interface for data management, reporting, and operational oversight. Key requirements include:

- ModelAdmin with list filters, search fields, and CSV export actions (FR-004)
- Bulk operations for donation management
- Role-specific admin access
- Data export capabilities for reporting
- Efficient management of donation lifecycle

## Decision Drivers

- **Operational Efficiency**: Admins need quick access to key metrics and bulk operations
- **Academic Requirements**: Demonstrate ModelAdmin customization from rubric
- **Data Export**: Support reporting and analytics requirements
- **User Management**: Efficient oversight of donor and pantry accounts
- **Donation Lifecycle**: Tools for managing expired/claimed donations

## Options Considered

### A) Basic Django Admin
```python
admin.site.register(Donation)
admin.site.register(Donor)
admin.site.register(Pantry)
```

**Pros**: Quick setup, all basic functionality  
**Cons**: Limited customization, poor user experience, no export

### B) Customized ModelAdmin with Actions
```python
@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('food_type', 'donor', 'status', 'expiry_date', 'created_at')
    list_filter = ('status', 'expiry_date', 'food_type')
    search_fields = ('donor__organization_name', 'food_type', 'location')
    actions = ['mark_expired', 'export_csv']
    readonly_fields = ('created_at', 'claimed_at')
```

**Pros**: Full customization, export capabilities, better UX  
**Cons**: More development time, requires Django admin knowledge

### C) Custom Admin Dashboard
Build a completely custom admin interface outside Django admin

**Pros**: Total control, custom analytics  
**Cons**: Significant development time, reinventing Django admin

## Decision

**We choose Option B (Customized ModelAdmin)** because:

1. **Meets Requirements**: Directly fulfills FR-004 for ModelAdmin customization
2. **Django Best Practices**: Leverages built-in admin capabilities effectively
3. **Time Efficiency**: Faster than custom dashboard, more useful than basic admin
4. **Academic Value**: Demonstrates ModelAdmin mastery required by rubric
5. **Extensible**: Easy to add features incrementally

## Implementation Strategy

### Donation Admin
```python
def mark_expired(modeladmin, request, queryset):
    \"\"\"Mark selected donations as expired\"\"\"\n    count = queryset.filter(status='available').update(\n        status='expired',\n        updated_at=timezone.now()\n    )\n    modeladmin.message_user(\n        request,\n        f\"Successfully marked {count} donations as expired.\"\n    )\nmark_expired.short_description = \"Mark selected donations as expired\"\n\ndef export_csv(modeladmin, request, queryset):\n    \"\"\"Export selected donations to CSV\"\"\"\n    response = HttpResponse(content_type='text/csv')\n    response['Content-Disposition'] = 'attachment; filename=\"donations.csv\"'\n    \n    writer = csv.writer(response)\n    writer.writerow([\n        'ID', 'Donor', 'Food Type', 'Quantity', 'Expiry Date', \n        'Status', 'Location', 'Claimed By', 'Created At'\n    ])\n    \n    for donation in queryset:\n        writer.writerow([\n            donation.id,\n            donation.donor.organization_name,\n            donation.food_type,\n            donation.quantity,\n            donation.expiry_date,\n            donation.status,\n            donation.location,\n            donation.claimed_by.organization_name if donation.claimed_by else '',\n            donation.created_at.strftime('%Y-%m-%d %H:%M')\n        ])\n    \n    return response\nexport_csv.short_description = \"Export selected donations to CSV\"\n\n@admin.register(Donation)\nclass DonationAdmin(admin.ModelAdmin):\n    list_display = (\n        'id', 'food_type', 'donor_name', 'quantity', \n        'status', 'expiry_date', 'days_until_expiry', 'created_at'\n    )\n    list_filter = (\n        'status', \n        ('expiry_date', admin.DateFieldListFilter),\n        ('created_at', admin.DateFieldListFilter),\n        'food_type',\n        'location'\n    )\n    search_fields = (\n        'donor__organization_name', \n        'food_type', \n        'location',\n        'claimed_by__organization_name'\n    )\n    readonly_fields = ('created_at', 'updated_at', 'claimed_at')\n    actions = [mark_expired, export_csv]\n    date_hierarchy = 'expiry_date'\n    \n    def donor_name(self, obj):\n        return obj.donor.organization_name\n    donor_name.short_description = 'Donor'\n    donor_name.admin_order_field = 'donor__organization_name'\n    \n    def days_until_expiry(self, obj):\n        if obj.expiry_date:\n            delta = obj.expiry_date - timezone.now().date()\n            days = delta.days\n            if days < 0:\n                return format_html('<span style=\"color: red;\">Expired ({} days ago)</span>', abs(days))\n            elif days == 0:\n                return format_html('<span style=\"color: orange;\">Expires today</span>')\n            elif days <= 2:\n                return format_html('<span style=\"color: orange;\">{} days</span>', days)\n            else:\n                return f\"{days} days\"\n        return \"-\"\n    days_until_expiry.short_description = 'Days Until Expiry'\n```

### Donor and Pantry Admin
```python
@admin.register(Donor)\nclass DonorAdmin(admin.ModelAdmin):\n    list_display = ('organization_name', 'user_email', 'location', 'total_donations', 'created_at')\n    list_filter = ('location', 'created_at')\n    search_fields = ('organization_name', 'user__email', 'location')\n    readonly_fields = ('created_at',)\n    \n    def user_email(self, obj):\n        return obj.user.email\n    user_email.short_description = 'Email'\n    user_email.admin_order_field = 'user__email'\n    \n    def total_donations(self, obj):\n        return obj.donations.count()\n    total_donations.short_description = 'Total Donations'\n\n@admin.register(Pantry)\nclass PantryAdmin(admin.ModelAdmin):\n    list_display = ('organization_name', 'user_email', 'location', 'capacity', 'total_claims', 'created_at')\n    list_filter = ('location', 'capacity', 'created_at')\n    search_fields = ('organization_name', 'user__email', 'location', 'service_area')\n    readonly_fields = ('created_at',)\n    \n    def user_email(self, obj):\n        return obj.user.email\n    user_email.short_description = 'Email'\n    \n    def total_claims(self, obj):\n        return obj.claimed_donations.count()\n    total_claims.short_description = 'Total Claims'\n```

### Admin Site Customization
```python
admin.site.site_header = \"CFMP Administration\"\nadmin.site.site_title = \"CFMP Admin\"\nadmin.site.index_title = \"Community Food Match Platform\"\n\n# Custom admin index view with metrics\nclass CFMPAdminSite(admin.AdminSite):\n    def index(self, request, extra_context=None):\n        extra_context = extra_context or {}\n        \n        # Add key metrics to admin index\n        from django.utils import timezone\n        from datetime import timedelta\n        \n        today = timezone.now().date()\n        week_ago = today - timedelta(days=7)\n        \n        extra_context.update({\n            'total_active_donations': Donation.objects.available().count(),\n            'expiring_soon': Donation.objects.near_expiry(hours=24).count(),\n            'donations_this_week': Donation.objects.filter(created_at__gte=week_ago).count(),\n            'total_donors': Donor.objects.count(),\n            'total_pantries': Pantry.objects.count(),\n        })\n        \n        return super().index(request, extra_context)\n```

## Consequences

**Positive**:
- Efficient bulk operations for donation management
- CSV export supports reporting requirements
- Enhanced list views improve operational efficiency
- Custom actions streamline common administrative tasks
- Academic requirements fully satisfied

**Negative**:
- More complex than basic admin (additional development time)
- Requires understanding of ModelAdmin customization patterns
- CSV export limited to selected records (not filtered results)

**Security Considerations**:
- Admin access restricted to staff users
- Sensitive operations (bulk delete) require confirmation
- Export functionality limited to authorized users
- Readonly fields prevent accidental data corruption

## Features Implemented

1. **List Customization**:
   - Relevant fields displayed for quick overview
   - Color-coded expiry warnings
   - Calculated fields (days until expiry, totals)

2. **Filtering and Search**:
   - Date filters for time-based analysis
   - Location and status filters for operational queries
   - Full-text search across relevant fields

3. **Bulk Actions**:
   - Mark donations as expired
   - CSV export for reporting
   - Future: bulk email notifications

4. **Data Export**:
   - CSV format for spreadsheet analysis
   - Comprehensive field coverage
   - Proper filename and content-type headers

## Testing Strategy
- Test all list filters and search functionality
- Verify bulk actions work correctly and safely
- Test CSV export with various data sets
- Verify readonly fields cannot be modified
- Performance testing with large datasets

## Future Enhancements (Phase 2)
- Dashboard with charts and analytics
- Advanced filtering with date ranges
- Email integration for bulk notifications
- Integration with external reporting tools
- Automated report generation and scheduling