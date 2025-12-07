# ADR-005: Observability and Monitoring Strategy

**Date**: 2025-12-07  
**Status**: Proposed  
**Related PRD**: Section 6 (FR-008), Section 7 (Reliability), Section 4 (Observability)

## Context

CFMP requires observability features to support the 99% uptime reliability requirement and enable monitoring of key success metrics. This includes:

- Health check endpoints for deployment monitoring (FR-008)
- Structured logging for debugging and operational insights
- Basic monitoring for key business metrics
- Support for tracking success metrics (80% donation claim rate)

## Decision Drivers

- **Reliability**: Support 99% uptime requirement with proper health checks
- **Academic Requirements**: Demonstrate observability concepts from "Best" rubric tier
- **Operational Needs**: Enable debugging and performance monitoring
- **Business Metrics**: Track donation claim rates and system usage
- **MVP Constraints**: Keep simple but functional for Phase 1

## Options Considered

### A) Basic Django Logging Only
```python
import logging
logger = logging.getLogger(__name__)

def create_donation(request):
    logger.info(f"User {request.user} created donation")
```

**Pros**: Simple, built into Django  
**Cons**: No structured logging, no health checks, limited operational value

### B) Health Checks + Structured Logging + Basic Metrics
```python
# Health check endpoint
def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'database': check_database(),
        'version': settings.VERSION
    })

# Structured logging
logger.info("Donation created", extra={
    'user_id': user.id,
    'donation_id': donation.id,
    'food_type': donation.food_type,
    'expires_in_hours': hours_until_expiry
})

# Basic metrics tracking
class MetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        
        logger.info("Request completed", extra={
            'path': request.path,
            'method': request.method,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'user_id': getattr(request.user, 'id', None)
        })
        
        return response
```

**Pros**: Comprehensive observability, structured data, operational value  
**Cons**: More complex setup, additional middleware

### C) Full APM Integration (Sentry, DataDog, etc.)
**Pros**: Professional monitoring, alerting, dashboards  
**Cons**: External dependencies, cost, complexity for academic project

## Decision

**We choose Option B (Health Checks + Structured Logging + Basic Metrics)** because:

1. **Meets Academic Requirements**: Demonstrates observability concepts from "Best" rubric tier
2. **Operational Value**: Provides practical monitoring for deployment and debugging
3. **MVP Appropriate**: Comprehensive but not overly complex for Phase 1
4. **No External Dependencies**: Self-contained within Django application
5. **Foundation for Growth**: Easy to enhance in Phase 2 with APM tools

## Implementation Strategy

### Health Check Endpoints
```python
# monitoring/views.py
from django.http import JsonResponse\nfrom django.db import connection\nfrom django.conf import settings\nfrom django.utils import timezone\nfrom django.core.cache import cache\nimport time\n\ndef health_check(request):\n    \"\"\"Basic health check endpoint\"\"\"\n    return JsonResponse({\n        'status': 'healthy',\n        'timestamp': timezone.now().isoformat(),\n        'version': getattr(settings, 'VERSION', '1.0.0')\n    })\n\ndef health_check_detailed(request):\n    \"\"\"Detailed health check with dependency verification\"\"\"\n    checks = {\n        'database': check_database(),\n        'cache': check_cache(),\n        'disk_space': check_disk_space(),\n    }\n    \n    overall_status = 'healthy' if all(check['status'] == 'healthy' for check in checks.values()) else 'unhealthy'\n    \n    return JsonResponse({\n        'status': overall_status,\n        'timestamp': timezone.now().isoformat(),\n        'checks': checks,\n        'version': getattr(settings, 'VERSION', '1.0.0')\n    })\n\ndef check_database():\n    \"\"\"Check database connectivity and responsiveness\"\"\"\n    try:\n        start_time = time.time()\n        with connection.cursor() as cursor:\n            cursor.execute(\"SELECT 1\")\n        duration_ms = round((time.time() - start_time) * 1000, 2)\n        \n        return {\n            'status': 'healthy',\n            'response_time_ms': duration_ms\n        }\n    except Exception as e:\n        return {\n            'status': 'unhealthy',\n            'error': str(e)\n        }\n\ndef check_cache():\n    \"\"\"Check cache functionality\"\"\"\n    try:\n        test_key = 'health_check_test'\n        test_value = str(timezone.now().timestamp())\n        \n        cache.set(test_key, test_value, timeout=30)\n        retrieved = cache.get(test_key)\n        cache.delete(test_key)\n        \n        if retrieved == test_value:\n            return {'status': 'healthy'}\n        else:\n            return {'status': 'unhealthy', 'error': 'Cache value mismatch'}\n    except Exception as e:\n        return {'status': 'unhealthy', 'error': str(e)}
```

### Structured Logging Configuration
```python
# settings/base.py
LOGGING = {\n    'version': 1,\n    'disable_existing_loggers': False,\n    'formatters': {\n        'verbose': {\n            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',\n            'style': '{',\n        },\n        'json': {\n            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',\n            'format': '%(levelname)s %(asctime)s %(module)s %(funcName)s %(lineno)d %(message)s'\n        },\n    },\n    'handlers': {\n        'file': {\n            'level': 'INFO',\n            'class': 'logging.FileHandler',\n            'filename': 'logs/cfmp.log',\n            'formatter': 'json',\n        },\n        'console': {\n            'level': 'INFO',\n            'class': 'logging.StreamHandler',\n            'formatter': 'verbose',\n        },\n    },\n    'loggers': {\n        'cfmp': {\n            'handlers': ['file', 'console'],\n            'level': 'INFO',\n            'propagate': False,\n        },\n        'django.request': {\n            'handlers': ['file'],\n            'level': 'WARNING',\n            'propagate': False,\n        },\n    },\n}
```

### Business Metrics Tracking
```python
# monitoring/metrics.py\nimport logging\nfrom django.utils import timezone\nfrom datetime import timedelta\n\nmetrics_logger = logging.getLogger('cfmp.metrics')\n\nclass BusinessMetrics:\n    @staticmethod\n    def log_donation_created(donation, user):\n        \"\"\"Log donation creation with business context\"\"\"\n        hours_until_expiry = (donation.expiry_date - timezone.now().date()).days * 24\n        \n        metrics_logger.info(\"Donation created\", extra={\n            'event_type': 'donation_created',\n            'user_id': user.id,\n            'user_type': 'donor',\n            'donation_id': donation.id,\n            'food_type': donation.food_type,\n            'quantity': str(donation.quantity),\n            'location': donation.location,\n            'hours_until_expiry': hours_until_expiry,\n            'expires_soon': hours_until_expiry < 24,\n            'timestamp': timezone.now().isoformat()\n        })\n    \n    @staticmethod\n    def log_donation_claimed(donation, pantry_user):\n        \"\"\"Log donation claim with timing analysis\"\"\"\n        time_to_claim = timezone.now() - donation.created_at\n        hours_to_claim = time_to_claim.total_seconds() / 3600\n        \n        metrics_logger.info(\"Donation claimed\", extra={\n            'event_type': 'donation_claimed',\n            'donation_id': donation.id,\n            'claimed_by_user_id': pantry_user.id,\n            'claimed_by_type': 'pantry',\n            'hours_to_claim': round(hours_to_claim, 2),\n            'food_type': donation.food_type,\n            'quantity': str(donation.quantity),\n            'location': donation.location,\n            'timestamp': timezone.now().isoformat()\n        })\n    \n    @staticmethod\n    def log_donation_expired(donation):\n        \"\"\"Log donation expiry for waste tracking\"\"\"\n        metrics_logger.warning(\"Donation expired unclaimed\", extra={\n            'event_type': 'donation_expired',\n            'donation_id': donation.id,\n            'food_type': donation.food_type,\n            'quantity': str(donation.quantity),\n            'location': donation.location,\n            'days_active': (timezone.now().date() - donation.created_at.date()).days,\n            'timestamp': timezone.now().isoformat()\n        })
```

### Metrics Analysis Management Command
```python
# management/commands/analyze_metrics.py\nfrom django.core.management.base import BaseCommand\nfrom django.utils import timezone\nfrom datetime import timedelta\nfrom donations.models import Donation\n\nclass Command(BaseCommand):\n    help = 'Analyze donation metrics and generate report'\n    \n    def add_arguments(self, parser):\n        parser.add_argument('--days', type=int, default=7, help='Number of days to analyze')\n    \n    def handle(self, *args, **options):\n        days = options['days']\n        start_date = timezone.now() - timedelta(days=days)\n        \n        # Query metrics\n        donations = Donation.objects.filter(created_at__gte=start_date)\n        total_donations = donations.count()\n        claimed_donations = donations.filter(status='claimed').count()\n        expired_donations = donations.filter(status='expired').count()\n        \n        claim_rate = (claimed_donations / total_donations * 100) if total_donations > 0 else 0\n        \n        self.stdout.write(f\"\\n=== CFMP Metrics Report (Last {days} days) ===\")\n        self.stdout.write(f\"Total Donations: {total_donations}\")\n        self.stdout.write(f\"Claimed Donations: {claimed_donations}\")\n        self.stdout.write(f\"Expired Donations: {expired_donations}\")\n        self.stdout.write(f\"Claim Rate: {claim_rate:.1f}%\")\n        self.stdout.write(f\"Target Claim Rate: 80%\")\n        \n        if claim_rate >= 80:\n            self.stdout.write(self.style.SUCCESS(\"✓ Meeting claim rate target\"))\n        else:\n            self.stdout.write(self.style.WARNING(\"⚠ Below claim rate target\"))
```

## Monitoring URLs
```python
# monitoring/urls.py
app_name = 'monitoring'\nurlpatterns = [\n    path('health/', health_check, name='health'),\n    path('health/detailed/', health_check_detailed, name='health_detailed'),\n]\n\n# cfmp/urls.py\nurlpatterns = [\n    # ... other patterns\n    path('monitoring/', include('monitoring.urls')),\n]
```

## Consequences

**Positive**:
- Comprehensive health checks support deployment monitoring
- Structured logging enables operational debugging and analysis
- Business metrics tracking supports success measurement
- Foundation for advanced monitoring in Phase 2
- Academic requirements satisfied (observability from "Best" tier)

**Negative**:
- Additional complexity in application setup
- Log storage requirements increase over time
- JSON logging may require log parsing tools for analysis

**Operational Benefits**:
- Health endpoints enable automated deployment verification
- Structured logs support troubleshooting and performance analysis
- Metrics tracking provides data for business decisions
- Command-line tools support operational reporting

## Testing Strategy
- Test health check endpoints return proper status codes
- Verify detailed health checks catch database/cache issues
- Test business metrics logging with various scenarios
- Performance testing to ensure logging doesn't impact response times

## Deployment Considerations
- Health check endpoints for load balancer configuration
- Log rotation strategy for production deployments
- Monitoring alerts based on health check failures
- Metrics dashboard integration in Phase 2

## Future Enhancements (Phase 2)
- Integration with APM tools (Sentry, DataDog)
- Custom metrics dashboard with charts
- Alerting for critical business metrics
- Performance monitoring and profiling
- Distributed tracing for complex operations