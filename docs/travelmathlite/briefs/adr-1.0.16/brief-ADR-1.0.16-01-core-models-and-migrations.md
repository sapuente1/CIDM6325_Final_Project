# BRIEF: Build core models and migrations for Country/City/Airport

Goal

- Create normalized Country, City, and Airport models with fields/indexes per ADR-1.0.16 to support search and nearest-airport features.

Scope (single PR)

- Files to touch: `apps/base/models.py`, `apps/airports/models.py`, migrations under `apps/base/migrations/` and `apps/airports/migrations/` as needed.
- Behavior: Define Country (iso code/name), City (name, country FK, lat/lon, search_name), Airport (ident, iata_code, name, city FK nullable, country FK, lat/lon, active). Add indexes/constraints on codes and `(lat, lon)`; keep Airport FK nullable where data missing.
- Non-goals: Trip/user models, importer logic (handled in later briefs).

Standards

- Commits: conventional (feat/migration).
- No secrets; env via settings.
- Django tests: unittest/Django TestCase (no pytest). Add basic model sanity tests.

Acceptance

- User flow: Migrations apply cleanly; models exist with expected fields/indexes and FKs; admin shell can create/query Country/City/Airport.
- Include migration? yes
- Update docs & PR checklist.

Prompts for Copilot

- "Add Country/City/Airport models with indexes (codes, lat/lon) and nullable city FK; generate migrations."
- "Write minimal model tests to assert fields exist and defaults/uniqueness hold."
