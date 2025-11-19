# TravelMathLite Caching Configuration

## Overview

TravelMathLite uses Django's caching framework to improve performance by storing expensive computation results and reducing database queries. This document describes the cache backend configuration, environment variables, and operational guidelines.

**Related:** ADR-1.0.10 — Caching Strategy

## Caching Strategies

TravelMathLite uses multiple caching strategies:

1. **Per-view caching** — Entire view responses cached with `@cache_page` decorator
2. **Low-level caching** — Manual caching of expensive computations and queries
3. **Template fragment caching** — Partial template caching (future)

### Per-View Caching

Hot-path views are cached using Django's `@cache_page` decorator:

| View | TTL | Cache Behavior |
|------|-----|----------------|
| Search results (`SearchView`) | 5 minutes (300s) | Varies by query string (`q`, `page`) |
| Distance calculator (`DistanceCalculatorView`) | 10 minutes (600s) | GET requests only; POST bypasses cache |
| Cost calculator (`CostCalculatorView`) | 10 minutes (600s) | GET requests only; POST bypasses cache |

**Cache key variation:**

- Full URL including all query parameters
- Method (GET only; POST/PUT/DELETE bypass cache)
- HTTP headers (Accept-Language, Cookie if session-based)

**Example:**

```python
# In apps/search/views.py
@method_decorator(cache_page(300), name="dispatch")  # 5 minutes
class SearchView(TemplateView):
    # ... view logic
```

### Low-Level Caching

Expensive operations (database queries, CPU-intensive calculations) are cached manually using Django's low-level cache API:

**TTL:** 15 minutes (900 seconds)

#### Airport Queries

Utility functions in `apps/airports/utils.py`:

| Function | Cache Key Pattern | Purpose |
|----------|-------------------|---------|
| `get_airports_by_country(code)` | `travelmathlite:airports:country:{code}` | Airports filtered by ISO country code |
| `get_airports_by_city(name)` | `travelmathlite:airports:city:{name}` | Airports in a specific city (case-insensitive) |
| `get_airports_by_iata(code)` | `travelmathlite:airports:iata:{code}` | Single airport by IATA code |
| `get_nearest_airports_cached(lat, lon, limit, radius)` | `travelmathlite:nearest:airports:{lat}:{lon}:{limit}:{radius}` | Nearest airports within radius |
| `search_airports_cached(query)` | `travelmathlite:airports:search:{query}` | Full-text search results |

**Cache invalidation:**

```python
from apps.airports.utils import clear_airport_cache, invalidate_airport_cache

# Clear all airport-related cache entries
clear_airport_cache()

# Invalidate cache for a specific airport (after updates)
invalidate_airport_cache(airport_id=123)
```

**Example usage:**

```python
from apps.airports.utils import get_airports_by_country, get_airports_by_iata

# First call: cache miss, database query executed
airports = get_airports_by_country("US")

# Second call: cache hit, returns cached list
airports = get_airports_by_country("US")

# Lookup by IATA code
airport = get_airports_by_iata("DFW")
if airport:
    print(f"Found: {airport.name}")
```

#### Calculator Functions

Utility functions in `apps/calculators/utils.py`:

| Function | Cache Key Pattern | Purpose |
|----------|-------------------|---------|
| `haversine_distance_cached(lat1, lon1, lat2, lon2)` | `travelmathlite:distance:haversine:{coords}` | Great-circle distance between coordinates |
| `calculate_route_distance_cached(...)` | `travelmathlite:distance:route:{coords}:{factor}` | Flight + driving distances with route factor |
| `calculate_fuel_cost_cached(distance, economy, price)` | `travelmathlite:cost:fuel:{params}` | Fuel cost estimation |
| `calculate_trip_metrics_cached(...)` | `travelmathlite:trip:metrics:{coords}:{params}` | Comprehensive trip metrics |

**Cache invalidation:**

```python
from apps.calculators.utils import clear_calculator_cache

# Clear all calculator-related cache entries
clear_calculator_cache()

# Clear specific pattern (e.g., all distance calculations)
clear_calculator_cache(pattern="travelmathlite:distance:*")
```

**Example usage:**

```python
from apps.calculators.utils import haversine_distance_cached, calculate_trip_metrics_cached

# Distance calculation (coordinates rounded to 4 decimals for cache key)
distance = haversine_distance_cached(32.7767, -96.7970, 29.7604, -95.3698)

# Comprehensive trip metrics
metrics = calculate_trip_metrics_cached(
    32.7767, -96.7970,  # Dallas
    29.7604, -95.3698,  # Houston
    route_factor=1.2,
    fuel_economy_l_per_100km=7.5,
    fuel_price_per_liter=1.50,
    avg_speed_kmh=80.0,
)
print(f"Flight: {metrics['flight_km']} km")
print(f"Driving: {metrics['driving_km']} km")
print(f"Fuel cost: ${metrics['fuel_cost']:.2f}")
print(f"Driving time: {metrics['driving_hours']:.1f} hours")
```

**Cache key design:**

- **Coordinates rounded to 4 decimals** (~11 meter precision) to improve cache hit rates
- **Parameters normalized** (lowercase, stripped) for consistent keys
- **Composite keys** include all relevant parameters to prevent stale data

## Cache Backends

### Local Development

For local development, TravelMathLite uses **locmem** (local memory cache):

- **Backend:** `django.core.cache.backends.locmem.LocMemCache`
- **Location:** `travelmathlite-cache`
- **Default TTL:** 300 seconds (5 minutes)
- **Max Entries:** 1,000 items

This is the default configuration and requires no additional setup.

### Production

For production environments, you can configure a more robust cache backend via the `CACHE_URL` environment variable or individual cache settings.

**Supported backends:**

1. **Redis** (recommended for production)
2. **File-based cache** (alternative for simpler deployments)
3. **Memcached** (supported via django-environ)

## Environment Variables

### Primary Configuration (Recommended)

Configure cache backend using individual environment variables:

```bash
# Cache backend class (default: locmem)
CACHE_BACKEND=django.core.cache.backends.locmem.LocMemCache

# Cache location/name
CACHE_LOCATION=travelmathlite-cache

# Default cache timeout in seconds (default: 300 = 5 minutes)
CACHE_TIMEOUT=300

# Maximum number of entries for locmem (default: 1000)
CACHE_MAX_ENTRIES=1000

# Key prefix for namespacing (default: travelmathlite)
CACHE_KEY_PREFIX=travelmathlite
```

### Alternative Configuration

Use `CACHE_URL` for URL-based configuration (requires uncommenting in `settings/base.py`):

```bash
# Local memory (default)
CACHE_URL=locmem://

# File-based cache
CACHE_URL=file:///tmp/django_cache

# Redis
CACHE_URL=redis://localhost:6379/1

# Redis with authentication
CACHE_URL=redis://username:password@redis-host:6379/1

# Memcached
CACHE_URL=memcached://127.0.0.1:11211
```

## Redis Setup (Production)

### Installation

For production deployments using Redis:

```bash
# Install Redis server (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install redis-server

# Install Python Redis client
uv pip install redis
```

### Configuration

Set environment variables:

```bash
export CACHE_BACKEND=django.core.cache.backends.redis.RedisCache
export CACHE_LOCATION=redis://127.0.0.1:6379/1
export CACHE_KEY_PREFIX=travelmathlite
export CACHE_TIMEOUT=300
```

Or use `CACHE_URL`:

```bash
export CACHE_URL=redis://127.0.0.1:6379/1
```

### Redis Best Practices

1. **Use database number for isolation:** `redis://host:6379/1` (database 1)
2. **Set key prefix:** Use `travelmathlite:` prefix for namespace isolation
3. **Configure maxmemory:** Set Redis `maxmemory` and `maxmemory-policy` (e.g., `allkeys-lru`)
4. **Monitor memory usage:** Use `redis-cli INFO memory`
5. **Enable persistence:** Configure RDB snapshots or AOF for cache durability

## File-Based Cache (Alternative)

For simpler deployments without Redis:

```bash
export CACHE_BACKEND=django.core.cache.backends.filebased.FileBasedCache
export CACHE_LOCATION=/var/tmp/travelmathlite_cache
export CACHE_TIMEOUT=300
```

Ensure the directory exists and is writable:

```bash
sudo mkdir -p /var/tmp/travelmathlite_cache
sudo chown www-data:www-data /var/tmp/travelmathlite_cache
```

## Cache TTL (Time-To-Live)

Default cache timeout is **300 seconds (5 minutes)**. Individual cache operations can override this:

```python
from django.core.cache import cache

# Use default TTL (300 seconds)
cache.set('key', 'value')

# Custom TTL (60 seconds)
cache.set('key', 'value', 60)

# Cache indefinitely (until cleared or evicted)
cache.set('key', 'value', None)
```

## Verification

### Check Cache Backend

```bash
cd travelmathlite
uv run python manage.py shell -c "
from django.core.cache import cache
print(f'Backend: {cache.__class__.__name__}')
print(f'Location: {cache._cache if hasattr(cache, \"_cache\") else \"N/A\"}')
"
```

### Test Cache Operations

```bash
uv run python manage.py shell -c "
from django.core.cache import cache
cache.set('test_key', 'test_value', 60)
print(f'Cached value: {cache.get(\"test_key\")}')
cache.delete('test_key')
print(f'After delete: {cache.get(\"test_key\")}')
"
```

### Run Cache Configuration Tests

```bash
uv run python manage.py test core.tests.test_cache_config
```

## Management Commands

### Clear Cache

Clear all cached data:

```bash
uv run python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```

### Cache Statistics (Redis only)

For Redis backends, check cache statistics:

```bash
redis-cli INFO stats
redis-cli INFO memory
redis-cli DBSIZE  # Show number of keys
```

## Troubleshooting

### Cache Not Working

1. **Check backend configuration:**

   ```bash
   uv run python manage.py shell -c "from django.conf import settings; print(settings.CACHES)"
   ```

2. **Verify cache operations:**

   ```bash
   uv run python manage.py shell -c "
   from django.core.cache import cache
   cache.set('test', 'value', 60)
   print(cache.get('test'))
   "
   ```

3. **Check Redis connection (if using Redis):**

   ```bash
   redis-cli ping  # Should return PONG
   ```

### Cache Growing Too Large

1. **For locmem:** Increase `MAX_ENTRIES` or clear cache periodically
2. **For Redis:** Configure `maxmemory` and `maxmemory-policy` in `redis.conf`
3. **Monitor cache usage** and adjust TTLs if needed

### Cache Key Collisions

Use the `KEY_PREFIX` setting to namespace cache keys:

```bash
export CACHE_KEY_PREFIX=travelmathlite
```

This prevents key collisions if multiple applications share the same cache backend.

## Performance Considerations

1. **Cache hit rates:** Monitor cache hit/miss ratios in application logs
2. **TTL tuning:** Adjust timeouts based on data freshness requirements
3. **Cache warming:** Pre-populate cache with frequently accessed data
4. **Selective caching:** Only cache expensive operations (database queries, computations)
5. **Memory limits:** Configure appropriate `MAX_ENTRIES` or Redis `maxmemory`

## Security

1. **Redis authentication:** Use Redis password authentication in production

   ```bash
   export CACHE_URL=redis://:password@localhost:6379/1
   ```

2. **Network isolation:** Bind Redis to localhost or use firewall rules
3. **No sensitive data:** Avoid caching sensitive information (passwords, tokens, PII)
4. **Key prefixes:** Use namespacing to prevent cross-application access

## References

- [Django Cache Framework Documentation](https://docs.djangoproject.com/en/stable/topics/cache/)
- [Redis Best Practices](https://redis.io/docs/manual/admin/)
- ADR-1.0.10: Caching Strategy
- Brief: ADR-1.0.10-01 — Cache Backend Configuration
