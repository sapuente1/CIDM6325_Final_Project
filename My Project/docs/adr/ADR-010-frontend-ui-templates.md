# ADR-010: Frontend UI Templates and Navigation

**Date**: 2025-12-07  
**Status**: Proposed  
**Related PRD**: Section 4 (User Interface), Section 5 (Functional Requirements), Section 7 (Non-Functional Requirements - Usability)

## Context

CFMP currently lacks a cohesive frontend user interface, templates, and navigation system. The application has backend functionality (donations, authentication, monitoring) but no accessible web interface for end users. Key gaps include:

- Missing base template with consistent layout and styling
- No navigation system for users to access different features  
- Missing templates for donation listing, creation, and claiming
- No responsive design for mobile/desktop usage
- Missing user dashboard and profile management
- No integration between frontend and existing backend apps

## Decision Drivers

- **User Experience**: Need intuitive navigation and clean interface
- **Academic Requirements**: Demonstrate Django templating and frontend concepts
- **Accessibility**: Mobile-responsive design for diverse users
- **Maintainability**: Template inheritance and reusable components
- **Integration**: Connect existing backend functionality to user interface

## Options Considered

### A) Minimal HTML/CSS Templates
```html
<!-- Basic HTML with minimal styling -->
<html>
<head><title>CFMP</title></head>
<body>
  <nav>Simple navigation</nav>
  <main>{{ content }}</main>
</body>
</html>
```

**Pros**: Simple, fast implementation  
**Cons**: Poor UX, not responsive, limited functionality

### B) Bootstrap 5 + Django Templates
```html
<!-- Bootstrap-based responsive templates -->
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}CFMP{% endblock %}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">...</nav>
  <main class="container my-4">
    {% block content %}{% endblock %}
  </main>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

**Pros**: Professional appearance, responsive, component library, Django best practices  
**Cons**: External dependency, larger footprint

### C) Custom CSS Framework
Build custom CSS grid and component system

**Pros**: Full control, lightweight  
**Cons**: Time-intensive, reinventing the wheel, maintenance burden

## Decision

**We choose Option B (Bootstrap 5 + Django Templates)** because:

1. **Rapid Development**: Bootstrap provides professional components out-of-the-box
2. **Responsive Design**: Mobile-first approach ensures accessibility across devices
3. **Django Integration**: Template inheritance and block system work seamlessly
4. **Academic Value**: Demonstrates industry-standard frontend/backend integration
5. **User Experience**: Professional appearance builds user trust
6. **Component Library**: Forms, navigation, alerts, and cards available immediately

## Implementation Strategy

### Base Template Architecture
```
templates/
├── base.html                    # Global layout and navigation
├── components/
│   ├── _navbar.html            # Navigation component
│   ├── _sidebar.html           # Sidebar for authenticated users
│   ├── _alerts.html            # Message alerts
│   └── _pagination.html        # Pagination component
├── donations/
│   ├── list.html              # Browse available donations
│   ├── detail.html            # Individual donation details
│   ├── create.html            # Create new donation
│   └── claim.html             # Claim donation form
├── authentication/
│   ├── login.html             # User login
│   ├── register.html          # User registration
│   ├── profile.html           # User profile/dashboard
│   └── choose_role.html       # Role selection after registration
└── monitoring/
    └── dashboard.html         # Admin monitoring dashboard
```

### Navigation Structure
```python
# Navigation menu configuration
NAVIGATION = [
    {'name': 'Home', 'url': 'donations:list', 'icon': 'house'},
    {'name': 'Donations', 'url': 'donations:list', 'icon': 'gift'},
    {'name': 'Create Donation', 'url': 'donations:create', 'icon': 'plus-circle', 'auth_required': True, 'roles': ['donor']},
    {'name': 'My Pantry', 'url': 'pantries:dashboard', 'icon': 'building', 'auth_required': True, 'roles': ['pantry']},
    {'name': 'Profile', 'url': 'auth:profile', 'icon': 'person', 'auth_required': True},
    {'name': 'Admin', 'url': 'admin:index', 'icon': 'gear', 'staff_required': True},
]
```

### Responsive Design Strategy
- **Mobile First**: Bootstrap's mobile-first breakpoints
- **Navigation**: Collapsible navbar for mobile, full navbar for desktop
- **Cards**: Donation cards that stack on mobile, grid on desktop
- **Forms**: Single-column on mobile, multi-column on larger screens
- **Tables**: Responsive tables with horizontal scrolling

### Component Design System
```scss
// Custom CFMP color scheme
:root {
  --cfmp-primary: #2563eb;     // Blue - trust and reliability
  --cfmp-secondary: #059669;   // Green - food and sustainability  
  --cfmp-warning: #d97706;     // Orange - urgency for expiring food
  --cfmp-danger: #dc2626;      // Red - alerts and errors
  --cfmp-success: #16a34a;     // Green - successful actions
}
```

### Template Inheritance Strategy
```django
<!-- base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  {% block meta %}
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
  {% endblock %}
  
  <title>{% block title %}CFMP - Community Food Management Platform{% endblock %}</title>
  
  {% block css %}
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{% static 'css/cfmp.css' %}">
  {% endblock %}
</head>
<body>
  {% include 'components/_navbar.html' %}
  
  <main class="container-fluid">
    {% include 'components/_alerts.html' %}
    
    <div class="row">
      {% if user.is_authenticated %}
        <div class="col-md-3 col-lg-2">
          {% include 'components/_sidebar.html' %}
        </div>
        <div class="col-md-9 col-lg-10">
          {% block content %}{% endblock %}
        </div>
      {% else %}
        <div class="col-12">
          {% block content %}{% endblock %}
        </div>
      {% endif %}
    </div>
  </main>
  
  {% block js %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{% static 'js/cfmp.js' %}"></script>
  {% endblock %}
</body>
</html>
```

### Form Integration with Crispy Forms
```python
# Install django-crispy-forms and crispy-bootstrap5
INSTALLED_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
```

### User Experience Flows
1. **Anonymous User**: Landing page → Browse donations → Register/Login → Create profile
2. **Donor**: Dashboard → Create donation → Manage active donations → View impact metrics
3. **Pantry**: Dashboard → Browse available donations → Claim donations → Manage inventory
4. **Admin**: Monitoring dashboard → User management → System health → Analytics

### Progressive Enhancement
- **Base Functionality**: All features work without JavaScript
- **Enhanced UX**: JavaScript adds real-time updates, form validation, and smooth transitions
- **Offline Support**: Service worker for basic offline browsing (future enhancement)

## Template Structure Details

### Donation Templates
```django
<!-- donations/list.html -->
{% extends 'base.html' %}
{% load crispy_forms_tags %}

{% block title %}Available Donations - CFMP{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
  <h1>Available Donations</h1>
  {% if user.is_authenticated and user.userprofile.role == 'donor' %}
    <a href="{% url 'donations:create' %}" class="btn btn-primary">
      <i class="bi bi-plus-circle"></i> Create Donation
    </a>
  {% endif %}
</div>

<!-- Search and filters -->
<div class="row mb-4">
  <div class="col-md-8">
    <form method="get" class="d-flex">
      <input type="search" name="q" value="{{ request.GET.q }}" 
             placeholder="Search donations..." class="form-control me-2">
      <button type="submit" class="btn btn-outline-primary">Search</button>
    </form>
  </div>
  <div class="col-md-4">
    <select name="food_type" class="form-select">
      <option value="">All Food Types</option>
      <option value="produce">Produce</option>
      <option value="dairy">Dairy</option>
      <option value="bread">Bread & Baked Goods</option>
    </select>
  </div>
</div>

<!-- Donation cards -->
<div class="row">
  {% for donation in donations %}
    <div class="col-lg-4 col-md-6 mb-4">
      {% include 'donations/_donation_card.html' %}
    </div>
  {% empty %}
    <div class="col-12">
      <div class="alert alert-info">
        <h4>No donations available</h4>
        <p>There are currently no donations available in your area. Check back later!</p>
      </div>
    </div>
  {% endfor %}
</div>

<!-- Pagination -->
{% include 'components/_pagination.html' %}
{% endblock %}
```

### Authentication Templates
```django
<!-- authentication/login.html -->
{% extends 'base.html' %}
{% load crispy_forms_tags %}

{% block title %}Login - CFMP{% endblock %}

{% block content %}
<div class="row justify-content-center">
  <div class="col-md-6 col-lg-4">
    <div class="card">
      <div class="card-header">
        <h3 class="text-center">Welcome Back</h3>
      </div>
      <div class="card-body">
        <form method="post">
          {% csrf_token %}
          {{ form|crispy }}
          <button type="submit" class="btn btn-primary w-100">Login</button>
        </form>
      </div>
      <div class="card-footer text-center">
        <p>Don't have an account? <a href="{% url 'auth:register' %}">Register here</a></p>
        <a href="{% url 'auth:password_reset' %}">Forgot your password?</a>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

## Consequences

**Positive**:
- Professional, responsive user interface immediately available
- Consistent look and feel across all pages
- Mobile-friendly design increases accessibility
- Template inheritance reduces code duplication
- Bootstrap components speed up development
- Integration with existing Django apps

**Negative**:
- External dependency on Bootstrap CDN
- Learning curve for Bootstrap classes and components
- Potential design limitations within Bootstrap framework

**Mitigation Strategies**:
- Host Bootstrap locally for production deployment
- Create custom CSS overrides for CFMP-specific styling
- Document template patterns for consistent development

## Security Considerations

### Template Security
- All user input escaped automatically by Django templates
- CSRF protection on all forms
- Secure headers configured in production settings
- Content Security Policy for external resources

### Navigation Security
- Role-based menu visibility
- Permission checks in views, not just templates
- Safe URL reversal using Django's `reverse()` function

## Testing Strategy

### Template Tests
```python
class TemplateTests(TestCase):
    def test_base_template_renders(self):
        """Test base template renders without errors"""
        response = self.client.get('/')
        self.assertContains(response, 'CFMP')
        self.assertContains(response, 'bootstrap')
    
    def test_navigation_visibility(self):
        """Test navigation shows appropriate links based on user role"""
        # Test anonymous user
        response = self.client.get('/')
        self.assertNotContains(response, 'Create Donation')
        
        # Test authenticated donor
        self.client.force_login(self.donor_user)
        response = self.client.get('/')
        self.assertContains(response, 'Create Donation')
    
    def test_responsive_elements(self):
        """Test responsive classes are present"""
        response = self.client.get('/')
        self.assertContains(response, 'navbar-expand-lg')
        self.assertContains(response, 'col-md')
```

### Accessibility Tests
- Color contrast ratios meet WCAG standards
- Keyboard navigation works for all interactive elements
- Screen reader compatibility with proper ARIA labels
- Form labels properly associated with inputs

This ADR establishes the foundation for a professional, accessible, and maintainable user interface that connects all existing backend functionality into a cohesive web application.