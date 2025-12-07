from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from donations.models import Donor, Pantry, Donation

class DonationManagerTests(TestCase):
    def setUp(self):
        # Create test data
        donor_user = User.objects.create_user('donor', 'donor@test.com', 'password')
        self.donor = Donor.objects.create(
            user=donor_user,
            organization_name='Test Donor',
            location='Test City'
        )
        
        pantry_user = User.objects.create_user('pantry', 'pantry@test.com', 'password')
        self.pantry = Pantry.objects.create(
            user=pantry_user,
            organization_name='Test Pantry',
            capacity=100,
            location='Test City',
            service_area='Test Area'
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
        
        # Expired donation (manually set status since auto-expire happens on save)
        self.expired_donation = Donation.objects.create(
            donor=self.donor,
            food_type='meat',
            description='Already expired',
            quantity=3,
            location='Test City',
            expiry_date=now - timedelta(hours=2)
        )
        # Override status since it auto-expires on save
        self.expired_donation.status = 'expired'
        self.expired_donation.save()
        
        # Claimed donation
        self.claimed_donation = Donation.objects.create(
            donor=self.donor,
            food_type='canned',
            description='Claimed donation',
            quantity=8,
            location='Test City',
            expiry_date=now + timedelta(days=1)
        )
        self.claimed_donation.claim(self.pantry)
    
    def test_available_queryset(self):
        """Test available() manager method"""
        available = Donation.objects.available()
        
        # Should include future and urgent donations
        self.assertIn(self.future_donation, available)
        self.assertIn(self.urgent_donation, available)
        
        # Should not include expired or claimed donations
        self.assertNotIn(self.expired_donation, available)
        self.assertNotIn(self.claimed_donation, available)
    
    def test_urgent_queryset(self):
        """Test urgent() manager method"""
        urgent = Donation.objects.urgent()
        
        # Should include only urgent donation
        self.assertIn(self.urgent_donation, urgent)
        
        # Should not include future, expired, or claimed donations
        self.assertNotIn(self.future_donation, urgent)
        self.assertNotIn(self.expired_donation, urgent)
        self.assertNotIn(self.claimed_donation, urgent)
    
    def test_near_expiry_queryset(self):
        """Test near_expiry() with custom hours"""
        # Test 48-hour window (2 days)
        near_expiry = Donation.objects.near_expiry(hours=48)
        
        self.assertIn(self.future_donation, near_expiry)
        self.assertIn(self.urgent_donation, near_expiry)
        self.assertNotIn(self.expired_donation, near_expiry)
        self.assertNotIn(self.claimed_donation, near_expiry)
        
        # Test 1-hour window (should only include very urgent items)
        very_urgent = Donation.objects.near_expiry(hours=1)
        self.assertNotIn(self.future_donation, very_urgent)
        self.assertNotIn(self.urgent_donation, very_urgent)  # 6 hours > 1 hour
    
    def test_location_filtering(self):
        """Test by_location() filtering"""
        city_donations = Donation.objects.by_location('Test City')
        self.assertEqual(city_donations.count(), 4)  # All our test donations
        
        # Test case-insensitive partial matching
        partial_donations = Donation.objects.by_location('test')
        self.assertEqual(partial_donations.count(), 4)
        
        # Test no matches
        no_matches = Donation.objects.by_location('Nonexistent City')
        self.assertEqual(no_matches.count(), 0)
    
    def test_food_type_filtering(self):
        """Test by_food_type() filtering"""
        produce_donations = Donation.objects.by_food_type('produce')
        self.assertEqual(produce_donations.count(), 1)
        self.assertIn(self.future_donation, produce_donations)
        
        dairy_donations = Donation.objects.by_food_type('dairy')
        self.assertEqual(dairy_donations.count(), 1)
        self.assertIn(self.urgent_donation, dairy_donations)
    
    def test_claimed_queryset(self):
        """Test claimed() manager method"""
        claimed = Donation.objects.claimed()
        self.assertEqual(claimed.count(), 1)
        self.assertIn(self.claimed_donation, claimed)
    
    def test_expired_unclaimed_queryset(self):
        """Test expired_unclaimed() manager method"""
        expired_unclaimed = Donation.objects.expired_unclaimed()
        self.assertEqual(expired_unclaimed.count(), 1)
        self.assertIn(self.expired_donation, expired_unclaimed)
    
    def test_for_donor_filtering(self):
        """Test for_donor() filtering"""
        donor_donations = Donation.objects.for_donor(self.donor)
        self.assertEqual(donor_donations.count(), 4)  # All test donations are from same donor
    
    def test_for_pantry_filtering(self):
        """Test for_pantry() filtering"""
        pantry_donations = Donation.objects.for_pantry(self.pantry)
        self.assertEqual(pantry_donations.count(), 1)
        self.assertIn(self.claimed_donation, pantry_donations)
    
    def test_with_related_optimization(self):
        """Test with_related() query optimization"""
        # This test verifies the method exists and runs without error
        # In a real application, you'd test query count reduction
        donations = Donation.objects.with_related()
        self.assertEqual(donations.count(), 4)
    
    def test_cleanup_expired_method(self):
        """Test cleanup_expired() utility method"""
        # Create an available donation with past expiry date
        past_date = timezone.now() - timedelta(days=1)  # Use days, not hours
        old_donation = Donation.objects.create(
            donor=self.donor,
            food_type='bakery',
            description='Old bread',
            quantity=2,
            location='Test City',
            expiry_date=past_date
        )
        
        # Force status to available using update() to bypass save() logic
        Donation.objects.filter(pk=old_donation.pk).update(status='available')
        
        # Verify it's set to available
        old_donation.refresh_from_db()
        self.assertEqual(old_donation.status, 'available')
        
        # Run cleanup
        expired_count = Donation.objects.cleanup_expired()
        
        # Should have marked 1 donation as expired
        self.assertEqual(expired_count, 1)
        
        # Verify the donation was marked as expired
        old_donation.refresh_from_db()
        self.assertEqual(old_donation.status, 'expired')