# ADR-007: Deployment & Hosting Strategy

**Date**: 2025-12-07  
**Status**: Proposed  
**Related PRD**: Section 8 (Technical Requirements), Section 9 (Deployment), Section 10 (Production Operations)

## Context

CFMP requires a production deployment strategy to provide the professor with a live, accessible website. The application needs hosting infrastructure, database services, environment management, and domain configuration for academic demonstration and evaluation.

Current deployment gaps:
- No production hosting platform selected
- Missing production database configuration (PostgreSQL)
- No SSL/TLS certificate management
- Missing environment variable management for production
- No CI/CD pipeline for automated deployments
- No monitoring and logging for production environment

## Decision Drivers

- **Academic Requirements**: Professor needs live website URL for evaluation
- **Production Readiness**: Demonstrate enterprise deployment practices
- **Cost Effectiveness**: Free or low-cost hosting for student project
- **Reliability**: Stable uptime for demonstration purposes
- **Scalability**: Handle expected academic evaluation traffic
- **Modern Practices**: Industry-standard deployment workflow

## Options Considered

### A) Heroku (Traditional Choice)
```yaml
# heroku.yml
build:
  docker:
    web: Dockerfile
    
release:
  image: web
  command:
    - python manage.py migrate
```

**Pros**: Django-optimized, easy deployment, addon ecosystem  
**Cons**: No longer free, expensive for students, limited free tier

### B) Railway (Recommended)
```toml
# railway.toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python manage.py migrate && gunicorn cfmp.wsgi"

[environments.production.variables]
DJANGO_SETTINGS_MODULE = "cfmp.settings.production"
```

**Pros**: Free tier, modern platform, excellent Django support, automatic SSL  
**Cons**: Newer platform, smaller ecosystem than Heroku

### C) Render.com
```yaml
# render.yaml
services:
  - type: web
    name: cfmp
    runtime: python3
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python manage.py migrate && gunicorn cfmp.wsgi"
```

**Pros**: Free tier, established platform, good documentation  
**Cons**: Limited database options on free tier, slower cold starts

### D) PythonAnywhere
```bash
# Manual deployment process
# Upload files via web interface
# Configure WSGI manually
```

**Pros**: Django-specific, educational discounts, beginner-friendly  
**Cons**: Manual deployment process, limited automation, legacy interface

## Decision

**We choose Railway** because:

1. **Free Tier**: $5/month credit covers student project needs
2. **Modern Platform**: Git-based deployments, infrastructure-as-code
3. **Django Optimized**: Excellent Python/Django support with automatic detection
4. **Database Included**: PostgreSQL included in free tier
5. **SSL/Domain**: Automatic HTTPS and custom domain support
6. **Academic Friendly**: Simple setup perfect for course demonstrations
7. **Industry Relevant**: Modern deployment practices students should learn

## Implementation Strategy

### Platform Setup and Configuration

#### Railway Project Configuration
```toml
# railway.toml
[build]
builder = "nixpacks"
buildCommand = "pip install -r requirements.txt"

[deploy]
healthcheckPath = "/health/"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
startCommand = "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:$PORT cfmp.wsgi:application"

[environments.production]
[environments.production.variables]
DJANGO_SETTINGS_MODULE = "cfmp.settings.production"
DEBUG = "False"
ALLOWED_HOSTS = "cfmp-production.up.railway.app"
```

#### Requirements.txt (Production Dependencies)
```txt
# Production requirements
Django==5.2.6
gunicorn==21.2.0
psycopg[binary]==3.1.13
whitenoise==6.6.0
django-environ==0.11.2

# Development tools (conditional install)
django-extensions==3.2.3
django-debug-toolbar==4.2.0

# Security and monitoring
django-csp==3.7
sentry-sdk[django]==1.38.0

# Additional production dependencies
Pillow==10.1.0
redis==5.0.1
celery==5.3.4
```

### Database Strategy

#### PostgreSQL Configuration
```python
# cfmp/settings/production.py
import dj_database_url

# Railway automatically provides DATABASE_URL
DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Connection pooling for performance
DATABASES['default']['OPTIONS'] = {
    'MAX_CONNS': 20,
    'OPTIONS': {
        'MAX_CONNS': 20,
    }
}
```

#### Migration Strategy
```python
# Custom management command for safe migrations
# management/commands/deploy.py
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Deploy application with safe migrations'
    
    def handle(self, *args, **options):
        self.stdout.write('Starting deployment...')
        
        # Check database connectivity
        call_command('check', '--database', 'default')
        
        # Run migrations
        call_command('migrate', '--no-input')
        
        # Collect static files
        call_command('collectstatic', '--no-input', '--clear')
        
        # Create superuser if needed (production)
        self.create_superuser_if_needed()
        
        self.stdout.write(self.style.SUCCESS('Deployment completed successfully'))
```

### Environment Configuration

#### Environment Variables Management
```python
# .env.production (template - not committed)
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=cfmp-production.up.railway.app,cfmp.example.com
DJANGO_SETTINGS_MODULE=cfmp.settings.production

# Email configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Monitoring (Sentry)
SENTRY_DSN=your-sentry-dsn-here

# Redis (for caching/sessions)
REDIS_URL=redis://localhost:6379/1
```

#### Settings Architecture Enhancement
```python
# cfmp/settings/production.py
import os
import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from .base import *

# Security settings
DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database configuration
DATABASES = {
    'default': dj_database_url.parse(
        os.environ['DATABASE_URL'],
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Static files (WhiteNoise)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MAX_AGE = 31536000  # 1 year

# Security headers
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Monitoring with Sentry
sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[
        DjangoIntegration(transaction_style='url'),
        LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
    ],
    traces_sample_rate=0.1,
    send_default_pii=True,
    environment='production',
)

# Caching with Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'KEY_PREFIX': 'cfmp',
        'TIMEOUT': 300,
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Email configuration
if os.environ.get('EMAIL_HOST'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ['EMAIL_HOST']
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'cfmp': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### Deployment Automation

#### GitHub Actions CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy to Railway

on:
  push:
    branches: [ main, FALL2025 ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: cfmp_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python manage.py test
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/cfmp_test
        SECRET_KEY: test-secret-key
        DEBUG: True
    
    - name: Check deployment readiness
      run: |
        python manage.py check --deploy
      env:
        SECRET_KEY: test-secret-key
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/cfmp_test
        DEBUG: False
        ALLOWED_HOSTS: localhost

  deploy:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/FALL2025'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to Railway
      uses: railwayapp/railway-deploy@v1
      with:
        railway_token: ${{ secrets.RAILWAY_TOKEN }}
        service: cfmp-production
```

#### Deployment Script
```bash
#!/bin/bash
# deploy.sh - Local deployment helper

set -e

echo "🚀 Starting CFMP deployment..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    curl -fsSL https://railway.app/install.sh | sh
fi

# Check for required environment variables
if [ -z "$RAILWAY_TOKEN" ]; then
    echo "❌ RAILWAY_TOKEN not set. Please set your Railway token."
    exit 1
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login --token $RAILWAY_TOKEN

# Deploy the application
echo "📦 Deploying to Railway..."
railway up --detach

# Run migrations
echo "🗄️ Running migrations..."
railway run python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
railway run python manage.py collectstatic --noinput

# Check deployment health
echo "🏥 Checking deployment health..."
railway run python manage.py check --deploy

echo "✅ Deployment completed successfully!"
echo "🌐 Your application is available at: https://cfmp-production.up.railway.app"
```

### Domain and SSL Configuration

#### Custom Domain Setup
```python
# Domain configuration in Railway
# 1. Add custom domain in Railway dashboard
# 2. Configure DNS records:
#    CNAME: www.cfmp-demo.com -> cfmp-production.up.railway.app
#    A: cfmp-demo.com -> Railway IP (provided in dashboard)

# Update allowed hosts
ALLOWED_HOSTS = [
    'cfmp-production.up.railway.app',
    'cfmp-demo.com',
    'www.cfmp-demo.com',
]

# Force HTTPS redirect
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### Health Monitoring and Logging

#### Health Check Endpoint
```python
# cfmp/health.py
from django.http import JsonResponse
from django.views import View
from django.db import connection
from django.core.cache import cache
import django

class HealthCheckView(View):
    def get(self, request):
        # Check database connectivity
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        
        # Check cache connectivity
        try:
            cache.set('health_check', 'ok', 10)
            cache_status = "healthy" if cache.get('health_check') == 'ok' else "unhealthy"
        except Exception as e:
            cache_status = f"unhealthy: {str(e)}"
        
        # Overall status
        status = "healthy" if db_status == "healthy" and cache_status == "healthy" else "unhealthy"
        
        return JsonResponse({
            'status': status,
            'django_version': django.get_version(),
            'database': db_status,
            'cache': cache_status,
        })

# cfmp/urls.py
from .health import HealthCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health_check'),
    # ... other patterns
]
```

## Consequences

**Positive**:
- Live website available for professor evaluation
- Modern deployment practices demonstrated
- Scalable infrastructure for future enhancements
- Professional domain and SSL configuration
- Automated CI/CD pipeline for reliable deployments
- Comprehensive monitoring and logging

**Negative**:
- Additional complexity in deployment configuration
- Dependency on external hosting platform
- Potential costs if usage exceeds free tier
- Learning curve for Railway platform

**Mitigation Strategies**:
- Comprehensive deployment documentation
- Local development environment mirrors production
- Automated testing before deployment
- Backup deployment strategy (Render.com as fallback)

## Security Considerations

### Production Security
- Environment variables for all secrets
- HTTPS enforcement with secure headers
- Database connection security with SSL
- Content Security Policy headers
- Regular security updates and dependency scanning

### Access Control
- Secure admin interface with strong passwords
- Limited database access permissions
- Production environment isolation
- Audit logging for admin actions

## Cost Management

### Free Tier Optimization
- Railway: $5/month credit (sufficient for academic project)
- PostgreSQL: Included in Railway free tier
- SSL certificates: Automatic and free
- Monitoring: Sentry free tier for error tracking

### Resource Monitoring
- Database usage tracking
- Memory and CPU monitoring
- Request volume analysis
- Cost alerts when approaching limits

This ADR establishes a complete deployment strategy that provides a professional, live website for academic evaluation while demonstrating industry-standard practices and maintaining cost effectiveness for student projects.