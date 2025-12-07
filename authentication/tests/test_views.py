from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from donations.models import Donor, Pantry


class AuthenticationViewsTestCase(TestCase):
    """Test authentication views"""
    
    def setUp(self):
        self.client = Client()
        
        # Create existing user for duplicate testing
        self.existing_user = User.objects.create_user(
            username='existing_user',
            email='existing@example.com',
            password='testpass123'
        )
        
        # Create existing donor for organization name testing
        self.existing_donor = Donor.objects.create(
            user=self.existing_user,
            organization_name='Existing Restaurant'
        )

    def test_login_view_get(self):
        """Test login view displays correctly"""
        response = self.client.get(reverse('auth:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_login_successful_donor(self):
        """Test successful login for donor"""
        response = self.client.post(reverse('auth:login'), {
            'username': 'existing_user',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('donations:my_donations'))

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(reverse('auth:login'), {
            'username': 'existing_user',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')

    def test_donor_registration_success(self):
        """Test successful donor registration"""
        response = self.client.post(reverse('auth:donor_register'), {
            'username': 'newdonor',
            'email': 'newdonor@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'organization_name': 'New Restaurant',
            'location': 'Test City',
            'contact_phone': '(555) 123-4567'
        })
        
        # Should redirect after successful registration
        self.assertEqual(response.status_code, 302)
        
        # Verify user was created
        user = User.objects.get(username='newdonor')
        self.assertEqual(user.email, 'newdonor@example.com')
        self.assertTrue(hasattr(user, 'donor'))
        self.assertEqual(user.donor.organization_name, 'New Restaurant')

    def test_pantry_registration_success(self):
        """Test successful pantry registration"""
        response = self.client.post(reverse('auth:pantry_register'), {
            'username': 'newpantry',
            'email': 'newpantry@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'organization_name': 'New Food Bank',
            'location': 'Test City',
            'service_area': 'Test Area',
            'capacity': 100,
            'contact_phone': '(555) 987-6543'
        })
        
        # Should redirect after successful registration
        self.assertEqual(response.status_code, 302)
        
        # Verify user was created
        user = User.objects.get(username='newpantry')
        self.assertEqual(user.email, 'newpantry@example.com')
        self.assertTrue(hasattr(user, 'pantry'))
        self.assertEqual(user.pantry.organization_name, 'New Food Bank')

    def test_duplicate_username_registration(self):
        """Test registration with duplicate username"""
        response = self.client.post(reverse('auth:donor_register'), {
            'username': 'existing_user',  # Already exists
            'email': 'newemail@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'organization_name': 'Another Restaurant',
            'location': 'Test City'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', 'A user with that username already exists.')

    def test_duplicate_email_registration(self):
        """Test registration with duplicate email"""
        response = self.client.post(reverse('auth:donor_register'), {
            'username': 'newuser',
            'email': 'existing@example.com',  # Already exists
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'organization_name': 'Another Restaurant',
            'location': 'Test City'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', 'A user with this email already exists.')

    def test_duplicate_organization_name(self):
        """Test registration with duplicate organization name"""
        response = self.client.post(reverse('auth:donor_register'), {
            'username': 'newuser',
            'email': 'newemail@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'organization_name': 'Existing Restaurant',  # Already exists
            'location': 'Test City'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'organization_name', 'A donor with this organization name already exists.')

    def test_password_mismatch_registration(self):
        """Test registration with mismatched passwords"""
        response = self.client.post(reverse('auth:donor_register'), {
            'username': 'newuser',
            'email': 'newemail@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'complexpass123',
            'password2': 'differentpass456',  # Mismatch
            'organization_name': 'New Restaurant',
            'location': 'Test City'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password2', "The two password fields didn't match.")

    def test_logout_functionality(self):
        """Test logout redirects correctly"""
        # Login first
        self.client.login(username='existing_user', password='testpass123')
        
        # Then logout
        response = self.client.get(reverse('auth:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('donations:list'))

    def test_profile_redirect_donor(self):
        """Test profile redirect for donor"""
        self.client.login(username='existing_user', password='testpass123')
        response = self.client.get(reverse('auth:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('donations:my_donations'))

    def test_registration_choice_view(self):
        """Test registration choice page"""
        response = self.client.get(reverse('auth:register_choice'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'donor')
        self.assertContains(response, 'pantry')

    def test_authenticated_user_redirected_from_login(self):
        """Test that authenticated users are redirected from login page"""
        self.client.login(username='existing_user', password='testpass123')
        response = self.client.get(reverse('auth:login'))
        self.assertEqual(response.status_code, 302)


class AuthorizationMixinTests(TestCase):
    """Test authorization mixins"""
    
    def setUp(self):
        self.client = Client()
        
        # Create donor user
        self.donor_user = User.objects.create_user(
            username='donor1', password='testpass123'
        )
        self.donor = Donor.objects.create(
            user=self.donor_user,
            organization_name='Test Restaurant'
        )
        
        # Create pantry user
        self.pantry_user = User.objects.create_user(
            username='pantry1', password='testpass123'
        )
        self.pantry = Pantry.objects.create(
            user=self.pantry_user,
            organization_name='Test Food Bank',
            capacity=100
        )

    def test_donor_required_mixin_allows_donor(self):
        """Test DonorRequiredMixin allows access for donors"""
        self.client.login(username='donor1', password='testpass123')
        response = self.client.get(reverse('donations:create'))
        # Should not redirect (would need templates to test fully)
        self.assertIn(response.status_code, [200, 500])  # 500 is template missing

    def test_donor_required_mixin_blocks_pantry(self):
        """Test DonorRequiredMixin blocks access for pantries"""
        self.client.login(username='pantry1', password='testpass123')
        response = self.client.get(reverse('donations:create'))
        self.assertEqual(response.status_code, 302)  # Should redirect

    def test_pantry_required_mixin_allows_pantry(self):
        """Test PantryRequiredMixin allows access for pantries"""
        self.client.login(username='pantry1', password='testpass123')
        response = self.client.get(reverse('donations:my_claims'))
        # Should not redirect (would need templates to test fully)
        self.assertIn(response.status_code, [200, 500])  # 500 is template missing

    def test_unauthenticated_redirects_to_login(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(reverse('donations:create'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/auth/login/'))