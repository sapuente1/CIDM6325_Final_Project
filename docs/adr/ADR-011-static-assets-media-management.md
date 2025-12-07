# ADR-011: Static Assets and Media Management

**Date**: 2025-12-07  
**Status**: Proposed  
**Related PRD**: Section 4 (User Interface), Section 7 (Non-Functional Requirements - Performance), Section 8 (Technical Requirements)

## Context

CFMP currently lacks static asset management and media file handling capabilities. The application needs:

- CSS stylesheets for custom styling beyond Bootstrap
- JavaScript for enhanced user interactions
- Image assets (logos, icons, placeholder images)
- Media file handling for donation photos
- Favicon and branding assets
- Production-ready static file serving

## Decision Drivers

- **User Experience**: Professional appearance with custom styling
- **Performance**: Optimized asset delivery and caching
- **Academic Requirements**: Demonstrate Django static files management
- **Branding**: Consistent visual identity for CFMP platform
- **Production Readiness**: Efficient static file serving for deployment

## Options Considered

### A) Basic Django Static Files
```python
# Simple static file configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

**Pros**: Simple setup, Django built-in support  
**Cons**: No optimization, limited asset management

### B) Django + WhiteNoise + Asset Pipeline
```python
# Enhanced static files with compression and optimization
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
```

**Pros**: Compression, cache-busting, production-ready  
**Cons**: Build step complexity, additional dependencies

### C) CDN + External Asset Management
Use external CDNs for all assets

**Pros**: Global performance, reduced server load  
**Cons**: External dependencies, cost considerations

## Decision

**We choose Option B (Django + WhiteNoise + Asset Pipeline)** because:

1. **Production Ready**: WhiteNoise provides efficient static file serving
2. **Performance**: Automatic compression and cache-busting
3. **Django Integration**: Seamless integration with Django collectstatic
4. **Academic Value**: Demonstrates production deployment concepts
5. **Self-Contained**: No external dependencies or ongoing costs

## Implementation Strategy

### Directory Structure
```
static/
├── css/
│   ├── cfmp.css              # Main application styles
│   ├── components/
│   │   ├── navbar.css        # Navigation styling
│   │   ├── cards.css         # Donation card styling
│   │   ├── forms.css         # Form enhancements
│   │   └── alerts.css        # Message styling
│   └── vendor/
│       └── custom-bootstrap.css  # Bootstrap customizations
├── js/
│   ├── cfmp.js              # Main application JavaScript
│   ├── components/
│   │   ├── donation-search.js   # Search functionality
│   │   ├── claim-modal.js       # Donation claiming
│   │   └── form-validation.js   # Client-side validation
│   └── vendor/
│       └── htmx.min.js      # HTMX for dynamic interactions
├── img/
│   ├── logo/
│   │   ├── cfmp-logo.png    # Main logo
│   │   ├── cfmp-logo.svg    # Vector logo
│   │   └── favicon.ico      # Browser favicon
│   ├── placeholders/
│   │   ├── donation-placeholder.jpg
│   │   └── user-avatar.png
│   └── icons/
│       ├── food-types/      # Food category icons
│       └── ui/              # Interface icons
└── fonts/
    └── custom-fonts/        # Custom typography (if needed)

media/
├── donations/
│   ├── photos/              # User-uploaded donation photos
│   └── documents/           # Any supporting documents
├── profiles/
│   ├── avatars/            # User profile pictures
│   └── organizations/      # Organization logos
└── uploads/
    └── temp/               # Temporary upload storage
```

### CSS Architecture

#### Main Stylesheet (static/css/cfmp.css)
```css
/* CFMP Custom Styles */
:root {
  /* Color Palette */
  --cfmp-primary: #2563eb;      /* Trust blue */
  --cfmp-secondary: #059669;    /* Fresh green */
  --cfmp-accent: #f59e0b;       /* Warm orange */
  --cfmp-danger: #dc2626;       /* Alert red */
  --cfmp-success: #16a34a;      /* Success green */
  --cfmp-warning: #d97706;      /* Warning orange */
  --cfmp-dark: #1f2937;         /* Dark text */
  --cfmp-light: #f8fafc;        /* Light background */
  
  /* Typography */
  --cfmp-font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --cfmp-font-size-base: 16px;
  --cfmp-line-height: 1.6;
  
  /* Spacing */
  --cfmp-spacing-xs: 0.25rem;
  --cfmp-spacing-sm: 0.5rem;
  --cfmp-spacing-md: 1rem;
  --cfmp-spacing-lg: 1.5rem;
  --cfmp-spacing-xl: 2rem;
  
  /* Borders */
  --cfmp-border-radius: 0.375rem;
  --cfmp-border-width: 1px;
  --cfmp-border-color: #e5e7eb;
  
  /* Shadows */
  --cfmp-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --cfmp-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --cfmp-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

/* Global Styles */
body {
  font-family: var(--cfmp-font-family);
  line-height: var(--cfmp-line-height);
  color: var(--cfmp-dark);
}

/* Custom Button Styles */
.btn-cfmp-primary {
  background-color: var(--cfmp-primary);
  border-color: var(--cfmp-primary);
  color: white;
}

.btn-cfmp-primary:hover {
  background-color: #1d4ed8;
  border-color: #1d4ed8;
}

.btn-cfmp-secondary {
  background-color: var(--cfmp-secondary);
  border-color: var(--cfmp-secondary);
  color: white;
}

/* Navigation Enhancements */
.navbar-cfmp {
  background: linear-gradient(135deg, var(--cfmp-primary), var(--cfmp-secondary));
  box-shadow: var(--cfmp-shadow-md);
}

.navbar-brand img {
  height: 32px;
  width: auto;
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, var(--cfmp-primary), var(--cfmp-secondary));
  color: white;
  padding: var(--cfmp-spacing-xl) 0;
}

/* Card Enhancements */
.donation-card {
  border: var(--cfmp-border-width) solid var(--cfmp-border-color);
  border-radius: var(--cfmp-border-radius);
  box-shadow: var(--cfmp-shadow-sm);
  transition: all 0.3s ease;
  height: 100%;
}

.donation-card:hover {
  box-shadow: var(--cfmp-shadow-md);
  transform: translateY(-2px);
}

.donation-card-image {
  height: 200px;
  object-fit: cover;
  border-top-left-radius: var(--cfmp-border-radius);
  border-top-right-radius: var(--cfmp-border-radius);
}

.donation-status-badge {
  position: absolute;
  top: var(--cfmp-spacing-sm);
  right: var(--cfmp-spacing-sm);
  font-size: 0.75rem;
  font-weight: 600;
}

/* Form Styling */
.form-floating > .form-control {
  border-radius: var(--cfmp-border-radius);
}

.form-floating > label {
  color: #6b7280;
}

/* Utility Classes */
.text-cfmp-primary { color: var(--cfmp-primary); }
.text-cfmp-secondary { color: var(--cfmp-secondary); }
.bg-cfmp-light { background-color: var(--cfmp-light); }

/* Responsive Utilities */
@media (max-width: 768px) {
  .donation-card-image {
    height: 150px;
  }
  
  .hero-section {
    padding: var(--cfmp-spacing-lg) 0;
  }
}

/* Loading States */
.loading-spinner {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Accessibility Enhancements */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

/* Focus styles for better accessibility */
.btn:focus,
.form-control:focus,
.form-select:focus {
  box-shadow: 0 0 0 0.25rem rgba(37, 99, 235, 0.25);
}
```

#### Component-Specific Styles
```css
/* static/css/components/cards.css */
.donation-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--cfmp-spacing-lg);
  margin: var(--cfmp-spacing-lg) 0;
}

.donation-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: var(--cfmp-spacing-sm);
}

.expiry-warning {
  color: var(--cfmp-warning);
  font-weight: 600;
}

.expiry-danger {
  color: var(--cfmp-danger);
  font-weight: 600;
}
```

### JavaScript Architecture

#### Main Application Script (static/js/cfmp.js)
```javascript
// CFMP Main JavaScript
class CFMP {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupCSRF();
        this.setupFormValidation();
        this.setupSearchHandlers();
        this.setupModalHandlers();
        this.setupTimeAgo();
    }
    
    // CSRF token setup for AJAX requests
    setupCSRF() {
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Set up CSRF for fetch requests
        window.fetch = new Proxy(window.fetch, {
            apply(target, thisArg, argumentsList) {
                const [url, options = {}] = argumentsList;
                
                if (options.method && options.method.toUpperCase() !== 'GET') {
                    options.headers = {
                        'X-CSRFToken': csrftoken,
                        ...options.headers
                    };
                }
                
                return target.apply(thisArg, [url, options]);
            }
        });
    }
    
    // Enhanced form validation
    setupFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        
        forms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    }
    
    // Real-time search functionality
    setupSearchHandlers() {
        const searchInput = document.querySelector('#donation-search');
        if (searchInput) {
            let searchTimeout;
            
            searchInput.addEventListener('input', (event) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.performSearch(event.target.value);
                }, 300);
            });
        }
    }
    
    async performSearch(query) {
        const url = new URL('/donations/search/', window.location.origin);
        url.searchParams.set('q', query);
        
        try {
            const response = await fetch(url.toString(), {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                const html = await response.text();
                document.querySelector('#search-results').innerHTML = html;
            }
        } catch (error) {
            console.error('Search error:', error);
        }
    }
    
    // Modal handling
    setupModalHandlers() {
        // Donation claim modal
        document.addEventListener('click', (event) => {
            if (event.target.matches('.claim-donation-btn')) {
                this.showClaimModal(event.target.dataset.donationId);
            }
        });
    }
    
    async showClaimModal(donationId) {
        const modal = new bootstrap.Modal(document.getElementById('claimModal'));
        const modalBody = document.querySelector('#claimModal .modal-body');
        
        try {
            const response = await fetch(`/donations/${donationId}/claim/`);
            if (response.ok) {
                modalBody.innerHTML = await response.text();
                modal.show();
            }
        } catch (error) {
            console.error('Error loading claim modal:', error);
        }
    }
    
    // Time ago functionality
    setupTimeAgo() {
        const timeElements = document.querySelectorAll('[data-time]');
        
        timeElements.forEach(element => {
            const timestamp = new Date(element.dataset.time);
            element.textContent = this.timeAgo(timestamp);
        });
    }
    
    timeAgo(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
        if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} days ago`;
        
        return date.toLocaleDateString();
    }
    
    // Utility methods
    showNotification(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const container = document.querySelector('#notification-container') || document.body;
        container.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    new CFMP();
});

// Global utilities
window.CFMP = CFMP;
```

### Media File Handling

#### Model Updates for File Fields
```python
# donations/models.py
import os
from django.db import models
from django.core.validators import FileExtensionValidator

def donation_photo_path(instance, filename):
    """Generate upload path for donation photos"""
    ext = filename.split('.')[-1]
    filename = f"donation_{instance.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return os.path.join('donations', 'photos', filename)

class Donation(models.Model):
    # ... existing fields ...
    
    photo = models.ImageField(
        upload_to=donation_photo_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text="Optional photo of the donation (max 5MB)"
    )
    
    def get_photo_url(self):
        """Get photo URL or placeholder"""
        if self.photo:
            return self.photo.url
        return '/static/img/placeholders/donation-placeholder.jpg'
```

#### Settings Configuration
```python
# settings/base.py
import os

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Security settings for file uploads
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
```

#### Production Configuration (settings/production.py)
```python
# WhiteNoise configuration for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Additional WhiteNoise settings
WHITENOISE_MAX_AGE = 31536000  # 1 year
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'mp4', 'webm', 'woff', 'woff2']

# Media files in production (consider cloud storage)
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
```

### Template Integration

#### Base Template Static Assets Loading
```django
<!-- templates/base.html -->
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="CFMP - Community Food Management Platform">
    
    <title>{% block title %}CFMP - Community Food Management Platform{% endblock %}</title>
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="{% static 'img/logo/favicon.ico' %}">
    
    <!-- Preload critical assets -->
    <link rel="preload" href="{% static 'css/cfmp.css' %}" as="style">
    
    {% block css %}
        <!-- Bootstrap CSS -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <!-- Bootstrap Icons -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
        <!-- Custom CSS -->
        <link href="{% static 'css/cfmp.css' %}" rel="stylesheet">
    {% endblock %}
</head>
<body>
    <!-- ... navbar and content ... -->
    
    {% block js %}
        <!-- Bootstrap JavaScript -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <!-- HTMX for dynamic interactions -->
        <script src="{% static 'js/vendor/htmx.min.js' %}"></script>
        <!-- Main application JavaScript -->
        <script src="{% static 'js/cfmp.js' %}"></script>
    {% endblock %}
</body>
</html>
```

### Build and Deployment Process

#### Management Command for Asset Optimization
```python
# management/commands/optimize_assets.py
from django.core.management.base import BaseCommand
from django.contrib.staticfiles.management.commands.collectstatic import Command as CollectStaticCommand

class Command(BaseCommand):
    help = 'Optimize and collect static assets for production'
    
    def handle(self, *args, **options):
        # Run collectstatic
        collect_command = CollectStaticCommand()
        collect_command.handle(interactive=False, verbosity=1)
        
        self.stdout.write(
            self.style.SUCCESS('Static assets optimized successfully!')
        )
```

## Consequences

**Positive**:
- Professional appearance with custom branding
- Optimized performance through compression and caching
- Scalable asset management for future growth
- Production-ready static file serving
- Enhanced user experience with interactive JavaScript

**Negative**:
- Increased complexity in build process
- Additional dependencies (WhiteNoise, Pillow for image handling)
- Larger initial setup time

**Mitigation Strategies**:
- Comprehensive documentation of asset management
- Automated build scripts for production deployment
- Fallback placeholders for missing images

## Security Considerations

### File Upload Security
- File type validation using Django validators
- Maximum file size limits
- Virus scanning for uploaded files (future enhancement)
- Proper file permissions and directory structure

### Static Asset Security
- Content Security Policy headers for external resources
- Subresource Integrity (SRI) for CDN assets
- HTTPS enforcement for all asset delivery

This ADR establishes a comprehensive static asset and media management system that provides professional styling, optimal performance, and secure file handling for the CFMP platform.