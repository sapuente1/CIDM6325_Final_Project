# Tutorial: ADR-1.0.11 Testing Strategy

**Date:** November 25, 2025  
**ADR Reference:** [ADR-1.0.11 Testing Strategy](../../travelmathlite/adr/adr-1.0.11-testing-strategy.md)  
**Briefs:** [adr-1.0.11 briefs](../../travelmathlite/briefs/adr-1.0.11/)  
**PRD trace:** §4 F-011 (FR-F-011-1), NF-004 (reliability)

---

## Overview

ADR-1.0.11 defines a Django `TestCase`-only strategy (no pytest) focused on deterministic tests: shared base classes for mocking/time control, calculator/search/auth coverage, and health/import checks. This guide walks through each brief with steps, code, commands, verification, and troubleshooting so you can extend or debug the suite safely.

**Learning Objectives**

- Use `BaseTestCase`, `MockingTestCase`, and `TimeTestCase` to keep tests deterministic (INV-1).
- Cover calculators/search/auth flows with happy paths and edge cases (FR-F-011-1).
- Mock external calls and freeze time to avoid flakiness; keep tests isolated (NF-004).
- Run targeted suites quickly and mirror them with manual smoke checks.

**Prerequisites**

- Working TravelMathLite dev environment with `uv`.
- No extra datasets required.
- Familiarity with Django `TestCase`, `RequestFactory`, and the test client.

---

## How to use this tutorial

- Cite ADR and briefs (links above) in each section.
- For each brief: context → why it matters → steps → code excerpt (file path) → commands → verification (tests/URLs/expected) → troubleshooting.
- Reference docs: Django, Python stdlib (`unittest.mock`), plus HTMX/Bootstrap if UI touches.

---

## Section 1 — Test infrastructure and base classes (Brief 01)

**Context:** [brief-ADR-1.0.11-01-test-infrastructure.md](../../travelmathlite/briefs/adr-1.0.11/brief-ADR-1.0.11-01-test-infrastructure.md)  
**Why it matters:** INV-1 determinism; shared helpers reduce duplication and prevent real network/time drift.

**Steps**

- Use `BaseTestCase` for common setup, `MockingTestCase` for HTTP mocks, `TimeTestCase` for time freezing.
- RequestFactory helpers keep view tests fast; `_ensure_requests_module` guards against missing `requests`.

**Key code** (`travelmathlite/apps/base/tests/base.py`):

```python
class MockingTestCase(BaseTestCase):
    def _ensure_requests_module(self) -> Any:
        if "requests" not in sys.modules:
            sys.modules["requests"] = SimpleNamespace(get=lambda *args, **kwargs: None, post=lambda *args, **kwargs: None)

    def mock_http_get(self, url: str, response_data: Any, status_code: int = 200) -> Mock:
        self._ensure_requests_module()
        mock_response = Mock(status_code=status_code)
        mock_response.json.return_value = response_data
        patcher = patch("requests.get", return_value=mock_response)
        self._mocks.append(patcher)
        patcher.start()
        return mock_response
```

**Commands**

```bash
uv run python travelmathlite/manage.py test apps.base.tests.test_mocking_examples
```

**Verification**

- Tests pass; no external HTTP calls. ImportErrors for `requests` are handled by the shim.

**Troubleshooting**

- If mocks leak, ensure `_mocks` is cleared (built into base class).  
- If RequestFactory tests fail on middleware-dependent views, switch to the client.

---

## Section 2 — Calculator unit tests (Brief 02)

**Context:** [brief-ADR-1.0.11-02-calculator-tests.md](../../travelmathlite/briefs/adr-1.0.11/brief-ADR-1.0.11-02-calculator-tests.md)  
**Why it matters:** FR-F-011-1 requires correct calculations and cache behavior.

**Steps**

- Cover pure functions (`test_geo.py`, `test_costs.py`) and caching utilities.
- Use deterministic inputs; assert numeric outputs with tolerances.

**Key code** (`travelmathlite/apps/calculators/tests/test_geo.py`):

```python
class GeoTests(TestCase):
    def test_haversine_distance(self) -> None:
        dist = haversine_distance((32.8998, -97.0403), (33.9416, -118.4085))
        self.assertGreater(dist, 0)
        self.assertAlmostEqual(round(dist, 1), 1983.9, places=1)
```

**Commands**

```bash
uv run python travelmathlite/manage.py test calculators
```

**Verification**

- All calculator tests pass; no network calls. Manual: submit forms on `/calculators/distance/` and `/calculators/cost/` to mirror coverage.

**Troubleshooting**

- If float drift occurs, use `assertAlmostEqual` and keep constants in settings stable.  
- If forms fail, check defaults in `core/settings/base.py` for speed/fuel values.

---

## Section 3 — View tests (Brief 03)

**Context:** [brief-ADR-1.0.11-03-view-tests.md](../../travelmathlite/briefs/adr-1.0.11/brief-ADR-1.0.11-03-view-tests.md)  
**Why it matters:** Stable templates/routes underpin UX; ensures HTMX/full-page behavior.

**Steps**

- Use client/RequestFactory to hit calculator views; assert status, templates, context.

**Key code** (`travelmathlite/apps/calculators/tests/test_views.py`):

```python
class DistanceViewTests(TestCase):
    def test_distance_view_renders(self) -> None:
        resp = self.client.get(reverse("calculators:distance"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "calculators/distance_calculator.html")
```

**Commands**

```bash
uv run python travelmathlite/manage.py test calculators.tests.test_views
```

**Verification**

- 200 responses, correct templates. Manual: browse `/calculators/` and partials; expect HTMX snippets to render.

**Troubleshooting**

- If URLs break, confirm inclusion in `core/urls.py`. Update template assertions if layout legitimately changes.

---

## Section 4 — Search tests (Brief 04)

**Context:** [brief-ADR-1.0.11-04-search-tests.md](../../travelmathlite/briefs/adr-1.0.11/brief-ADR-1.0.11-04-search-tests.md)  
**Why it matters:** Search is user-facing; results/pagination/highlighting must hold.

**Steps**

- Test `/search/` with/without query; assert help text vs results and pagination.

**Key code** (`travelmathlite/apps/search/tests/test_views.py`):

```python
class SearchViewTests(TestCase):
    def test_search_page_without_query(self) -> None:
        resp = self.client.get(reverse("search:index"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Enter a term to search airports and cities.")
```

**Commands**

```bash
uv run python travelmathlite/manage.py test search
```

**Verification**

- No query → help text; query → results + pagination. Manual: `/search/?q=dfw` should show airports/cities with highlights.

**Troubleshooting**

- If highlighting fails, check `apps/search/templatetags/highlight.py`.  
- If fixtures missing, ensure tests use bundled data (avoid external calls).

---

## Section 5 — Auth tests (Brief 05)

**Context:** [brief-ADR-1.0.11-05-auth-tests.md](../../travelmathlite/briefs/adr-1.0.11/brief-ADR-1.0.11-05-auth-tests.md)  
**Why it matters:** Login/logout/signup/profile flows are core (FR-F-011-1).

**Steps**

- Test login 302 to home, logout 302 to home, signup creates user and redirects, profile requires auth.

**Key code** (`travelmathlite/core/tests/test_auth.py`):

```python
def test_login_success_redirects_to_home(self) -> None:
    resp = self.client.post(reverse("accounts:login"), {"username": self.user.username, "password": self.password})
    self.assertEqual(resp.status_code, 302)
    self.assertEqual(resp.url, reverse("base:index"))
```

**Commands**

```bash
uv run python travelmathlite/manage.py test core.tests.test_auth
```

**Verification**

- Login/logout redirect as expected; profile redirects anon to login. Manual: log in at `/accounts/login/`, hit `/accounts/profile/`, then logout.

**Troubleshooting**

- 301s in dev? Ensure `SECURE_SSL_REDIRECT=0` locally.  
- Profile 404? Confirm accounts URLs are included and Profile migrations applied.

---

## Section 6 — Health and import tests (Brief 06)

**Context:** [brief-ADR-1.0.11-06-health-and-import-tests.md](../../travelmathlite/briefs/adr-1.0.11/brief-ADR-1.0.11-06-health-and-import-tests.md)  
**Why it matters:** NF-004 reliability; health must be stable and imports deterministic.

**Steps**

- Test `/health/` returns 200 + JSON; ensure request ID header present.
- Import-related tests should mock external data (keep local).

**Key code** (`travelmathlite/core/tests/test_health.py`):

```python
class HealthEndpointTests(TestCase):
    def test_health_returns_ok(self) -> None:
        resp = self.client.get(reverse("health"))
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(resp.content.decode(), {"status": "ok"})
        self.assertIn("X-Request-ID", resp.headers)
```

**Commands**

```bash
uv run python travelmathlite/manage.py test core.tests.test_health
```

**Verification**

- 200 + JSON + `X-Request-ID`. Manual: `curl -i http://localhost:8000/health/`.

**Troubleshooting**

- If ALLOWED_HOSTS issues arise, set `ALLOWED_HOSTS=["*"]` for local tests (or use default local settings).

---

## Section 7 — Mocking and time helpers (Brief 07)

**Context:** [brief-ADR-1.0.11-07-mocking-and-time-tests.md](../../travelmathlite/briefs/adr-1.0.11/brief-ADR-1.0.11-07-mocking-and-time-tests.md)  
**Why it matters:** Determinism depends on controlled time/network (INV-1).

**Steps**

- Use `MockingTestCase` to patch `requests.get/post`; `TimeTestCase` to freeze time.

**Key code** (`travelmathlite/apps/base/tests/test_mocking_examples.py`):

```python
def test_freeze_time_for_duration(self) -> None:
    frozen = self.get_fixed_datetime(2025, 11, 19, hour=12, minute=34, second=56)
    self.freeze_time(frozen)
    self.assertEqual(timezone.now(), frozen)
```

**Commands**

```bash
uv run python travelmathlite/manage.py test apps.base.tests.test_mocking_examples
```

**Verification**

- Frozen time returns same value; HTTP mocks return deterministic payloads.

**Troubleshooting**

- Patch fully-qualified names; avoid external libs like freezegun (course norm).

---

## Section 8 — Visual checks integration (Brief 08)

**Context:** [brief-ADR-1.0.11-08-visual-checks-integration.md](../../travelmathlite/briefs/adr-1.0.11/brief-ADR-1.0.11-08-visual-checks-integration.md)  
**Why it matters:** Visual smoke tests catch UI regressions complementary to unit tests.

**Steps**

- Use Playwright scripts under `travelmathlite/scripts/`; store screenshots under `travelmathlite/screenshots/`.

**Commands (example)**

```bash
# Calculators HTMX visual checks
uv run python travelmathlite/scripts/visual_check_htmx_calculators.py
```

**Verification**

- Screenshots written; flows complete without 404/500. Manually review for layout issues.

**Troubleshooting**

- Install browsers if missing: `uvx playwright install chromium`.  
- Update selectors if templates change.

---

## Verification summary (quick run)

```bash
# Core suites
uv run python travelmathlite/manage.py test calculators search core.tests.test_auth core.tests.test_health

# Mocking/time helpers
uv run python travelmathlite/manage.py test apps.base.tests.test_mocking_examples
```

Expected: all pass; no external network calls; redirects match assertions.  
If failures: check ALLOWED_HOSTS/SECURE_SSL_REDIRECT for redirects; ensure mocks/caches not leaking; re-run focused suites (use `--keepdb` for speed when iterating).

---

## References

- [Understand Django (Matt Layman)](https://www.mattlayman.com/understand-django/)
- [Django documentation](https://docs.djangoproject.com/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [HTMX documentation](https://htmx.org/docs/)
- [Bootstrap documentation](https://getbootstrap.com/docs/)
