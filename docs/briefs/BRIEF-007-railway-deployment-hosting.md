# BRIEF-007: Railway Deployment & Production Hosting Implementation

## Goal
Implement complete production deployment strategy for CFMP using Railway platform based on ADR-007, establishing live website with PostgreSQL database, SSL certificates, environment management, and monitoring for professor evaluation.

## Scope (Single PR)
**Files to Create/Modify:**
- `railway.toml` - Railway platform configuration
- `requirements.txt` - Production dependencies with pinned versions
- `cfmp/settings/production.py` - Production-specific Django settings
- `cfmp/health.py` - Health check endpoint for monitoring
- `cfmp/urls.py` - Health check URL routing
- `.env.production` - Production environment template (not committed)
- `deploy.sh` - Local deployment helper script
- `.github/workflows/deploy.yml` - CI/CD pipeline for automated deployment
- `management/commands/deploy.py` - Custom deploy management command
- `Procfile` - Process configuration for Railway

**Non-goals:**
- Custom domain setup (can be added later)
- Advanced monitoring dashboards
- Load balancing or auto-scaling
- Multiple environment stages

## Standards
- **Platform**: Railway for hosting with automatic PostgreSQL and SSL
- **Database**: PostgreSQL with connection pooling and health checks
- **Security**: Environment variables for secrets, HTTPS enforcement
- **Monitoring**: Sentry for error tracking, health check endpoints
- **CI/CD**: GitHub Actions for automated testing and deployment

## Acceptance Criteria

### Railway Platform Setup
- [x] Railway project created with Django service detection
- [x] PostgreSQL database automatically provisioned
- [x] Automatic HTTPS/SSL certificate configuration
- [x] Environment variables configured for production
- [x] Custom domain ready for future setup

### Production Configuration
- [x] Production settings module with security headers
- [x] Database connection with pooling and health checks
- [x] WhiteNoise static file serving with compression
- [x] Redis caching configuration (optional)
- [x] Email backend configuration for notifications

### Deployment Automation
- [x] GitHub Actions pipeline for testing and deployment
- [x] Automated migrations and static file collection
- [x] Health check verification before deployment completion
- [x] Rollback strategy documented and tested
- [x] Local deployment script for manual deploys

### Security Implementation
- [x] All secrets managed through environment variables
- [x] HTTPS enforcement with secure headers
- [x] CSRF and session cookie security
- [x] Content Security Policy headers
- [x] Database SSL connection configuration

### Monitoring & Health Checks
- [x] Health check endpoint responding at `/health/`
- [x] Database connectivity verification
- [x] Cache system status monitoring
- [x] Sentry integration for error tracking
- [x] Production logging configuration

## Technical Implementation Details

### Railway Configuration
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
```

### Production Requirements
```txt
# Production dependencies
Django==5.2.6
gunicorn==21.2.0
psycopg[binary]==3.1.13
whitenoise==6.6.0
django-environ==0.11.2
dj-database-url==2.1.0

# Security and monitoring
django-csp==3.7
sentry-sdk[django]==1.38.0

# Additional production dependencies
Pillow==10.1.0
redis==5.0.1
```

### Production Settings Architecture
```python
# cfmp/settings/production.py
import os
import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *

# Security configuration
DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database with Railway automatic configuration
DATABASES = {
    'default': dj_database_url.parse(
        os.environ['DATABASE_URL'],
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Static files with WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security headers for production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Health Check Implementation
```python
# cfmp/health.py
from django.http import JsonResponse
from django.views import View
from django.db import connection
import django

class HealthCheckView(View):
    def get(self, request):
        # Database connectivity check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        
        # Overall system status
        status = "healthy" if db_status == "healthy" else "unhealthy"
        
        return JsonResponse({
            'status': status,
            'django_version': django.get_version(),
            'database': db_status,
        })
```

### CI/CD Pipeline Configuration
```yaml
# .github/workflows/deploy.yml
name: Deploy to Railway

on:
  push:
    branches: [ main, FALL2025 ]

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
      run: pip install -r requirements.txt
    - name: Run tests
      run: python manage.py test
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/cfmp_test
        SECRET_KEY: test-secret-key
        DEBUG: True

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

## Prompts for AI Implementation

### Phase 1: Railway Platform Setup
"Create Railway deployment configuration for Django CFMP application. Set up railway.toml with nixpacks builder, configure health check path at /health/, implement startup command with migrations and static file collection, and configure production environment variables. Include PostgreSQL database auto-provisioning and gunicorn WSGI server setup."

### Phase 2: Production Settings Configuration
"Implement Django production settings module with security best practices. Configure database connection using dj-database-url for Railway DATABASE_URL, implement WhiteNoise for static file serving, add security headers (HTTPS redirect, secure cookies, CSP), integrate Sentry for error monitoring, and configure email backend for notifications."

### Phase 3: Health Monitoring Implementation
"Create comprehensive health check system with Django view at /health/ endpoint. Implement database connectivity verification, cache system status monitoring, system status aggregation, JSON response format, and error handling for degraded service states. Include monitoring integration for production observability."

### Phase 4: CI/CD Pipeline Setup
"Build GitHub Actions workflow for automated testing and Railway deployment. Configure PostgreSQL service for testing, implement Python environment setup, add dependency installation and test execution, create deployment job with Railway CLI integration, and implement branch-based deployment triggers for main and FALL2025 branches."

### Phase 5: Deployment Automation
"Create deployment automation tools including local deployment script with Railway CLI integration, custom Django management command for safe production deployments, environment variable validation, migration safety checks, static file collection automation, and deployment verification steps."

## Environment Configuration Strategy

### Required Environment Variables
```bash
# Core Django settings
SECRET_KEY=your-production-secret-key-here
DEBUG=False
DJANGO_SETTINGS_MODULE=cfmp.settings.production
ALLOWED_HOSTS=cfmp-production.up.railway.app

# Database (automatically provided by Railway)
DATABASE_URL=postgresql://user:password@host:port/database

# Monitoring and logging
SENTRY_DSN=your-sentry-dsn-for-error-tracking

# Email configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Railway-Specific Configuration
```python
# Railway automatically provides:
# - DATABASE_URL for PostgreSQL
# - PORT for web service binding
# - RAILWAY_ENVIRONMENT for environment detection
# - SSL certificates for custom domains
```

## Migration and Deployment Strategy

### Safe Deployment Process
1. **Pre-deployment**: Automated testing via GitHub Actions
2. **Database Migration**: Safe migration execution with rollback plan
3. **Static Files**: Compressed static file collection with WhiteNoise
4. **Health Check**: Post-deployment verification of all systems
5. **Monitoring**: Error tracking and performance monitoring activation

### Rollback Procedure
```bash
# Railway rollback to previous deployment
railway rollback

# Database rollback (if migrations need reversal)
python manage.py migrate <app_name> <previous_migration>

# Static file cleanup (if needed)
python manage.py collectstatic --clear --noinput
```

## Security Implementation

### Production Security Checklist
- [x] HTTPS enforcement with secure headers
- [x] Environment variables for all sensitive data
- [x] Database SSL connection configuration
- [x] CSRF protection with secure cookies
- [x] Content Security Policy headers
- [x] Regular security dependency updates

### Access Control
- [x] Django admin interface with strong authentication
- [x] Database access limited to application connections
- [x] Production environment isolation
- [x] Audit logging for administrative actions

## Cost Management & Resource Optimization

### Railway Free Tier Optimization
- **Compute**: Efficient gunicorn configuration for memory usage
- **Database**: Connection pooling to minimize connection overhead
- **Storage**: WhiteNoise compression for reduced bandwidth
- **Monitoring**: Sentry free tier for error tracking (10k events/month)

### Resource Monitoring Setup
```python
# Monitor key metrics
# - Database connection count
# - Memory usage per process
# - Request response times
# - Error rates and types
```

## Acceptance Validation

### Live Website Requirements
- [x] Public URL accessible for professor evaluation
- [x] HTTPS certificate and secure connection
- [x] Database connectivity and data persistence
- [x] Admin interface accessible and functional
- [x] Health check endpoint responding correctly

### Production Readiness Validation
- [x] All tests passing in CI pipeline
- [x] Deployment process automated and reproducible
- [x] Error monitoring active and configured
- [x] Performance metrics within acceptable ranges
- [x] Security headers properly configured

### Professor Demonstration Ready
- [x] Stable uptime and reliable access
- [x] Professional appearance and functionality
- [x] Admin access for content management
- [x] Responsive design for various devices
- [x] Error handling and graceful degradation

## Troubleshooting Guide

### Common Deployment Issues
1. **Migration Failures**: Check DATABASE_URL format and permissions
2. **Static File 404s**: Verify WhiteNoise configuration and STATIC_ROOT
3. **Health Check Failures**: Validate database connection and settings
4. **Environment Variable Issues**: Confirm Railway environment configuration
5. **Memory Limits**: Optimize gunicorn worker configuration

### Debugging Production Issues
```bash
# Railway logs access
railway logs

# Health check validation
curl https://cfmp-production.up.railway.app/health/

# Database connection test
railway run python manage.py dbshell
```

This brief provides comprehensive guidance for implementing the Railway deployment strategy defined in ADR-007, ensuring CFMP becomes a live, production-ready website suitable for academic evaluation and demonstration.