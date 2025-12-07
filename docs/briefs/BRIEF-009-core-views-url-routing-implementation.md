# BRIEF-009: Core Application Views and URL Routing Implementation

**Date**: 2025-12-07  
**Related ADR**: ADR-009-core-views-url-routing.md  
**Issue**: Implement complete view layer and URL routing for CFMP web interface  
**Sprint Goal**: Transform CFMP from Django models to fully functional web application with role-based access

## Goal

Implement comprehensive view layer using Class-Based Views (CBVs) with proper URL routing, authentication mixins, and role-based access control to create a complete web interface for donors and pantries to interact with the donation system.

## Scope (Single PR)

### Files to Create:
- **donations/views.py**: Complete CBV implementation for donation CRUD operations
- **donations/urls.py**: URL patterns for all donation workflows  
- **donations/mixins.py**: Custom authentication and authorization mixins
- **donations/forms.py**: Django forms for donation creation and search
- **authentication/views.py**: User registration, profile, and role selection views
- **authentication/urls.py**: Authentication workflow URL patterns
- **authentication/forms.py**: Custom user and profile forms
- **pantries/views.py**: Pantry-specific views and dashboards
- **pantries/urls.py**: Pantry app URL patterns

### Files to Update:
- **cfmp/urls.py**: Main project URL routing with namespace configuration
- **cfmp/settings/base.py**: Add view-related configurations (login URLs, pagination, messages)
- **donations/models.py**: Add any missing methods needed by views (claim, fulfill)
- **authentication/models.py**: Enhance user profile models if needed

### Non-goals for this PR:
- Template implementation (HTML/CSS)
- Static file management
- Email notifications
- API endpoints
- Advanced search functionality

## Standards & Requirements

### View Architecture
- **CBVs Preferred**: Use Class-Based Views for standard CRUD operations
- **FBVs for Complex Logic**: Function-based views only for complex business logic
- **Security Mixins**: All views must use appropriate authentication/authorization mixins
- **Error Handling**: Proper error messages and exception handling
- **Form Validation**: Server-side validation with custom validators

### URL Patterns
- **Namespace Organization**: Each app uses proper URL namespacing
- **RESTful URLs**: Follow RESTful URL conventions where appropriate
- **Meaningful Names**: URL names should be descriptive and consistent
- **Parameter Validation**: URL patterns should validate parameters (e.g., pk as int)

### Security Requirements
- **Authentication**: All protected views require authentication
- **Authorization**: Role-based access control (donor vs pantry)
- **Ownership**: Users can only modify their own data
- **CSRF Protection**: All forms must include CSRF tokens
- **Input Validation**: Validate all user input through Django forms

## Acceptance Criteria

### UC-001: Public Donation Browsing
**Given** any user (authenticated or anonymous)  
**When** they visit the donations list page  
**Then** they should see:
- List of available donations with pagination
- Search functionality by food type and description
- Filter options by donation category
- View details link for each donation
- No edit/delete options for non-owners

**Validation Steps**:
```powershell
# Test public access to donation list
curl -I http://localhost:8000/donations/
# Should return 200 OK

# Test search functionality
curl "http://localhost:8000/donations/?search=vegetables"
# Should return filtered results

# Test anonymous access to protected pages
curl -I http://localhost:8000/donations/create/
# Should return 302 redirect to login
```

### UC-002: Donor Donation Management
**Given** an authenticated user with donor role  
**When** they access donation management features  
**Then** they should be able to:
- Create new donations with form validation
- View/edit/delete their own donations only
- See dashboard of their donation history
- Receive success/error messages for all actions
- Be blocked from accessing pantry-only features

**Validation Steps**:
```powershell
# Test donor authentication and authorization
python manage.py test donations.tests.DonationViewTests.test_donation_create_requires_donor
python manage.py test donations.tests.DonationViewTests.test_owner_required_for_edit
python manage.py test donations.tests.DonationViewTests.test_pantry_cannot_access_donor_features
```

### UC-003: Pantry Claiming System
**Given** an authenticated user with pantry role  
**When** they interact with available donations  
**Then** they should be able to:
- View all available donations
- Claim donations for their pantry
- See dashboard of claimed donations
- Mark donations as fulfilled
- Be blocked from creating/editing donations

**Validation Steps**:
```powershell
# Test pantry claiming functionality
python manage.py test donations.tests.DonationClaimTests.test_claim_available_donation
python manage.py test donations.tests.DonationClaimTests.test_cannot_claim_unavailable_donation
python manage.py test donations.tests.DonationClaimTests.test_claimed_donations_dashboard
```

### UC-004: Authentication and Role Management
**Given** a new or existing user  
**When** they interact with the authentication system  
**Then** they should be able to:
- Register new account with email/password
- Choose role (donor or pantry) during registration
- View and edit their profile information
- Login/logout with proper redirects
- Access appropriate features based on role

**Validation Steps**:
```powershell
# Test complete registration flow
python manage.py test authentication.tests.RegistrationTests.test_complete_registration_flow
python manage.py test authentication.tests.ProfileTests.test_role_based_dashboard
```

### UC-005: URL Routing and Security
**Given** the application is deployed  
**When** users access various URLs  
**Then** the routing should:
- Resolve all URL patterns correctly
- Enforce authentication on protected URLs
- Return appropriate HTTP status codes
- Handle invalid URLs with 404 errors
- Redirect authenticated users appropriately

**Validation Steps**:
```powershell
# Test URL resolution
python manage.py test donations.tests.URLTests.test_all_urls_resolve
python manage.py test authentication.tests.URLTests.test_protected_urls_require_login
```

## Implementation Guidance for Copilot

### Phase 1: URL Routing Infrastructure
**Prompt**: "Create comprehensive URL routing for CFMP Django project. Update main cfmp/urls.py with namespace routing for donations, authentication, pantries, and monitoring apps. Each app should have proper URL patterns following RESTful conventions with meaningful URL names."

**Key Requirements**:
- Main project URLs with RedirectView for root URL
- Namespace configuration for each app (donations, auth, pantries, monitoring)
- Include Django admin and static file serving
- Proper import statements and URL pattern organization

### Phase 2: Authentication Views and Forms
**Prompt**: "Implement Django authentication views using CBVs for user registration, role selection, profile management, and login/logout. Create custom forms for user registration and profile editing. Include role-based redirects and proper success messages."

**Key Requirements**:
- RegisterView with custom user creation form
- ChooseRoleView for post-registration role selection
- ProfileView with role-based dashboard display
- Integration with Django's built-in auth views
- Custom forms with proper validation and styling

### Phase 3: Donation Management Views
**Prompt**: "Create complete donation management views using Django CBVs. Implement DonationListView with search/filter, DonationCreateView with donor authentication, DonationUpdateView/DeleteView with ownership validation, and DonationClaimView for pantries. Include proper mixins for authentication and authorization."

**Key Requirements**:
- ListView with pagination, search, and filtering
- CreateView, UpdateView, DeleteView with proper authentication
- Custom mixins for donor/pantry role enforcement
- Owner validation for edit/delete operations
- Claim functionality for pantries

### Phase 4: Security Mixins and Authorization
**Prompt**: "Create custom Django authentication mixins for role-based access control. Implement DonorRequiredMixin, PantryRequiredMixin, and OwnerRequiredMixin with proper error handling and permission denied exceptions. Include comprehensive test cases for security validation."

**Key Requirements**:
- Custom mixins inheriting from LoginRequiredMixin and UserPassesTestMixin
- Proper error handling for unauthorized access
- Clear error messages for permission denied scenarios
- Integration with existing user/donor/pantry models

### Phase 5: Forms and Validation
**Prompt**: "Create Django forms for donation creation/editing and search functionality. Include proper field validation, custom validators for business rules (expiry dates, quantities), and Bootstrap-compatible form widgets. Add client-side and server-side validation."

**Key Requirements**:
- DonationForm with model validation and custom clean methods
- DonationSearchForm for filtering and search
- Proper widget configuration with CSS classes
- Custom validators for business logic (future dates, positive quantities)

### Phase 6: Dashboard and Management Views
**Prompt**: "Implement dashboard views for donors and pantries showing their respective donation histories. Create MyDonationsView for donors and ClaimedDonationsView for pantries with pagination and status filtering. Include summary statistics and recent activity."

**Key Requirements**:
- Role-specific dashboard views with different data
- Pagination for large datasets
- Status-based filtering and ordering
- Summary statistics and counts

## Implementation Details

### URL Structure
```python
# Main project URL structure
/                           -> Redirect to /donations/
/admin/                     -> Django admin
/donations/                 -> Public donation list
/donations/<id>/            -> Donation detail
/donations/create/          -> Create donation (donors only)
/donations/<id>/edit/       -> Edit donation (owner only)
/donations/<id>/claim/      -> Claim donation (pantries only)
/donations/my-donations/    -> Donor dashboard
/donations/claimed/         -> Pantry claimed donations
/auth/register/             -> User registration
/auth/choose-role/          -> Role selection
/auth/profile/              -> User profile
/auth/login/                -> Login
/auth/logout/               -> Logout
```

### View Hierarchy
```
BaseView
├── ListView (donations, my-donations, claimed)
├── DetailView (donation detail, claim view)
├── CreateView (donation create, user register)
├── UpdateView (donation edit, profile edit)
└── DeleteView (donation delete)

Mixins Applied:
├── LoginRequiredMixin (all protected views)
├── DonorRequiredMixin (create, edit, delete donations)
├── PantryRequiredMixin (claim, claimed dashboard)
└── OwnerRequiredMixin (edit/delete own donations)
```

### Form Validation Examples
```python
# Business rule validation examples
def clean_expiry_date(self):
    expiry_date = self.cleaned_data['expiry_date']
    if expiry_date <= timezone.now().date():
        raise forms.ValidationError("Expiry date must be in the future.")
    return expiry_date

def clean_quantity(self):
    quantity = self.cleaned_data['quantity']
    if quantity <= 0:
        raise forms.ValidationError("Quantity must be positive.")
    return quantity
```

## Risk Mitigation

### Security Risks
- **Risk**: Unauthorized access to sensitive operations
- **Mitigation**: Comprehensive mixin-based authentication and authorization
- **Testing**: Security-focused test cases for all protected views

### Performance Risks
- **Risk**: Slow page loads with large datasets
- **Mitigation**: Pagination, select_related queries, database indexing
- **Monitoring**: Query optimization and performance testing

### User Experience Risks
- **Risk**: Confusing navigation or unclear error messages
- **Mitigation**: Consistent URL patterns, clear success/error messages, proper redirects
- **Testing**: User workflow testing and accessibility validation

## Testing Strategy

### View Testing
- Unit tests for all view classes and methods
- Authentication and authorization testing
- Form validation testing
- URL resolution testing
- Integration tests for complete workflows

### Security Testing
- Test unauthorized access attempts
- Validate role-based access control
- Test CSRF protection
- Verify input validation

### User Workflow Testing
- Test complete registration and role selection flow
- Test donation creation to fulfillment workflow
- Test claiming process from pantry perspective
- Test error handling and edge cases

## Success Metrics

### Functionality
- All URL patterns resolve correctly
- All views return appropriate HTTP status codes
- Authentication and authorization work as designed
- Forms validate input correctly
- User workflows complete successfully

### Security
- Protected views require authentication
- Role-based access control enforced
- Users cannot modify others' data
- All forms protected against CSRF
- Input validation prevents malicious data

### Performance
- Page load times under acceptable thresholds
- Database queries optimized with select_related
- Pagination prevents memory issues
- Search functionality performs well

This brief provides comprehensive guidance for implementing the complete view layer architecture while maintaining security, usability, and Django best practices.