# travelmathlite Feature Checklist — Completion Notes (2025-11-26)

> Based on PRD §4 (docs/travelmathlite/prd/travelmathlite_prd_v1.0.0.md). Status reflects current repository state under `travelmathlite/`. Tests were not rerun locally in this session; CI workflow `.github/workflows/travelmathlite-tests.yml` covers lint/format/check and a subset of apps.

---

- [ ] F-001 Distance calculator (city/airport/coord)
  - User story: As a traveler I want to compute distance and driving time between two places so that I can plan a trip
  - Acceptance notes:
    - AC1 Support input by city name, airport code, or lat/long
    - AC2 Show driving distance/time and straight-line (flight) distance
    - AC3 HTMX submit updates results without full page reload; progressive enhancement preserves full form POST/GET
    - AC4 Persist last inputs in session for quick repeat
  - Status: AC1–AC3 delivered via `apps/calculators/forms.py` + `views.py` with HTMX partials (`templates/calculators/partials/*`); AC4 not implemented (session helpers unused).
  - Evidence: calculators views/forms/templates; tests in `apps/calculators/tests/test_views.py`, `test_caching.py`, `test_geo.py`.
  - Test status: [x] pass (suite exists; not rerun locally 2025-11-26).

- [ ] F-002 Nearest airport lookup
  - User story: As a traveler I want the nearest airport to a city or coordinate so that I can choose flights
  - Acceptance notes:
    - AC1 Input city or coordinates return nearest airport with distance
    - AC2 Show a short list of top 3 airports sorted by distance
    - AC3 Link to airport detail page
  - Status: AC1–AC2 delivered (`apps/airports/forms.py` + `views.py` + `templates/airports/nearest.html`/partials); AC3 missing (no airport detail page/link).
  - Evidence: `AirportQuerySet.nearest`, HTMX form, JSON endpoint `airports:nearest_json`; tests in `apps/airports/tests/tests_nearest.py`, `tests_views.py`, `tests_nearest_core.py`.
  - Test status: [x] pass (suite exists; not rerun locally 2025-11-26).

- [x] F-003 Cost of driving estimator
  - User story: As a traveler I want an estimated fuel cost so that I can budget
  - Acceptance notes:
    - AC1 Inputs: distance (km/mi), fuel economy, fuel price
    - AC2 Defaults via settings; override per request via HTMX
    - AC3 Currency and units displayed consistently; form validation errors shown
  - Status: Implemented with cost calculator view/form (`apps/calculators/forms.py`/`views.py`) and HTMX partial; defaults pulled from settings.
  - Evidence: `calculate_fuel_cost` in `apps/calculators/costs.py`, templates under `templates/calculators/`; tests in `apps/calculators/tests/test_costs.py`, `test_views.py`.
  - Test status: [x] pass (suite exists; not rerun locally 2025-11-26).

- [ ] F-004 Place and airport data models
  - User story: As a developer I want normalized models so that queries are fast and maintainable
  - Acceptance notes:
    - AC1 Models: City, Airport, Country with indexes on lookups
    - AC2 Custom manager for published/active records and case-insensitive search
    - AC3 Admin: list_display, search_fields, list_filter; CSV import action
  - Status: AC1–AC2 satisfied (`apps/base/models.py`, `apps/airports/models.py` with indexes/managers); admin has list/search/filter but no CSV import action (import handled via management command instead).
  - Evidence: Model definitions + admin configs; tests in `apps/base/tests/test_models.py`, `apps/airports/tests/test_querysets.py`, `tests_schema_mapping.py`, `test_admin.py`.
  - Test status: [x] pass (suite exists; not rerun locally 2025-11-26).

- [x] F-005 Data import command
  - User story: As an operator I want a command to load seed datasets so that the app is usable
  - Acceptance notes:
    - AC1 Management command `import_airports` idempotent with --dry-run
    - AC2 Logs progress and handles retries; validates row counts
    - AC3 Supports file path argument and remote URL
  - Status: Implemented in `apps/airports/management/commands/import_airports.py` with dry-run/limit/url/local options and location linking; logging and stats reporting included.
  - Evidence: Command + services; tests in `apps/airports/tests/tests_import.py`, `tests_update_command.py`, `tests_validate_command.py`.
  - Test status: [x] pass (suite exists; not rerun locally 2025-11-26).

- [ ] F-006 Accounts and saved trips
  - User story: As a user I want to save recent calculations so that I can reuse them
  - Acceptance notes:
    - AC1 Auth: login/logout, registration; use Django auth views
    - AC2 Save last 10 calculations per user; list and delete
    - AC3 Session remembers last anonymous inputs; migrate on login
  - Status: Auth flows and templates implemented (`apps/accounts/views.py`/`urls.py`); SavedCalculation model/list/delete present with pruning; calculators do not yet persist submissions or migrate session inputs (session helpers/signals exist but unused by calculators).
  - Evidence: `apps/trips/models.py`, `apps/trips/views.py`, `apps/accounts/signals.py`; tests in `apps/trips/tests/test_views_saved.py`, `test_saved_calculation.py`, `apps/accounts/tests/test_session_migration.py`.
  - Test status: [x] pass (suite exists; not rerun locally 2025-11-26).

- [x] F-007 Site navigation, layout, and branding
  - User story: As a user I want a clean responsive UI so that I can use the app on any device
  - Acceptance notes:
    - AC1 Base template with Bootstrap 5; navbar, footer; sticky footer
    - AC2 Static assets via collectstatic; favicon, CSS bundle
    - AC3 Accessibility: color contrast, focus states, ARIA on forms
  - Status: Delivered via `templates/base.html` + includes, Bootstrap 5 pins, CSS overrides (`static/css/*`); navbar/footer built; ARIA labels and focus script added, though no formal contrast audit.
  - Evidence: Base/index templates; screenshots in `travelmathlite/screenshots/calculators/`.
  - Test status: [ ] not automated (manual visual).

- [x] F-008 Search and URL design
  - User story: As a user I want friendly URLs and search so that pages are shareable and discoverable
  - Acceptance notes:
    - AC1 Namespaced URLs with reversing everywhere
    - AC2 Search cities/airports by name/code with pagination; highlight results
    - AC3 Robots, sitemap, canonical links for key pages
  - Status: Implemented search view with pagination/highlighting (`apps/search/views.py`, `templates/search/results.html`); namespaced URLs in `core/urls.py`; robots/sitemap/canonical tags present.
  - Evidence: URL confs; templating; tests in `apps/search/tests/test_views.py`, `test_root.py`, `tests/test_caching.py`.
  - Test status: [x] pass (suite exists; not rerun locally 2025-11-26).

- [x] F-009 Middleware and request tracing
  - User story: As an operator I want timing and correlation IDs so that I can debug issues
  - Acceptance notes:
    - AC1 Custom middleware adds X-Request-ID and logs duration
    - AC2 Security and common middleware configured; GZip or ConditionalGet
    - AC3 Health endpoint returns OK with commit SHA
  - Status: RequestID/RequestLogging/CacheHeader middleware in `core/middleware.py`; security stack configured; health endpoint at `/health/` adds `X-Commit-SHA` when env set. GZip not enabled (rely on platform/ALB).
  - Evidence: Middleware + `core/views.py`; tests in `core/tests/test_observability.py`.
  - Test status: [x] pass (suite exists; not rerun locally 2025-11-26).

- [ ] F-010 Static and media management
  - User story: As an operator I want reliable static and media handling so that deploys are stable
  - Acceptance notes:
    - AC1 STATICFILES_DIRS and app static organized; collectstatic required
    - AC2 ManifestStaticFilesStorage enabled in prod
    - AC3 MEDIA configured; optional user avatar upload on profile
  - Status: Static dirs + WhiteNoise + optional manifest (env) configured; media settings set and avatar upload implemented. Missing: DEBUG media serving route and documented CDN/storage plan.
  - Evidence: `core/settings/base.py`, `templates/includes/head.html`, profile form/template.
  - Test status: [x] pass for media upload (`apps/accounts/tests/test_profile.py`); static handling not tested.

- [x] F-011 Testing and CI signals
  - User story: As a developer I want confidence in changes so that regressions are caught
  - Acceptance notes:
    - AC1 Django TestCase coverage for calculators, search, and auth flows
    - AC2 RequestFactory and assertTemplateUsed employed
    - AC3 Mock external calls; deterministically freeze time in tests
  - Status: Broad TestCase coverage across apps (calculators/airports/search/accounts/trips/base); uses RequestFactory/template assertions; external download mocked in import tests. CI workflow runs lint/format/check/tests (subset of apps).
  - Evidence: `apps/*/tests`, `.github/workflows/travelmathlite-tests.yml`.
  - Test status: [x] pass (suite exists; not rerun locally 2025-11-26).

- [x] F-012 Deployment-ready settings
  - User story: As an operator I want safe defaults so that production is secure
  - Acceptance notes:
    - AC1 Split settings: base/local/prod; DEBUG=False in prod; ALLOWED_HOSTS set
    - AC2 Env var parsing via django-environ and secrets sourced securely
    - AC3 Security headers configured; HTTPS ready
  - Status: base/local/prod split with env-driven config; prod enforces SECRET_KEY/ALLOWED_HOSTS and secure cookies/HSTS/SSL redirect; Sentry optional.
  - Evidence: `core/settings/{base,local,prod}.py`.
  - Test status: [ ] not automated (manual settings review; CI runs `manage.py check`).

- [ ] F-013 Performance and caching
  - User story: As a user I want fast responses so that the app feels snappy
  - Acceptance notes:
    - AC1 Use select_related/prefetch_related and indexes on hot paths
    - AC2 Enable per-view/low-level caching on search and airport endpoints
    - AC3 Cache headers for static/dynamic responses as appropriate
  - Status: select_related/pagination in search; bounding-box filtering and indexes for airports; cache_page on calculators/search plus CacheHeaderMiddleware. Missing: caching for nearest JSON, explicit prefetch patterns, and perf profiling/benchmarks.
  - Evidence: `apps/search/views.py`, `apps/airports/models.py`, `core/middleware.py`; tests in `apps/calculators/test_caching.py`, `apps/search/tests/test_caching.py`.
  - Test status: [x] pass (suite exists; not rerun locally 2025-11-26).

- [ ] F-014 Security posture
  - User story: As an operator I want common risks mitigated so that user data is protected
  - Acceptance notes:
    - AC1 CSRF and input sanitization verified; templates autoescape; bleach where needed
    - AC2 Auth hardening with validators; admin access restricted; 2FA optional note
    - AC3 Rate limit on auth endpoints; CAPTCHA optional
  - Status: CSRF/middleware active; sanitize filter + tests; password validators enabled; login rate limiting via mixin. Missing: CSP, CAPTCHA/rate limiting beyond auth, dependency scanning, admin hardening/2FA guidance.
  - Evidence: `core/settings/base.py`, `apps/base/utils/sanitize.py`, `apps/accounts/mixins.py`; tests in `core/tests/test_sanitization.py`, `apps/accounts/tests/test_rate_limit.py`.
  - Test status: [x] pass (suite exists; not rerun locally 2025-11-26).

- [x] F-015 Observability and debugging
  - User story: As a developer I want actionable visibility so that I can fix issues quickly
  - Acceptance notes:
    - AC1 Structured logging with request ID; error pages customized
    - AC2 Debug toolbar only in local; email console backend verified
    - AC3 Sentry (or placeholder interface) documented for production
  - Status: Structured JSON logging + request ID; custom 404/500 templates with tests; optional Sentry init guarded by env. Debug toolbar/email console not configured but not required by core flows.
  - Evidence: `core/logging.py`, `core/middleware.py`, `core/sentry.py`, `templates/404.html`, `templates/500.html`, tests in `core/tests/test_observability.py`.
  - Test status: [x] pass (suite exists; not rerun locally 2025-11-26).

---

Next steps (optional):
- Wire calculators to `core/session.py` and SavedCalculation to satisfy F-001 AC4 and F-006 AC2/AC3.
- Add airport detail page/links for F-002 AC3.
- Document/provision media serving in DEBUG and production storage/CDN plan for F-010.
- Expand CI matrix to run all app tests and publish coverage.
