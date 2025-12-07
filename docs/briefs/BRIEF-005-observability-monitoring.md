# BRIEF-005: Observability and Monitoring Implementation

**Date**: 2025-12-07  
**Related ADR**: ADR-005  
**Estimated Effort**: 4-6 hours  
**Phase**: 1 (MVP)

## Objective

Implement comprehensive observability and monitoring features for CFMP to support 99% uptime reliability requirement and enable tracking of key business metrics (80% donation claim rate target).

## Scope

### In Scope
- Health check endpoints for deployment monitoring
- Structured JSON logging with business context
- Basic metrics tracking middleware
- Business metrics for donation lifecycle events
- Management command for metrics analysis
- Log configuration for operational debugging

### Out of Scope
- External APM tool integration (Phase 2)
- Real-time dashboards (Phase 2)
- Alerting systems (Phase 2)
- Performance profiling tools (Phase 2)

## Technical Requirements

### 1. Health Check Endpoints

Create `monitoring` Django app with health check views:

#### Basic Health Check (`/monitoring/health/`)
```python
def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': getattr(settings, 'VERSION', '1.0.0')
    })
```

#### Detailed Health Check (`/monitoring/health/detailed/`)
```python
def health_check_detailed(request):
    checks = {
        'database': check_database(),
        'cache': check_cache(),
        'disk_space': check_disk_space()
    }
    
    overall_status = 'healthy' if all(check['status'] == 'healthy' for check in checks.values()) else 'unhealthy'
    
    return JsonResponse({
        'status': overall_status,
        'timestamp': timezone.now().isoformat(),
        'checks': checks,
        'version': getattr(settings, 'VERSION', '1.0.0')
    })
```

**Expected Behavior**:
- Basic endpoint returns 200 OK with status
- Detailed endpoint validates database connectivity, cache functionality
- Response times under 500ms
- JSON format for programmatic consumption

### 2. Structured Logging Configuration

#### Settings Configuration
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(levelname)s %(asctime)s %(module)s %(funcName)s %(lineno)d %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/cfmp.log',
            'formatter': 'json',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'cfmp': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'cfmp.metrics': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
```

**Expected Behavior**:
- JSON-formatted logs for structured data
- Separate metrics logger for business events
- File and console output handlers
- Log rotation ready configuration

### 3. Metrics Tracking Middleware

#### Request Metrics Middleware
```python
class MetricsMiddleware:
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
            'user_id': getattr(request.user, 'id', None),
            'user_type': self._get_user_type(request.user),
            'timestamp': timezone.now().isoformat()
        })
        
        return response
```

**Expected Behavior**:
- Log all HTTP requests with timing
- Include user context when authenticated
- Structured data for analysis
- Minimal performance impact (<5ms overhead)

### 4. Business Metrics Tracking

#### Donation Lifecycle Events
```python
class BusinessMetrics:
    @staticmethod
    def log_donation_created(donation, user):
        hours_until_expiry = (donation.expiry_date - timezone.now().date()).days * 24
        
        metrics_logger.info("Donation created", extra={
            'event_type': 'donation_created',
            'user_id': user.id,
            'user_type': 'donor',
            'donation_id': donation.id,
            'food_type': donation.food_type,
            'quantity': str(donation.quantity),
            'location': donation.location,
            'hours_until_expiry': hours_until_expiry,
            'expires_soon': hours_until_expiry < 24,
            'timestamp': timezone.now().isoformat()
        })
    
    @staticmethod
    def log_donation_claimed(donation, pantry_user):
        time_to_claim = timezone.now() - donation.created_at
        hours_to_claim = time_to_claim.total_seconds() / 3600
        
        metrics_logger.info("Donation claimed", extra={
            'event_type': 'donation_claimed',
            'donation_id': donation.id,
            'claimed_by_user_id': pantry_user.id,
            'claimed_by_type': 'pantry',
            'hours_to_claim': round(hours_to_claim, 2),
            'food_type': donation.food_type,
            'quantity': str(donation.quantity),
            'location': donation.location,
            'timestamp': timezone.now().isoformat()
        })
    
    @staticmethod
    def log_donation_expired(donation):
        metrics_logger.warning("Donation expired unclaimed", extra={
            'event_type': 'donation_expired',
            'donation_id': donation.id,
            'food_type': donation.food_type,
            'quantity': str(donation.quantity),
            'location': donation.location,
            'days_active': (timezone.now().date() - donation.created_at.date()).days,
            'timestamp': timezone.now().isoformat()
        })
```

**Integration Points**:
- Call `log_donation_created()` in donation creation views
- Call `log_donation_claimed()` in claim action views
- Call `log_donation_expired()` in expiry management commands

### 5. Metrics Analysis Management Command

#### Command: `analyze_metrics`
```python
class Command(BaseCommand):
    help = 'Analyze donation metrics and generate report'
    
    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=7, help='Number of days to analyze')
        parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    
    def handle(self, *args, **options):
        days = options['days']
        start_date = timezone.now() - timedelta(days=days)
        
        # Calculate metrics
        donations = Donation.objects.filter(created_at__gte=start_date)
        total_donations = donations.count()
        claimed_donations = donations.filter(status='claimed').count()
        expired_donations = donations.filter(status='expired').count()
        
        claim_rate = (claimed_donations / total_donations * 100) if total_donations > 0 else 0
        
        # Output report
        if options['format'] == 'json':
            self._output_json_report(...)
        else:
            self._output_text_report(...)
```

**Expected Functionality**:
- Calculate donation claim rates over specified periods
- Compare against 80% target claim rate
- Support JSON output for programmatic use
- Color-coded console output for operational use

## Implementation Tasks

### Task 1: Create Monitoring App
- [ ] Create `monitoring` Django app
- [ ] Implement basic and detailed health check views
- [ ] Create health check helper functions (database, cache, disk)
- [ ] Configure URL routing for health endpoints
- [ ] Test health endpoints return correct responses

### Task 2: Configure Structured Logging
- [ ] Install `python-json-logger` dependency
- [ ] Configure logging settings in Django settings
- [ ] Create logs directory structure
- [ ] Test JSON log output formatting
- [ ] Verify separate metrics logger functionality

### Task 3: Implement Metrics Middleware
- [ ] Create `MetricsMiddleware` class
- [ ] Add middleware to Django settings
- [ ] Implement request timing and context logging
- [ ] Test middleware captures request metrics
- [ ] Verify minimal performance impact

### Task 4: Add Business Metrics
- [ ] Create `BusinessMetrics` utility class
- [ ] Integrate metrics calls into donation views
- [ ] Add metrics calls to existing claim/expiry logic
- [ ] Test metrics logging with various scenarios
- [ ] Verify structured data format

### Task 5: Create Metrics Analysis Command
- [ ] Implement `analyze_metrics` management command
- [ ] Add calculation logic for claim rates and statistics
- [ ] Support multiple output formats (text/JSON)
- [ ] Add command-line argument handling
- [ ] Test command with various date ranges

### Task 6: Integration Testing
- [ ] Test health endpoints under load
- [ ] Verify log file creation and rotation
- [ ] Test metrics analysis with real data
- [ ] Performance test logging overhead
- [ ] Validate all integration points

## Acceptance Criteria

### Health Check Endpoints
- [ ] `/monitoring/health/` returns JSON with status, timestamp, version
- [ ] `/monitoring/health/detailed/` validates database and cache connectivity
- [ ] Health checks respond within 500ms under normal conditions
- [ ] Unhealthy responses return appropriate HTTP status codes

### Structured Logging
- [ ] All application logs written in JSON format to `logs/cfmp.log`
- [ ] Separate metrics logger captures business events
- [ ] Console output uses human-readable format for development
- [ ] Log configuration supports production deployment

### Metrics Tracking
- [ ] All HTTP requests logged with timing and context
- [ ] Donation lifecycle events captured with business context
- [ ] Structured log entries include all required fields
- [ ] Minimal performance overhead (verified with load testing)

### Analysis Tools
- [ ] `analyze_metrics` command calculates accurate claim rates
- [ ] Command supports date range selection and output formats
- [ ] Report identifies when below 80% claim rate target
- [ ] JSON output format suitable for programmatic consumption

### Integration
- [ ] Metrics logging integrated into all donation workflows
- [ ] Health checks work with deployment monitoring tools
- [ ] Log files readable by standard log analysis tools
- [ ] No impact on existing functionality or performance

## Testing Strategy

### Unit Tests
- Health check view responses and status codes
- Metrics middleware timing accuracy
- Business metrics data structure validation
- Management command calculation logic

### Integration Tests
- End-to-end request logging through middleware
- Donation workflow metrics generation
- Health check dependency validation
- Log file creation and formatting

### Performance Tests
- Middleware overhead measurement
- Health check response times under load
- Log write performance with high volume
- Memory usage with extended operation

## Deployment Considerations

### Infrastructure Requirements
- Log directory with write permissions
- Log rotation configuration (logrotate)
- Health check endpoint exposure for load balancers
- Monitoring integration points

### Configuration
- Production log levels and destinations
- Health check timeout configurations
- Metrics retention policies
- Alert thresholds for key metrics

## Success Metrics

### Technical Metrics
- Health check availability: 99.9%
- Health check response time: <500ms
- Log processing overhead: <5ms per request
- Metrics capture rate: 100% of donation events

### Business Metrics
- Donation claim rate tracking accuracy
- Time-to-claim analysis capability
- Expiry rate monitoring
- User behavior insights from logs

This implementation provides the foundation for reliable operations monitoring while supporting the academic requirement to demonstrate observability concepts from the "Best" rubric tier.