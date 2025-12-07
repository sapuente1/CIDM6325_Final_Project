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