# TravelMathLite PRD Alignment Checklist — Completed with Notes

This document is a filled-in, travelmathlite-focused copy of `LAYMAN_CHECKLIST_01.md`, marked against the current repository state (`travelmathlite/` app suite) and annotated with brief notes pointing to code, tests, and gaps/TODOs.

Legend

- [x] Completed and verified
- [ ] Not yet completed or pending docs/tests

---

## 1. From Browser to Django (Introductory Context)

- [x] HTTP request/response flow — `core/urls.py` wires calculators/airports/search/accounts/trips to CBVs in `apps/*/views.py`, returning templates/partials.
- [ ] Runserver demonstration — Not recorded; run `uv run python manage.py runserver` from `travelmathlite/` to capture screenshots/asciinema.
- [x] Console inspection — `core.middleware.RequestLoggingMiddleware` emits JSON logs with request_id/duration; validated in `core/tests/test_observability.py`.
- [x] Code commentary — Views/models carry concise docstrings (e.g., `apps/calculators/views.py`, `apps/airports/models.py`).
- [ ] Visual diagram (optional) — No request/response diagram checked in.

---

## 2. URLs Lead the Way

- [x] urls.py created — Namespaced app URLs under `core/urls.py`; app routes in `apps/*/urls.py`.
- [x] Namespace clarity — `include(..., namespace=...)` used for calculators, airports, search, accounts, trips, base.
- [x] URL naming discipline — All routes named and reversed in templates/tests (see `apps/base/tests/test_namespaces.py`, `apps/calculators/tests.py`).
- [x] Canonical link alignment — Canonical tags on search results (`apps/search/templates/search/results.html`); SEO endpoints `sitemap.xml`/`robots.txt` wired.
- [x] Test coverage (resolve/reverse) — URL reverse/resolve tests across apps (e.g., `apps/airports/tests/tests_views.py`, `apps/search/tests/test_root.py`).

---

## 3. Views on Views

- [x] Views defined — CBVs for calculators (FormView), airports (FormView/JSON), search (TemplateView), auth/trips (Template/List/Delete).
- [x] Proper rendering — Views return templates or HTMX partials with fallbacks for non-HTMX POSTs.
- [x] View docstrings — Present on custom middleware, models, and views for intent/context.
- [x] Error handling — Form validation and queryset scoping (e.g., `SavedCalculationDeleteView` filters by user) ensure 404/validation paths.
- [x] Unit tests — Extensive view/form tests in `apps/calculators/tests`, `apps/airports/tests/tests_views.py`, `apps/search/tests/test_views.py`.

---

## 4. Templates for User Interfaces

- [x] Templates configured — `core/settings/base.py` includes project `templates/` and app directories.
- [x] Base template — `templates/base.html` with navbar/footer/includes; pages extend base and use Bootstrap 5 + HTMX pins.
- [x] Feature templates — Calculators, nearest airports, search results, auth, and trips render structured layouts with partials for HTMX swaps.
- [x] Template tags — Safe highlight filter (`apps/search/templatetags/highlight.py`) and sanitize filter (`apps/base/templatetags/sanitize.py`) used for user text.
- [ ] Accessibility compliance — ARIA labels/focus scripting exist, but no formal a11y audit/contrast report checked in.

---

## 5. User Interaction with Forms

- [x] Forms created — Calculator and nearest-airport forms with custom validators (`apps/calculators/forms.py`, `apps/airports/forms.py`).
- [x] CSRF token — Present across templates.
- [x] Validation handled — Clean methods resolve city/IATA/latlon and enforce ranges/units.
- [x] Form lifecycle — GET shows form; POST/HTMX renders partial results; non-HTMX POST falls back to full template.
- [ ] Persistence — Session helpers exist (`core/session.py`) but calculators do not yet persist last inputs for reuse.

---

## 6. Store Data with Models

- [x] Domain models — Country/City (normalized), Airport, Profile, SavedCalculation implemented with indexes and managers.
- [x] Migrations applied — Initial migrations under each app.
- [x] Admin entry — ModelAdmins for base/airports/trips with search/filter (`apps/base/admin.py`, `apps/airports/admin.py`, `apps/trips/admin.py`).
- [ ] Model methods — No `get_absolute_url()` on public models (not needed yet).
- [x] ORM queries — Views rely on QuerySets (nearest search, search results) with tests covering CRUD (`apps/airports/tests/tests_import.py`, `apps/trips/tests/test_saved_calculation.py`).

---

## 7. Administer All the Things

- [x] Admin site enabled — `core/urls.py: admin/`; custom ModelAdmins registered.
- [ ] Admin usage docs — Superuser creation and screenshots not documented.
- [x] Custom ModelAdmin — List/search/filter configs for Airport/Country/City/SavedCalculation; select_related in trips admin queryset.
- [ ] Permissions model — No staff-only customization beyond defaults; calculators remain public.
- [x] Admin tests — See `apps/airports/tests/test_admin.py`, `apps/base/tests/test_admin.py`.

---

## 8. Anatomy of an Application

- [x] App layout — Conventional Django app structure under `travelmathlite/apps/`.
- [x] Settings modularization — `core/settings/{base,local,prod}.py` with env-driven config.
- [x] INSTALLED_APPS — Domain apps plus contrib apps declared in `core/settings/base.py`.
- [x] Static files pipeline — WhiteNoise middleware plus `STATICFILES_DIRS`; CSS overrides in `static/css/`.
- [x] README mapping — `travelmathlite/README.md` documents structure and quickstart.

---

## 9. User Authentication

- [x] Authentication system enabled — Django auth in INSTALLED_APPS/middleware.
- [x] Login/Logout views — `RateLimitedLoginView` + Logout wired; password reset routes configured.
- [x] User registration — `SignupView` uses `UserCreationForm`; templates under `apps/accounts/templates/registration/`.
- [ ] Permissions — No role/permission gating beyond LoginRequired for saved calculations; calculators open to anonymous users.
- [x] Tests — Auth templates/rate limiting/profile upload covered (`apps/accounts/tests/test_rate_limit.py`, `test_profile.py`).

---

## 10. Middleware Do You Go?

- [x] Middleware stack reviewed — RequestID, RequestLogging, CacheHeader, WhiteNoise, security/auth stack in `core/settings/base.py`.
- [x] Custom middleware created — Request ID/timing and cache headers in `core/middleware.py` with tests in `core/tests/test_observability.py`.
- [x] Common middleware explained — Cache policies per ADR-1.0.10 applied to calculators/search.
- [ ] Middleware ordering docs — No README narrative; GZip not enabled (rely on platform).
- [x] Tests — Caching and request logging verified (`apps/calculators/test_caching.py`, `apps/search/tests/test_caching.py`).

---

## 11. Serving Static Files

- [x] Static files configuration — `STATIC_URL`, `STATICFILES_DIRS`, optional ManifestStaticFilesStorage via env; WhiteNoise middleware active.
- [x] Template integration — `{% load static %}` and Bootstrap/HTMX pins in `templates/includes/head.html`.
- [x] Assets verified — CSS overrides and screenshots for calculators under `travelmathlite/screenshots/calculators/`.
- [ ] Production strategy — CDN/cache headers not documented; STATIC_ROOT/collectstatic steps not recorded.
- [ ] Tests — No static asset tests.

---

## 12. Test Your Apps

- [x] Test suite created — Django TestCase suites across calculators, airports, base, search, accounts, trips.
- [x] Model/view/form tests — Coverage for nearest lookup, calculators (HTMX), search pagination/highlight, auth rate limiting, saved calculations.
- [x] CI integration — `.github/workflows/travelmathlite-tests.yml` runs lint/format/check/migrations/tests on push/PR.
- [ ] Coverage target — No coverage report; tests not rerun locally in this session.
- [ ] CI scope — Workflow currently runs app subset (airports/base); full suite relies on local runs.

---

## 13. Deploy A Site Live

- [x] Production settings — `core/settings/prod.py` enforces SECRET_KEY/ALLOWED_HOSTS, secure cookies, HSTS, SSL redirect.
- [ ] Deployment target — No platform/ALB/CDN docs or rollback plan.
- [ ] Static/media serving — WhiteNoise ready, but CDN/collectstatic steps and monitoring not documented.
- [ ] HTTPS enforcement — No cert/ingress setup captured; deploy checklist not run.

---

## 14. Per-visitor Data With Sessions

- [x] Session middleware — Enabled with default DB backend.
- [ ] Session data usage — Calculator views do not persist last inputs; helpers in `core/session.py` unused by views.
- [x] Session binding — Login signal marks session user-bound (`apps/accounts/signals.py`); tests in `apps/accounts/tests/test_session_migration.py`.
- [ ] Session security/cleanup — No `clearsessions`/rotation docs; secure flags rely on env defaults.

---

## 15. Making Sense Of Settings

- [x] Settings organization — base/local/prod split; django-environ for env parsing.
- [x] Environment-specific configs — DB/cache/settings driven by env vars; SECRET_KEY required in prod.
- [x] Logging configuration — Structured JSON logging with request_id/duration in `core/logging.py`.
- [ ] Email backend — Not configured per environment; README lacks mail guidance.
- [ ] Validation — No custom `check` hooks for settings; limited documentation of required env vars.

---

## 16. User File Use (Media Files)

- [x] Media configuration — `MEDIA_URL`/`MEDIA_ROOT` set; default FileSystemStorage.
- [x] File upload field — Profile avatar upload form/template (`apps/accounts/forms.py`, `accounts/profile_form.html`) with tests in `test_profile.py`.
- [ ] Development serving — `core/urls.py` does not mount `MEDIA_URL` for DEBUG; needs doc or URL helper.
- [ ] Production serving — No CDN/storage backend plan; file validation limited to accept=image/*.

---

## 17. Command Your App (Management Commands)

- [x] Custom management command — `import_airports`, `update_airports`, `validate_airports` with dry-run/limit/URL options.
- [x] Command structure — Uses BaseCommand with arguments; idempotent upsert and location linking (`apps/airports/management/commands/import_airports.py`).
- [x] Tests — Import/update/validate commands covered in `apps/airports/tests/tests_import.py`, `tests_update_command.py`, `tests_validate_command.py`.
- [ ] Automation — Scheduling/cron docs not present.

---

## 18. Go Fast With Django (Performance)

- [x] Database query optimization — Bounding-box filters and haversine in `AirportQuerySet.nearest`; indexes on hot fields.
- [x] Caching implemented — `@cache_page` on calculators/search; CacheHeaderMiddleware sets cache-control; cache backend configurable via env.
- [x] Pagination — Search results paginated; saved calculations paginated.
- [ ] Profiling — No Debug Toolbar/profiling tools; nearest JSON endpoint not cached.
- [ ] Documentation — No performance benchmarks/notes.

---

## 19. Security And Django

- [x] Security settings enabled — Secure cookies, HSTS, SSL redirect, referrer/XFO headers in base/prod settings.
- [x] CSRF protection — Middleware active; forms include CSRF tokens.
- [x] Input sanitization — `sanitize_html` filter and highlight escaping; saved calculations sanitized in templates/tests.
- [ ] CSP/rate limiting breadth — CSP not configured; rate limiting only on auth; dependency scanning not automated.
- [ ] Deploy check — `manage.py check --deploy` not documented in CI/readme.

---

## 20. Debugging Tips And Techniques

- [x] Logging configured — Request logging with request_id/duration; JSON formatter; health endpoint.
- [x] Error pages — Custom 404/500 templates tested in `core/tests/test_observability.py`.
- [x] Error tracking toggle — Optional Sentry init guarded by env (`core/sentry.py`).
- [ ] Tooling — No Debug Toolbar/VS Code launch configs or query logging guidance.
- [ ] Reproduction docs — Debug how-to and bug reproduction steps not documented.

---

## 21. Validation with PRD Alignment

- [x] FR coverage — Calculators, nearest lookup, search, auth, and saved-calculation scaffolding align with PRD §4; ADRs under `docs/travelmathlite/adr/`.
- [ ] Traceability — No matrix mapping PRD → ADR → tests/files; acceptance tracked loosely in feature checklist.
- [ ] NFRs — Accessibility/performance/security documentation partial; no lint/coverage badges.

---

## 22. Deliverables

- [x] CHECKLIST_COMPLETION.md — This file (travelmathlite edition).
- [x] Screenshots/asciinema — Calculator screenshots in `travelmathlite/screenshots/calculators/`.
- [ ] Summary table (PRD → ADR → Tests) — Not yet created.
- [ ] Additional media — Search/nearest/auth flows and deployment evidence not captured.

---

### Notes and pointers

- Caching and observability
  - Cache directives for calculators/search via `@cache_page` and `CacheHeaderMiddleware`; cache backend/env toggles in `core/settings/base.py`.
  - Request ID + structured logging in `core/middleware.py` and `core/logging.py`; tested in `core/tests/test_observability.py`.
  - Health endpoint returns status (and optional commit SHA) at `/health/`.

- Data/imports
  - OurAirports import pipeline with location linking in `apps/airports/management/commands/import_airports.py`; dry-run and limit flags covered by tests.
  - Normalized Country/City models (`apps/base/models.py`) back Airport foreign keys; search uses select_related for pagination efficiency.

- Auth/trips
  - Auth views/templates live under `apps/accounts/`; login rate limiting toggled via env in `RateLimitMixin`.
  - SavedCalculation list/delete flows and sanitization are implemented, but calculators do not yet persist submissions into SavedCalculation or sessions. Action item: hook calculators to `core/session.py` helpers and persist to trips when logged in.

- Quick wins (low risk)
  - Add `MEDIA_URL` serving in DEBUG, plus storage/CDN note for prod.
  - Add deployment/runbook steps (collectstatic, ALLOWED_HOSTS, certs, rollback) and map PRD → ADR → tests.
  - Enable full test matrix in CI (accounts/calculators/search/trips) and add coverage badge/report.
