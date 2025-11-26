# BRIEF: Importer integration and data normalization

Goal

- Wire importer to populate Country/City FKs on Airport where possible and report linkage coverage, aligning with ADR-1.0.16 implementation results.

Scope (single PR)

- Files to touch: importer/commands under `apps/base`/`apps/airports` (e.g., `AirportLocationIntegrator`), any data integration modules, `docs/travelmathlite/data-model-integration.md`.
- Behavior: Parse dataset fields, upsert Country/City, attach FKs to Airport when matches found; allow nulls if missing. Produce a summary (counts, linkage %) after import. Validate code uniqueness and normalize search_name for cities. Keep admin usable.
- Non-goals: Dataset downloads beyond existing workflow; adding new external dependencies.

Standards

- Commits: conventional (feat/chore/docs).
- No secrets; env via settings.
- Django tests: importer regression (FKs set, counts reported, duplicates handled).

Acceptance

- User flow: Running import populates Country/City and links Airports; summary shows linkage coverage; no integrity errors on duplicates.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Update import command to upsert Country/City, set Airport FKs, and print linkage coverage; add tests."
- "Document the data-model integration steps and expected import output."
