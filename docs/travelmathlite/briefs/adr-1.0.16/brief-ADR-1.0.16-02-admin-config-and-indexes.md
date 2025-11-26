# BRIEF: Admin configuration and indexes for core models

Goal

- Configure Django admin for Country, City, and Airport with search, filters, and read-only timestamps; verify indexes align to ADR-1.0.16.

Scope (single PR)

- Files to touch: `apps/base/admin.py`, `apps/airports/admin.py` (or equivalent), ensure models imported; confirm indexes/Meta ordering reflect ADR.
- Behavior: Admin list/search on codes/name/municipality; list_filter on country/active; read-only created/updated; sensible list_display; ensure indexes in Meta match admin queries (codes, country, lat/lon).
- Non-goals: Data import, UI restyle beyond admin essentials.

Standards

- Commits: conventional (chore/docs).
- No secrets; env via settings.
- Django tests: admin registration sanity (Smoke TestCase to assert models registered).

Acceptance

- User flow: Admin users can search Airport by code/name, filter by country/active; Country/City searchable; timestamps read-only.
- Include migration? no (unless new indexes/Meta changes needed)
- Update docs & PR checklist.

Prompts for Copilot

- "Add admin classes for Country/City/Airport with search_fields, list_display, list_filter, readonly_fields."
- "Verify indexes/Meta align to admin queries; add a quick test asserting admin registration."
