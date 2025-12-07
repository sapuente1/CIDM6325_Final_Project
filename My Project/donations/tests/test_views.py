# donations/tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from ..models import Donor, Pantry, Donation


class DonationViewsTestCase(TestCase):
    """Test cases for donation views"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.donor_user = User.objects.create_user(
            username='donor1', password='testpass123'
        )
        self.pantry_user = User.objects.create_user(
            username='pantry1', password='testpass123'
        )
        self.regular_user = User.objects.create_user(
            username='regular1', password='testpass123'
        )
        
        # Create donor and pantry profiles
        self.donor = Donor.objects.create(
            user=self.donor_user,
            organization_name='Test Restaurant'
        )
        self.pantry = Pantry.objects.create(
            user=self.pantry_user,
            organization_name='Test Food Bank',
            capacity=100
        )
        
        # Create test donation
        self.donation = Donation.objects.create(
            donor=self.donor,
            food_type='prepared',
            description='Test meal',
            quantity=10,
            unit='servings',
            location='Test City',
            expiry_date=timezone.now() + timedelta(days=1)
        )
        
        self.client = Client()

    def test_donation_list_view(self):
        """Test donation list view accessibility and content"""
        response = self.client.get(reverse('donations:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test meal')
        self.assertContains(response, 'Test Restaurant')
        self.assertIn('donations', response.context)
        self.assertIn('total_available', response.context)

    def test_donation_detail_view(self):
        """Test donation detail view shows correct information"""
        response = self.client.get(
            reverse('donations:detail', kwargs={'pk': self.donation.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.donation.description)
        self.assertContains(response, str(self.donation.quantity))
        self.assertEqual(response.context['donation'], self.donation)

    def test_donation_create_requires_donor_login(self):
        """Test that creating donations requires donor authentication"""
        response = self.client.get(reverse('donations:create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_donation_create_requires_donor_role(self):
        """Test that creating donations requires donor role"""
        self.client.login(username='regular1', password='testpass123')
        response = self.client.get(reverse('donations:create'))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_donation_create_by_donor(self):
        """Test donation creation by authenticated donor"""
        self.client.login(username='donor1', password='testpass123')
        
        response = self.client.get(reverse('donations:create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        
        # Test POST request
        future_date = timezone.now() + timedelta(days=2)
        response = self.client.post(reverse('donations:create'), {
            'food_type': 'bakery',
            'description': 'Fresh bread for donation',
            'quantity': 5,
            'unit': 'loaves',
            'location': 'Downtown',
            'expiry_date': future_date.strftime('%Y-%m-%dT%H:%M')
        })
        
        # Should redirect to detail page
        self.assertEqual(response.status_code, 302)
        
        # Verify donation was created
        new_donation = Donation.objects.filter(description='Fresh bread for donation').first()
        self.assertIsNotNone(new_donation)
        if new_donation:
            self.assertEqual(new_donation.donor, self.donor)

    def test_donation_update_owner_only(self):
        """Test that only donation owner can update"""
        # Test unauthorized access (pantry user)
        self.client.login(username='pantry1', password='testpass123')
        response = self.client.get(
            reverse('donations:update', kwargs={'pk': self.donation.pk})
        )
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test authorized access (owner)
        self.client.login(username='donor1', password='testpass123')
        response = self.client.get(
            reverse('donations:update', kwargs={'pk': self.donation.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_donation_delete_owner_only(self):
        """Test that only donation owner can delete"""
        self.client.login(username='donor1', password='testpass123')
        
        response = self.client.get(
            reverse('donations:delete', kwargs={'pk': self.donation.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        # Test actual deletion
        response = self.client.post(
            reverse('donations:delete', kwargs={'pk': self.donation.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        
        # Verify donation was deleted
        self.assertFalse(
            Donation.objects.filter(pk=self.donation.pk).exists()
        )

    def test_donation_claim_by_pantry(self):
        """Test donation claiming by pantry"""
        self.client.login(username='pantry1', password='testpass123')
        
        response = self.client.get(
            reverse('donations:claim', kwargs={'pk': self.donation.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect after claim
        
        # Verify donation was claimed
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.status, 'claimed')
        self.assertEqual(self.donation.claimed_by, self.pantry)

    def test_donation_claim_requires_pantry_role(self):
        """Test that claiming requires pantry role"""
        self.client.login(username='regular1', password='testpass123')
        response = self.client.get(
            reverse('donations:claim', kwargs={'pk': self.donation.pk})
        )
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_url_reversing(self):
        """Test that all named URLs reverse correctly"""
        urls_to_test = [
            ('donations:list', {}),
            ('donations:create', {}),
            ('donations:detail', {'pk': self.donation.pk}),
            ('donations:update', {'pk': self.donation.pk}),
            ('donations:delete', {'pk': self.donation.pk}),
            ('donations:claim', {'pk': self.donation.pk}),
            ('donations:my_donations', {}),
            ('donations:my_claims', {}),
        ]
        
        for url_name, kwargs in urls_to_test:
            url = reverse(url_name, kwargs=kwargs)
            self.assertTrue(url.startswith('/donations/'))

    def test_pagination_works(self):
        """Test pagination in list view"""
        # Create many donations to test pagination
        for i in range(25):
            Donation.objects.create(
                donor=self.donor,
                food_type='other',
                description=f'Test donation {i}',
                quantity=1,
                location='Test',
                expiry_date=timezone.now() + timedelta(days=1)
            )
        
        response = self.client.get(reverse('donations:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['donations']), 20)  # paginate_by=20

    def test_search_functionality(self):
        """Test search functionality in list view"""
        # Create donation with specific keywords
        Donation.objects.create(
            donor=self.donor,
            food_type='vegetables',
            description='Fresh organic vegetables',
            quantity=5,
            location='Organic Farm',
            expiry_date=timezone.now() + timedelta(days=1)
        )
        
        # Test search by description
        response = self.client.get(reverse('donations:list') + '?q=organic')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fresh organic vegetables')

    def test_my_donations_view(self):
        """Test my donations view for donors"""
        self.client.login(username='donor1', password='testpass123')
        response = self.client.get(reverse('donations:my_donations'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('donations', response.context)
        self.assertIn('total_donations', response.context)

    def test_my_claims_view(self):
        """Test my claims view for pantries"""
        # First claim a donation
        self.donation.claim(self.pantry)
        
        self.client.login(username='pantry1', password='testpass123')
        response = self.client.get(reverse('donations:my_claims'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('donations', response.context)
        self.assertIn('total_claims', response.context)

    def test_form_validation_expiry_date(self):
        """Test form validation for expiry date"""
        self.client.login(username='donor1', password='testpass123')
        
        # Try to create donation with past expiry date
        past_date = timezone.now() - timedelta(days=1)
        response = self.client.post(reverse('donations:create'), {
            'food_type': 'bakery',
            'description': 'Fresh bread for donation',
            'quantity': 5,
            'unit': 'loaves',
            'location': 'Downtown',
            'expiry_date': past_date.strftime('%Y-%m-%dT%H:%M')
        })
        
        # Should not redirect (form has errors)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'expiry_date', 'Expiry date must be in the future.')

    def test_form_validation_quantity(self):
        """Test form validation for quantity"""
        self.client.login(username='donor1', password='testpass123')
        
        # Try to create donation with zero quantity
        future_date = timezone.now() + timedelta(days=1)
        response = self.client.post(reverse('donations:create'), {
            'food_type': 'bakery',
            'description': 'Fresh bread for donation',
            'quantity': 0,
            'unit': 'loaves',
            'location': 'Downtown',
            'expiry_date': future_date.strftime('%Y-%m-%dT%H:%M')
        })
        
        # Should not redirect (form has errors)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'quantity', 'Quantity must be greater than zero.')


class PantryViewsTestCase(TestCase):
    """Test cases for pantry views"""
    
    def setUp(self):
        self.pantry_user = User.objects.create_user(
            username='pantry1', password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='other1', password='testpass123'
        )
        self.pantry = Pantry.objects.create(
            user=self.pantry_user,
            organization_name='Test Food Bank',
            capacity=100,
            address='123 Main St',
            phone='(555) 123-4567'
        )
        self.client = Client()

    def test_pantry_detail_view(self):
        """Test pantry detail view shows correct information"""
        response = self.client.get(
            reverse('pantries:detail', kwargs={'pk': self.pantry.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.pantry.organization_name)
        self.assertContains(response, '123 Main St')
        self.assertEqual(response.context['pantry'], self.pantry)

    def test_pantry_update_owner_only(self):
        """Test that only pantry owner can update profile"""
        # Test without login
        response = self.client.get(
            reverse('pantries:update', kwargs={'pk': self.pantry.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test with wrong user
        self.client.login(username='other1', password='testpass123')
        response = self.client.get(
            reverse('pantries:update', kwargs={'pk': self.pantry.pk})
        )
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test with correct owner
        self.client.login(username='pantry1', password='testpass123')
        response = self.client.get(
            reverse('pantries:update', kwargs={'pk': self.pantry.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        # Test update submission
        response = self.client.post(
            reverse('pantries:update', kwargs={'pk': self.pantry.pk}), {
                'organization_name': 'Updated Food Bank',
                'capacity': 150,
                'address': '456 Oak Ave',
                'phone': '(555) 987-6543'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect after update
        
        # Verify update
        self.pantry.refresh_from_db()
        self.assertEqual(self.pantry.organization_name, 'Updated Food Bank')
        self.assertEqual(self.pantry.capacity, 150)

    def test_pantry_form_validation(self):
        """Test pantry form validation"""
        self.client.login(username='pantry1', password='testpass123')
        
        # Test with invalid capacity
        response = self.client.post(
            reverse('pantries:update', kwargs={'pk': self.pantry.pk}), {
                'organization_name': 'Updated Food Bank',
                'capacity': 0,  # Invalid
                'address': '456 Oak Ave',
                'phone': '555-1234'  # Too short
            }
        )
        
        self.assertEqual(response.status_code, 200)  # Form has errors
        self.assertFormError(response, 'form', 'capacity', 'Capacity must be greater than zero.')