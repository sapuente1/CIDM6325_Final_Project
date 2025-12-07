# BRIEF-002: Django Views & URL Architecture Implementation

**Date**: 2025-12-07  
**Related ADR**: ADR-002  
**PRD Reference**: Section 6 (FR-001, FR-006), Section 4  
**Dependencies**: ADR-001 data models (completed)

## Goal

Implement a complete Django views architecture using Class-Based Views (CBVs) for all CRUD operations on the CFMP platform, with proper URL routing, authorization mixins, and template integration.

## Scope (Single PR)

### Files to Create/Modify
- `donations/views.py` - Complete CBV implementation
- `donations/urls.py` - Named URL patterns  
- `donations/forms.py` - ModelForms for validation
- `pantries/views.py` - Pantry profile management views
- `pantries/urls.py` - Pantry URL patterns
- `cfmp/urls.py` - Root URL configuration
- `donations/tests/test_views.py` - Comprehensive view testing
- `pantries/tests/test_views.py` - Pantry view testing

### Non-Goals (Future PRs)
- Template implementations (HTML/CSS)
- JavaScript functionality
- REST API endpoints
- Advanced search/filtering UI
- Email notifications

## Standards

### Project Norms
- **Language**: Python 3.12 + Django 5.2
- **Style**: PEP 8, docstrings on public methods, type hints on new code
- **Commits**: Conventional style (feat/fix/docs/refactor/test/chore)
- **Testing**: Django TestCase (no pytest), use `Client` for view testing

### Django Norms
- **Views**: Generic CBVs for all CRUD operations (ListView, CreateView, DetailView, UpdateView, DeleteView)
- **Forms**: ModelForm for all model operations with proper validation
- **URLs**: Named patterns with app namespaces, proper reversing
- **Authorization**: Custom mixins for role-based access control
- **Templates**: Consistent naming convention (`app/model_action.html`)

## Detailed Requirements

### 1. Class-Based Views Architecture

#### Donation Views (donations/views.py)
```python
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .models import Donation
from .forms import DonationForm

class DonorRequiredMixin(UserPassesTestMixin):
    """Ensure user is a donor"""
    def test_func(self):
        return hasattr(self.request.user, 'donor')
    
    def handle_no_permission(self):
        # Redirect to donor registration or show appropriate message
        pass

class DonationListView(ListView):
    """List all available donations with pagination and filtering"""
    model = Donation
    template_name = 'donations/list.html'
    context_object_name = 'donations'
    paginate_by = 20
    
    def get_queryset(self):
        # Return available donations with optimized queries
        return Donation.objects.available().select_related('donor__user').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_available'] = Donation.objects.available().count()
        context['urgent_count'] = Donation.objects.urgent().count()
        return context

class DonationCreateView(LoginRequiredMixin, DonorRequiredMixin, CreateView):
    """Create new donation (donor only)"""
    model = Donation
    form_class = DonationForm
    template_name = 'donations/create.html'
    success_url = reverse_lazy('donations:list')
    
    def form_valid(self, form):
        form.instance.donor = self.request.user.donor
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('donations:detail', kwargs={'pk': self.object.pk})

class DonationDetailView(DetailView):
    """View donation details (public access)"""
    model = Donation
    template_name = 'donations/detail.html'
    context_object_name = 'donation'
    
    def get_queryset(self):
        return Donation.objects.select_related('donor__user', 'claimed_by__user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_claim'] = (
            hasattr(self.request.user, 'pantry') and 
            self.object.status == 'available'
        )
        context['is_owner'] = (
            hasattr(self.request.user, 'donor') and 
            self.object.donor == self.request.user.donor
        )
        return context

class DonationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update donation (owner only)"""
    model = Donation
    form_class = DonationForm
    template_name = 'donations/update.html'
    
    def test_func(self):
        donation = self.get_object()
        return (hasattr(self.request.user, 'donor') and 
                donation.donor == self.request.user.donor and
                donation.status == 'available')
    
    def get_success_url(self):
        return reverse_lazy('donations:detail', kwargs={'pk': self.object.pk})

class DonationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete donation (owner only)"""
    model = Donation
    template_name = 'donations/delete.html'
    success_url = reverse_lazy('donations:list')
    
    def test_func(self):
        donation = self.get_object()
        return (hasattr(self.request.user, 'donor') and 
                donation.donor == self.request.user.donor and
                donation.status == 'available')

# Additional views for business logic
class DonationClaimView(LoginRequiredMixin, UserPassesTestMixin, RedirectView):
    """Claim donation (pantry only)"""
    def test_func(self):
        return hasattr(self.request.user, 'pantry')
    
    def get_redirect_url(self, *args, **kwargs):
        donation = get_object_or_404(Donation, pk=kwargs['pk'])
        if donation.claim(self.request.user.pantry):
            messages.success(self.request, 'Donation claimed successfully!')
        else:
            messages.error(self.request, 'Unable to claim this donation.')
        return reverse('donations:detail', kwargs={'pk': donation.pk})
```

#### Pantry Views (pantries/views.py)
```python
class PantryRequiredMixin(UserPassesTestMixin):
    """Ensure user is a pantry"""
    def test_func(self):
        return hasattr(self.request.user, 'pantry')

class PantryDetailView(DetailView):
    """View pantry profile (public)"""
    model = Pantry
    template_name = 'pantries/detail.html'
    context_object_name = 'pantry'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['claimed_donations'] = self.object.claimed_donations.all()[:5]
        context['total_claims'] = self.object.total_claims
        return context

class PantryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update pantry profile (owner only)"""
    model = Pantry
    form_class = PantryForm
    template_name = 'pantries/update.html'
    
    def test_func(self):
        pantry = self.get_object()
        return (hasattr(self.request.user, 'pantry') and 
                pantry == self.request.user.pantry)
    
    def get_success_url(self):
        return reverse_lazy('pantries:detail', kwargs={'pk': self.object.pk})
```

### 2. URL Configuration

#### Donations URLs (donations/urls.py)
```python
from django.urls import path
from . import views

app_name = 'donations'
urlpatterns = [
    path('', views.DonationListView.as_view(), name='list'),
    path('create/', views.DonationCreateView.as_view(), name='create'),
    path('<int:pk>/', views.DonationDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.DonationUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.DonationDeleteView.as_view(), name='delete'),
    path('<int:pk>/claim/', views.DonationClaimView.as_view(), name='claim'),
]
```

#### Pantries URLs (pantries/urls.py)
```python
from django.urls import path
from . import views

app_name = 'pantries'
urlpatterns = [
    path('<int:pk>/', views.PantryDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.PantryUpdateView.as_view(), name='update'),
]
```

#### Root URLs (cfmp/urls.py)
```python
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('donations/', include('donations.urls')),
    path('pantries/', include('pantries.urls')),
    path('', RedirectView.as_view(pattern_name='donations:list'), name='home'),
]
```

### 3. Django Forms Implementation

#### Donation Form (donations/forms.py)
```python
from django import forms
from .models import Donation

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['food_type', 'description', 'quantity', 'unit', 'location', 'expiry_date']
        widgets = {
            'expiry_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'description': forms.Textarea(
                attrs={'rows': 4, 'class': 'form-control'}
            ),
            'quantity': forms.NumberInput(
                attrs={'min': 0.1, 'step': 0.1, 'class': 'form-control'}
            ),
        }
    
    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get('expiry_date')
        from django.utils import timezone
        if expiry_date and expiry_date <= timezone.now():
            raise forms.ValidationError("Expiry date must be in the future.")
        return expiry_date
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity
```

#### Pantry Form (pantries/forms.py)
```python
from django import forms
from .models import Pantry

class PantryForm(forms.ModelForm):
    class Meta:
        model = Pantry
        fields = ['organization_name', 'phone', 'address', 'capacity']
        widgets = {
            'address': forms.Textarea(
                attrs={'rows': 3, 'class': 'form-control'}
            ),
            'capacity': forms.NumberInput(
                attrs={'min': 1, 'class': 'form-control'}
            ),
        }
    
    def clean_capacity(self):
        capacity = self.cleaned_data.get('capacity')
        if capacity and capacity <= 0:
            raise forms.ValidationError("Capacity must be greater than zero.")
        return capacity
```

### 4. Comprehensive Testing Strategy

#### View Tests (donations/tests/test_views.py)
```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from ..models import Donor, Pantry, Donation

class DonationViewsTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.donor_user = User.objects.create_user(
            username='donor1', password='testpass123'
        )
        self.pantry_user = User.objects.create_user(
            username='pantry1', password='testpass123'
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

    def test_donation_detail_view(self):
        """Test donation detail view shows correct information"""
        response = self.client.get(
            reverse('donations:detail', kwargs={'pk': self.donation.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.donation.description)
        self.assertContains(response, str(self.donation.quantity))

    def test_donation_create_requires_donor_login(self):
        """Test that creating donations requires donor authentication"""
        response = self.client.get(reverse('donations:create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_donation_create_by_donor(self):
        """Test donation creation by authenticated donor"""
        self.client.login(username='donor1', password='testpass123')
        
        response = self.client.get(reverse('donations:create'))
        self.assertEqual(response.status_code, 200)
        
        # Test POST request
        future_date = timezone.now() + timedelta(days=2)
        response = self.client.post(reverse('donations:create'), {
            'food_type': 'bakery',
            'description': 'Fresh bread',
            'quantity': 5,
            'unit': 'loaves',
            'location': 'Downtown',
            'expiry_date': future_date.strftime('%Y-%m-%dT%H:%M')
        })
        
        # Should redirect to detail page
        self.assertEqual(response.status_code, 302)
        
        # Verify donation was created
        new_donation = Donation.objects.filter(description='Fresh bread').first()
        self.assertIsNotNone(new_donation)
        self.assertEqual(new_donation.donor, self.donor)

    def test_donation_update_owner_only(self):
        """Test that only donation owner can update"""
        # Test unauthorized access
        self.client.login(username='pantry1', password='testpass123')
        response = self.client.get(
            reverse('donations:update', kwargs={'pk': self.donation.pk})
        )
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test authorized access
        self.client.login(username='donor1', password='testpass123')
        response = self.client.get(
            reverse('donations:update', kwargs={'pk': self.donation.pk})
        )
        self.assertEqual(response.status_code, 200)

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

    def test_url_reversing(self):
        """Test that all named URLs reverse correctly"""
        urls_to_test = [
            ('donations:list', {}),
            ('donations:create', {}),
            ('donations:detail', {'pk': self.donation.pk}),
            ('donations:update', {'pk': self.donation.pk}),
            ('donations:delete', {'pk': self.donation.pk}),
            ('donations:claim', {'pk': self.donation.pk}),
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

class PantryViewsTestCase(TestCase):
    def setUp(self):
        self.pantry_user = User.objects.create_user(
            username='pantry1', password='testpass123'
        )
        self.pantry = Pantry.objects.create(
            user=self.pantry_user,
            organization_name='Test Food Bank',
            capacity=100,
            address='123 Main St'
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

    def test_pantry_update_owner_only(self):
        """Test that only pantry owner can update profile"""
        # Test without login
        response = self.client.get(
            reverse('pantries:update', kwargs={'pk': self.pantry.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test with login
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
                'address': '456 Oak Ave'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect after update
        
        # Verify update
        self.pantry.refresh_from_db()
        self.assertEqual(self.pantry.organization_name, 'Updated Food Bank')
        self.assertEqual(self.pantry.capacity, 150)
```

### 5. Integration Requirements

#### Template Naming Convention
- `donations/list.html` - Donation list view
- `donations/detail.html` - Donation detail view  
- `donations/create.html` - Donation creation form
- `donations/update.html` - Donation update form
- `donations/delete.html` - Donation deletion confirmation
- `pantries/detail.html` - Pantry profile view
- `pantries/update.html` - Pantry profile update form

#### Context Variables
All views must provide consistent context variable names:
- `donations` for lists of donations
- `donation` for single donation instances
- `pantry` for single pantry instances
- `form` for form instances
- `can_claim`, `is_owner`, etc. for permission flags

#### Error Handling
- Use Django's built-in 403/404 error pages
- Provide user-friendly error messages via Django messages framework
- Handle form validation errors gracefully with field-specific error display

## Acceptance Criteria

### Functional Requirements
- [ ] All donation CRUD operations work via CBVs
- [ ] Named URL patterns reverse correctly in views and templates
- [ ] Authorization mixins prevent unauthorized access
- [ ] Form validation works with proper error messages
- [ ] Pagination works on list views (20 items per page)
- [ ] Donation claiming workflow functions correctly
- [ ] Pantry profile management works

### Technical Requirements  
- [ ] All views inherit from appropriate Django generic CBVs
- [ ] Custom mixins for role-based authorization
- [ ] ModelForms for all user input validation
- [ ] Proper use of select_related() for query optimization
- [ ] Success/error messages via Django messages framework
- [ ] Consistent template naming and context variables

### Testing Requirements
- [ ] Minimum 15 view tests covering all CRUD operations
- [ ] Authorization testing (logged in/out, donor/pantry roles)
- [ ] Form validation testing
- [ ] URL reversing tests
- [ ] Pagination tests where applicable
- [ ] All tests pass with >90% code coverage on views

### Code Quality Requirements
- [ ] PEP 8 compliance (use ruff for linting)
- [ ] Docstrings on all view classes and complex methods
- [ ] Type hints on new methods
- [ ] No security vulnerabilities (proper authorization checks)
- [ ] Efficient database queries (use django-debug-toolbar to verify)

## Prompts for Copilot

### Implementation Guidance
1. **"Generate Django CBVs for donations app following the exact patterns in this brief"**
2. **"Create named URL patterns with proper app namespacing for donations and pantries"**
3. **"Implement authorization mixins that check for donor/pantry roles with proper error handling"**
4. **"Build ModelForms with validation for donation and pantry models"**
5. **"Write comprehensive Django TestCase tests for all view operations with Client requests"**

### Code Review Focus
- **"Review views for proper CBV inheritance and method overrides"**
- **"Check authorization logic prevents unauthorized access"**  
- **"Verify URL patterns support all required operations with correct reversing"**
- **"Validate form handling includes proper validation and error display"**
- **"Ensure database queries are optimized with select_related/prefetch_related"**

## Success Criteria

**Implementation Complete When**:
1. All 6 donation views (List, Create, Detail, Update, Delete, Claim) implemented as CBVs
2. All 2 pantry views (Detail, Update) implemented as CBVs  
3. Named URL patterns work for all operations
4. Authorization mixins prevent unauthorized access
5. ModelForms handle validation with user-friendly errors
6. Minimum 15 tests pass covering all functionality
7. Code follows Django best practices and project standards

**Deliverables**:
- Working Django views with full CRUD functionality
- Complete URL routing configuration
- Form validation and error handling
- Comprehensive test coverage
- Documentation of view behavior and authorization rules

## Risk Assessment & Rollback

**Risk Level**: Medium
- **Technical Risk**: CBV complexity and mixin interactions
- **Business Risk**: Authorization vulnerabilities if mixins fail

**Rollback Plan**:
1. Revert to previous working models-only state
2. Implement simple function-based views as fallback
3. Use git revert for specific commits if needed

**Mitigation**:
- Extensive testing of authorization logic
- Manual security testing of access controls
- Code review focused on permission handling