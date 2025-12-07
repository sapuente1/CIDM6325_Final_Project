# BRIEF: CFMP Data Model Implementation

**Goal**: Implement the data model design for Community Food Match Platform as specified in ADR-001  
**Scope**: Create Django models, custom managers/QuerySets, and supporting infrastructure for the CFMP application  
**Related ADR**: [ADR-001: Data Model Design for CFMP](../../../My%20Project/adr/ADR-001-data-model-design.md)

---

## Implementation Requirements

### 1. Django App Structure
Create a Django app called `donations` with the following structure:
```
donations/
├── __init__.py
├── models.py          # Core models: Donor, Pantry, Donation
├── managers.py        # Custom managers and QuerySets
├── admin.py          # Admin configuration
├── apps.py           # App configuration
├── migrations/       # Database migrations
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_managers.py
└── signals.py        # Django signals (for future use)
```

### 2. Core Models Implementation

#### A. Donor Model
```python
# donations/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Donor(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        help_text="Associated user account"
    )
    organization_name = models.CharField(
        max_length=100,
        help_text="Name of donating organization or individual"
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number')]
    )
    location = models.CharField(
        max_length=100,
        help_text="City or general location (for privacy)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Donor"
        verbose_name_plural = "Donors"
        ordering = ['organization_name']
    
    def __str__(self):
        return f"{self.organization_name} ({self.user.username})"
    
    @property
    def total_donations(self):
        """Get total number of donations by this donor"""
        return self.donations.count()
    
    @property
    def active_donations(self):
        """Get number of active (available) donations"""
        return self.donations.available().count()
```

#### B. Pantry Model
```python
class Pantry(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        help_text="Associated user account"
    )
    organization_name = models.CharField(
        max_length=100,
        help_text="Name of pantry organization"
    )
    capacity = models.PositiveIntegerField(
        help_text="Approximate weekly capacity (number of families served)"
    )
    location = models.CharField(
        max_length=100,
        help_text="City or general location"
    )
    service_area = models.CharField(
        max_length=100,
        help_text="Geographic area served by this pantry"
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Pantry"
        verbose_name_plural = "Pantries"
        ordering = ['organization_name']
    
    def __str__(self):
        return f"{self.organization_name} ({self.user.username})"
    
    @property
    def total_claims(self):
        """Get total number of donations claimed by this pantry"""
        return self.claimed_donations.count()
    
    @property
    def recent_claims(self):
        """Get donations claimed in the last 30 days"""
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=30)
        return self.claimed_donations.filter(claimed_at__gte=cutoff)
```

#### C. Donation Model with Custom Manager
```python
from .managers import DonationManager

class Donation(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('claimed', 'Claimed'),
        ('expired', 'Expired'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ]
    
    FOOD_TYPE_CHOICES = [
        ('produce', 'Fresh Produce'),
        ('dairy', 'Dairy Products'),
        ('meat', 'Meat & Protein'),
        ('bakery', 'Bakery Items'),
        ('canned', 'Canned Goods'),
        ('frozen', 'Frozen Foods'),
        ('pantry', 'Pantry Staples'),
        ('prepared', 'Prepared Meals'),
        ('other', 'Other'),
    ]
    
    # Core fields
    donor = models.ForeignKey(
        Donor,
        on_delete=models.CASCADE,
        related_name='donations'
    )
    claimed_by = models.ForeignKey(
        Pantry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='claimed_donations'
    )
    
    # Food details
    food_type = models.CharField(
        max_length=20,
        choices=FOOD_TYPE_CHOICES,
        default='other'
    )
    description = models.TextField(
        help_text="Detailed description of the food items"
    )
    quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Quantity (lbs, count, servings, etc.)"
    )
    unit = models.CharField(
        max_length=20,
        default='lbs',
        help_text="Unit of measurement (lbs, servings, boxes, etc.)"
    )
    
    # Location and timing
    location = models.CharField(
        max_length=100,
        help_text="Pickup location (city level for privacy)"
    )
    expiry_date = models.DateTimeField(
        help_text="When this food expires"
    )
    pickup_instructions = models.TextField(
        blank=True,
        help_text="Special instructions for pickup"
    )
    
    # Status and tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    claimed_at = models.DateTimeField(null=True, blank=True)
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    
    # Custom manager
    objects = DonationManager()
    
    class Meta:
        verbose_name = "Donation"
        verbose_name_plural = "Donations"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'expiry_date']),
            models.Index(fields=['location']),
            models.Index(fields=['food_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_food_type_display()} - {self.quantity} {self.unit} (expires {self.expiry_date.date()})"
    
    @property
    def days_until_expiry(self):
        """Calculate days until expiry"""
        from django.utils import timezone
        if self.expiry_date:
            delta = self.expiry_date.date() - timezone.now().date()
            return delta.days
        return None
    
    @property
    def is_urgent(self):
        """Check if donation expires within 24 hours"""
        days = self.days_until_expiry
        return days is not None and days <= 1
    
    @property
    def is_expired(self):
        """Check if donation has expired"""
        days = self.days_until_expiry
        return days is not None and days < 0
    
    def claim(self, pantry):
        """Claim this donation for a pantry"""
        from django.utils import timezone
        if self.status == 'available':
            self.claimed_by = pantry
            self.status = 'claimed'
            self.claimed_at = timezone.now()
            self.save()
            return True
        return False
    
    def mark_fulfilled(self):
        """Mark donation as fulfilled/completed"""
        from django.utils import timezone
        if self.status == 'claimed':
            self.status = 'fulfilled'
            self.fulfilled_at = timezone.now()
            self.save()
            return True
        return False
    
    def save(self, *args, **kwargs):
        """Override save to auto-update status based on expiry"""
        from django.utils import timezone
        
        # Auto-mark expired donations
        if self.expiry_date and self.expiry_date <= timezone.now():
            if self.status == 'available':
                self.status = 'expired'
        
        super().save(*args, **kwargs)
```

### 3. Custom Managers and QuerySets

#### Create managers.py file:
```python
# donations/managers.py
from django.db import models
from django.utils import timezone
from datetime import timedelta

class DonationQuerySet(models.QuerySet):
    def available(self):
        """Return only available donations that haven't expired"""
        return self.filter(
            status='available',
            expiry_date__gte=timezone.now()
        )
    
    def near_expiry(self, hours=24):
        """Return available donations expiring within specified hours"""
        cutoff = timezone.now() + timedelta(hours=hours)
        return self.available().filter(expiry_date__lte=cutoff)
    
    def urgent(self):
        """Return donations expiring within 12 hours"""
        return self.near_expiry(hours=12)
    
    def by_location(self, city):
        """Filter donations by city (case-insensitive partial match)"""
        return self.filter(location__icontains=city)
    
    def by_food_type(self, food_type):
        """Filter donations by food type"""
        return self.filter(food_type=food_type)
    
    def claimed(self):
        """Return claimed donations"""
        return self.filter(status='claimed')
    
    def expired_unclaimed(self):
        """Return expired donations that were never claimed"""
        return self.filter(
            status='expired',
            claimed_by__isnull=True
        )
    
    def with_related(self):
        """Optimize queries by selecting related objects"""
        return self.select_related('donor', 'donor__user', 'claimed_by', 'claimed_by__user')
    
    def for_donor(self, donor):
        """Return donations for a specific donor"""
        return self.filter(donor=donor)
    
    def for_pantry(self, pantry):
        """Return donations claimed by a specific pantry"""
        return self.filter(claimed_by=pantry)

class DonationManager(models.Manager):
    def get_queryset(self):
        return DonationQuerySet(self.model, using=self._db)
    
    def available(self):
        """Public interface for available donations"""
        return self.get_queryset().available()
    
    def urgent(self):
        """Public interface for urgent donations"""
        return self.get_queryset().urgent()
    
    def near_expiry(self, hours=24):
        """Public interface for near-expiry donations"""
        return self.get_queryset().near_expiry(hours=hours)
    
    def by_location(self, city):
        """Public interface for location-based filtering"""
        return self.get_queryset().by_location(city)
    
    def cleanup_expired(self):
        """Management command helper: mark expired donations"""
        expired_count = self.get_queryset().filter(
            status='available',
            expiry_date__lt=timezone.now()
        ).update(status='expired')
        return expired_count
```

### 4. Model Registration and Admin Integration

#### Basic admin.py setup:
```python
# donations/admin.py
from django.contrib import admin
from .models import Donor, Pantry, Donation

# Register basic admin (will be enhanced in ADR-004 implementation)
@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'user', 'location', 'total_donations', 'created_at')
    search_fields = ('organization_name', 'user__username', 'location')

@admin.register(Pantry)
class PantryAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'user', 'location', 'capacity', 'total_claims', 'created_at')
    search_fields = ('organization_name', 'user__username', 'location', 'service_area')

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('description', 'donor', 'food_type', 'quantity', 'status', 'expiry_date', 'created_at')
    list_filter = ('status', 'food_type', 'expiry_date', 'created_at')
    search_fields = ('description', 'donor__organization_name', 'location')
    readonly_fields = ('created_at', 'updated_at', 'claimed_at', 'fulfilled_at')
```

### 5. Testing Requirements

#### Create comprehensive test suite:
```python
# donations/tests/test_models.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from donations.models import Donor, Pantry, Donation

class DonorModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('donor1', 'donor@test.com', 'password')
        self.donor = Donor.objects.create(
            user=self.user,
            organization_name='Test Org',
            location='Test City'
        )
    
    def test_donor_creation(self):
        """Test donor model creation and string representation"""
        self.assertEqual(str(self.donor), 'Test Org (donor1)')
        self.assertEqual(self.donor.total_donations, 0)

class DonationModelTests(TestCase):
    def setUp(self):
        # Create test users
        donor_user = User.objects.create_user('donor', 'donor@test.com', 'password')
        pantry_user = User.objects.create_user('pantry', 'pantry@test.com', 'password')
        
        # Create test profiles
        self.donor = Donor.objects.create(
            user=donor_user,
            organization_name='Test Donor',
            location='Test City'
        )
        
        self.pantry = Pantry.objects.create(
            user=pantry_user,
            organization_name='Test Pantry',
            capacity=100,
            location='Test City',
            service_area='Test Area'
        )
    
    def test_donation_creation(self):
        """Test basic donation creation"""
        future_date = timezone.now() + timedelta(days=2)
        donation = Donation.objects.create(
            donor=self.donor,
            food_type='produce',
            description='Fresh apples',
            quantity=10,
            unit='lbs',
            location='Test City',
            expiry_date=future_date
        )
        
        self.assertEqual(donation.status, 'available')
        self.assertFalse(donation.is_expired)
        self.assertFalse(donation.is_urgent)
    
    def test_donation_claim_process(self):
        """Test donation claiming functionality"""
        future_date = timezone.now() + timedelta(days=2)
        donation = Donation.objects.create(
            donor=self.donor,
            food_type='produce',
            description='Fresh apples',
            quantity=10,
            unit='lbs',
            location='Test City',
            expiry_date=future_date
        )
        
        # Test successful claim
        result = donation.claim(self.pantry)
        self.assertTrue(result)
        self.assertEqual(donation.status, 'claimed')
        self.assertEqual(donation.claimed_by, self.pantry)
        self.assertIsNotNone(donation.claimed_at)
        
        # Test cannot claim already claimed donation
        result2 = donation.claim(self.pantry)
        self.assertFalse(result2)

# donations/tests/test_managers.py
class DonationManagerTests(TestCase):
    def setUp(self):
        # Create test data
        donor_user = User.objects.create_user('donor', 'donor@test.com', 'password')
        self.donor = Donor.objects.create(
            user=donor_user,
            organization_name='Test Donor',
            location='Test City'
        )
        
        # Create donations with different expiry dates
        now = timezone.now()
        
        # Available donation expiring in 2 days
        self.future_donation = Donation.objects.create(
            donor=self.donor,
            food_type='produce',
            description='Future expiry',
            quantity=10,
            location='Test City',
            expiry_date=now + timedelta(days=2)
        )
        
        # Urgent donation expiring in 6 hours
        self.urgent_donation = Donation.objects.create(
            donor=self.donor,
            food_type='dairy',
            description='Urgent expiry',
            quantity=5,
            location='Test City',
            expiry_date=now + timedelta(hours=6)
        )
        
        # Expired donation
        self.expired_donation = Donation.objects.create(
            donor=self.donor,
            food_type='meat',
            description='Already expired',
            quantity=3,
            location='Test City',
            expiry_date=now - timedelta(hours=2),
            status='expired'
        )
    
    def test_available_queryset(self):
        """Test available() manager method"""
        available = Donation.objects.available()
        self.assertIn(self.future_donation, available)
        self.assertIn(self.urgent_donation, available)
        self.assertNotIn(self.expired_donation, available)
    
    def test_urgent_queryset(self):
        """Test urgent() manager method"""
        urgent = Donation.objects.urgent()
        self.assertIn(self.urgent_donation, urgent)
        self.assertNotIn(self.future_donation, urgent)
        self.assertNotIn(self.expired_donation, urgent)
    
    def test_near_expiry_queryset(self):
        """Test near_expiry() with custom hours"""
        near_expiry = Donation.objects.near_expiry(hours=48)  # 2 days
        self.assertIn(self.future_donation, near_expiry)
        self.assertIn(self.urgent_donation, near_expiry)
        self.assertNotIn(self.expired_donation, near_expiry)
    
    def test_location_filtering(self):
        """Test by_location() filtering"""
        city_donations = Donation.objects.by_location('Test City')
        self.assertEqual(city_donations.count(), 3)
        
        # Test case-insensitive partial matching
        partial_donations = Donation.objects.by_location('test')
        self.assertEqual(partial_donations.count(), 3)
```

### 6. Migration Strategy

Create initial migration with:
```bash
python manage.py makemigrations donations
python manage.py migrate
```

### 7. Validation Requirements

#### Performance Tests:
- Test custom QuerySet methods with 1000+ donation records
- Verify database indexes are created correctly
- Test select_related optimization in with_related() method

#### Business Logic Tests:
- Verify donation claiming workflow
- Test automatic expiry status updates
- Validate location-based filtering accuracy
- Test property methods (is_urgent, is_expired, etc.)

#### Data Integrity Tests:
- Test OneToOneField relationships
- Verify foreign key cascading behavior
- Test model validation and constraints

### 8. Integration Points

#### For Future ADRs:
- **Views (ADR-002)**: Models provide the foundation for CBV implementation
- **Authentication (ADR-003)**: User profiles link to Django User model
- **Admin (ADR-004)**: Enhanced ModelAdmin builds on basic admin setup
- **Monitoring (ADR-005)**: Model methods support metrics collection

#### Management Commands:
Create management command for expired donation cleanup:
```bash
python manage.py cleanup_expired_donations
```

---

## Success Criteria

✅ **Models Created**: Donor, Pantry, Donation models with proper relationships  
✅ **Custom Managers**: DonationManager with required QuerySet methods implemented  
✅ **Business Logic**: Claiming workflow and status management working  
✅ **Performance**: Database indexes and query optimization in place  
✅ **Testing**: Comprehensive test suite with >90% code coverage  
✅ **Admin Integration**: Basic admin registration for all models  
✅ **Documentation**: Models have proper docstrings and help_text  

## Next Steps

1. Implement this data model foundation
2. Create and run migrations
3. Add sample data for testing
4. Move to ADR-002 implementation (Django Views Architecture)
5. Integrate with authentication system (ADR-003)