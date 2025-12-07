# ADR-003: Authentication and Authorization Strategy

**Date**: 2025-12-07  
**Status**: Proposed  
**Related PRD**: Section 6 (FR-005), Section 4 (Authentication), Section 7 (Security)

## Context

CFMP requires role-based access control to separate donor, pantry, and admin functionalities. The system must:

- Implement Django's authentication middleware (FR-005)
- Support role-based template rendering
- Protect sensitive operations (posting, claiming donations)
- Provide secure login/logout flow
- Defer social authentication to Phase 2

## Decision Drivers

- **Security**: Proper access control for sensitive operations
- **User Experience**: Clear role separation and appropriate access
- **Django Patterns**: Leverage built-in authentication effectively
- **Academic Requirements**: Demonstrate authentication middleware understanding
- **Phase 1 Constraints**: Keep MVP simple, defer complex auth to Phase 2

## Options Considered

### A) Django Groups-Based Permissions
```python
# Use Django's built-in Group and Permission system
user.groups.add(donors_group)
user.has_perm('donations.add_donation')

@permission_required('donations.add_donation')
def create_donation(request):
    # view logic
```

**Pros**: Built into Django, flexible permissions  
**Cons**: Complex for simple role separation, overkill for MVP

### B) Profile-Based Roles with OneToOne
```python
class Donor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=100)
    # donor-specific fields

class Pantry(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    capacity = models.IntegerField()
    # pantry-specific fields

# Usage
if hasattr(request.user, 'donor'):
    # donor logic
elif hasattr(request.user, 'pantry'):
    # pantry logic
```

**Pros**: Simple role detection, supports role-specific data  
**Cons**: Requires careful handling of role assignment

### C) User Type Field
```python
class CustomUser(AbstractUser):
    USER_TYPES = [
        ('donor', 'Donor'),
        ('pantry', 'Pantry'),
        ('admin', 'Admin'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
```

**Pros**: Simple role checking  
**Cons**: Custom user model complexity, less extensible

## Decision

**We choose Option B (Profile-Based Roles)** because:

1. **Separation of Concerns**: Role-specific data naturally separated
2. **Django Patterns**: Uses standard OneToOneField relationship
3. **Extensibility**: Easy to add role-specific fields and methods
4. **Testing**: Simple role checking with hasattr()
5. **No Custom User**: Avoids complexity of custom user model in MVP

## Implementation Strategy

### Model Design
```python
class Donor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.organization_name} ({self.user.username})"

class Pantry(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=100)
    capacity = models.IntegerField(help_text="Approximate weekly capacity")
    service_area = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.organization_name} ({self.user.username})"
```

### Authentication Mixins
```python
class DonorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'donor')
    
    def handle_no_permission(self):
        messages.error(self.request, "You must be registered as a donor to access this page.")
        return redirect('auth:login')

class PantryRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'pantry')

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff
```

### Template Context Processor
```python
def user_role_context(request):
    \"\"\"Add user role information to all templates\"\"\"\n    context = {\n        'is_donor': hasattr(request.user, 'donor') if request.user.is_authenticated else False,\n        'is_pantry': hasattr(request.user, 'pantry') if request.user.is_authenticated else False,\n        'is_admin': request.user.is_staff if request.user.is_authenticated else False,\n    }\n    return context
```

### Registration Flow
```python
class DonorRegistrationView(CreateView):
    model = Donor
    form_class = DonorRegistrationForm
    template_name = 'auth/donor_register.html'
    success_url = reverse_lazy('donations:list')
    
    def form_valid(self, form):
        # Create User first, then Donor profile
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password']
        )
        form.instance.user = user
        response = super().form_valid(form)
        login(self.request, user)  # Auto-login after registration
        return response
```

## URL Structure
```python
# auth/urls.py
app_name = 'auth'
urlpatterns = [
    path('login/', LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/donor/', DonorRegistrationView.as_view(), name='donor_register'),
    path('register/pantry/', PantryRegistrationView.as_view(), name='pantry_register'),
]
```

## Consequences

**Positive**:
- Clear role separation supports business logic
- Simple role checking in templates and views
- Extensible for role-specific functionality
- No custom user model complexity
- Supports Django admin role management

**Negative**:
- Requires careful handling of user creation flow
- Need to ensure every user has exactly one role
- Role switching requires admin intervention

**Security Considerations**:
- All views use LoginRequiredMixin for authenticated access
- Role-based mixins prevent cross-role access
- CSRF protection on all forms (Django default)
- No sensitive data in session (user ID only)

## Testing Strategy
- Test role-based view access with Django Client
- Verify template context processor works correctly
- Test registration flow creates proper User + Profile
- Security testing for unauthorized access attempts

## Future Migration Path (Phase 2)
- Add django-allauth for social authentication
- Keep existing role models, add social accounts
- Consider groups/permissions for fine-grained control
- Add role switching functionality for multi-role users

## Rollback Plan
- Standard Django User model remains unchanged
- Profile models can be removed without affecting core auth
- Views can fall back to basic login_required decorator
- Template changes are minimal and reversible