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
            for donation in old_donations[:10]:  # Show first 10
                self.stdout.write(f'  - {donation.food_type}: {donation.status} - {donation.updated_at}')
            return
        
        # Delete old donations
        deleted_count, _ = old_donations.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {deleted_count} old donations')
        )