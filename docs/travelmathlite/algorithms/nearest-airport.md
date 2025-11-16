# Nearest Airport Lookup: Bounding Box + Haversine

This note explains how TravelMathLite computes the nearest airports for a given coordinate without PostGIS, aligning with ADR-1.0.3.

## Approach Overview

- Prefilter via a coarse geographic bounding box around the query point to limit DB candidates.
- Compute precise distances in Python using the Haversine formula for each candidate.
- Sort by distance and return the top N (default 3).

## Bounding Box Prefilter

Given a query `(lat, lon)` and a radius in kilometers `R_km`, we derive an approximate bounding box:

- Degrees per km (latitude): ~1° per 111 km
- Latitude delta: `dlat = R_km / 111`
- Longitude delta: `dlon = dlat / max(cos(lat in radians), 0.1)`

The query applies:

- `latitude_deg BETWEEN (lat - dlat) AND (lat + dlat)`
- `longitude_deg BETWEEN (lon - dlon) AND (lon + dlon)`

Default radius: `radius_km = 2000` (portable default for SQLite-first; tune per use case).

## Country Prefilter (iso_country)

To improve precision and performance, callers can include an ISO 3166-1 alpha-2 country code:

- `iso_country = 'US'` filters candidates to United States airports only.
- The queryset also supports normalized `country` FK when present.

This optional prefilter reduces cross-border candidates and speeds up lookups in dense regions.

## Distance Calculation (Haversine)

For each candidate airport `(lat2, lon2)`, compute great-circle distance to `(lat1, lon1)`:

```text
R = 6371.0  # km
Δφ = radians(lat2 - lat1)
Δλ = radians(lon2 - lon1)
a = sin²(Δφ/2) + cos φ1 · cos φ2 · sin²(Δλ/2)
c = 2 · atan2(√a, √(1−a))
distance_km = R · c
```

Units: results always include `distance_km`; when requested, a `distance_mi` convenience value is attached using `mi = km × 0.621371`.

## Defaults and Outputs

- Limit: `limit = 3`
- Radius: `radius_km = 2000`
- Unit: `unit = 'km' | 'mi'` (affects the extra attached value; sorting is by km)

Returned list is ordered by `distance_km` ascending with distances attached to each instance.

## References

- ADR: `docs/travelmathlite/adr/adr-1.0.3-nearest-airport-lookup-implementation.md`
- Implementation: `travelmathlite/apps/airports/models.py` (`AirportQuerySet.nearest`)
- Tests: `travelmathlite/apps/airports/tests_nearest_core.py`
- Django docs: <https://docs.djangoproject.com/>
