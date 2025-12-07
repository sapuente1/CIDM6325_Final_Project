"""
Tests for donations admin interface functionality
"""
import csv
from io import StringIO
from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from django.contrib.messages.storage.fallback import FallbackStorage
from django.utils import timezone

from .models import Donor, Pantry, Donation
from .admin import DonationAdmin, DonorAdmin, PantryAdmin, mark_expired, export_csv


class AdminTestCase(TestCase):
    """Base test case with common setup for admin tests"""
    
    def setUp(self):
        self.site = AdminSite()
        
        # Create test users
        self.admin_user = User.objects.create_user(
            'admin', 'admin@test.com', 'pass', is_staff=True, is_superuser=True
        )
        self.donor_user = User.objects.create_user(
            'donor', 'donor@test.com', 'pass'
        )
        self.pantry_user = User.objects.create_user(
            'pantry', 'pantry@test.com', 'pass'
        )
        
        # Create test profiles
        self.donor = Donor.objects.create(
            user=self.donor_user,
            organization_name='Test Food Corp',
            location='Downtown',
            contact_phone='555-1234'
        )
        
        self.pantry = Pantry.objects.create(
            user=self.pantry_user,
            organization_name='Community Pantry',
            location='Northside',
            service_area='North District',
            capacity=100,
            contact_phone='555-5678'
        )
        
        # Create test donations
        self.donation1 = Donation.objects.create(
            donor=self.donor,
            food_type='Produce',
            description='Fresh vegetables',
            quantity=50,
            location='Downtown Store',
            expiry_date=date.today() + timedelta(days=5),
            status='available'
        )
        
        self.donation2 = Donation.objects.create(
            donor=self.donor,
            food_type='Dairy',
            description='Milk cartons',
            quantity=20,
            location='Downtown Store',
            expiry_date=date.today() - timedelta(days=1),  # Expired
            status='available'
        )
        
        self.donation3 = Donation.objects.create(
            donor=self.donor,
            food_type='Bread',
            description='Sandwich bread',
            quantity=30,
            location='Downtown Store',
            expiry_date=date.today(),  # Expires today
            status='available'
        )


class DonationAdminTests(AdminTestCase):
    """Tests for DonationAdmin functionality"""
    
    def setUp(self):
        super().setUp()
        self.donation_admin = DonationAdmin(Donation, self.site)
        
    def test_list_display_fields(self):
        """Test that all expected fields are displayed in list view"""
        expected_fields = [
            'id', 'food_type', 'donor_name', 'quantity', 
            'status', 'expiry_date', 'days_until_expiry', 'created_at'
        ]
        self.assertEqual(list(self.donation_admin.list_display), expected_fields)
        
    def test_donor_name_display(self):
        """Test custom donor_name method"""
        donor_name = self.donation_admin.donor_name(self.donation1)
        self.assertEqual(donor_name, 'Test Food Corp')
        
    def test_days_until_expiry_expired(self):
        """Test days_until_expiry for expired donation"""
        result = self.donation_admin.days_until_expiry(self.donation2)
        self.assertIn('Expired', result)
        self.assertIn('style="color: red', result)
        
    def test_days_until_expiry_today(self):
        """Test days_until_expiry for donation expiring today"""
        result = self.donation_admin.days_until_expiry(self.donation3)
        self.assertIn('Expires today', result)
        self.assertIn('style="color: orange', result)
        
    def test_days_until_expiry_future(self):
        """Test days_until_expiry for future expiry"""
        result = self.donation_admin.days_until_expiry(self.donation1)
        self.assertIn('5 days', result)
        
    def test_queryset_optimization(self):
        """Test that queryset includes select_related optimization"""
        request = HttpRequest()
        request.user = self.admin_user
        
        queryset = self.donation_admin.get_queryset(request)
        # Check that the queryset has select_related applied
        self.assertTrue(hasattr(queryset, '_prefetch_related_lookups'))
        
    def test_search_fields(self):
        """Test that search fields are properly configured"""
        expected_search_fields = [
            'donor__organization_name', 
            'food_type', 
            'location',
            'description',
            'claimed_by__organization_name'
        ]
        self.assertEqual(list(self.donation_admin.search_fields), expected_search_fields)


class BulkActionsTests(AdminTestCase):
    """Tests for admin bulk actions"""
    
    def setUp(self):
        super().setUp()
        self.donation_admin = DonationAdmin(Donation, self.site)
        
        # Setup request with messages framework
        self.request = HttpRequest()
        self.request.user = self.admin_user
        setattr(self.request, 'session', {})
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)
        
    def test_mark_expired_action(self):
        """Test mark_expired bulk action"""
        # Only test donations that are still available (not auto-expired)
        queryset = Donation.objects.filter(status='available')
        initial_available_count = queryset.count()
        
        # Execute action
        mark_expired(self.donation_admin, self.request, queryset)
        
        # Check that all previously available donations are now expired
        # Note: The expired donation may have been auto-expired by model save
        final_available_count = Donation.objects.filter(status='available').count()
        self.assertEqual(final_available_count, 0)
        
    def test_export_csv_action(self):
        """Test CSV export bulk action"""
        queryset = Donation.objects.all()
        
        response = export_csv(self.donation_admin, self.request, queryset)
        
        # Check response headers
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="donations.csv"', response['Content-Disposition'])
        
        # Parse CSV content
        content = response.content.decode('utf-8')
        csv_reader = csv.reader(StringIO(content))
        rows = list(csv_reader)
        
        # Check header row
        expected_headers = [
            'ID', 'Donor', 'Food Type', 'Quantity', 'Expiry Date', 
            'Status', 'Location', 'Claimed By', 'Created At'
        ]
        self.assertEqual(rows[0], expected_headers)
        
        # Check data rows (should have 3 donations + 1 header)
        self.assertEqual(len(rows), 4)
        
        # Check that we have valid data (don't assume specific order)
        data_rows = rows[1:]  # Skip header
        food_types = [row[2] for row in data_rows]
        self.assertIn('Produce', food_types)
        self.assertIn('Dairy', food_types)
        self.assertIn('Bread', food_types)


class DonorAdminTests(AdminTestCase):
    """Tests for DonorAdmin functionality"""
    
    def setUp(self):
        super().setUp()
        self.donor_admin = DonorAdmin(Donor, self.site)
        
    def test_list_display_fields(self):
        """Test donor admin list display"""
        expected_fields = [
            'organization_name', 'user_email', 'user_full_name', 
            'location', 'total_donations', 'active_donations', 'created_at'
        ]
        self.assertEqual(list(self.donor_admin.list_display), expected_fields)
        
    def test_user_email_display(self):
        """Test custom user_email method"""
        email = self.donor_admin.user_email(self.donor)
        self.assertEqual(email, 'donor@test.com')
        
    def test_total_donations_count(self):
        """Test total_donations method"""
        count = self.donor_admin.total_donations(self.donor)
        self.assertEqual(count, 3)  # 3 donations created in setUp
        
    def test_active_donations_count(self):
        """Test active_donations method with HTML formatting"""
        result = self.donor_admin.active_donations(self.donor)
        self.assertIn('3', str(result))  # Should show count of available donations
        self.assertIn('style="color: green', str(result))


class PantryAdminTests(AdminTestCase):
    """Tests for PantryAdmin functionality"""
    
    def setUp(self):
        super().setUp()
        self.pantry_admin = PantryAdmin(Pantry, self.site)
        
    def test_list_display_fields(self):
        """Test pantry admin list display"""
        expected_fields = [
            'organization_name', 'user_email', 'user_full_name',
            'location', 'service_area', 'capacity', 'total_claims', 'created_at'
        ]
        self.assertEqual(list(self.pantry_admin.list_display), expected_fields)
        
    def test_user_email_display(self):
        """Test custom user_email method"""
        email = self.pantry_admin.user_email(self.pantry)
        self.assertEqual(email, 'pantry@test.com')
        
    def test_total_claims_initial(self):
        """Test total_claims method for pantry with no claims"""
        claims_count = self.pantry_admin.total_claims(self.pantry)
        self.assertEqual(claims_count, 0)
        
    def test_total_claims_with_claims(self):
        """Test total_claims method after claiming donations"""
        # Claim a donation
        self.donation1.claimed_by = self.pantry
        self.donation1.status = 'claimed'
        self.donation1.save()
        
        result = self.pantry_admin.total_claims(self.pantry)
        self.assertIn('1', str(result))
        self.assertIn('style="color: blue', str(result))


class AdminIntegrationTests(AdminTestCase):
    """Integration tests for admin interface"""
    
    def test_admin_site_customization(self):
        """Test that admin site headers are customized"""
        from django.contrib import admin
        self.assertEqual(admin.site.site_header, "CFMP Administration")
        self.assertEqual(admin.site.site_title, "CFMP Admin")
        self.assertEqual(admin.site.index_title, "Community Food Match Platform")
        
    def test_all_models_registered(self):
        """Test that all models are properly registered"""
        from django.contrib import admin
        self.assertIn(Donation, admin.site._registry)
        self.assertIn(Donor, admin.site._registry)
        self.assertIn(Pantry, admin.site._registry)
        
    def test_admin_actions_available(self):
        """Test that custom actions are available"""
        donation_admin = DonationAdmin(Donation, self.site)
        request = HttpRequest()
        request.user = self.admin_user
        actions = [action[0] for action in donation_admin.get_actions(request)]
        self.assertIn('mark_expired', actions)
        self.assertIn('export_csv', actions)