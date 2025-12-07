# BRIEF-004: Django Admin Interface Implementation

**Date**: 2025-12-07  
**Related ADR**: ADR-004  
**PRD Reference**: Section 6 (FR-004), Section 4 (Django Admin), Section 10 (Administration)  
**Dependencies**: ADR-001 (data models), ADR-002 (views architecture), ADR-003 (authentication)

## Goal

Implement a comprehensive Django admin interface for CFMP with customized ModelAdmin classes, bulk operations, CSV export capabilities, and role-specific administrative tools for efficient data management and operational oversight.

## Scope (Single PR)

### Files to Create/Modify
- `donations/admin.py` - Custom ModelAdmin classes with actions and filters
- `pantries/admin.py` - Pantry admin configuration  
- `authentication/admin.py` - User management admin configuration
- `cfmp/admin.py` - Custom admin site configuration and metrics (optional)
- `donations/tests/test_admin.py` - Admin interface testing
- `pantries/tests/test_admin.py` - Pantry admin testing
- `authentication/tests/test_admin.py` - User admin testing

### Non-Goals (Future PRs)
- Custom admin dashboard with charts/analytics
- Advanced reporting with external tools
- Automated report generation and scheduling
- Email integration for bulk notifications
- Complex data visualization dashboards

## Standards

### Project Norms
- **Language**: Python 3.12 + Django 5.2
- **Style**: PEP 8, docstrings on admin methods, type hints on new code
- **Commits**: Conventional style (feat/fix/docs/refactor/test/chore)
- **Testing**: Django TestCase (no pytest), use AdminClient for admin testing

### Django Admin Norms
- **ModelAdmin**: Use list_display, list_filter, search_fields for efficiency
- **Actions**: Custom admin actions with user feedback messages
- **Security**: Restrict admin access to staff users only
- **Export**: CSV export with proper headers and content-type
- **Readonly Fields**: Prevent accidental modification of sensitive data

## Detailed Requirements

### 1. Donation Admin Interface

#### Custom Admin Actions
```python
import csv
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html
from django.contrib import admin


def mark_expired(modeladmin, request, queryset):
    """Mark selected donations as expired"""
    count = queryset.filter(status='available').update(
        status='expired',
        updated_at=timezone.now()
    )
    modeladmin.message_user(
        request,
        f"Successfully marked {count} donations as expired.",
        level=admin.SUCCESS
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
```

### 2. Donor Admin Interface

```python
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
```

### 3. Pantry Admin Interface

```python
@admin.register(Pantry)
class PantryAdmin(admin.ModelAdmin):
    list_display = (
        'organization_name', 'user_email', 'user_full_name',
        'location', 'service_area', 'capacity', 'total_claims', 'created_at'
    )
    list_filter = (
        'location', 
        'service_area',
        ('capacity', admin.RangeNumericFilter) if hasattr(admin, 'RangeNumericFilter') else 'capacity',
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
```

### 4. User Management Admin

```python
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html


# Unregister the default User admin
admin.site.unregister(User)


@admin.register(User)
class CFMPUserAdmin(BaseUserAdmin):
    """Enhanced User admin for CFMP"""
    list_display = (
        'username', 'email', 'first_name', 'last_name', 
        'user_role', 'organization_name', 'is_staff', 'date_joined'
    )
    list_filter = (
        'is_staff', 'is_superuser', 'is_active',
        ('date_joined', admin.DateFieldListFilter)
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    # Add custom fields to the default UserAdmin fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ('CFMP Profile', {
            'fields': ('user_role', 'organization_name'),
            'description': 'Role and organization information for CFMP users'
        }),
    )
    
    readonly_fields = ('user_role', 'organization_name')
    
    def user_role(self, obj):
        """Display user role with color coding"""
        if hasattr(obj, 'donor'):
            return format_html(
                '<span style="color: green; font-weight: bold;">Donor</span>'
            )
        elif hasattr(obj, 'pantry'):
            return format_html(
                '<span style="color: blue; font-weight: bold;">Pantry</span>'
            )
        elif obj.is_staff:
            return format_html(
                '<span style="color: red; font-weight: bold;">Admin</span>'
            )
        else:
            return format_html(
                '<span style="color: gray;">No Role</span>'
            )
    user_role.short_description = 'Role'
    
    def organization_name(self, obj):
        """Display organization name"""
        if hasattr(obj, 'donor'):
            return obj.donor.organization_name
        elif hasattr(obj, 'pantry'):
            return obj.pantry.organization_name
        return '-'
    organization_name.short_description = 'Organization'
    
    def get_queryset(self, request):
        """Optimize queryset with role relationships"""
        queryset = super().get_queryset(request)
        return queryset.select_related('donor', 'pantry')
```

### 5. Admin Site Customization

```python
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils import timezone
from datetime import timedelta


class CFMPAdminSite(AdminSite):
    """Custom admin site with CFMP branding and metrics"""
    site_header = "CFMP Administration"
    site_title = "CFMP Admin"
    index_title = "Community Food Match Platform"
    
    def index(self, request, extra_context=None):
        """Add key metrics to admin index"""
        extra_context = extra_context or {}
        
        # Calculate metrics
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        # Import models here to avoid circular imports
        from donations.models import Donation, Donor, Pantry
        
        extra_context.update({
            'cfmp_metrics': {
                'total_active_donations': Donation.objects.available().count(),
                'expiring_soon': Donation.objects.near_expiry(hours=24).count(),
                'donations_this_week': Donation.objects.filter(
                    created_at__gte=week_ago
                ).count(),
                'total_donors': Donor.objects.count(),
                'total_pantries': Pantry.objects.count(),
                'total_claimed': Donation.objects.filter(status='claimed').count(),
            }
        })
        
        return super().index(request, extra_context)


# Apply customizations to default admin site
admin.site.site_header = "CFMP Administration"
admin.site.site_title = "CFMP Admin"
admin.site.index_title = "Community Food Match Platform"
```

### 6. Comprehensive Testing Strategy

#### Admin Interface Tests (donations/tests/test_admin.py)
```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from donations.models import Donation, Donor, Pantry
from donations.admin import mark_expired, export_csv


class DonationAdminTestCase(TestCase):
    """Test Donation admin interface"""
    
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create test donor and pantry
        self.donor_user = User.objects.create_user(
            username='donor1', email='donor1@example.com'
        )
        self.donor = Donor.objects.create(
            user=self.donor_user,
            organization_name='Test Restaurant'
        )
        
        self.pantry_user = User.objects.create_user(
            username='pantry1', email='pantry1@example.com'
        )
        self.pantry = Pantry.objects.create(
            user=self.pantry_user,
            organization_name='Test Food Bank',
            capacity=100
        )
        
        # Create test donations
        self.donation1 = Donation.objects.create(
            donor=self.donor,
            food_type='produce',
            description='Fresh vegetables',
            quantity=10,
            expiry_date=timezone.now().date() + timedelta(days=2),
            location='Test City'
        )
        
        self.donation2 = Donation.objects.create(
            donor=self.donor,
            food_type='bakery',
            description='Day-old bread',
            quantity=5,
            expiry_date=timezone.now().date() - timedelta(days=1),  # Expired
            location='Test City'
        )
        
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_admin_list_view(self):
        """Test admin list view displays correctly"""
        response = self.client.get(reverse('admin:donations_donation_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Restaurant')
        self.assertContains(response, 'Fresh vegetables')
        self.assertContains(response, 'Day-old bread')

    def test_admin_search_functionality(self):
        """Test search functionality works"""
        response = self.client.get(
            reverse('admin:donations_donation_changelist') + '?q=vegetables'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fresh vegetables')
        self.assertNotContains(response, 'Day-old bread')

    def test_admin_filter_functionality(self):
        """Test filtering by status works"""
        response = self.client.get(
            reverse('admin:donations_donation_changelist') + '?status=available'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fresh vegetables')

    def test_mark_expired_action(self):
        """Test mark expired admin action"""
        from django.http import HttpRequest
        from donations.admin import DonationAdmin
        
        request = HttpRequest()
        request.user = self.admin_user
        
        admin_instance = DonationAdmin(Donation, admin.site)
        queryset = Donation.objects.filter(id=self.donation1.id)
        
        # Mock the message_user method
        admin_instance.message_user = lambda req, msg, level=None: None
        
        mark_expired(admin_instance, request, queryset)
        
        self.donation1.refresh_from_db()
        self.assertEqual(self.donation1.status, 'expired')

    def test_csv_export_action(self):
        """Test CSV export admin action"""
        from django.http import HttpRequest
        from donations.admin import DonationAdmin
        
        request = HttpRequest()
        request.user = self.admin_user
        
        admin_instance = DonationAdmin(Donation, admin.site)
        queryset = Donation.objects.all()
        
        response = export_csv(admin_instance, request, queryset)
        
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        
        # Check CSV content
        content = response.content.decode('utf-8')
        self.assertIn('Test Restaurant', content)
        self.assertIn('Fresh vegetables', content)

    def test_admin_detail_view(self):
        """Test admin detail view"""
        response = self.client.get(
            reverse('admin:donations_donation_change', args=[self.donation1.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fresh vegetables')

    def test_admin_permissions(self):
        """Test admin requires proper permissions"""
        # Test with non-admin user
        non_admin = User.objects.create_user(
            username='user', email='user@example.com', password='userpass'
        )
        self.client.force_login(non_admin)
        
        response = self.client.get(reverse('admin:donations_donation_changelist'))
        self.assertEqual(response.status_code, 302)  # Redirect to login


class DonorAdminTestCase(TestCase):
    """Test Donor admin interface"""
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass'
        )
        
        self.donor_user = User.objects.create_user(
            username='donor1', 
            email='donor1@example.com',
            first_name='John',
            last_name='Doe'
        )
        self.donor = Donor.objects.create(
            user=self.donor_user,
            organization_name='Test Restaurant',
            location='Test City'
        )
        
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_donor_admin_list(self):
        """Test donor admin list view"""
        response = self.client.get(reverse('admin:donations_donor_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Restaurant')
        self.assertContains(response, 'donor1@example.com')
        self.assertContains(response, 'John Doe')

    def test_donor_admin_search(self):
        """Test donor admin search functionality"""
        response = self.client.get(
            reverse('admin:donations_donor_changelist') + '?q=Test Restaurant'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Restaurant')


class PantryAdminTestCase(TestCase):
    """Test Pantry admin interface"""
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass'
        )
        
        self.pantry_user = User.objects.create_user(
            username='pantry1',
            email='pantry1@example.com',
            first_name='Jane',
            last_name='Smith'
        )
        self.pantry = Pantry.objects.create(
            user=self.pantry_user,
            organization_name='Test Food Bank',
            location='Test City',
            service_area='Downtown',
            capacity=200
        )
        
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_pantry_admin_list(self):
        """Test pantry admin list view"""
        response = self.client.get(reverse('admin:donations_pantry_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Food Bank')
        self.assertContains(response, 'pantry1@example.com')
        self.assertContains(response, 'Downtown')
        self.assertContains(response, '200')

    def test_pantry_admin_capacity_filter(self):
        """Test capacity filtering"""
        # Create another pantry with different capacity
        user2 = User.objects.create_user(username='pantry2', email='pantry2@example.com')
        Pantry.objects.create(
            user=user2,
            organization_name='Small Pantry',
            capacity=50
        )
        
        response = self.client.get(reverse('admin:donations_pantry_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Food Bank')
        self.assertContains(response, 'Small Pantry')


class UserAdminTestCase(TestCase):
    """Test enhanced User admin interface"""
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass'
        )
        
        # Create donor user
        self.donor_user = User.objects.create_user(
            username='donor1',
            email='donor1@example.com',
            first_name='John',
            last_name='Doe'
        )
        self.donor = Donor.objects.create(
            user=self.donor_user,
            organization_name='Test Restaurant'
        )
        
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_user_admin_role_display(self):
        """Test that user roles are displayed correctly"""
        response = self.client.get(reverse('admin:auth_user_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Restaurant')
        self.assertContains(response, 'donor1@example.com')
```

### 7. Admin Performance Optimization

#### QuerySet Optimization
- Use `select_related()` for foreign key relationships
- Use `prefetch_related()` for reverse foreign key relationships
- Implement `get_queryset()` overrides for consistent optimization
- Add database indexes for commonly filtered fields

#### Pagination and Limits
- Set appropriate `list_per_page` values (50-100)
- Configure `list_max_show_all` to prevent large datasets from loading entirely
- Use date hierarchies for time-based filtering

## Integration Requirements

### Admin Settings Configuration
```python
# In settings.py
ADMIN_MEDIA_PREFIX = '/admin/media/'

# Optional: Custom admin site instance
# ADMIN_SITE_CLASS = 'cfmp.admin.CFMPAdminSite'
```

### URL Configuration
```python
# urls.py already includes admin URLs by default
path('admin/', admin.site.urls),
```

## Acceptance Criteria

### Functional Requirements
- [ ] DonationAdmin displays all required fields with proper formatting
- [ ] Color-coded expiry warnings work correctly
- [ ] CSV export includes all necessary fields
- [ ] Mark expired action updates donation status
- [ ] Search functionality works across relevant fields
- [ ] Filtering works for status, dates, and categories
- [ ] Donor and Pantry admins show organization and user information
- [ ] User admin displays role and organization information

### Technical Requirements
- [ ] All admin classes use optimized querysets
- [ ] CSV export uses proper HTTP headers
- [ ] Admin actions include user feedback messages
- [ ] Readonly fields prevent accidental data modification
- [ ] Custom display methods use admin_order_field for sorting
- [ ] Fieldsets organize admin forms logically

### Testing Requirements
- [ ] Minimum 15 admin tests covering all functionality
- [ ] Test CSV export content and headers
- [ ] Test admin actions work correctly
- [ ] Test search and filtering functionality
- [ ] Test admin permissions and access control
- [ ] All tests pass with >90% code coverage

### Code Quality Requirements
- [ ] PEP 8 compliance (use ruff for linting)
- [ ] Docstrings on all admin methods and actions
- [ ] Type hints on new methods where applicable
- [ ] No performance bottlenecks (N+1 queries avoided)
- [ ] Consistent naming conventions for admin methods

## Prompts for Copilot

### Implementation Guidance
1. **"Generate Django ModelAdmin classes with custom display methods, filters, and actions following the exact patterns in this brief"**
2. **"Create CSV export admin action with proper HTTP response headers and comprehensive field coverage"**
3. **"Implement admin list views with color-coded status indicators and optimized querysets"**
4. **"Build admin search and filtering for efficient data management and operational queries"**
5. **"Write comprehensive Django admin tests covering all functionality and edge cases"**

### Code Review Focus
- **"Review admin querysets for N+1 query issues and optimization opportunities"**
- **"Check CSV export functionality for proper headers and complete data coverage"**
- **"Verify admin actions provide proper user feedback and handle edge cases"**
- **"Validate admin permissions restrict access to authorized users only"**
- **"Ensure custom display methods are sortable and performant"**

## Success Criteria

**Implementation Complete When**:
1. All ModelAdmin classes display relevant information with proper formatting
2. CSV export produces complete donation reports with proper headers
3. Admin actions (mark expired) work correctly with user feedback
4. Search and filtering enable efficient data management
5. Color-coded indicators improve operational visibility
6. Performance optimizations prevent slow page loads
7. Minimum 15 admin tests pass covering all functionality

**Deliverables**:
- Comprehensive Django admin interface for all models
- CSV export functionality for reporting needs
- Bulk administrative actions for operational efficiency
- Optimized admin queries for performance
- Complete test coverage for admin functionality

## Risk Assessment & Rollback

**Risk Level**: Low
- **Data Risk**: Readonly fields prevent accidental modification
- **Performance Risk**: Optimized querysets prevent slow admin pages
- **Security Risk**: Admin access restricted to staff users

**Rollback Plan**:
1. Revert admin.py files to basic registration
2. Remove custom admin actions and display methods
3. Use git revert for specific admin enhancement commits

**Mitigation**:
- Extensive testing of admin actions before deployment
- Performance testing with realistic data volumes  
- Security review of admin access controls and permissions
- User training on new admin functionality and CSV exports