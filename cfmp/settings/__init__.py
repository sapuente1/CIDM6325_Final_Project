import os

# Determine which settings to use based on environment variable
ENVIRONMENT = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    from .production import *
else:
    from .development import *

# NUCLEAR OPTION: Force Railway compatibility regardless of other settings
# This will override any ALLOWED_HOSTS setting from above
if os.environ.get('RAILWAY_ENVIRONMENT') or 'railway' in os.environ.get('RAILWAY_PROJECT_NAME', '').lower():
    # Running on Railway - allow all hosts to fix health check issues
    ALLOWED_HOSTS = ['*']
elif 'healthcheck.railway.app' not in ALLOWED_HOSTS:
    # Ensure Railway health check domain is always included
    ALLOWED_HOSTS = list(ALLOWED_HOSTS) + ['healthcheck.railway.app', '.railway.app']
