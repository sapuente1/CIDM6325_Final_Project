from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import uuid
from .managers import DonationManager, DonorQuerySet, PantryQuerySet
from .validators import validate_future_date, validate_positive_quantity, validate_phone_number

class Donor(models.Model):
    """Enhanced donor model with business logic"""
    
    ORGANIZATION_TYPE_CHOICES = [
        ('restaurant', 'Restaurant'),
        ('grocery', 'Grocery Store'),
        ('bakery', 'Bakery'),
        ('farm', 'Farm'),
        ('caterer', 'Catering Service'),
        ('event', 'Event Organizer'),
        ('individual', 'Individual'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        help_text="Associated user account"
    )
    organization_name = models.CharField(
        max_length=255,
        help_text="Name of donating organization or individual"
    )
    organization_type = models.CharField(
        max_length=100, 
        choices=ORGANIZATION_TYPE_CHOICES,
        default='other'
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[validate_phone_number]
    )
    address = models.TextField(blank=True)
    location = models.CharField(
        max_length=255,
        help_text="City or general location (for privacy)"
    )
    
    # Business information
    business_hours = models.TextField(
        blank=True, 
        help_text="Hours when donations can be picked up"
    )
    special_instructions = models.TextField(blank=True)
    
    # Verification status
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = models.Manager.from_queryset(DonorQuerySet)()
    
    class Meta:
        verbose_name = "Donor"
        verbose_name_plural = "Donors"
        ordering = ['organization_name']
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
    
    @property
    def total_donations(self):
        """Get total number of donations by this donor"""
        return self.donations.count()
    
    @property
    def active_donations(self):
        """Get number of active (available) donations"""
        return self.donations.available().count()


class Pantry(models.Model):
    """Enhanced pantry model with business logic"""
    
    ORGANIZATION_TYPE_CHOICES = [
        ('food_bank', 'Food Bank'),
        ('soup_kitchen', 'Soup Kitchen'),
        ('shelter', 'Homeless Shelter'),
        ('community_center', 'Community Center'),
        ('church', 'Religious Organization'),
        ('school', 'School'),
        ('nonprofit', 'Nonprofit Organization'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        help_text="Associated user account"
    )
    organization_name = models.CharField(
        max_length=255,
        help_text="Name of pantry organization"
    )
    organization_type = models.CharField(
        max_length=100, 
        choices=ORGANIZATION_TYPE_CHOICES,
        default='other'
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[validate_phone_number]
    )
    address = models.TextField(blank=True)
    location = models.CharField(
        max_length=255,
        help_text="City or general location"
    )
    service_area = models.CharField(
        max_length=255,
        help_text="Geographic area served by this pantry"
    )
    
    # Capacity and logistics
    capacity = models.PositiveIntegerField(
        help_text="Maximum items that can be handled"
    )
    storage_types = models.JSONField(
        default=list, 
        help_text="Types of storage available"
    )
    pickup_hours = models.TextField(
        blank=True,
        help_text="Hours when donations can be picked up"
    )
    
    # Verification status
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = models.Manager.from_queryset(PantryQuerySet)()
    
    class Meta:
        verbose_name = "Pantry"
        verbose_name_plural = "Pantries"
        ordering = ['organization_name']
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
    
    @property
    def total_claims(self):
        """Get total number of donations claimed by this pantry"""
        return self.claimed_donations.count()
    
    @property
    def recent_claims(self):
        """Get donations claimed in the last 30 days"""
        cutoff = timezone.now() - timedelta(days=30)
        return self.claimed_donations.filter(claimed_at__gte=cutoff)


class Donation(models.Model):
    """Enhanced donation model with business logic"""
    
    FOOD_TYPE_CHOICES = [
        ('produce', 'Fresh Produce'),
        ('dairy', 'Dairy Products'),
        ('bread', 'Bread & Baked Goods'),
        ('canned', 'Canned Goods'),
        ('frozen', 'Frozen Items'),
        ('meat', 'Meat & Poultry'),
        ('pantry', 'Pantry Staples'),
        ('prepared', 'Prepared Meals'),
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
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donations')
    food_type = models.CharField(max_length=50, choices=FOOD_TYPE_CHOICES)
    description = models.TextField(help_text="Detailed description of the food items")
    quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[validate_positive_quantity],
        help_text="Quantity (lbs, count, servings, etc.)"
    )
    unit = models.CharField(
        max_length=20,
        default='lbs',
        help_text="Unit of measurement (lbs, servings, boxes, etc.)"
    )
    location = models.CharField(max_length=255)
    expiry_date = models.DateTimeField(
        validators=[validate_future_date],
        help_text="When this food expires"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Claiming information
    claimed_by = models.ForeignKey(
        Pantry, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='claimed_donations'
    )
    claimed_at = models.DateTimeField(null=True, blank=True)
    
    # Fulfillment information
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    fulfillment_notes = models.TextField(blank=True)
    pickup_instructions = models.TextField(
        blank=True,
        help_text="Special instructions for pickup"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Custom manager
    objects = DonationManager()
    
    class Meta:
        verbose_name = "Donation"
        verbose_name_plural = "Donations"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'expiry_date']),
            models.Index(fields=['location', 'status']),
            models.Index(fields=['food_type', 'status']),
            models.Index(fields=['created_at']),
        ]
    
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
            try:
                original = Donation.objects.get(pk=self.pk)
                if not self._is_valid_status_transition(original.status, self.status):
                    raise ValidationError({
                        'status': f'Invalid status transition from {original.status} to {self.status}'
                    })
            except Donation.DoesNotExist:
                pass
    
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
        
        return self
    
    @transaction.atomic
    def expire(self):
        """Business logic for expiring a donation"""
        if self.status in ['fulfilled', 'expired']:
            return self  # Already in terminal state
        
        self.status = 'expired'
        self.save()
        
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
    
    def mark_fulfilled(self):
        """Legacy method - use fulfill() instead"""
        return self.fulfill()
    
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
    
    @property
    def is_urgent(self):
        """Check if donation expires within 24 hours"""
        days = self.days_until_expiry
        return days is not None and days <= 1
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('donations:detail', kwargs={'pk': self.pk})
    
    def __str__(self):
        return f"{self.food_type} - {self.description[:50]}"
    
    def save(self, *args, **kwargs):
        """Override save to auto-update status based on expiry"""
        # Auto-mark expired donations
        if self.expiry_date and self.expiry_date < timezone.now():
            if self.status == 'available':
                self.status = 'expired'
        
        super().save(*args, **kwargs)
