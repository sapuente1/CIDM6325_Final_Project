# Tutorial: ADR-1.0.1 Dataset Source for Airports and Cities

Goal

- Understand the dataset selection (OurAirports), import commands, schema mapping, normalization, and update automation.

Context

- ADR: `docs/travelmathlite/adr/adr-1.0.1-dataset-source-for-airports-and-cities.md`
- Briefs: `docs/travelmathlite/briefs/adr-1.0.1/`
- App: `travelmathlite/apps/airports/`

Prerequisites

- TravelMathLite dev environment ready; internet access or CSV downloaded to `downloads/`

Steps (guided by briefs)

1) Dataset selection (Brief 01)
   - Source: OurAirports CSVs (airports.csv). License: public domain.
2) Data ingestion (Brief 02)
   - Management command `import_airports` parses CSV, validates fields, and upserts by `ident`/IATA.
   - Try `--dry-run` first.
3) Data validation (Brief 03)
   - Sanity checks, range validation for coordinates, required fields.
4) Schema mapping (Brief 04)
   - See `apps/airports/schema_mapping.py` and `docs/travelmathlite/schema-mapping-airports.md`.
   - Type conversions and field name mappings.
5) Update automation (Brief 05)
   - `update_airports` wraps import with scheduling hooks, logging, and safety.
6) Licensing compliance (Brief 06)
   - Review `docs/travelmathlite/licensing-compliance-airports.md`.
7) Integration with core models (Brief 07)
   - `Country`/`City` normalization and linker; optional flags during import.
8) Documentation & onboarding (Brief 08)
   - Onboarding doc updates and references.
9) Test coverage (Brief 09)
   - Verify importer and mapping tests.
10) Rollback & recovery (Brief 10)
    - Backup/restore notes; dry-run and idempotence.

Commands

```bash
# Import (dry-run first)
uv run python travelmathlite/manage.py import_airports --file downloads/airports.csv --dry-run
uv run python travelmathlite/manage.py import_airports --file downloads/airports.csv

# Update automation (example)
uv run python travelmathlite/manage.py update_airports --dry-run
```

How to Verify

- Admin/search shows imported airports; nearest lookups work using lat/long.
- Run airports tests:

```bash
uv run python travelmathlite/manage.py test apps.airports
```

References

- [Understand Django (Matt Layman)](https://www.mattlayman.com/understand-django/)
  - Suggested topics: Management commands, Models, Testing
- [Django documentation](https://docs.djangoproject.com/)
- [Bootstrap documentation](https://getbootstrap.com/docs/)
- [HTMX documentation](https://htmx.org/docs/)
