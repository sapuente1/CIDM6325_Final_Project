# Tutorial: ADR-1.0.3 Nearest Airport Lookup

Goal

- Explain the nearest-airport lookup (bounding box + haversine) and how to use it via forms/views/API.

Context

- ADR: `docs/travelmathlite/adr/adr-1.0.3-nearest-airport-lookup-implementation.md`
- Briefs: `docs/travelmathlite/briefs/adr-1.0.3/`
- App: `travelmathlite/apps/airports/`

Prerequisites

- TravelMathLite project set up; airports available (use importer/fixtures)

Steps (guided by briefs)

1) Core & indexes (Brief 01)
   - `AirportQuerySet.nearest(...)` in `apps/airports/models.py`: bounding box prefilter → compute haversine → sort → top N.
   - Indexes include `(latitude_deg, longitude_deg)`, `iso_country`, `active`.
2) Algorithm docs (Brief 02)
   - Draft/consult `docs/travelmathlite/algorithms/nearest-airport.md` for delta formulas and rationale.
3) Forms (Brief 03)
   - `NearestAirportForm` (when implemented): normalize city/IATA/coords to lat/lon; validate; optional country.
4) Views/API (Brief 04)
   - Page CBV + JSON endpoint returning top results with distance + unit.
5) Templates & HTMX (Brief 05)
   - Minimal page + partial list; HTMX for partial updates.
6) Tests & performance (Brief 06)
   - Ordering and unit assertions; light timing evidence for p95 under 300 ms on sample.

Commands

```bash
uv run python travelmathlite/manage.py migrate
uv run python travelmathlite/manage.py runserver
```

How to Verify

- Programmatic: in a shell, call `Airport.objects.nearest(lat, lon, limit=3)` and inspect ordering/distances.
- UI/API: visit the nearest airports page (if implemented) and hit the JSON endpoint.
- Run airports tests:

```bash
uv run python travelmathlite/manage.py test apps.airports
```

References

- [Understand Django (Matt Layman)](https://www.mattlayman.com/understand-django/)
  - Suggested topics: QuerySets/Managers, Testing, Views, Templates
- [Django documentation](https://docs.djangoproject.com/)
- [Bootstrap documentation](https://getbootstrap.com/docs/)
- [HTMX documentation](https://htmx.org/docs/)
