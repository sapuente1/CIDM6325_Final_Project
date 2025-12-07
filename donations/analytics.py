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