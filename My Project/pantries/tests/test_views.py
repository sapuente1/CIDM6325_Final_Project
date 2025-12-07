# pantries/tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from donations.models import Pantry


class PantryViewsTestCase(TestCase):
    """Test cases for pantry views"""
    
    def setUp(self):
        """Set up test data"""
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
            location='Test City',
            contact_phone='(555) 123-4567'
        )
        self.client = Client()

    def test_pantry_detail_view_public_access(self):
        """Test pantry detail view is accessible to public"""
        response = self.client.get(
            reverse('pantries:detail', kwargs={'pk': self.pantry.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.pantry.organization_name)
        self.assertContains(response, 'Test City')
        self.assertEqual(response.context['pantry'], self.pantry)
        self.assertFalse(response.context['is_owner'])  # Not logged in

    def test_pantry_detail_view_as_owner(self):
        """Test pantry detail view when viewed by owner"""
        self.client.login(username='pantry1', password='testpass123')
        response = self.client.get(
            reverse('pantries:detail', kwargs={'pk': self.pantry.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_owner'])  # Logged in as owner

    def test_pantry_update_requires_login(self):
        """Test that updating pantry requires login"""
        response = self.client.get(
            reverse('pantries:update', kwargs={'pk': self.pantry.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_pantry_update_requires_ownership(self):
        """Test that updating pantry requires ownership"""
        # Test with different user
        self.client.login(username='other1', password='testpass123')
        response = self.client.get(
            reverse('pantries:update', kwargs={'pk': self.pantry.pk})
        )
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_pantry_update_by_owner(self):
        """Test successful pantry update by owner"""
        self.client.login(username='pantry1', password='testpass123')
        
        # GET request should show form
        response = self.client.get(
            reverse('pantries:update', kwargs={'pk': self.pantry.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        
        # POST request should update pantry
        response = self.client.post(
            reverse('pantries:update', kwargs={'pk': self.pantry.pk}), {
                'organization_name': 'Updated Food Bank',
                'capacity': 150,
                'location': 'Updated City',
                'service_area': 'Updated Area',
                'contact_phone': '(555) 987-6543'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect after update
        
        # Verify update worked
        self.pantry.refresh_from_db()
        self.assertEqual(self.pantry.organization_name, 'Updated Food Bank')
        self.assertEqual(self.pantry.capacity, 150)
        self.assertEqual(self.pantry.location, 'Updated City')
        self.assertEqual(self.pantry.contact_phone, '(555) 987-6543')

    def test_pantry_form_validation_capacity(self):
        """Test pantry form validation for capacity"""
        self.client.login(username='pantry1', password='testpass123')
        
        # Test with invalid capacity (zero)
        response = self.client.post(
            reverse('pantries:update', kwargs={'pk': self.pantry.pk}), {
                'organization_name': 'Updated Food Bank',
                'capacity': 0,  # Invalid
                'location': 'Updated City',
                'contact_phone': '(555) 987-6543'
            }
        )
        
        self.assertEqual(response.status_code, 200)  # Form has errors
        self.assertFormError(response, 'form', 'capacity', 'Capacity must be greater than zero.')

    def test_pantry_form_validation_phone(self):
        """Test pantry form validation for phone number"""
        self.client.login(username='pantry1', password='testpass123')
        
        # Test with invalid phone (too short)
        response = self.client.post(
            reverse('pantries:update', kwargs={'pk': self.pantry.pk}), {
                'organization_name': 'Updated Food Bank',
                'capacity': 150,
                'location': 'Updated City',
                'contact_phone': '123'  # Too short
            }
        )
        
        self.assertEqual(response.status_code, 200)  # Form has errors
        self.assertFormError(response, 'form', 'contact_phone', 'Please enter a valid phone number with at least 10 digits.')

    def test_pantry_context_data(self):
        """Test that pantry detail view provides correct context"""
        response = self.client.get(
            reverse('pantries:detail', kwargs={'pk': self.pantry.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        # Check context variables
        context = response.context
        self.assertIn('pantry', context)
        self.assertIn('claimed_donations', context)
        self.assertIn('total_claims', context)
        self.assertIn('recent_claims', context)
        self.assertIn('is_owner', context)
        
        # Verify values
        self.assertEqual(context['pantry'], self.pantry)
        self.assertEqual(context['total_claims'], self.pantry.total_claims)

    def test_url_reversing(self):
        """Test that pantry URLs reverse correctly"""
        urls_to_test = [
            ('pantries:detail', {'pk': self.pantry.pk}),
            ('pantries:update', {'pk': self.pantry.pk}),
        ]
        
        for url_name, kwargs in urls_to_test:
            url = reverse(url_name, kwargs=kwargs)
            self.assertTrue(url.startswith('/pantries/'))

    def test_pantry_detail_404(self):
        """Test that accessing non-existent pantry returns 404"""
        response = self.client.get(
            reverse('pantries:detail', kwargs={'pk': 99999})
        )
        self.assertEqual(response.status_code, 404)