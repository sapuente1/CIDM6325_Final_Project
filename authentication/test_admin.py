"""
Tests for authentication admin interface functionality
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest

from donations.models import Donor, Pantry
from .admin import UserAdmin


class UserAdminTests(TestCase):
    """Tests for enhanced UserAdmin functionality"""
    
    def setUp(self):
        self.site = AdminSite()
        self.user_admin = UserAdmin(User, self.site)
        
        # Create test users with different roles
        self.admin_user = User.objects.create_user(
            'admin', 'admin@test.com', 'pass', 
            is_staff=True, is_superuser=True,
            first_name='Admin', last_name='User'
        )
        
        self.staff_user = User.objects.create_user(
            'staff', 'staff@test.com', 'pass',
            is_staff=True, is_superuser=False,
            first_name='Staff', last_name='Member'
        )
        
        self.donor_user = User.objects.create_user(
            'donor', 'donor@test.com', 'pass',
            first_name='John', last_name='Donor'
        )
        
        self.pantry_user = User.objects.create_user(
            'pantry', 'pantry@test.com', 'pass',
            first_name='Jane', last_name='Pantry'
        )
        
        self.regular_user = User.objects.create_user(
            'regular', 'regular@test.com', 'pass',
            first_name='Regular', last_name='User'
        )
        
        # Create associated profiles
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
        
    def test_list_display_fields(self):
        """Test that enhanced list display includes role and organization"""
        expected_fields = [
            'username', 'email', 'first_name', 'last_name',
            'user_role', 'organization_name', 'is_staff', 'is_active', 'date_joined'
        ]
        self.assertEqual(list(self.user_admin.list_display), expected_fields)
        
    def test_user_role_admin(self):
        """Test user_role display for admin user"""
        result = self.user_admin.user_role(self.admin_user)
        self.assertIn('👑 Admin', result)
        self.assertIn('style="color: red', result)
        
    def test_user_role_staff(self):
        """Test user_role display for staff user"""
        result = self.user_admin.user_role(self.staff_user)
        self.assertIn('👤 Staff', result)
        self.assertIn('style="color: orange', result)
        
    def test_user_role_donor(self):
        """Test user_role display for donor user"""
        result = self.user_admin.user_role(self.donor_user)
        self.assertIn('🏢 Donor', result)
        self.assertIn('style="color: green', result)
        
    def test_user_role_pantry(self):
        """Test user_role display for pantry user"""
        result = self.user_admin.user_role(self.pantry_user)
        self.assertIn('🏪 Pantry', result)
        self.assertIn('style="color: blue', result)
        
    def test_user_role_regular(self):
        """Test user_role display for regular user"""
        result = self.user_admin.user_role(self.regular_user)
        self.assertIn('👤 Regular User', result)
        self.assertIn('style="color: gray', result)
        
    def test_organization_name_donor(self):
        """Test organization_name for donor user"""
        org_name = self.user_admin.organization_name(self.donor_user)
        self.assertEqual(org_name, 'Test Food Corp')
        
    def test_organization_name_pantry(self):
        """Test organization_name for pantry user"""
        org_name = self.user_admin.organization_name(self.pantry_user)
        self.assertEqual(org_name, 'Community Pantry')
        
    def test_organization_name_no_profile(self):
        """Test organization_name for user without profile"""
        org_name = self.user_admin.organization_name(self.regular_user)
        self.assertEqual(org_name, '-')
        
    def test_queryset_optimization(self):
        """Test that queryset includes select_related for profiles"""
        request = HttpRequest()
        request.user = self.admin_user
        
        queryset = self.user_admin.get_queryset(request)
        # The queryset should have select_related applied
        # We can check the query to see if it includes joins
        query_str = str(queryset.query)
        self.assertIn('donor', query_str.lower())
        self.assertIn('pantry', query_str.lower())
        
    def test_search_fields_include_organizations(self):
        """Test that search fields include organization names"""
        search_fields = list(self.user_admin.search_fields)
        self.assertIn('donor__organization_name', search_fields)
        self.assertIn('pantry__organization_name', search_fields)
        
    def test_readonly_fields_include_custom(self):
        """Test that readonly fields include custom role fields"""
        readonly_fields = list(self.user_admin.readonly_fields)
        self.assertIn('user_role', readonly_fields)
        self.assertIn('organization_name', readonly_fields)