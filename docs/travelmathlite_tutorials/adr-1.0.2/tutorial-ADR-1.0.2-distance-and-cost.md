# Tutorial: ADR-1.0.2 Distance & Cost Calculators

Goal

- Explain the distance/time/cost calculators implemented in ADR-1.0.2 and show how to verify and extend them.

Context

- ADR: `docs/travelmathlite/adr/adr-1.0.2-geo-calculation-methods.md`
- Briefs: `docs/travelmathlite/briefs/adr-1.0.2/`
- App: `travelmathlite/apps/calculators/`

Prerequisites

- TravelMathLite project set up (see docs/travelmathlite/django-project-setup-with-uv.md)
- Optional: `geopy` available for geodesic distance (fallback to haversine is included)

Steps (guided by briefs)

1) Core algorithms (Brief 01)
   - Review `apps/calculators/geo.py`: `haversine_distance`, `geodesic_distance`, `km_to_miles`, `miles_to_km`, `estimate_driving_distance`, `calculate_distance_between_points`.
   - Key idea: flight distance + heuristic driving distance (route_factor).
2) Settings (Brief 02)
   - See `travelmathlite/core/settings.py` defaults: `ROUTE_FACTOR`, `AVG_SPEED_KMH`, `FUEL_PRICE_PER_LITER`, `FUEL_ECONOMY_L_PER_100KM`.
3) Cost calculations (Brief 03)
   - Review `apps/calculators/costs.py`: cost = (km/100) × L/100km × price/L. Conversions MPG↔L/100km, gallons↔liters.
4) Forms (Brief 04)
   - `apps/calculators/forms.py`: accept city, IATA, or "lat,lon"; normalize to coords; validate ranges; default from settings.
5) Views & HTMX (Brief 05)
   - `apps/calculators/views.py` + `urls.py`: CBVs for pages; partial endpoints for HTMX.
   - Templates: `calculators/distance_calculator.html`, `calculators/cost_calculator.html`, partials in `calculators/partials/`.
6) Documentation (Brief 06)
   - `docs/travelmathlite/algorithms/distance-and-cost.md` for formulas and examples.

Commands

```bash
uv run python travelmathlite/manage.py migrate
uv run python travelmathlite/manage.py runserver
```

How to Verify

- Browse: `/calculators/distance/` and `/calculators/cost/` (see nav in `templates/base.html`).
- Try inputs: city ("paris"), IATA ("JFK"), or "40.7128,-74.0060".
- Run tests for calculators:

```bash
uv run python travelmathlite/manage.py test apps.calculators
```

References

- [Understand Django (Matt Layman)](https://www.mattlayman.com/understand-django/)
  - Suggested topics: Views, Forms, Templates, Settings, Testing
- [Django documentation](https://docs.djangoproject.com/)
- [Bootstrap documentation](https://getbootstrap.com/docs/)
- [HTMX documentation](https://htmx.org/docs/)
