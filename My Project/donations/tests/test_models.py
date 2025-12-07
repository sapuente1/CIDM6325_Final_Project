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
    
    def test_donor_properties(self):
        """Test donor property methods"""
        # Create a test donation
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
        
        self.assertEqual(self.donor.total_donations, 1)
        self.assertEqual(self.donor.active_donations, 1)


class PantryModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('pantry1', 'pantry@test.com', 'password')
        self.pantry = Pantry.objects.create(
            user=self.user,
            organization_name='Test Pantry',
            capacity=100,
            location='Test City',
            service_area='Test Area'
        )
    
    def test_pantry_creation(self):
        """Test pantry model creation and string representation"""
        self.assertEqual(str(self.pantry), 'Test Pantry (pantry1)')
        self.assertEqual(self.pantry.total_claims, 0)
    
    def test_pantry_properties(self):
        """Test pantry property methods"""
        # Create test data
        donor_user = User.objects.create_user('donor', 'donor@test.com', 'password')
        donor = Donor.objects.create(
            user=donor_user,
            organization_name='Test Donor',
            location='Test City'
        )
        
        # Create and claim a donation
        future_date = timezone.now() + timedelta(days=2)
        donation = Donation.objects.create(
            donor=donor,
            food_type='produce',
            description='Fresh apples',
            quantity=10,
            unit='lbs',
            location='Test City',
            expiry_date=future_date
        )
        
        donation.claim(self.pantry)
        
        self.assertEqual(self.pantry.total_claims, 1)
        self.assertEqual(self.pantry.recent_claims.count(), 1)


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
        # Days until expiry should be positive
        days = donation.days_until_expiry
        self.assertIsNotNone(days)
        if days is not None:
            self.assertTrue(days > 0)
    
    def test_donation_urgent_status(self):
        """Test urgent donation detection"""
        urgent_date = timezone.now() + timedelta(hours=6)
        donation = Donation.objects.create(
            donor=self.donor,
            food_type='dairy',
            description='Fresh milk',
            quantity=5,
            unit='gallons',
            location='Test City',
            expiry_date=urgent_date
        )
        
        self.assertTrue(donation.is_urgent)
    
    def test_donation_expired_status(self):
        """Test expired donation detection"""
        past_date = timezone.now() - timedelta(days=2)  # Use days, not hours
        donation = Donation.objects.create(
            donor=self.donor,
            food_type='meat',
            description='Expired meat',
            quantity=3,
            unit='lbs',
            location='Test City',
            expiry_date=past_date
        )
        
        # Should auto-mark as expired on save
        self.assertEqual(donation.status, 'expired')
        self.assertTrue(donation.is_expired)
    
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
    
    def test_donation_fulfill_process(self):
        """Test donation fulfillment process"""
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
        
        # Claim first
        donation.claim(self.pantry)
        
        # Then fulfill
        result = donation.mark_fulfilled()
        self.assertTrue(result)
        self.assertEqual(donation.status, 'fulfilled')
        self.assertIsNotNone(donation.fulfilled_at)
    
    def test_donation_string_representation(self):
        """Test donation string representation"""
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
        
        expected_str = f"Fresh Produce - 10 lbs (expires {future_date.date()})"
        self.assertEqual(str(donation), expected_str)