# BRIEF-003: Authentication and Authorization Implementation

**Date**: 2025-12-07  
**Related ADR**: ADR-003  
**PRD Reference**: Section 6 (FR-005), Section 4 (Authentication), Section 7 (Security)  
**Dependencies**: ADR-001 (data models), ADR-002 (views architecture)

## Goal

Implement a complete authentication and authorization system for the CFMP platform using Django's built-in authentication with profile-based role separation for donors, pantries, and admin users.

## Scope (Single PR)

### Files to Create/Modify
- `authentication/` - New Django app for auth functionality
- `authentication/views.py` - Login, logout, registration views
- `authentication/forms.py` - Registration and profile forms
- `authentication/urls.py` - Authentication URL patterns
- `authentication/context_processors.py` - Role-based template context
- `cfmp/settings.py` - Add authentication app and context processor
- `cfmp/urls.py` - Include authentication URLs
- `authentication/tests/test_views.py` - Authentication view testing
- `authentication/tests/test_forms.py` - Form validation testing
- `donations/views.py` - Update existing mixins (already implemented)

### Non-Goals (Future PRs)
- Template implementations (HTML/CSS)
- Social authentication (django-allauth)
- Password reset via email
- Account verification system
- Multi-role user support
- Advanced permission granularity

## Standards

### Project Norms
- **Language**: Python 3.12 + Django 5.2
- **Style**: PEP 8, docstrings on public methods, type hints on new code
- **Commits**: Conventional style (feat/fix/docs/refactor/test/chore)
- **Testing**: Django TestCase (no pytest), use `Client` for view testing

### Django Norms
- **Authentication**: Use Django's built-in auth system with profile extensions
- **Views**: Generic CBVs where appropriate, FBVs for complex auth logic
- **Forms**: ModelForm for profile registration, built-in forms where possible
- **Security**: LoginRequiredMixin, UserPassesTestMixin for access control
- **URLs**: Named patterns, proper reversing, logical URL structure

## Detailed Requirements

### 1. Authentication App Structure

#### Django App Creation
```bash
cd "My Project"
python manage.py startapp authentication
```

#### App Configuration (authentication/apps.py)
```python
from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'
    
    def ready(self):
        # Import signal handlers if needed
        pass
```

### 2. Registration Forms and Views

#### Registration Forms (authentication/forms.py)
```python
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from donations.models import Donor, Pantry


class BaseUserRegistrationForm(UserCreationForm):
    """Base registration form with common fields"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class DonorRegistrationForm(BaseUserRegistrationForm):
    """Registration form for food donors"""
    organization_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Restaurant, Grocery Store, etc.'
        }),
        help_text="Name of your organization or business"
    )
    contact_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(555) 123-4567'
        })
    )
    location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City, State'
        }),
        help_text="Your location for pickup coordination"
    )
    
    def clean_organization_name(self):
        org_name = self.cleaned_data.get('organization_name')
        if Donor.objects.filter(organization_name=org_name).exists():
            raise forms.ValidationError("A donor with this organization name already exists.")
        return org_name


class PantryRegistrationForm(BaseUserRegistrationForm):
    """Registration form for food pantries"""
    organization_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Community Food Bank, etc.'
        }),
        help_text="Name of your food pantry or organization"
    )
    contact_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(555) 123-4567'
        })
    )
    location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City, State'
        }),
        help_text="Your service location"
    )
    service_area = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Geographic area you serve'
        })
    )
    capacity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '100'
        }),
        help_text="Approximate number of people served weekly"
    )
    
    def clean_organization_name(self):
        org_name = self.cleaned_data.get('organization_name')
        if Pantry.objects.filter(organization_name=org_name).exists():
            raise forms.ValidationError("A pantry with this organization name already exists.")
        return org_name
```

#### Authentication Views (authentication/views.py)
```python
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.models import User
from donations.models import Donor, Pantry
from .forms import DonorRegistrationForm, PantryRegistrationForm


class CustomLoginView(DjangoLoginView):
    """Custom login view with role-based redirects"""
    template_name = 'authentication/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect based on user role"""
        user = self.request.user
        if hasattr(user, 'donor'):
            return reverse_lazy('donations:my_donations')
        elif hasattr(user, 'pantry'):
            return reverse_lazy('donations:my_claims')
        elif user.is_staff:
            return reverse_lazy('admin:index')
        else:
            return reverse_lazy('donations:list')
    
    def form_valid(self, form):
        """Add welcome message on successful login"""
        response = super().form_valid(form)
        user = self.request.user
        if hasattr(user, 'donor'):
            messages.success(self.request, f'Welcome back, {user.donor.organization_name}!')
        elif hasattr(user, 'pantry'):
            messages.success(self.request, f'Welcome back, {user.pantry.organization_name}!')
        else:
            messages.success(self.request, f'Welcome back, {user.get_full_name() or user.username}!')
        return response


class CustomLogoutView(DjangoLogoutView):
    """Custom logout view with confirmation message"""
    next_page = 'donations:list'
    
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'You have been successfully logged out.')
        return super().dispatch(request, *args, **kwargs)


class RegistrationChoiceView(TemplateView):
    """Landing page for choosing registration type"""
    template_name = 'authentication/register_choice.html'


class DonorRegistrationView(CreateView):
    """Registration view for food donors"""
    model = Donor
    form_class = DonorRegistrationForm
    template_name = 'authentication/donor_register.html'
    success_url = reverse_lazy('donations:my_donations')
    
    def form_valid(self, form):
        """Create User and Donor profile, then auto-login"""
        # Create the User instance
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            password=form.cleaned_data['password1']
        )
        
        # Create the Donor profile
        donor = Donor.objects.create(
            user=user,
            organization_name=form.cleaned_data['organization_name'],
            contact_phone=form.cleaned_data['contact_phone'],
            location=form.cleaned_data['location']
        )
        
        # Auto-login the user
        login(self.request, user)
        messages.success(
            self.request, 
            f'Welcome to CFMP, {donor.organization_name}! Your donor account has been created.'
        )
        
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        """Add error message for form validation failures"""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class PantryRegistrationView(CreateView):
    """Registration view for food pantries"""
    model = Pantry
    form_class = PantryRegistrationForm
    template_name = 'authentication/pantry_register.html'
    success_url = reverse_lazy('donations:my_claims')
    
    def form_valid(self, form):
        """Create User and Pantry profile, then auto-login"""
        # Create the User instance
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            password=form.cleaned_data['password1']
        )
        
        # Create the Pantry profile
        pantry = Pantry.objects.create(
            user=user,
            organization_name=form.cleaned_data['organization_name'],
            contact_phone=form.cleaned_data['contact_phone'],
            location=form.cleaned_data['location'],
            service_area=form.cleaned_data['service_area'],
            capacity=form.cleaned_data['capacity']
        )
        
        # Auto-login the user
        login(self.request, user)
        messages.success(
            self.request, 
            f'Welcome to CFMP, {pantry.organization_name}! Your pantry account has been created.'
        )
        
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        """Add error message for form validation failures"""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ProfileRedirectView(TemplateView):
    """Redirect authenticated users to appropriate profile view"""
    
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth:login')
        
        if hasattr(request.user, 'donor'):
            return redirect('donations:my_donations')
        elif hasattr(request.user, 'pantry'):
            return redirect('donations:my_claims')
        elif request.user.is_staff:
            return redirect('admin:index')
        else:
            messages.warning(request, 'Please contact an administrator to set up your account.')
            return redirect('donations:list')
```

### 3. Template Context Processor

#### Context Processor (authentication/context_processors.py)
```python
def user_role_context(request):
    """Add user role information to all template contexts"""
    if not request.user.is_authenticated:
        return {
            'is_donor': False,
            'is_pantry': False,
            'is_admin': False,
            'user_role': None,
            'user_organization': None,
        }
    
    user = request.user
    context = {
        'is_donor': hasattr(user, 'donor'),
        'is_pantry': hasattr(user, 'pantry'),
        'is_admin': user.is_staff,
    }
    
    # Add role-specific information
    if context['is_donor']:
        context['user_role'] = 'donor'
        context['user_organization'] = user.donor.organization_name
    elif context['is_pantry']:
        context['user_role'] = 'pantry'
        context['user_organization'] = user.pantry.organization_name
    elif context['is_admin']:
        context['user_role'] = 'admin'
        context['user_organization'] = 'Administrator'
    else:
        context['user_role'] = 'unknown'
        context['user_organization'] = user.get_full_name() or user.username
    
    return context
```

### 4. URL Configuration

#### Authentication URLs (authentication/urls.py)
```python
from django.urls import path
from . import views

app_name = 'auth'
urlpatterns = [
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Registration
    path('register/', views.RegistrationChoiceView.as_view(), name='register_choice'),
    path('register/donor/', views.DonorRegistrationView.as_view(), name='donor_register'),
    path('register/pantry/', views.PantryRegistrationView.as_view(), name='pantry_register'),
    
    # Profile
    path('profile/', views.ProfileRedirectView.as_view(), name='profile'),
]
```

#### Update Main URLs (cfmp/urls.py)
```python
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('donations/', include('donations.urls')),
    path('pantries/', include('pantries.urls')),
    path('', RedirectView.as_view(pattern_name='donations:list'), name='home'),
]
```

### 5. Settings Configuration

#### Update Settings (cfmp/settings.py)
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'donations',  # Our CFMP donations app
    'pantries',   # Our CFMP pantries app
    'authentication',  # Our authentication app
]

# Template context processors
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'authentication.context_processors.user_role_context',  # Add our context processor
            ],
        },
    },
]

# Authentication settings
LOGIN_URL = 'auth:login'
LOGIN_REDIRECT_URL = 'auth:profile'
LOGOUT_REDIRECT_URL = 'donations:list'

# Session settings
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
```

### 6. Enhanced Authorization Mixins

#### Update Existing Mixins (donations/views.py - enhancement)
```python
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect

class DonorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Ensure user is authenticated and is a donor"""
    
    def test_func(self):
        return hasattr(self.request.user, 'donor')
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.info(self.request, "Please log in to access this page.")
            return redirect('auth:login')
        else:
            messages.error(self.request, "You must be registered as a donor to access this page.")
            return redirect('auth:donor_register')


class PantryRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Ensure user is authenticated and is a pantry"""
    
    def test_func(self):
        return hasattr(self.request.user, 'pantry')
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.info(self.request, "Please log in to access this page.")
            return redirect('auth:login')
        else:
            messages.error(self.request, "You must be registered as a food pantry to access this page.")
            return redirect('auth:pantry_register')


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Ensure user is authenticated and is an admin"""
    
    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.info(self.request, "Please log in to access this page.")
            return redirect('auth:login')
        else:
            messages.error(self.request, "Administrator access required.")
            return redirect('donations:list')
```

### 7. Comprehensive Testing Strategy

#### Authentication View Tests (authentication/tests/test_views.py)
```python
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
```

#### Form Tests (authentication/tests/test_forms.py)
```python
from django.test import TestCase
from django.contrib.auth.models import User
from donations.models import Donor, Pantry
from ..forms import DonorRegistrationForm, PantryRegistrationForm


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
```

### 8. Integration Requirements

#### Template Context Variables
All templates will have access to:
- `is_donor` - Boolean indicating if user is a donor
- `is_pantry` - Boolean indicating if user is a pantry
- `is_admin` - Boolean indicating if user is admin
- `user_role` - String indicating user role ('donor', 'pantry', 'admin', 'unknown')
- `user_organization` - Organization name for role-based users

#### Template Naming Convention
- `authentication/login.html` - Login form
- `authentication/register_choice.html` - Registration type selection
- `authentication/donor_register.html` - Donor registration form
- `authentication/pantry_register.html` - Pantry registration form

#### Security Headers
- CSRF protection enabled (Django default)
- Session cookies configured for security
- Login required for sensitive operations
- Role-based access control enforced

## Acceptance Criteria

### Functional Requirements
- [ ] User registration flow works for both donors and pantries
- [ ] Login/logout functionality works correctly
- [ ] Role-based redirects work after authentication
- [ ] Authorization mixins prevent unauthorized access
- [ ] Form validation prevents duplicate accounts
- [ ] Auto-login after successful registration
- [ ] Context processor provides role information to templates

### Technical Requirements
- [ ] All authentication views use Django CBVs where appropriate
- [ ] Forms extend Django's built-in forms properly
- [ ] Authorization mixins provide clear error messages
- [ ] Settings configured for authentication
- [ ] URL routing follows RESTful patterns
- [ ] Session security configured appropriately

### Testing Requirements
- [ ] Minimum 20 authentication tests covering all flows
- [ ] Registration form validation testing
- [ ] Authorization mixin testing
- [ ] Login/logout flow testing
- [ ] Duplicate prevention testing
- [ ] All tests pass with >90% code coverage

### Code Quality Requirements
- [ ] PEP 8 compliance (use ruff for linting)
- [ ] Docstrings on all view classes and forms
- [ ] Type hints on new methods
- [ ] No security vulnerabilities (proper CSRF, validation)
- [ ] Clean separation of authentication and authorization logic

## Prompts for Copilot

### Implementation Guidance
1. **"Generate Django authentication app with role-based registration following the exact patterns in this brief"**
2. **"Create custom login/logout views with role-based redirects and user messaging"**
3. **"Implement registration forms with proper validation for donors and pantries"**
4. **"Build authorization mixins that provide clear error messages and proper redirects"**
5. **"Write comprehensive Django TestCase tests for all authentication flows"**

### Code Review Focus
- **"Review authentication forms for proper validation and security"**
- **"Check authorization mixins prevent cross-role access effectively"**
- **"Verify registration flow creates proper User + Profile relationships"**
- **"Validate context processor provides correct role information"**
- **"Ensure no sensitive data is exposed in templates or forms"**

## Success Criteria

**Implementation Complete When**:
1. All registration and login flows work correctly
2. Role-based authorization prevents unauthorized access
3. Forms validate input and prevent duplicate accounts
4. Context processor provides role information to templates
5. Authorization mixins work with existing views
6. Minimum 20 tests pass covering all functionality
7. Security headers and settings properly configured

**Deliverables**:
- Working authentication system with role separation
- Complete registration flow for donors and pantries
- Authorization mixins integrated with existing views
- Comprehensive test coverage
- Security-focused configuration

## Risk Assessment & Rollback

**Risk Level**: Medium
- **Security Risk**: Authentication vulnerabilities if forms/views not properly secured
- **Business Risk**: Users unable to register or access features

**Rollback Plan**:
1. Remove authentication app from INSTALLED_APPS
2. Revert to anonymous access for all views
3. Use git revert for specific authentication commits

**Mitigation**:
- Extensive testing of all authentication flows
- Security review of form validation and access controls
- Manual testing of registration and login processes
- Code review focused on authorization logic