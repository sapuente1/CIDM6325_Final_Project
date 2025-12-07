# ADR-006: Deployment and Environment Strategy

**Date**: 2025-12-07  
**Status**: Proposed  
**Related PRD**: Section 6 (FR-010), Section 7 (Security), Section 8 (Dependencies)

## Context

CFMP requires a deployment strategy that supports secure production deployment with proper environment management. Key requirements include:

- Environment variable management for secure settings (FR-010)
- Static file serving for production deployment
- Database configuration for development vs. production
- Security settings (HTTPS, CSRF protection) as per NFR requirements
- Academic demonstration of deployment concepts from rubric

## Decision Drivers

- **Security**: Proper secret management and secure production settings
- **Academic Requirements**: Demonstrate deployment concepts from "Baseline" tier
- **Development Efficiency**: Easy local development setup
- **Production Readiness**: Deployable to common platforms (Heroku, Railway, etc.)
- **Django Best Practices**: Standard settings organization patterns

## Options Considered

### A) Single settings.py with Environment Detection
```python
import os
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
if DEBUG:
    # development settings
else:
    # production settings
```

**Pros**: Simple, single file  
**Cons**: Complex conditionals, hard to maintain, mixing concerns

### B) Split Settings with Environment Variables
```
settings/
├── __init__.py
├── base.py       # Common settings
├── development.py # Development overrides
└── production.py  # Production overrides
```

**Pros**: Clear separation, maintainable, Django best practice  
**Cons**: Slightly more complex setup

### C) Settings with python-dotenv and .env Files
Combine split settings with .env file management

**Pros**: Easy secret management, clear environment separation  
**Cons**: Additional dependency

## Decision

**We choose Option B (Split Settings) with selective use of environment variables** because:

1. **Django Best Practices**: Standard pattern recommended by Django documentation
2. **Clear Separation**: Development and production concerns separated
3. **Academic Value**: Demonstrates proper settings management concepts
4. **Maintainability**: Easy to understand and modify
5. **No Extra Dependencies**: Uses only Django and Python standard library

## Implementation Strategy

### Base Settings (settings/base.py)
```python
import os\nfrom pathlib import Path\n\n# Build paths\nBASE_DIR = Path(__file__).resolve().parent.parent.parent\n\n# Security warning: keep the secret key used in production secret!\nSECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-not-for-production')\n\n# Application definition\nDJANGO_APPS = [\n    'django.contrib.admin',\n    'django.contrib.auth',\n    'django.contrib.contenttypes',\n    'django.contrib.sessions',\n    'django.contrib.messages',\n    'django.contrib.staticfiles',\n]\n\nTHIRD_PARTY_APPS = [\n    'crispy_forms',\n    'crispy_bootstrap5',\n]\n\nLOCAL_APPS = [\n    'donations',\n    'accounts',\n    'monitoring',\n]\n\nINSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS\n\nMIDDLEWARE = [\n    'django.middleware.security.SecurityMiddleware',\n    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files\n    'django.contrib.sessions.middleware.SessionMiddleware',\n    'django.middleware.common.CommonMiddleware',\n    'django.middleware.csrf.CsrfViewMiddleware',\n    'django.contrib.auth.middleware.AuthenticationMiddleware',\n    'django.contrib.messages.middleware.MessageMiddleware',\n    'django.middleware.clickjacking.XFrameOptionsMiddleware',\n    'monitoring.middleware.MetricsMiddleware',  # Custom metrics\n]\n\nROOT_URLCONF = 'cfmp.urls'\n\n# Database (will be overridden in environment-specific settings)\nDATABASES = {\n    'default': {\n        'ENGINE': 'django.db.backends.sqlite3',\n        'NAME': BASE_DIR / 'db.sqlite3',\n    }\n}\n\n# Internationalization\nLANGUAGE_CODE = 'en-us'\nTIME_ZONE = 'UTC'\nUSE_I18N = True\nUSE_TZ = True\n\n# Static files (CSS, JavaScript, Images)\nSTATIC_URL = '/static/'\nSTATIC_ROOT = BASE_DIR / 'staticfiles'\nSTATICFILES_DIRS = [\n    BASE_DIR / 'static',\n]\n\n# Media files\nMEDIA_URL = '/media/'\nMEDIA_ROOT = BASE_DIR / 'media'\n\n# Default primary key field type\nDEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'\n\n# Forms\nCRISPY_ALLOWED_TEMPLATE_PACKS = \"bootstrap5\"\nCRISPY_TEMPLATE_PACK = \"bootstrap5\"\n\n# Authentication\nLOGIN_URL = 'auth:login'\nLOGIN_REDIRECT_URL = '/'\nLOGOUT_REDIRECT_URL = '/'\n\n# Logging (basic configuration)\nLOGGING = {\n    'version': 1,\n    'disable_existing_loggers': False,\n    'handlers': {\n        'file': {\n            'level': 'INFO',\n            'class': 'logging.FileHandler',\n            'filename': BASE_DIR / 'logs' / 'cfmp.log',\n        },\n        'console': {\n            'level': 'INFO',\n            'class': 'logging.StreamHandler',\n        },\n    },\n    'loggers': {\n        'cfmp': {\n            'handlers': ['file', 'console'],\n            'level': 'INFO',\n        },\n    },\n}
```

### Development Settings (settings/development.py)
```python
from .base import *\n\n# Debug mode\nDEBUG = True\n\n# Allowed hosts for development\nALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']\n\n# Database for development (SQLite)\nDATABASES = {\n    'default': {\n        'ENGINE': 'django.db.backends.sqlite3',\n        'NAME': BASE_DIR / 'db.sqlite3',\n    }\n}\n\n# Cache (simple local memory cache for development)\nCACHES = {\n    'default': {\n        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',\n        'LOCATION': 'cfmp-dev-cache',\n    }\n}\n\n# Email backend for development (console)\nEMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'\n\n# Django Debug Toolbar (if installed)\ntry:\n    import debug_toolbar\n    INSTALLED_APPS += ['debug_toolbar']\n    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']\n    INTERNAL_IPS = ['127.0.0.1']\nexcept ImportError:\n    pass\n\n# Less strict security for development\nCSRF_COOKIE_SECURE = False\nSESSION_COOKIE_SECURE = False
```

### Production Settings (settings/production.py)
```python
from .base import *\nimport os\n\n# Security settings\nDEBUG = False\nSECRET_KEY = os.environ.get('SECRET_KEY')\n\n# Allowed hosts from environment\nALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')\n\n# Database configuration (PostgreSQL for production)\nDATABASES = {\n    'default': {\n        'ENGINE': 'django.db.backends.postgresql',\n        'NAME': os.environ.get('DB_NAME'),\n        'USER': os.environ.get('DB_USER'),\n        'PASSWORD': os.environ.get('DB_PASSWORD'),\n        'HOST': os.environ.get('DB_HOST', 'localhost'),\n        'PORT': os.environ.get('DB_PORT', '5432'),\n    }\n}\n\n# Cache configuration (Redis for production)\nCACHES = {\n    'default': {\n        'BACKEND': 'django.core.cache.backends.redis.RedisCache',\n        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),\n        'KEY_PREFIX': 'cfmp',\n        'TIMEOUT': 300,\n    }\n}\n\n# Static files (WhiteNoise configuration)\nSTATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'\n\n# Security settings\nSECURE_BROWSER_XSS_FILTER = True\nSECURE_CONTENT_TYPE_NOSNIFF = True\nX_FRAME_OPTIONS = 'DENY'\n\n# HTTPS settings (uncomment for HTTPS deployment)\n# SECURE_SSL_REDIRECT = True\n# SESSION_COOKIE_SECURE = True\n# CSRF_COOKIE_SECURE = True\n# SECURE_HSTS_SECONDS = 31536000\n# SECURE_HSTS_INCLUDE_SUBDOMAINS = True\n# SECURE_HSTS_PRELOAD = True\n\n# Email configuration\nEMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'\nEMAIL_HOST = os.environ.get('EMAIL_HOST')\nEMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))\nEMAIL_USE_TLS = True\nEMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')\nEMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')\nDEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')\n\n# Logging for production\nLOGGING['handlers']['file']['filename'] = '/tmp/cfmp.log'  # Use /tmp for most platforms\nLOGGING['loggers']['cfmp']['level'] = 'WARNING'\n\n# Performance settings\nUSE_TZ = True\nUSE_I18N = False  # Disable if not using internationalization
```

### Environment Management
```python
# settings/__init__.py\nimport os\n\n# Determine which settings to use based on environment variable\nENVIRONMENT = os.environ.get('DJANGO_ENVIRONMENT', 'development')\n\nif ENVIRONMENT == 'production':\n    from .production import *\nelse:\n    from .development import *
```

### Development .env Template
```bash
# .env.example (template for local development)\nDJANGO_ENVIRONMENT=development\nSECRET_KEY=your-secret-key-here\n\n# Database (uncomment if using PostgreSQL locally)\n# DB_NAME=cfmp_dev\n# DB_USER=cfmp_user\n# DB_PASSWORD=cfmp_password\n# DB_HOST=localhost\n# DB_PORT=5432\n\n# Cache (uncomment if using Redis locally)\n# REDIS_URL=redis://localhost:6379/1\n\n# Email (for testing)\n# EMAIL_HOST=smtp.gmail.com\n# EMAIL_HOST_USER=your-email@gmail.com\n# EMAIL_HOST_PASSWORD=your-app-password\n# DEFAULT_FROM_EMAIL=cfmp@example.com
```

### Production Environment Variables
```bash
# Required production environment variables\nDJANGO_ENVIRONMENT=production\nSECRET_KEY=your-production-secret-key\nALLOWED_HOSTS=yourdomain.com,www.yourdomain.com\n\n# Database\nDB_NAME=cfmp_production\nDB_USER=cfmp_user\nDB_PASSWORD=secure-database-password\nDB_HOST=your-db-host\nDB_PORT=5432\n\n# Cache\nREDIS_URL=redis://your-redis-host:6379/0\n\n# Email\nEMAIL_HOST=smtp.sendgrid.net\nEMAIL_HOST_USER=apikey\nEMAIL_HOST_PASSWORD=your-sendgrid-api-key\nDEFAULT_FROM_EMAIL=noreply@yourdomain.com\n\n# Optional: Sentry for error tracking\n# SENTRY_DSN=your-sentry-dsn
```

## Django Management
```python
# manage.py (updated for environment-based settings)\nimport os\nimport sys\n\nif __name__ == '__main__':\n    # Default to development if no environment specified\n    os.environ.setdefault('DJANGO_ENVIRONMENT', 'development')\n    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfmp.settings')\n    \n    try:\n        from django.core.management import execute_from_command_line\n    except ImportError as exc:\n        raise ImportError(\n            \"Couldn't import Django. Are you sure it's installed and \"\n            \"available on your PYTHONPATH environment variable? Did you \"\n            \"forget to activate a virtual environment?\"\n        ) from exc\n    \n    execute_from_command_line(sys.argv)
```

## Deployment Scripts
```bash
#!/bin/bash\n# deploy.sh - Production deployment script\n\necho \"Starting CFMP deployment...\"\n\n# Install dependencies\nuv pip install -r requirements.txt\n\n# Run migrations\nDJANGO_ENVIRONMENT=production python manage.py migrate\n\n# Collect static files\nDJANGO_ENVIRONMENT=production python manage.py collectstatic --noinput\n\n# Create superuser if needed (interactive)\n# DJANGO_ENVIRONMENT=production python manage.py createsuperuser\n\necho \"Deployment complete!\"\necho \"Remember to set environment variables in your hosting platform\"\necho \"Health check available at: /monitoring/health/\"
```

## Consequences

**Positive**:
- Clear separation between development and production settings
- Secure secret management via environment variables
- Easy deployment to common platforms (Heroku, Railway, etc.)
- Supports both SQLite (dev) and PostgreSQL (prod) seamlessly
- Academic requirements satisfied for deployment concepts

**Negative**:
- Multiple settings files require understanding of import chain
- Environment variable management requires careful documentation
- Production deployment requires more configuration steps

**Security Benefits**:
- Secret keys never committed to version control
- Production security settings properly configured
- HTTPS support ready for deployment
- CSRF and XSS protection enabled

## Platform-Specific Deployment Notes

### Railway.app
```bash
# Railway automatically detects Python apps\n# Set environment variables in Railway dashboard\n# Add Procfile:\nweb: gunicorn cfmp.wsgi:application --bind 0.0.0.0:$PORT
```

### Heroku
```bash
# Procfile\nweb: gunicorn cfmp.wsgi:application --bind 0.0.0.0:$PORT\nrelease: python manage.py migrate
```

### Traditional VPS
```bash
# Use systemd service with gunicorn\n# Configure nginx as reverse proxy\n# Set environment variables in systemd service file
```

## Testing Strategy
- Test settings loading in both development and production modes
- Verify environment variable handling with missing values
- Test static file collection and serving
- Validate database migrations in both environments
- Test health check endpoints in deployed environment

## Security Checklist
- ✅ SECRET_KEY from environment variable
- ✅ DEBUG=False in production
- ✅ ALLOWED_HOSTS properly configured
- ✅ HTTPS settings ready for deployment
- ✅ CSRF protection enabled
- ✅ XSS filtering enabled
- ✅ Static files served securely

This deployment strategy provides a solid foundation for both academic demonstration and real-world deployment while maintaining Django best practices.