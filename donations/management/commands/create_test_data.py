"""
Management command to create test data for CFMP application.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from donations.models import Donor, Pantry, Donation


class Command(BaseCommand):
    help = 'Create test accounts and sample donations for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating test data...'))

        # Create test donor user
        try:
            donor_user = User.objects.get(username='testdonor')
            self.stdout.write(self.style.WARNING('Test donor user already exists'))
        except User.DoesNotExist:
            donor_user = User.objects.create_user(
                username='testdonor',
                password='testpass123',
                email='donor@example.com',
                first_name='John',
                last_name='Donor'
            )
            self.stdout.write(self.style.SUCCESS('Created test donor user: testdonor/testpass123'))

        # Create donor profile
        try:
            donor = Donor.objects.get(user=donor_user)
            self.stdout.write(self.style.WARNING('Donor profile already exists'))
        except Donor.DoesNotExist:
            donor = Donor.objects.create(
                user=donor_user,
                organization_name='Test Restaurant',
                contact_phone='555-0123',
                address='123 Main St, Test City, TX 79000',
                organization_type='restaurant'
            )
            self.stdout.write(self.style.SUCCESS('Created donor profile for Test Restaurant'))

        # Create test pantry user
        try:
            pantry_user = User.objects.get(username='testpantry')
            self.stdout.write(self.style.WARNING('Test pantry user already exists'))
        except User.DoesNotExist:
            pantry_user = User.objects.create_user(
                username='testpantry',
                password='testpass123',
                email='pantry@example.com',
                first_name='Jane',
                last_name='Pantry'
            )
            self.stdout.write(self.style.SUCCESS('Created test pantry user: testpantry/testpass123'))

        # Create pantry profile
        try:
            pantry = Pantry.objects.get(user=pantry_user)
            self.stdout.write(self.style.WARNING('Pantry profile already exists'))
        except Pantry.DoesNotExist:
            pantry = Pantry.objects.create(
                user=pantry_user,
                organization_name='Test Food Pantry',
                organization_type='food_bank',
                contact_phone='555-0456',
                address='456 Oak Ave, Test City, TX 79001',
                location='Test City, TX',
                service_area='Test City and surrounding areas',
                capacity=500,
                pickup_hours='Mon-Fri 9AM-5PM'
            )
            self.stdout.write(self.style.SUCCESS('Created pantry profile for Test Food Pantry'))

        # Create sample donations
        sample_donations = [
            {
                'food_type': 'produce',
                'description': 'Fresh mixed vegetables including carrots, broccoli, and bell peppers',
                'quantity': 20,
                'unit': 'pounds',
                'expiry_date': timezone.now() + timedelta(days=3),
                'location': '123 Main St, Test City, TX',
                'pickup_instructions': 'Keep refrigerated. Call before pickup.'
            },
            {
                'food_type': 'bread',
                'description': 'Day-old bread, muffins, and pastries from bakery',
                'quantity': 15,
                'unit': 'items',
                'expiry_date': timezone.now() + timedelta(days=1),
                'location': '123 Main St, Test City, TX',
                'pickup_instructions': 'Best if picked up before 6PM'
            },
            {
                'food_type': 'prepared',
                'description': 'Individually packaged chicken and rice meals',
                'quantity': 30,
                'unit': 'servings',
                'expiry_date': timezone.now() + timedelta(days=2),
                'location': '123 Main St, Test City, TX',
                'pickup_instructions': 'Keep frozen until pickup'
            },
            {
                'food_type': 'canned',
                'description': 'Mixed canned vegetables, soups, and fruits',
                'quantity': 50,
                'unit': 'cans',
                'expiry_date': timezone.now() + timedelta(days=365),
                'location': '123 Main St, Test City, TX',
                'pickup_instructions': 'No special handling required'
            }
        ]

        for donation_data in sample_donations:
            # Check if similar donation already exists
            existing = Donation.objects.filter(
                donor=donor,
                food_type=donation_data['food_type']
            ).first()
            
            if existing:
                self.stdout.write(self.style.WARNING(f'Similar donation already exists: {donation_data["food_type"]}'))
                continue

            donation = Donation.objects.create(
                donor=donor,
                **donation_data
            )
            self.stdout.write(self.style.SUCCESS(f'Created donation: {donation.food_type} ({donation.quantity} {donation.unit})'))

        # Create one claimed donation for testing
        try:
            claimed_donation = Donation.objects.filter(
                donor=donor,
                food_type='bread'
            ).first()
            
            if claimed_donation and claimed_donation.status == 'available':
                claimed_donation.claim(pantry)
                self.stdout.write(self.style.SUCCESS(f'Test pantry claimed: {claimed_donation.food_type}'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not create claimed donation: {e}'))

        self.stdout.write(self.style.SUCCESS('\n=== TEST DATA CREATED ==='))
        self.stdout.write(self.style.SUCCESS('Donor Account: testdonor / testpass123'))
        self.stdout.write(self.style.SUCCESS('Pantry Account: testpantry / testpass123'))
        self.stdout.write(self.style.SUCCESS('Admin Account: admin / admin123'))
        self.stdout.write(self.style.SUCCESS('\nYou can now test:'))
        self.stdout.write('• Login as donor to create/manage donations')
        self.stdout.write('• Login as pantry to view/claim donations')
        self.stdout.write('• Admin panel at /admin/ to manage everything')
        self.stdout.write('• Public donation list at /donations/')