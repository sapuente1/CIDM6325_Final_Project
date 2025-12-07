import time
import shutil
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache


def health_check(request):
    """Basic health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': getattr(settings, 'VERSION', '1.0.0')
    })


def health_check_detailed(request):
    """Detailed health check with dependency verification"""
    checks = {
        'database': check_database(),
        'cache': check_cache(),
        'disk_space': check_disk_space(),
    }
    
    overall_status = 'healthy' if all(check['status'] == 'healthy' for check in checks.values()) else 'unhealthy'
    
    return JsonResponse({
        'status': overall_status,
        'timestamp': timezone.now().isoformat(),
        'checks': checks,
        'version': getattr(settings, 'VERSION', '1.0.0')
    })


def check_database():
    """Check database connectivity and responsiveness"""
    try:
        start_time = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        duration_ms = round((time.time() - start_time) * 1000, 2)
        
        return {
            'status': 'healthy',
            'response_time_ms': duration_ms
        }
    except Exception as e:  # noqa: BLE001
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


def check_cache():
    """Check cache functionality"""
    try:
        test_key = 'health_check_test'
        test_value = str(timezone.now().timestamp())
        
        cache.set(test_key, test_value, timeout=30)
        retrieved = cache.get(test_key)
        cache.delete(test_key)
        
        if retrieved == test_value:
            return {'status': 'healthy'}
        else:
            return {'status': 'unhealthy', 'error': 'Cache value mismatch'}
    except Exception as e:  # noqa: BLE001
        return {'status': 'unhealthy', 'error': str(e)}


def check_disk_space():
    """Check available disk space"""
    try:
        total, _, free = shutil.disk_usage('.')
        free_percent = (free / total) * 100
        
        if free_percent > 10:  # At least 10% free space
            return {
                'status': 'healthy',
                'free_space_percent': round(free_percent, 2)
            }
        else:
            return {
                'status': 'unhealthy',
                'error': f'Low disk space: {free_percent:.1f}% free',
                'free_space_percent': round(free_percent, 2)
            }
    except Exception as e:  # noqa: BLE001
        return {
            'status': 'unhealthy',
            'error': str(e)
        }
