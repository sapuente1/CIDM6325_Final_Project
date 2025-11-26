# BRIEF: QuerySets and nearest/search helpers

Goal

- Implement QuerySet helpers for active/search/nearest to support fast lookups and nearest-airport features per ADR-1.0.16.

Scope (single PR)

- Files to touch: `apps/airports/models.py` (QuerySet methods), optional utils; ensure City/Country search helpers as needed.
- Behavior: `Airport.objects.active()`, `search(term)` (case-insensitive across name/codes/municipality/country), `nearest(lat, lon, limit, unit, iso_country, radius_km)` with bounding-box prefilter and haversine sort attaching distance_km/mi. Add `City.objects.active/search` if not present.
- Non-goals: Importer logic; UI changes.

Standards

- Commits: conventional (feat/test).
- No secrets; env via settings.
- Django tests: TestCase for QuerySet helpers (active, search filters expected results; nearest returns sorted list with distance fields).

Acceptance

- User flow: Code consumers can call `Airport.objects.nearest(...)` and get ordered results with distance attributes; search returns expected airports/cities.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Implement Airport QuerySet with active/search/nearest (bounding box + haversine); add tests for search and nearest ordering."
- "Ensure distance_km/mi attached to returned airports; cover iso_country filter."
