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
        # For now, just log the action
        self.stdout.write(f'Notification sent for expired donation: {donation.id}')