"""
Tests for monitoring app functionality
"""
import json
import time
from datetime import date, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.management import call_command
from django.test.utils import override_settings
from io import StringIO

from donations.models import Donor, Pantry, Donation
from monitoring.metrics import BusinessMetrics
from monitoring.middleware import MetricsMiddleware


class HealthCheckTests(TestCase):
    """Test health check endpoints"""
    
    def setUp(self):
        self.client = Client()
    
    def test_basic_health_check(self):
        """Test basic health check endpoint"""
        response = self.client.get(reverse('monitoring:health'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('version', data)
    
    def test_detailed_health_check(self):
        """Test detailed health check endpoint"""
        response = self.client.get(reverse('monitoring:health_detailed'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('timestamp', data)
        self.assertIn('checks', data)
        
        # Check that all expected checks are present
        checks = data['checks']
        self.assertIn('database', checks)
        self.assertIn('cache', checks)
        self.assertIn('disk_space', checks)
        
        # All checks should be healthy in test environment
        for check_name, check_result in checks.items():
            self.assertEqual(check_result['status'], 'healthy')
    
    def test_health_check_response_time(self):
        """Test that health checks respond quickly"""
        start_time = time.time()
        response = self.client.get(reverse('monitoring:health'))
        duration = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(duration, 1.0)  # Should respond within 1 second


class BusinessMetricsTests(TestCase):
    """Test business metrics tracking"""
    
    def setUp(self):
        # Create test users
        self.donor_user = User.objects.create_user(
            'donor', 'donor@test.com', 'pass',
            first_name='John', last_name='Donor'
        )
        self.pantry_user = User.objects.create_user(
            'pantry', 'pantry@test.com', 'pass',
            first_name='Jane', last_name='Pantry'
        )
        
        # Create profiles
        self.donor = Donor.objects.create(
            user=self.donor_user,
            organization_name='Test Donor Org',
            location='Downtown',
            contact_phone='555-1234'
        )
        
        self.pantry = Pantry.objects.create(
            user=self.pantry_user,
            organization_name='Test Pantry Org',
            location='Northside',
            service_area='North District',
            capacity=100,
            contact_phone='555-5678'
        )
        
        # Create test donation
        self.donation = Donation.objects.create(
            donor=self.donor,
            food_type='Produce',
            description='Test vegetables',
            quantity=50,
            location='Downtown Store',
            expiry_date=date.today() + timedelta(days=3),
            status='available'
        )
    
    @override_settings(LOGGING_CONFIG=None)  # Disable logging for tests
    def test_log_donation_created(self):
        """Test donation creation metrics logging"""
        # This test mainly verifies the method doesn't crash
        # In a real implementation, you'd capture log output
        try:
            BusinessMetrics.log_donation_created(self.donation, self.donor_user)
        except Exception as e:
            self.fail(f"log_donation_created raised an exception: {e}")
    
    @override_settings(LOGGING_CONFIG=None)
    def test_log_donation_claimed(self):
        """Test donation claim metrics logging"""
        # Claim the donation first
        self.donation.claim(self.pantry)
        
        try:
            BusinessMetrics.log_donation_claimed(self.donation, self.pantry_user)
        except Exception as e:
            self.fail(f"log_donation_claimed raised an exception: {e}")
    
    @override_settings(LOGGING_CONFIG=None)
    def test_log_donation_expired(self):
        """Test donation expiry metrics logging"""
        # Mark donation as expired
        self.donation.status = 'expired'
        self.donation.save()
        
        try:
            BusinessMetrics.log_donation_expired(self.donation)
        except Exception as e:
            self.fail(f"log_donation_expired raised an exception: {e}")
    
    @override_settings(LOGGING_CONFIG=None)
    def test_log_user_registration(self):
        """Test user registration metrics logging"""
        try:
            BusinessMetrics.log_user_registration(self.donor_user, 'donor')
            BusinessMetrics.log_user_registration(self.pantry_user, 'pantry')
        except Exception as e:
            self.fail(f"log_user_registration raised an exception: {e}")
    
    @override_settings(LOGGING_CONFIG=None)
    def test_log_user_login(self):
        """Test user login metrics logging"""
        try:
            BusinessMetrics.log_user_login(self.donor_user)
            BusinessMetrics.log_user_login(self.pantry_user)
        except Exception as e:
            self.fail(f"log_user_login raised an exception: {e}")


class MetricsMiddlewareTests(TestCase):
    """Test metrics middleware functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test', 'test@test.com', 'pass')
    
    def test_middleware_tracks_requests(self):
        """Test that middleware tracks request metrics"""
        # Make a request
        response = self.client.get(reverse('monitoring:health'))
        
        # Verify response is successful
        self.assertEqual(response.status_code, 200)
        
        # Middleware should not interfere with request processing
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
    
    def test_middleware_with_authenticated_user(self):
        """Test middleware behavior with authenticated users"""
        self.client.login(username='test', password='pass')
        
        response = self.client.get(reverse('monitoring:health'))
        self.assertEqual(response.status_code, 200)
    
    def test_get_user_type_method(self):
        """Test the _get_user_type method of MetricsMiddleware"""
        middleware = MetricsMiddleware(lambda x: None)
        
        # Test different user types
        admin_user = User.objects.create_user('admin', 'admin@test.com', 'pass', is_superuser=True)
        staff_user = User.objects.create_user('staff', 'staff@test.com', 'pass', is_staff=True)
        
        self.assertEqual(middleware._get_user_type(admin_user), 'admin')
        self.assertEqual(middleware._get_user_type(staff_user), 'staff')
        self.assertEqual(middleware._get_user_type(self.user), 'regular')
        
        # Test with an unauthenticated user (use AnonymousUser)
        from django.contrib.auth.models import AnonymousUser
        anonymous_user = AnonymousUser()
        self.assertIsNone(middleware._get_user_type(anonymous_user))


class AnalyzeMetricsCommandTests(TestCase):
    """Test the analyze_metrics management command"""
    
    def setUp(self):
        # Create test data
        donor_user = User.objects.create_user('donor', 'donor@test.com', 'pass')
        pantry_user = User.objects.create_user('pantry', 'pantry@test.com', 'pass')
        
        donor = Donor.objects.create(
            user=donor_user,
            organization_name='Test Donor',
            location='Downtown',
            contact_phone='555-1234'
        )
        
        pantry = Pantry.objects.create(
            user=pantry_user,
            organization_name='Test Pantry',
            location='Northside',
            service_area='North District',
            capacity=100,
            contact_phone='555-5678'
        )
        
        # Create donations with different statuses
        Donation.objects.create(
            donor=donor,
            food_type='Produce',
            description='Available donation',
            quantity=25,
            location='Store A',
            expiry_date=date.today() + timedelta(days=3),
            status='available'
        )
        
        claimed_donation = Donation.objects.create(
            donor=donor,
            food_type='Dairy',
            description='Claimed donation',
            quantity=15,
            location='Store B',
            expiry_date=date.today() + timedelta(days=2),
            status='claimed',
            claimed_by=pantry,
            claimed_at=timezone.now()
        )
        
        Donation.objects.create(
            donor=donor,
            food_type='Bread',
            description='Expired donation',
            quantity=10,
            location='Store C',
            expiry_date=date.today() - timedelta(days=1),
            status='expired'
        )
    
    def test_command_text_output(self):
        """Test command with text output format"""
        out = StringIO()
        call_command('analyze_metrics', '--days=30', '--format=text', stdout=out)
        
        output = out.getvalue()
        
        # Check that report contains expected sections
        self.assertIn('CFMP Metrics Report', output)
        self.assertIn('OVERALL STATISTICS', output)
        self.assertIn('KEY METRICS', output)
        self.assertIn('Total Donations:', output)
        self.assertIn('Claim Rate:', output)
        self.assertIn('Target Claim Rate:', output)
    
    def test_command_json_output(self):
        """Test command with JSON output format"""
        out = StringIO()
        call_command('analyze_metrics', '--days=30', '--format=json', stdout=out)
        
        output = out.getvalue()
        
        # Should be valid JSON
        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            self.fail("Command output is not valid JSON")
        
        # Check expected fields
        expected_fields = [
            'period_days', 'total_donations', 'claimed_donations',
            'expired_donations', 'claim_rate', 'target_claim_rate'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
        
        # Check data types
        self.assertIsInstance(data['total_donations'], int)
        self.assertIsInstance(data['claim_rate'], (int, float))
        self.assertIsInstance(data['meets_target'], bool)
    
    def test_command_with_custom_days(self):
        """Test command with custom day range"""
        out = StringIO()
        call_command('analyze_metrics', '--days=1', '--format=json', stdout=out)
        
        data = json.loads(out.getvalue())
        self.assertEqual(data['period_days'], 1)
    
    def test_command_calculates_metrics_correctly(self):
        """Test that command calculates metrics correctly"""
        out = StringIO()
        call_command('analyze_metrics', '--days=30', '--format=json', stdout=out)
        
        data = json.loads(out.getvalue())
        
        # We created 3 donations: 1 available, 1 claimed, 1 expired
        self.assertEqual(data['total_donations'], 3)
        self.assertEqual(data['available_donations'], 1)
        self.assertEqual(data['claimed_donations'], 1)
        self.assertEqual(data['expired_donations'], 1)
        
        # Claim rate should be 33.3% (1 out of 3)
        expected_claim_rate = round(1/3 * 100, 1)
        self.assertEqual(data['claim_rate'], expected_claim_rate)
        
        # Should not meet 80% target
        self.assertFalse(data['meets_target'])


class IntegrationTests(TestCase):
    """Integration tests for the complete monitoring system"""
    
    def test_end_to_end_monitoring_workflow(self):
        """Test complete monitoring workflow"""
        # 1. Test health checks work
        client = Client()
        health_response = client.get(reverse('monitoring:health'))
        self.assertEqual(health_response.status_code, 200)
        
        detailed_response = client.get(reverse('monitoring:health_detailed'))
        self.assertEqual(detailed_response.status_code, 200)
        
        # 2. Test metrics command works
        out = StringIO()
        call_command('analyze_metrics', '--days=7', '--format=json', stdout=out)
        
        # Should not crash and should return valid JSON
        data = json.loads(out.getvalue())
        self.assertIn('total_donations', data)
        
        # 3. Test middleware doesn't break request processing
        response = client.get(reverse('monitoring:health'))
        self.assertEqual(response.status_code, 200)
    
    def test_monitoring_with_real_data_flow(self):
        """Test monitoring with realistic data flow"""
        # Create users and profiles
        donor_user = User.objects.create_user('donor', 'donor@test.com', 'pass')
        donor = Donor.objects.create(
            user=donor_user,
            organization_name='Integration Test Donor',
            location='Test Location',
            contact_phone='555-9999'
        )
        
        # Create donation (this should trigger metrics if integrated)
        donation = Donation.objects.create(
            donor=donor,
            food_type='Test Food',
            description='Integration test donation',
            quantity=100,
            location='Test Store',
            expiry_date=date.today() + timedelta(days=5),
            status='available'
        )
        
        # Test that metrics command includes this donation
        out = StringIO()
        call_command('analyze_metrics', '--days=1', '--format=json', stdout=out)
        
        data = json.loads(out.getvalue())
        self.assertGreaterEqual(data['total_donations'], 1)
