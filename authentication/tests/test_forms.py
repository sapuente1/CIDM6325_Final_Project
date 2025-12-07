from django.test import TestCase
from django.contrib.auth.models import User
from donations.models import Donor, Pantry
from authentication.forms import DonorRegistrationForm, PantryRegistrationForm


class AuthenticationFormTests(TestCase):
    """Test authentication forms"""
    
    def setUp(self):
        # Create existing user for duplicate testing
        self.existing_user = User.objects.create_user(
            username='existing',
            email='existing@example.com'
        )
        self.existing_donor = Donor.objects.create(
            user=self.existing_user,
            organization_name='Existing Org'
        )

    def test_donor_registration_form_valid(self):
        """Test valid donor registration form"""
        form_data = {
            'username': 'newdonor',
            'email': 'newdonor@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'organization_name': 'New Restaurant',
            'location': 'Test City',
            'contact_phone': '(555) 123-4567'
        }
        form = DonorRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_donor_registration_form_duplicate_email(self):
        """Test donor registration form with duplicate email"""
        form_data = {
            'username': 'newdonor',
            'email': 'existing@example.com',  # Duplicate
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'organization_name': 'New Restaurant',
            'location': 'Test City'
        }
        form = DonorRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_donor_registration_form_duplicate_organization(self):
        """Test donor registration form with duplicate organization name"""
        form_data = {
            'username': 'newdonor',
            'email': 'newdonor@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'organization_name': 'Existing Org',  # Duplicate
            'location': 'Test City'
        }
        form = DonorRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('organization_name', form.errors)

    def test_pantry_registration_form_valid(self):
        """Test valid pantry registration form"""
        form_data = {
            'username': 'newpantry',
            'email': 'newpantry@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'organization_name': 'New Food Bank',
            'location': 'Test City',
            'service_area': 'Test Area',
            'capacity': 100
        }
        form = PantryRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_pantry_registration_form_invalid_capacity(self):
        """Test pantry registration form with invalid capacity"""
        form_data = {
            'username': 'newpantry',
            'email': 'newpantry@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'organization_name': 'New Food Bank',
            'location': 'Test City',
            'service_area': 'Test Area',
            'capacity': 0  # Invalid
        }
        form = PantryRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('capacity', form.errors)

    def test_password_mismatch(self):
        """Test form validation with password mismatch"""
        form_data = {
            'username': 'newdonor',
            'email': 'newdonor@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'complexpass123',
            'password2': 'differentpass',  # Mismatch
            'organization_name': 'New Restaurant',
            'location': 'Test City'
        }
        form = DonorRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)