"""Local development settings.

Import all settings from base and apply developer-friendly overrides.
"""

from .base import *  # noqa: F401,F403
from .base import BASE_DIR

# Local development defaults
DEBUG = True

# Useful local defaults: allow all hosts for convenience
ALLOWED_HOSTS = ["*"]

# Disable HTTPS redirects locally even when DJANGO_DEBUG is unset.
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# When developing locally, prefer an on-disk sqlite DB unless overridden.
# Use BASE_DIR from base.py for consistent paths.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
