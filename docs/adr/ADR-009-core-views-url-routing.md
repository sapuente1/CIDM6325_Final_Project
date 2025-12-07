# ADR-009: Core Application Views and URL Routing

**Date**: 2025-12-07  
**Status**: Proposed  
**Related PRD**: Section 4 (Functional Requirements), Section 5 (User Stories), Section 6 (System Integration)

## Context

CFMP currently has Django models and basic structure but lacks the view layer and URL routing needed for a functional web application. Users cannot access the system through web browsers because:

- No views implemented for donation listing, creation, claiming
- No URL patterns defined for user workflows
- No integration between authentication system and donation management
- Missing view logic for role-based access (donor vs pantry)
- No connection between frontend templates and backend functionality

## Decision Drivers

- **User Access**: Users need web interface to interact with the system
- **Academic Requirements**: Demonstrate Django MVT (Model-View-Template) pattern
- **Role-Based Functionality**: Different interfaces for donors vs pantries
- **Security**: Proper authentication and authorization in views
- **Maintainability**: Clean, testable view architecture

## Options Considered

### A) Function-Based Views (FBVs)
```python
def donation_list(request):
    donations = Donation.objects.filter(status='available')
    return render(request, 'donations/list.html', {'donations': donations})

def donation_create(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user.donor
            donation.save()
            return redirect('donations:list')
    else:
        form = DonationForm()
    return render(request, 'donations/create.html', {'form': form})
```

**Pros**: Simple, explicit, easy to understand  
**Cons**: Code duplication, harder to extend, more verbose

### B) Class-Based Views (CBVs)
```python
class DonationListView(ListView):
    model = Donation
    template_name = 'donations/list.html'
    context_object_name = 'donations'
    paginate_by = 20
    
    def get_queryset(self):
        return Donation.objects.filter(status='available').select_related('donor__user')

class DonationCreateView(LoginRequiredMixin, CreateView):
    model = Donation
    form_class = DonationForm
    template_name = 'donations/create.html'
    success_url = reverse_lazy('donations:list')
    
    def form_valid(self, form):
        form.instance.donor = self.request.user.donor
        return super().form_valid(form)
```

**Pros**: DRY principle, built-in functionality, extensible, Django best practice  
**Cons**: Learning curve, implicit behavior, debugging complexity

### C) Mixed Approach
Use CBVs for CRUD operations, FBVs for complex business logic

**Pros**: Best of both approaches  
**Cons**: Inconsistent patterns, decision overhead

## Decision

**We choose Option B (Class-Based Views with targeted FBVs)** because:

1. **Django Best Practice**: CBVs are the recommended pattern for standard CRUD operations
2. **Code Reuse**: Generic views reduce boilerplate code significantly
3. **Built-in Security**: Mixins provide authentication, permissions, and CSRF protection
4. **Extensibility**: Easy to customize behavior through method overrides
5. **Academic Value**: Demonstrates advanced Django patterns and OOP principles
6. **Maintainability**: Consistent patterns across the application

## Implementation Strategy

### URL Structure
```python
# cfmp/urls.py (main project URLs)
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/donations/', permanent=False)),
    path('donations/', include('donations.urls', namespace='donations')),
    path('auth/', include('authentication.urls', namespace='auth')),
    path('pantries/', include('pantries.urls', namespace='pantries')), 
    path('monitoring/', include('monitoring.urls', namespace='monitoring')),
]
```

### Donations App URLs
```python
# donations/urls.py
from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    # Public donation browsing
    path('', views.DonationListView.as_view(), name='list'),
    path('<int:pk>/', views.DonationDetailView.as_view(), name='detail'),
    path('search/', views.DonationSearchView.as_view(), name='search'),
    
    # Donor actions (authentication required)
    path('create/', views.DonationCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.DonationUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.DonationDeleteView.as_view(), name='delete'),
    
    # Pantry actions
    path('<int:pk>/claim/', views.DonationClaimView.as_view(), name='claim'),
    path('<int:pk>/fulfill/', views.DonationFulfillView.as_view(), name='fulfill'),
    
    # Dashboard and management
    path('my-donations/', views.MyDonationsView.as_view(), name='my_donations'),
    path('claimed/', views.ClaimedDonationsView.as_view(), name='claimed'),
]
```

### Authentication App URLs
```python
# authentication/urls.py
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'auth'

urlpatterns = [
    # Registration and profile
    path('register/', views.RegisterView.as_view(), name='register'),
    path('choose-role/', views.ChooseRoleView.as_view(), name='choose_role'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    
    # Django built-in auth views
    path('login/', auth_views.LoginView.as_view(template_name='authentication/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Password management
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='authentication/password_change.html'), name='password_change'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='authentication/password_reset.html'), name='password_reset'),
]
```

### View Architecture

#### Base Views and Mixins
```python
# donations/mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

class DonorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Require user to be authenticated and have donor role"""
    
    def test_func(self):
        return hasattr(self.request.user, 'donor')
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied("You must be registered as a donor to access this page.")

class PantryRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Require user to be authenticated and have pantry role"""
    
    def test_func(self):
        return hasattr(self.request.user, 'pantry')
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied("You must be registered as a pantry to access this page.")

class OwnerRequiredMixin(UserPassesTestMixin):
    """Require user to be the owner of the object"""
    
    def test_func(self):
        obj = self.get_object()
        return obj.donor.user == self.request.user
```

#### Donation Views
```python
# donations/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Donation
from .forms import DonationForm, DonationSearchForm
from .mixins import DonorRequiredMixin, PantryRequiredMixin, OwnerRequiredMixin

class DonationListView(ListView):
    """Public list of available donations"""
    model = Donation
    template_name = 'donations/list.html'
    context_object_name = 'donations'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Donation.objects.filter(
            status='available'
        ).select_related('donor__user').order_by('-created_at')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(food_type__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        
        # Filter by food type
        food_type = self.request.GET.get('food_type')
        if food_type:
            queryset = queryset.filter(food_type=food_type)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = DonationSearchForm(self.request.GET)
        context['food_types'] = Donation.FOOD_TYPE_CHOICES
        return context

class DonationDetailView(DetailView):
    """Detailed view of a single donation"""
    model = Donation
    template_name = 'donations/detail.html'
    context_object_name = 'donation'
    
    def get_queryset(self):
        return Donation.objects.select_related('donor__user', 'claimed_by__user')

class DonationCreateView(DonorRequiredMixin, CreateView):
    """Create a new donation (donor only)"""
    model = Donation
    form_class = DonationForm
    template_name = 'donations/create.html'
    success_url = reverse_lazy('donations:my_donations')
    
    def form_valid(self, form):
        form.instance.donor = self.request.user.donor
        messages.success(self.request, 'Donation created successfully!')
        return super().form_valid(form)

class DonationUpdateView(DonorRequiredMixin, OwnerRequiredMixin, UpdateView):
    """Edit existing donation (owner only)"""
    model = Donation
    form_class = DonationForm
    template_name = 'donations/update.html'
    success_url = reverse_lazy('donations:my_donations')
    
    def form_valid(self, form):
        messages.success(self.request, 'Donation updated successfully!')
        return super().form_valid(form)

class DonationDeleteView(DonorRequiredMixin, OwnerRequiredMixin, DeleteView):
    """Delete donation (owner only)"""
    model = Donation
    template_name = 'donations/delete.html'
    success_url = reverse_lazy('donations:my_donations')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Donation deleted successfully!')
        return super().delete(request, *args, **kwargs)

class DonationClaimView(PantryRequiredMixin, DetailView):
    """Claim a donation (pantry only)"""
    model = Donation
    template_name = 'donations/claim.html'
    
    def post(self, request, *args, **kwargs):
        donation = self.get_object()
        
        if donation.status != 'available':
            messages.error(request, 'This donation is no longer available.')
            return redirect('donations:detail', pk=donation.pk)
        
        # Claim the donation
        donation.claim(request.user.pantry)
        messages.success(request, f'You have successfully claimed "{donation.food_type}" from {donation.donor.organization_name}!')
        
        return redirect('donations:claimed')

class MyDonationsView(DonorRequiredMixin, ListView):
    """Donor's own donations dashboard"""
    template_name = 'donations/my_donations.html'
    context_object_name = 'donations'
    paginate_by = 20
    
    def get_queryset(self):
        return Donation.objects.filter(
            donor=self.request.user.donor
        ).order_by('-created_at')

class ClaimedDonationsView(PantryRequiredMixin, ListView):
    """Pantry's claimed donations"""
    template_name = 'donations/claimed.html'
    context_object_name = 'donations'
    paginate_by = 20
    
    def get_queryset(self):
        return Donation.objects.filter(
            claimed_by=self.request.user.pantry,
            status='claimed'
        ).order_by('-claimed_at')
```

#### Authentication Views
```python
# authentication/views.py
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomUserCreationForm, DonorProfileForm, PantryProfileForm
from .models import UserProfile
from donations.models import Donor, Pantry

class RegisterView(CreateView):
    """User registration"""
    form_class = CustomUserCreationForm
    template_name = 'authentication/register.html'
    success_url = reverse_lazy('auth:choose_role')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Registration successful! Please choose your role.')
        return response

class ChooseRoleView(LoginRequiredMixin, TemplateView):
    """Role selection after registration"""
    template_name = 'authentication/choose_role.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Redirect if user already has a profile
        if hasattr(request.user, 'userprofile'):
            return redirect('auth:profile')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        role = request.POST.get('role')
        
        if role == 'donor':
            return redirect('auth:donor_profile_create')
        elif role == 'pantry':
            return redirect('auth:pantry_profile_create')
        else:
            messages.error(request, 'Please select a valid role.')
            return self.get(request, *args, **kwargs)

class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile dashboard"""
    template_name = 'authentication/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if hasattr(user, 'donor'):
            context['role'] = 'donor'
            context['profile'] = user.donor
            context['recent_donations'] = user.donor.donation_set.filter(
                status__in=['available', 'claimed']
            )[:5]
        elif hasattr(user, 'pantry'):
            context['role'] = 'pantry'
            context['profile'] = user.pantry
            context['recent_claims'] = Donation.objects.filter(
                claimed_by=user.pantry
            )[:5]
        
        return context
```

### Form Classes
```python
# donations/forms.py
from django import forms
from .models import Donation

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['food_type', 'description', 'quantity', 'location', 'expiry_date']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'food_type': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_expiry_date(self):
        expiry_date = self.cleaned_data['expiry_date']
        if expiry_date <= timezone.now().date():
            raise forms.ValidationError("Expiry date must be in the future.")
        return expiry_date

class DonationSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search donations...',
            'class': 'form-control'
        })
    )
    food_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Donation.FOOD_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
```

### Settings Integration
```python
# Update settings to include view-related configurations
LOGIN_URL = 'auth:login'
LOGIN_REDIRECT_URL = 'auth:profile'
LOGOUT_REDIRECT_URL = 'donations:list'

# Pagination
PAGINATE_BY = 20

# Messages framework
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}
```

## Consequences

**Positive**:
- Complete web interface connecting frontend to backend
- Role-based access control properly implemented
- Consistent URL patterns and view architecture
- Built-in security through Django mixins
- Scalable structure for additional features

**Negative**:
- Complex inheritance hierarchy with mixins
- More files to maintain across multiple apps
- Learning curve for understanding CBV method resolution order

**Mitigation Strategies**:
- Comprehensive documentation of view patterns
- Unit tests for all view functionality
- Code comments explaining complex mixin combinations

## Security Implementation

### Authentication and Authorization
- `LoginRequiredMixin` ensures authentication
- Custom mixins (`DonorRequiredMixin`, `PantryRequiredMixin`) enforce role-based access
- `OwnerRequiredMixin` ensures users can only modify their own data
- CSRF protection on all forms
- Permission denied exceptions provide clear error messages

### Input Validation
- Django form validation prevents invalid data
- Model constraints enforce data integrity
- Custom validators for business rules (e.g., future expiry dates)

## Testing Strategy

### View Tests
```python
class DonationViewTests(TestCase):
    def setUp(self):
        self.donor_user = User.objects.create_user('donor', 'donor@test.com', 'pass')
        self.donor = Donor.objects.create(user=self.donor_user, ...)
        self.pantry_user = User.objects.create_user('pantry', 'pantry@test.com', 'pass')
        self.pantry = Pantry.objects.create(user=self.pantry_user, ...)
        
    def test_donation_list_anonymous_access(self):
        """Anonymous users can view donation list"""
        response = self.client.get(reverse('donations:list'))
        self.assertEqual(response.status_code, 200)
    
    def test_donation_create_requires_donor(self):
        """Only donors can create donations"""
        url = reverse('donations:create')
        
        # Anonymous user redirected to login
        response = self.client.get(url)
        self.assertRedirects(response, f'/auth/login/?next={url}')
        
        # Pantry user denied access
        self.client.force_login(self.pantry_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        
        # Donor user can access
        self.client.force_login(self.donor_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
```

This ADR establishes the complete view layer architecture needed to make CFMP a fully functional web application with proper security, role-based access, and user-friendly interfaces.