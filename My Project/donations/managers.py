# donations/managers.py
from django.db import models, transaction
from django.utils import timezone
from datetime import timedelta

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
        now = timezone.now()
        return self.annotate(
            is_expiring_soon=models.Case(
                models.When(
                    expiry_date__lte=now + timedelta(days=2),
                    then=models.Value(True)
                ),
                default=models.Value(False),
                output_field=models.BooleanField()
            )
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
    
    def urgent(self):
        """Public interface for urgent donations"""
        return self.get_queryset().urgent()
    
    def near_expiry(self, hours=24):
        """Public interface for near-expiry donations"""
        return self.get_queryset().near_expiry(hours=hours)
    
    def by_location(self, city):
        """Public interface for location-based filtering"""
        return self.get_queryset().by_location(city)
    
    def by_food_type(self, food_type):
        """Public interface for food type filtering"""
        return self.get_queryset().by_food_type(food_type)
    
    def claimed(self):
        """Public interface for claimed donations"""
        return self.get_queryset().claimed()
    
    def expired_unclaimed(self):
        """Public interface for expired unclaimed donations"""
        return self.get_queryset().expired_unclaimed()
    
    def with_related(self):
        """Public interface for query optimization"""
        return self.get_queryset().with_related()
    
    def for_donor(self, donor):
        """Public interface for donor-specific donations"""
        return self.get_queryset().for_donor(donor)
    
    def for_pantry(self, pantry):
        """Public interface for pantry-specific donations"""
        return self.get_queryset().for_pantry(pantry)
    
    def cleanup_expired(self):
        """Management command helper: mark expired donations"""
        expired_count = self.get_queryset().filter(
            status='available',
            expiry_date__date__lt=timezone.now().date()
        ).update(status='expired')
        return expired_count


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