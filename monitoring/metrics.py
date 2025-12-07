"""
Business metrics tracking for CFMP observability
"""
import logging
from django.utils import timezone


metrics_logger = logging.getLogger('cfmp.metrics')


class BusinessMetrics:
    """Utility class for tracking business metrics and events"""
    
    @staticmethod
    def log_donation_created(donation, user):
        """Log donation creation with business context"""
        hours_until_expiry = (donation.expiry_date - timezone.now().date()).days * 24 if donation.expiry_date else None
        
        metrics_logger.info("Donation created", extra={
            'event_type': 'donation_created',
            'user_id': user.id,
            'user_type': 'donor',
            'donation_id': donation.id,
            'food_type': donation.food_type,
            'quantity': str(donation.quantity),
            'location': donation.location,
            'hours_until_expiry': hours_until_expiry,
            'expires_soon': hours_until_expiry < 24 if hours_until_expiry else False,
            'timestamp': timezone.now().isoformat()
        })
    
    @staticmethod
    def log_donation_claimed(donation, pantry_user):
        """Log donation claim with timing analysis"""
        time_to_claim = timezone.now() - donation.created_at
        hours_to_claim = time_to_claim.total_seconds() / 3600
        
        metrics_logger.info("Donation claimed", extra={
            'event_type': 'donation_claimed',
            'donation_id': donation.id,
            'claimed_by_user_id': pantry_user.id,
            'claimed_by_type': 'pantry',
            'hours_to_claim': round(hours_to_claim, 2),
            'food_type': donation.food_type,
            'quantity': str(donation.quantity),
            'location': donation.location,
            'timestamp': timezone.now().isoformat()
        })
    
    @staticmethod
    def log_donation_expired(donation):
        """Log donation expiry for waste tracking"""
        metrics_logger.warning("Donation expired unclaimed", extra={
            'event_type': 'donation_expired',
            'donation_id': donation.id,
            'food_type': donation.food_type,
            'quantity': str(donation.quantity),
            'location': donation.location,
            'days_active': (timezone.now().date() - donation.created_at.date()).days,
            'timestamp': timezone.now().isoformat()
        })
    
    @staticmethod
    def log_user_registration(user, user_type):
        """Log user registration events"""
        metrics_logger.info("User registered", extra={
            'event_type': 'user_registered',
            'user_id': user.id,
            'user_type': user_type,
            'email': user.email,
            'timestamp': timezone.now().isoformat()
        })
    
    @staticmethod
    def log_user_login(user):
        """Log user login events"""
        user_type = 'admin' if user.is_superuser else 'staff' if user.is_staff else 'regular'
        if hasattr(user, 'donor'):
            user_type = 'donor'
        elif hasattr(user, 'pantry'):
            user_type = 'pantry'
            
        metrics_logger.info("User logged in", extra={
            'event_type': 'user_login',
            'user_id': user.id,
            'user_type': user_type,
            'timestamp': timezone.now().isoformat()
        })
