# ADR-012: Data Management and Business Logic

**Date**: 2025-12-07  
**Status**: Proposed  
**Related PRD**: Section 3 (Core Functionality), Section 4 (Business Logic), Section 5 (Data Management)

## Context

CFMP currently has basic model definitions but lacks comprehensive business logic, data validation, and management features necessary for a production food management platform. Key missing components include:

- Business logic for donation lifecycle management
- Data validation and integrity constraints
- Automated processes (expiry notifications, cleanup tasks)
- Reporting and analytics capabilities
- Integration between donation and pantry management
- Performance optimizations for database queries

## Decision Drivers

- **Business Requirements**: Automated donation lifecycle management
- **Data Integrity**: Consistent and valid data across the platform
- **Performance**: Efficient database queries and operations
- **Academic Requirements**: Demonstrate Django ORM and business logic patterns
- **Scalability**: Support for growing user base and donation volume

## Options Considered

### A) Basic Model Methods Only
```python
class Donation(models.Model):
    # Basic fields only
    
    def save(self, *args, **kwargs):
        # Simple save logic
        super().save(*args, **kwargs)
```

**Pros**: Simple implementation, minimal complexity  
**Cons**: Limited functionality, business logic scattered across views

### B) Rich Domain Models + Manager Classes
```python
class DonationQuerySet(models.QuerySet):
    def available(self):
        return self.filter(status='available', expiry_date__gt=timezone.now())
    
    def expiring_soon(self):
        cutoff = timezone.now() + timedelta(days=2)
        return self.available().filter(expiry_date__lte=cutoff)

class DonationManager(models.Manager):
    def get_queryset(self):
        return DonationQuerySet(self.model, using=self._db)
    
    def available(self):
        return self.get_queryset().available()

class Donation(models.Model):
    objects = DonationManager()
    
    def claim(self, pantry):
        # Business logic for claiming donations
        
    def expire(self):
        # Business logic for expiration
```

**Pros**: Centralized business logic, reusable queries, Django best practices  
**Cons**: More complex architecture, learning curve

### C) Service Layer Pattern
```python
class DonationService:
    @staticmethod
    def claim_donation(donation_id, pantry):
        # Business logic in service layer
        
    @staticmethod  
    def process_expired_donations():
        # Background processing logic
```

**Pros**: Clear separation of concerns, testable business logic  
**Cons**: Additional abstraction layer, not standard Django pattern

## Decision

**We choose Option B (Rich Domain Models + Manager Classes)** because:

1. **Django Best Practice**: Leverage Django ORM patterns effectively
2. **Code Organization**: Business logic lives close to the data model
3. **Reusability**: Custom managers and querysets promote code reuse
4. **Performance**: Query optimization at the ORM level
5. **Academic Value**: Demonstrates advanced Django ORM concepts
6. **Maintainability**: Clear boundaries between data access and business logic

## Implementation Strategy

### Enhanced Model Architecture

#### Donation Model with Business Logic
```python
# donations/models.py
from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
import uuid

class DonationQuerySet(models.QuerySet):
    """Custom queryset for donations with business logic"""
    
    def available(self):
        """Return donations that are available for claiming"""
        return self.filter(
            status='available',
            expiry_date__gt=timezone.now()
        ).select_related('donor__user')
    
    def expiring_soon(self, days=2):
        """Return donations expiring within specified days"""
        cutoff = timezone.now() + timedelta(days=days)
        return self.available().filter(expiry_date__lte=cutoff)
    
    def expired(self):
        """Return donations that have expired"""
        return self.filter(
            models.Q(expiry_date__lte=timezone.now()) |
            models.Q(status='expired')
        )
    
    def for_pantry_area(self, pantry):
        """Return donations in pantry's service area"""
        return self.available().filter(
            location__icontains=pantry.service_area
        )
    
    def by_food_type(self, food_type):
        """Filter by food type"""
        return self.filter(food_type=food_type)
    
    def with_metrics(self):
        """Add calculated metrics to queryset"""
        return self.annotate(
            days_until_expiry=models.ExpressionWrapper(
                models.F('expiry_date') - timezone.now(),
                output_field=models.DurationField()
            ),
            is_expiring_soon=models.Case(
                models.When(
                    expiry_date__lte=timezone.now() + timedelta(days=2),
                    then=models.Value(True)
                ),
                default=models.Value(False),
                output_field=models.BooleanField()
            )
        )

class DonationManager(models.Manager):
    """Custom manager for donations"""
    
    def get_queryset(self):
        return DonationQuerySet(self.model, using=self._db)
    
    def available(self):
        return self.get_queryset().available()
    
    def expiring_soon(self, days=2):
        return self.get_queryset().expiring_soon(days)
    
    def expired(self):
        return self.get_queryset().expired()
    
    def for_pantry_area(self, pantry):
        return self.get_queryset().for_pantry_area(pantry)
    
    def create_with_validation(self, **kwargs):
        """Create donation with full business validation"""
        donation = self.model(**kwargs)
        donation.full_clean()
        donation.save()
        return donation
    
    def bulk_expire_old(self):
        """Bulk expire donations past their expiry date"""
        expired_count = self.filter(
            expiry_date__lte=timezone.now(),
            status='available'
        ).update(
            status='expired',
            updated_at=timezone.now()
        )
        return expired_count

class Donation(models.Model):
    """Enhanced donation model with business logic"""
    
    FOOD_TYPE_CHOICES = [
        ('produce', 'Fresh Produce'),
        ('dairy', 'Dairy Products'),
        ('bread', 'Bread & Baked Goods'),
        ('canned', 'Canned Goods'),
        ('frozen', 'Frozen Items'),
        ('meat', 'Meat & Poultry'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('claimed', 'Claimed'),
        ('fulfilled', 'Fulfilled'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey('Donor', on_delete=models.CASCADE, related_name='donations')
    food_type = models.CharField(max_length=50, choices=FOOD_TYPE_CHOICES)
    description = models.TextField()
    quantity = models.PositiveIntegerField()
    location = models.CharField(max_length=255)
    expiry_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Claiming information
    claimed_by = models.ForeignKey(
        'pantries.Pantry', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='claimed_donations'
    )
    claimed_at = models.DateTimeField(null=True, blank=True)
    
    # Fulfillment information
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    fulfillment_notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Custom manager
    objects = DonationManager()
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'expiry_date']),
            models.Index(fields=['location', 'status']),
            models.Index(fields=['food_type', 'status']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def clean(self):
        """Model-level validation"""
        super().clean()
        
        if self.expiry_date and self.expiry_date <= timezone.now():
            raise ValidationError({
                'expiry_date': 'Expiry date must be in the future.'
            })
        
        if self.quantity <= 0:
            raise ValidationError({
                'quantity': 'Quantity must be greater than zero.'
            })
        
        # Status transition validation
        if self.pk:  # Existing object
            original = Donation.objects.get(pk=self.pk)
            if not self._is_valid_status_transition(original.status, self.status):
                raise ValidationError({
                    'status': f'Invalid status transition from {original.status} to {self.status}'
                })
    
    def _is_valid_status_transition(self, old_status, new_status):
        """Validate status transitions"""
        valid_transitions = {
            'available': ['claimed', 'expired', 'cancelled'],
            'claimed': ['fulfilled', 'available', 'expired'],
            'fulfilled': [],  # Terminal state
            'expired': [],    # Terminal state
            'cancelled': [],  # Terminal state
        }
        return new_status in valid_transitions.get(old_status, [])
    
    @transaction.atomic
    def claim(self, pantry, notes=''):
        """Business logic for claiming a donation"""
        if self.status != 'available':
            raise ValidationError(f'Cannot claim donation with status: {self.status}')
        
        if self.is_expired:
            raise ValidationError('Cannot claim expired donation')
        
        self.claimed_by = pantry
        self.claimed_at = timezone.now()
        self.status = 'claimed'
        self.save()
        
        # Log the business event
        from monitoring.metrics import BusinessMetrics
        BusinessMetrics.log_donation_claimed(self, pantry.user)
        
        return self
    
    @transaction.atomic
    def fulfill(self, notes=''):
        """Business logic for fulfilling a donation"""
        if self.status != 'claimed':
            raise ValidationError(f'Cannot fulfill donation with status: {self.status}')
        
        self.status = 'fulfilled'
        self.fulfilled_at = timezone.now()
        self.fulfillment_notes = notes
        self.save()
        
        # Log the business event
        from monitoring.metrics import BusinessMetrics
        BusinessMetrics.log_donation_fulfilled(self)
        
        return self
    
    @transaction.atomic
    def expire(self):
        """Business logic for expiring a donation"""
        if self.status in ['fulfilled', 'expired']:
            return self  # Already in terminal state
        
        old_status = self.status
        self.status = 'expired'
        self.save()
        
        # Log the business event if it was available
        if old_status == 'available':
            from monitoring.metrics import BusinessMetrics
            BusinessMetrics.log_donation_expired(self)
        
        return self
    
    @transaction.atomic
    def cancel(self, reason=''):
        """Business logic for cancelling a donation"""
        if self.status == 'fulfilled':
            raise ValidationError('Cannot cancel fulfilled donation')
        
        self.status = 'cancelled'
        self.fulfillment_notes = f'Cancelled: {reason}'
        self.save()
        
        return self
    
    @property
    def is_expired(self):
        """Check if donation has expired"""
        return self.expiry_date <= timezone.now()
    
    @property
    def is_expiring_soon(self, hours=48):
        """Check if donation is expiring within specified hours"""
        cutoff = timezone.now() + timedelta(hours=hours)
        return self.expiry_date <= cutoff
    
    @property
    def days_until_expiry(self):
        """Calculate days until expiry"""
        if self.is_expired:
            return 0
        delta = self.expiry_date - timezone.now()
        return max(0, delta.days)
    
    @property
    def time_since_created(self):
        """Time since donation was created"""
        return timezone.now() - self.created_at
    
    @property
    def time_to_claim(self):
        """Time taken to claim (if claimed)"""
        if not self.claimed_at:
            return None
        return self.claimed_at - self.created_at
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('donations:detail', kwargs={'pk': self.pk})
    
    def __str__(self):
        return f"{self.food_type} - {self.description[:50]}"
```

#### Enhanced Donor and Pantry Models
```python
# donations/models.py (continued)

class DonorQuerySet(models.QuerySet):
    """Custom queryset for donors"""
    
    def active(self):
        """Donors with recent activity"""
        cutoff = timezone.now() - timedelta(days=90)
        return self.filter(
            donations__created_at__gte=cutoff
        ).distinct()
    
    def with_stats(self):
        """Annotate donors with statistics"""
        return self.annotate(
            total_donations=models.Count('donations'),
            active_donations=models.Count(
                'donations',
                filter=models.Q(donations__status='available')
            ),
            claimed_donations=models.Count(
                'donations',
                filter=models.Q(donations__status__in=['claimed', 'fulfilled'])
            )
        )

class Donor(models.Model):
    """Enhanced donor model"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=255)
    organization_type = models.CharField(max_length=100, choices=[
        ('restaurant', 'Restaurant'),
        ('grocery', 'Grocery Store'),
        ('bakery', 'Bakery'),
        ('farm', 'Farm'),
        ('caterer', 'Catering Service'),
        ('event', 'Event Organizer'),
        ('individual', 'Individual'),
        ('other', 'Other'),
    ])
    contact_phone = models.CharField(max_length=20)
    address = models.TextField()
    location = models.CharField(max_length=255)
    
    # Business information
    business_hours = models.TextField(blank=True, help_text="Hours when donations can be picked up")
    special_instructions = models.TextField(blank=True)
    
    # Verification status
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = models.Manager.from_queryset(DonorQuerySet)()
    
    class Meta:
        indexes = [
            models.Index(fields=['location', 'is_verified']),
            models.Index(fields=['organization_type']),
        ]
    
    def get_donation_stats(self):
        """Get donation statistics for this donor"""
        donations = self.donations.all()
        
        return {
            'total': donations.count(),
            'available': donations.filter(status='available').count(),
            'claimed': donations.filter(status='claimed').count(),
            'fulfilled': donations.filter(status='fulfilled').count(),
            'expired': donations.filter(status='expired').count(),
            'this_month': donations.filter(
                created_at__gte=timezone.now().replace(day=1)
            ).count(),
        }
    
    def get_claim_rate(self):
        """Calculate percentage of donations that get claimed"""
        total = self.donations.exclude(status='available').count()
        if total == 0:
            return 0
        claimed = self.donations.filter(
            status__in=['claimed', 'fulfilled']
        ).count()
        return round((claimed / total) * 100, 1)
    
    def __str__(self):
        return self.organization_name

class PantryQuerySet(models.QuerySet):
    """Custom queryset for pantries"""
    
    def in_area(self, location):
        """Pantries serving a specific area"""
        return self.filter(service_area__icontains=location)
    
    def with_capacity(self):
        """Pantries with remaining capacity"""
        return self.filter(capacity__gt=0)
    
    def with_stats(self):
        """Annotate pantries with statistics"""
        return self.annotate(
            total_claims=models.Count('claimed_donations'),
            active_claims=models.Count(
                'claimed_donations',
                filter=models.Q(claimed_donations__status='claimed')
            )
        )

class Pantry(models.Model):
    """Enhanced pantry model"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=255)
    organization_type = models.CharField(max_length=100, choices=[
        ('food_bank', 'Food Bank'),
        ('soup_kitchen', 'Soup Kitchen'),
        ('shelter', 'Homeless Shelter'),
        ('community_center', 'Community Center'),
        ('church', 'Religious Organization'),
        ('school', 'School'),
        ('nonprofit', 'Nonprofit Organization'),
        ('other', 'Other'),
    ])
    
    contact_phone = models.CharField(max_length=20)
    address = models.TextField()
    location = models.CharField(max_length=255)
    service_area = models.CharField(max_length=255, help_text="Areas served by this pantry")
    
    # Capacity and logistics
    capacity = models.PositiveIntegerField(help_text="Maximum items that can be handled")
    storage_types = models.JSONField(default=list, help_text="Types of storage available")
    pickup_hours = models.TextField(help_text="Hours when donations can be picked up")
    
    # Verification status
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = models.Manager.from_queryset(PantryQuerySet)()
    
    class Meta:
        verbose_name_plural = "pantries"
        indexes = [
            models.Index(fields=['location', 'service_area']),
            models.Index(fields=['organization_type']),
        ]
    
    def get_claim_stats(self):
        """Get claim statistics for this pantry"""
        claims = self.claimed_donations.all()
        
        return {
            'total': claims.count(),
            'pending': claims.filter(status='claimed').count(),
            'fulfilled': claims.filter(status='fulfilled').count(),
            'this_month': claims.filter(
                claimed_at__gte=timezone.now().replace(day=1)
            ).count(),
        }
    
    def get_available_capacity(self):
        """Calculate available capacity"""
        active_claims = self.claimed_donations.filter(status='claimed').count()
        return max(0, self.capacity - active_claims)
    
    def can_claim_donation(self, donation):
        """Check if pantry can claim a specific donation"""
        if self.get_available_capacity() <= 0:
            return False, "Pantry at capacity"
        
        if not donation.status == 'available':
            return False, "Donation not available"
        
        if donation.is_expired:
            return False, "Donation has expired"
        
        return True, "Can claim"
    
    def __str__(self):
        return self.organization_name
```

### Management Commands for Data Operations

#### Automated Expiry Processing
```python
# donations/management/commands/process_expired_donations.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from donations.models import Donation

class Command(BaseCommand):
    help = 'Process expired donations and update their status'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        
        parser.add_argument(
            '--send-notifications',
            action='store_true',
            help='Send notifications to affected users',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        send_notifications = options['send_notifications']
        
        # Find expired donations
        expired_donations = Donation.objects.filter(
            expiry_date__lte=timezone.now(),
            status='available'
        )
        
        count = expired_donations.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would expire {count} donations')
            )
            for donation in expired_donations[:10]:  # Show first 10
                self.stdout.write(f'  - {donation.food_type}: {donation.description}')
            return
        
        # Process expired donations
        expired_count = 0
        for donation in expired_donations:
            try:
                donation.expire()
                expired_count += 1
                
                if send_notifications:
                    self._send_expiry_notification(donation)
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing donation {donation.id}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully expired {expired_count} donations')
        )
    
    def _send_expiry_notification(self, donation):
        """Send notification to donor about expired donation"""
        # Implementation would depend on notification system
        pass
```

#### Data Cleanup and Maintenance
```python
# donations/management/commands/cleanup_old_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from donations.models import Donation

class Command(BaseCommand):
    help = 'Clean up old fulfilled/expired donations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Delete records older than this many days (default: 90)',
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without making changes',
        )
    
    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Find old fulfilled/expired donations
        old_donations = Donation.objects.filter(
            status__in=['fulfilled', 'expired'],
            updated_at__lte=cutoff_date
        )
        
        count = old_donations.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would delete {count} old donations')
            )
            return
        
        # Delete old donations
        deleted_count, _ = old_donations.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {deleted_count} old donations')
        )
```

### Analytics and Reporting

#### Donation Analytics Service
```python
# donations/analytics.py
from django.db.models import Count, Avg, F, Q
from django.utils import timezone
from datetime import timedelta
from .models import Donation, Donor, Pantry

class DonationAnalytics:
    """Analytics service for donation data"""
    
    @staticmethod
    def get_platform_stats(days=30):
        """Get overall platform statistics"""
        cutoff = timezone.now() - timedelta(days=days)
        
        return {
            'total_donations': Donation.objects.count(),
            'recent_donations': Donation.objects.filter(created_at__gte=cutoff).count(),
            'active_donors': Donor.objects.filter(donations__created_at__gte=cutoff).distinct().count(),
            'active_pantries': Pantry.objects.filter(claimed_donations__claimed_at__gte=cutoff).distinct().count(),
            'claim_rate': DonationAnalytics.get_claim_rate(),
            'avg_time_to_claim': DonationAnalytics.get_avg_time_to_claim(),
        }
    
    @staticmethod
    def get_claim_rate():
        """Calculate overall claim rate"""
        total_donations = Donation.objects.exclude(status='available').count()
        if total_donations == 0:
            return 0
        
        claimed_donations = Donation.objects.filter(
            status__in=['claimed', 'fulfilled']
        ).count()
        
        return round((claimed_donations / total_donations) * 100, 1)
    
    @staticmethod
    def get_avg_time_to_claim():
        """Calculate average time to claim donations"""
        claimed_donations = Donation.objects.filter(
            status__in=['claimed', 'fulfilled'],
            claimed_at__isnull=False
        ).annotate(
            time_to_claim=F('claimed_at') - F('created_at')
        )
        
        if not claimed_donations.exists():
            return None
        
        avg_seconds = claimed_donations.aggregate(
            avg_time=Avg('time_to_claim')
        )['avg_time'].total_seconds()
        
        return timedelta(seconds=avg_seconds)
    
    @staticmethod
    def get_food_type_distribution():
        """Get distribution of donations by food type"""
        return Donation.objects.values('food_type').annotate(
            count=Count('id')
        ).order_by('-count')
    
    @staticmethod
    def get_geographic_distribution():
        """Get distribution of donations by location"""
        return Donation.objects.values('location').annotate(
            count=Count('id')
        ).order_by('-count')[:20]
    
    @staticmethod
    def get_donor_leaderboard(limit=10):
        """Get top donors by donation count"""
        return Donor.objects.annotate(
            donation_count=Count('donations')
        ).order_by('-donation_count')[:limit]
    
    @staticmethod
    def get_expiry_analysis():
        """Analyze donation expiry patterns"""
        return {
            'expired_total': Donation.objects.filter(status='expired').count(),
            'expiring_soon': Donation.objects.expiring_soon().count(),
            'avg_shelf_life': DonationAnalytics._get_avg_shelf_life(),
        }
    
    @staticmethod
    def _get_avg_shelf_life():
        """Calculate average shelf life of donations"""
        donations = Donation.objects.exclude(status='available').annotate(
            shelf_life=F('expiry_date') - F('created_at')
        )
        
        if not donations.exists():
            return None
        
        avg_seconds = donations.aggregate(
            avg_shelf_life=Avg('shelf_life')
        )['avg_shelf_life'].total_seconds()
        
        return timedelta(seconds=avg_seconds)
```

### Data Validation and Integrity

#### Model Validators
```python
# donations/validators.py
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

def validate_future_date(value):
    """Ensure date is in the future"""
    if value <= timezone.now():
        raise ValidationError("Date must be in the future.")

def validate_reasonable_expiry(value):
    """Ensure expiry date is reasonable (not too far in future)"""
    max_future = timezone.now() + timedelta(days=365)  # 1 year max
    if value > max_future:
        raise ValidationError("Expiry date cannot be more than 1 year in the future.")

def validate_phone_number(value):
    """Basic phone number validation"""
    import re
    if not re.match(r'^\+?1?\d{9,15}$', value.replace('-', '').replace(' ', '')):
        raise ValidationError("Enter a valid phone number.")

def validate_positive_quantity(value):
    """Ensure quantity is positive"""
    if value <= 0:
        raise ValidationError("Quantity must be greater than zero.")
```

## Consequences

**Positive**:
- Robust business logic centralized in models
- Efficient database queries through custom managers
- Automated data maintenance and cleanup
- Comprehensive analytics capabilities
- Strong data integrity and validation

**Negative**:
- Increased model complexity
- More files to maintain
- Learning curve for advanced ORM patterns

**Mitigation Strategies**:
- Comprehensive documentation of business logic
- Unit tests for all business methods
- Performance monitoring for complex queries

## Testing Strategy

### Business Logic Tests
```python
class DonationBusinessLogicTests(TestCase):
    def test_claim_donation_success(self):
        """Test successful donation claiming"""
        donation = DonationFactory(status='available')
        pantry = PantryFactory()
        
        result = donation.claim(pantry)
        
        self.assertEqual(result.status, 'claimed')
        self.assertEqual(result.claimed_by, pantry)
        self.assertIsNotNone(result.claimed_at)
    
    def test_claim_expired_donation_fails(self):
        """Test claiming expired donation fails"""
        donation = DonationFactory(
            status='available',
            expiry_date=timezone.now() - timedelta(hours=1)
        )
        pantry = PantryFactory()
        
        with self.assertRaises(ValidationError):
            donation.claim(pantry)
```

This ADR establishes comprehensive business logic and data management capabilities that make CFMP a robust, maintainable platform for food donation management.