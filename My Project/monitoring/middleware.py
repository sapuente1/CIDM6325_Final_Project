"""
Metrics tracking middleware for CFMP observability
"""
import time
import logging
from django.utils import timezone


class MetricsMiddleware:
    """Middleware to track request metrics and timing"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('cfmp.metrics')
    
    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        
        self.logger.info("Request completed", extra={
            'event_type': 'request_completed',
            'path': request.path,
            'method': request.method,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') and request.user.is_authenticated else None,
            'user_type': self._get_user_type(request.user) if hasattr(request, 'user') and request.user.is_authenticated else None,
            'timestamp': timezone.now().isoformat()
        })
        
        return response
    
    def _get_user_type(self, user):
        """Determine the type of user for metrics context"""
        if not user or not user.is_authenticated:
            return None
        
        if user.is_superuser:
            return 'admin'
        elif user.is_staff:
            return 'staff'
        elif hasattr(user, 'donor'):
            return 'donor'
        elif hasattr(user, 'pantry'):
            return 'pantry'
        else:
            return 'regular'