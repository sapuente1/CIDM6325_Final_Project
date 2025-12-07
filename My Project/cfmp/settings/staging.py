"""
Staging settings for CFMP project.
Similar to production but with debug enabled for testing.
"""

from .production import *

# Override debug for staging
DEBUG = env.bool('DEBUG', default=True)

# Staging-specific logging
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['cfmp']['level'] = 'DEBUG'

# Allow more relaxed security for staging
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '*.railway.app'])

# Staging-specific middleware (add debug toolbar if needed)
if DEBUG:
    try:
        import debug_toolbar
        INSTALLED_APPS.insert(-1, 'debug_toolbar')
        MIDDLEWARE.insert(-1, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        INTERNAL_IPS = ['127.0.0.1']
    except ImportError:
        pass