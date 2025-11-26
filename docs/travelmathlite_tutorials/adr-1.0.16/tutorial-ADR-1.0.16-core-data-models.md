# Tutorial: ADR-1.0.16 Core Data Models (City, Airport, Country)

**Date:** November 26, 2025  
**ADR Reference:** [ADR-1.0.16 Core data models](../../travelmathlite/adr/adr-1.0.16-core-data-models.md)  
**Briefs:** [adr-1.0.16 briefs](../../travelmathlite/briefs/adr-1.0.16/)

---

## Overview

This tutorial walks through the normalized Country, City, and Airport models that power TravelMathLite, aligning with ADR-1.0.16. You will see how the schema maps to the OurAirports dataset, how admin/search/indexes are configured, how querysets implement nearest-airport lookups, and how the importer links data to normalized tables.

**Learning Objectives**

- Define normalized geo models with constraints and indexes for fast lookup.
- Configure Django admin for search/filter usability.
- Implement queryset helpers for search and nearest-airport retrieval.
- Run the importer to hydrate normalized Country/City rows alongside Airport records.
- Verify the slice with targeted tests and admin/shell checks.

**Prerequisites**

- TravelMathLite project set up with uv (`uv run python travelmathlite/manage.py …`).
- Access to the OurAirports dataset (download handled automatically by the import command).
- Django superuser for admin verification.
- Familiarity with Django models and management commands.

---

## Section 1 — Core models and migrations

**Brief Context:** [brief-ADR-1.0.16-01-core-models-and-migrations.md](../../travelmathlite/briefs/adr-1.0.16/brief-ADR-1.0.16-01-core-models-and-migrations.md)  
**Goal:** Create normalized Country/City models plus Airport fields/migrations keyed to OurAirports columns.

### Documentation context

- From Django docs on models: a model is “the single, definitive source of information about your data,” defining fields, constraints, and default behaviors.
- Understand Django (Models chapter) stresses keeping models focused and normalized to avoid duplicated data.
- Django migrations capture schema changes so they can be applied predictably across environments.

### Implementation highlights

- `travelmathlite/apps/base/models.py` defines:
  - `Country` with ISO codes, search slugging, and `CountryQuerySet.active()/search()`.
  - `City` with unique constraints per country on `search_name` and `slug`, and `CityQuerySet.active()/search()`.
  - `TimestampedModel` abstract base adds `created_at/updated_at`.
- `travelmathlite/apps/airports/models.py` defines `Airport` mapped to OurAirports columns (`ident`, `iata_code`, `latitude_deg`, `iso_country`, etc.) with FKs to `Country` (PROTECT) and `City` (SET_NULL).
- Indexes:
  - Country/City: search_name, slug, country composite indexes.
  - Airport: codes, country, city, lat/lon, active flag for fast filtering.
- Uniqueness:
  - `Country.iso_code` unique; City unique per country on `search_name` and `slug`; `Airport.ident` unique.

### Steps (already implemented)

1) Define models and querysets:

```python
# Country (apps/base/models.py)
class Country(TimestampedModel):
    iso_code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=128)
    search_name = models.CharField(max_length=128, db_index=True)
    slug = models.SlugField(max_length=64, unique=True)
    active = models.BooleanField(default=True)
    objects = CountryQuerySet.as_manager()

# City with per-country uniqueness
class City(TimestampedModel):
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="cities")
    search_name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["country", "search_name"], name="city_country_search_unique"),
            models.UniqueConstraint(fields=["country", "slug"], name="city_country_slug_unique"),
        ]
```

2) Normalize on save (slugify, lower search names, ISO uppercasing) to keep search/index consistency.

3) Airport schema:

```python
# Airport (apps/airports/models.py)
ident = models.CharField(max_length=10, unique=True, db_index=True)
iata_code = models.CharField(max_length=3, blank=True, db_index=True)
latitude_deg = models.FloatField()
longitude_deg = models.FloatField()
iso_country = models.CharField(max_length=2, db_index=True)
country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.PROTECT, related_name="airports")
city = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL, related_name="airports")
```

4) Migrations were generated (`base/0001_initial.py`, `airports/0002_airport_core_integrations.py`) to create tables, indexes, and constraints.

### How to verify

- Apply migrations locally: `uv run python travelmathlite/manage.py migrate`.
- Inspect schema: `uv run python travelmathlite/manage.py showmigrations base airports`.
- Quick shell check:

```bash
uv run python travelmathlite/manage.py shell -c "
from apps.base.models import Country, City
us = Country.objects.create(iso_code='US', name='United States', search_name='united states', slug='us')
City.objects.create(country=us, name='Dallas', search_name='dallas', slug='us-dallas')
print(Country.objects.count(), City.objects.count())
"
```

---

## Section 2 — Admin config and indexes

**Brief Context:** [brief-ADR-1.0.16-02-admin-config-and-indexes.md](../../travelmathlite/briefs/adr-1.0.16/brief-ADR-1.0.16-02-admin-config-and-indexes.md)  
**Goal:** Expose Country/City/Airport in Django admin with search and filters; ensure indexes support admin queries.

### Documentation context

- Django admin docs: `list_display`, `search_fields`, and `list_filter` make data discoverable; `readonly_fields` protect timestamps.
- Understand Django (Admin chapter) recommends surfacing the columns people actually search and filter on to avoid slow queries.

### Implementation highlights

- `apps/base/admin.py`:

```python
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "iso_code", "iso3_code", "active", "latitude", "longitude")
    list_filter = ("active",)
    search_fields = ("name", "iso_code", "iso3_code")
    readonly_fields = ("created_at", "updated_at")
```

- `apps/airports/admin.py`:

```python
@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "iata_code", "ident", "iso_country", "country", "city", "active", "updated_at")
    list_filter = ("active", "airport_type", "country", "iso_country")
    search_fields = ("name", "iata_code", "ident", "municipality", "country__name", "country__iso_code", "city__name", "iso_country")
    readonly_fields = ("created_at", "updated_at")
```

- Indexes defined in models back these admin lookups (codes, country/city, active).

### How to verify

- Create a superuser: `uv run python travelmathlite/manage.py createsuperuser`.
- Run server: `uv run python travelmathlite/manage.py runserver`, then visit `/admin/` and confirm:
  - Airport list shows columns above; filters toggle active/type/country.
  - Search finds airports by IATA/ICAO/name/municipality/country.
- Tests: `travelmathlite/apps/airports/tests/test_admin.py` asserts Airport is registered in admin.

---

## Section 3 — QuerySets and nearest search

**Brief Context:** [brief-ADR-1.0.16-03-querysets-and-nearest-search.md](../../travelmathlite/briefs/adr-1.0.16/brief-ADR-1.0.16-03-querysets-and-nearest-search.md)  
**Goal:** Provide queryset helpers for active/search plus nearest-airport retrieval using a bounding box + haversine.

### Documentation context

- Django docs on custom managers/querysets: attach helpers with `QuerySet.as_manager()` to keep logic reusable and chainable.
- Understand Django (Queries chapter): push filtering logic into querysets to keep views thin and ensure consistent behavior.
- Geospatial note: prefiltering with a bounding box reduces the candidate set before computing haversine distances.

### Implementation highlights

- Country/City `active()` and `search()` filter and normalize search terms to lowercase.
- AirportQuerySet:

```python
class AirportQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)

    def search(self, term):
        if not term:
            return self.active()
        normalized = term.strip()
        return self.active().filter(
            models.Q(name__icontains=normalized)
            | models.Q(iata_code__icontains=normalized)
            | models.Q(ident__icontains=normalized)
            | models.Q(municipality__icontains=normalized)
            | models.Q(country__name__icontains=normalized)
            | models.Q(country__iso_code__icontains=normalized)
            | models.Q(iso_country__icontains=normalized)
        )

    def nearest(self, latitude, longitude, *, limit=3, radius_km=2000, iso_country=None, unit="km"):
        filters = self._bounding_box_filters(latitude, longitude, radius_km)
        qs = self.active().filter(**filters)
        if iso_country:
            qs = qs.filter(models.Q(country__iso_code__iexact=iso_country) | models.Q(iso_country__iexact=iso_country))
        candidates = list(qs)
        for airport in candidates:
            airport.distance_km = _haversine_km(latitude, longitude, airport.latitude_deg, airport.longitude_deg)
            if unit == "mi":
                from apps.base.utils.units import km_to_mi
                airport.distance_mi = km_to_mi(airport.distance_km)
        candidates.sort(key=lambda a: getattr(a, "distance_km", math.inf))
        return candidates[:limit]
```

- Bounding box uses ~111 km per degree to trim the dataset before sorting by computed distances.

### How to verify

- Run queryset tests: `uv run python travelmathlite/manage.py test travelmathlite/apps/airports/tests/test_querysets.py travelmathlite/apps/airports/tests/tests_nearest.py`.
- Shell check:

```bash
uv run python travelmathlite/manage.py shell -c "
from apps.airports.models import Airport
results = Airport.objects.nearest(32.8998, -97.0403, limit=2)  # near DFW
print([(a.name, round(a.distance_km, 1)) for a in results])
"
```

Expect to see nearby Dallas-area airports ordered by distance.

---

## Section 4 — Importer and data integration

**Brief Context:** [brief-ADR-1.0.16-04-importer-and-data-integration.md](../../travelmathlite/briefs/adr-1.0.16/brief-ADR-1.0.16-04-importer-and-data-integration.md)  
**Goal:** Extend the OurAirports import command to create/link normalized Country/City rows and attach them to Airport records.

### Documentation context

- Django docs on management commands: use `BaseCommand` to add CLI arguments and encapsulate long-running jobs.
- Understand Django (Management Commands chapter) notes commands are ideal for data imports/maintenance and should be idempotent.

### Implementation highlights

- Command: `travelmathlite/apps/airports/management/commands/import_airports.py`
  - Arguments: `--url/--file`, `--dry-run`, `--filter-iata`, `--limit`, `--skip-country-link`, `--skip-city-link`.
  - Downloads CSV (or uses local file), validates rows, and upserts `Airport` rows.
  - Integrates with `AirportLocationIntegrator` (`apps/airports/services/integration.py`) to:
    - Create/link `Country` by `iso_country`.
    - Create/link `City` by municipality + coordinates.
    - Track stats for countries/cities created and linked.
- Idempotency: `_upsert_airport` updates existing rows by `ident`; skip flags avoid touching linked tables.

### How to verify

- Dry run (no DB writes):

```bash
uv run python travelmathlite/manage.py import_airports --dry-run --limit 5
```

- Import with linkage:

```bash
uv run python travelmathlite/manage.py import_airports --filter-iata --limit 20
```

Check summary lines for `Country links` and `City links`; confirm Airport rows have `country`/`city` set when data is present.

- Tests:
  - `travelmathlite/apps/airports/tests/tests_import.py` (import stats and idempotency)
  - `travelmathlite/apps/airports/tests/tests_city_country_integration.py` (linkage coverage)
  - `travelmathlite/apps/airports/tests/tests_validate_command.py` (row validation)

---

## Section 5 — Tests and docs

**Brief Context:** [brief-ADR-1.0.16-05-tests-and-docs.md](../../travelmathlite/briefs/adr-1.0.16/brief-ADR-1.0.16-05-tests-and-docs.md)  
**Goal:** Ensure the slice is covered by unit tests and documented patterns.

### Documentation context

- Django testing docs: use `TestCase` for DB-isolated tests; `assertTemplateUsed`, `RequestFactory`, and queryset assertions keep behaviors stable.
- Understand Django (Testing chapter) highlights isolating model/query logic and using factories/setup to keep tests readable.

### Implementation highlights

- Model/queryset coverage:
  - `apps/airports/tests/test_querysets.py` (search, active filter)
  - `apps/airports/tests/tests_nearest.py` / `tests_nearest_core.py` (nearest sorting, distance math)
  - `apps/airports/tests/tests_city_country_integration.py` (Country/City link creation)
  - `apps/airports/tests/tests_import.py` (upserts, stats)
  - `apps/base/tests` (URL/template smoke; timestamped base already exercised)
- Docs targets (per ADR): `docs/data-models/airports.md`, `docs/travelmathlite/data-model-integration.md` describe schema and importer flow.

### How to verify

- Run focused suite:

```bash
uv run python travelmathlite/manage.py test travelmathlite/apps/airports/tests travelmathlite/apps/base/tests
```

- Review docs for schema/integration notes in the paths above.

---

## Summary and next steps

- You now have normalized Country/City/Airport models with indexes and queryset helpers, wired admin UX, and an importer that keeps normalized links up to date.
- Next steps:
  1) Capture admin screenshots for attestation (Airports list with filters/search).
  2) If deploying to Postgres, consider adding partial indexes or trigram search for faster fuzzy matching.
  3) Keep importer stats in logs/metrics for linkage coverage over time.

---

## References

- ADR: [ADR-1.0.16 Core data models](../../travelmathlite/adr/adr-1.0.16-core-data-models.md)
- Briefs: [adr-1.0.16](../../travelmathlite/briefs/adr-1.0.16/)
- Django docs: Models, Custom managers/querysets, Admin (`list_display`, `search_fields`, `list_filter`), Management commands, Testing (`TestCase`)
- Understand Django: Models, Queries, Admin, Management Commands, Testing chapters
- Dataset: [OurAirports](https://ourairports.com/data/) (CSV schema for fields like `ident`, `iata_code`, `iso_country`, `municipality`)
