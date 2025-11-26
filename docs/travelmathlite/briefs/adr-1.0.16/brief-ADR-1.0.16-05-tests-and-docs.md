# BRIEF: Tests and documentation for core data models

Goal

- Add tests and docs covering Country/City/Airport models, QuerySet helpers, and importer outcomes to satisfy ADR-1.0.16 acceptance and attestation.

Scope (single PR)

- Files to touch: `apps/airports/tests/` (model/queryset/import tests), `apps/base/tests/` if needed, docs (`docs/travelmathlite/data-model-integration.md`, `docs/data-models/airports.md`).
- Behavior: Tests for model constraints/index assumptions, search/nearest helpers, and importer linkage. Docs explain schema, indexes, admin usage, and import runbook with sample outputs.
- Non-goals: New models or importer features (covered earlier).

Standards

- Commits: conventional (test/docs).
- No secrets; env via settings.
- Django tests: unittest/Django TestCase (no pytest).

Acceptance

- User flow: Tests pass covering models/querysets/importer; docs updated with schema and runbook; screenshots/notes collected for admin/search/nearest as evidence.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Add tests for Country/City/Airport models and nearest/search helpers; include importer coverage."
- "Update data-model integration docs with schema/indexes and import runbook."
