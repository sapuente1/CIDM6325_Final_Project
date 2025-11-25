# Tutorial: ADR-1.0.11 Testing Strategy

Goal

- Explain and guide the testing strategy delivered by ADR-1.0.11 using its briefs and the implemented tooling.

How to use this tutorial

- Cite ADR and briefs (with links) in overview/context.
- Anchor “why it matters” to PRD/FR/NF IDs from the ADR.
- For each brief area: context → steps → code excerpt with file path → commands to run → verification (URLs/tests/expected outputs) → troubleshooting.
- Reference docs: Django, Python stdlib (unittest/mock), plus relevant libs (Bootstrap/HTMX if UI touches).

Context

- ADR: `docs/travelmathlite/adr/adr-1.0.11-testing-strategy.md`
- Briefs: `docs/travelmathlite/briefs/adr-1.0.11/` (base test classes, calculator tests, search tests, mocking/time helpers, auth flows)

Prerequisites

- Working TravelMathLite dev environment
- `uv` available for running Django commands
- No additional datasets required

Steps (guided by briefs)

1. Summary of decisions and scope from ADR

- Use Django `TestCase` (no pytest) with custom base classes for determinism.
- Provide mocking/time helpers and consistent fixtures.
- Cover calculators/search/auth flows with deterministic tests.

1. Key files to touch or review

- Base test classes: `travelmathlite/apps/base/tests/base.py`
- Mocking/time examples: `travelmathlite/apps/base/tests/test_mocking_examples.py`
- Auth flow tests: `travelmathlite/core/tests/test_auth.py`
- Calculator/search tests: see `travelmathlite/apps/calculators/tests/` and `travelmathlite/apps/search/tests/`
- Docs: `docs/travelmathlite/testing.md` (security/observability test entry points included)

1. Minimal, copy-pasteable commands

- Run full test suite:

```bash
  uv run python travelmathlite/manage.py test
```

- Run focused suites:

```bash
  # Base classes + mocking examples + auth flows
  uv run python travelmathlite/manage.py test apps.base.tests.test_mocking_examples core.tests.test_auth

  # Calculators
  uv run python travelmathlite/manage.py test calculators

  # Search
  uv run python travelmathlite/manage.py test search
```

1. Minimal code snippets with links to source files

- Base test classes (`travelmathlite/apps/base/tests/base.py`):

```python
  class MockingTestCase(BaseTestCase):
      def mock_http_get(self, url: str, response_data: Any, status_code: int = 200) -> Mock:
          self._ensure_requests_module()
          mock_response = Mock()
          mock_response.status_code = status_code
          mock_response.json.return_value = response_data
          patcher = patch("requests.get", return_value=mock_response)
          self._mocks.append(patcher)
          patcher.start()
          return mock_response
```

- Auth flow coverage (`travelmathlite/core/tests/test_auth.py`):

```python
  def test_login_success_redirects_to_home(self) -> None:
      resp = self.client.post(reverse("accounts:login"), {"username": self.user.username, "password": self.password})
      self.assertEqual(resp.status_code, 302)
      self.assertEqual(resp.url, reverse("base:index"))
```

- Mocking examples (`travelmathlite/apps/base/tests/test_mocking_examples.py`):

 ```python
  def test_mock_http_get_replaces_requests_get(self) -> None:
      payload = {"message": "ok"}
      self.mock_http_get("https://example.com/api/status", payload, status_code=201)
      response = requests.get("https://example.com/api/status")
      self.assertEqual(response.status_code, 201)
      self.assertEqual(response.json(), payload)
```

1. Verification

- URLs to visit (manual smoke):
  - `/accounts/login/` → log in and hit `/accounts/profile/` to confirm redirects match tests.
  - `/calculators/` → run a calculation; `/search/` → perform a query to mirror tested flows.
- Tests to run (expected pass):

  ```bash
  uv run python travelmathlite/manage.py test apps.base.tests.test_mocking_examples core.tests.test_auth
  uv run python travelmathlite/manage.py test calculators
  uv run python travelmathlite/manage.py test search
  ```
  
- Expected outputs: All tests should pass; auth tests expect 302 redirects and template usage, mocking examples should not touch the network.

References

- [Understand Django (Matt Layman)](https://www.mattlayman.com/understand-django/)
- [Django documentation](https://docs.djangoproject.com/)
- [Python unittest/mock](https://docs.python.org/3/library/unittest.mock.html)
- [Bootstrap documentation](https://getbootstrap.com/docs/)
- [HTMX documentation](https://htmx.org/docs/)
# Tutorial: ADR-1.0.11 Testing Strategy

**Date:** November 25, 2025  
**ADR Reference:** [ADR-1.0.11 Testing Strategy](../../travelmathlite/adr/adr-1.0.11-testing-strategy.md)  
**Briefs:** [adr-1.0.11 briefs](../../travelmathlite/briefs/adr-1.0.11/)

---

## Overview

This tutorial walks through implementing ADR-1.0.11’s testing strategy: deterministic Django `TestCase` suites (no pytest), helper base classes for mocking/time control, and coverage for calculators, search, auth, and health/import flows.

**Learning Objectives**

- Use shared base test classes (`BaseTestCase`, `MockingTestCase`, `TimeTestCase`) to keep tests deterministic (INV-1).
- Write calculator/search/auth tests that assert happy paths and edge cases (FR-F-011-1).
- Mock external calls and freeze time to avoid flakiness.
- Run and interpret focused test suites and smoke URLs that mirror test coverage.

**Prerequisites**

- Working TravelMathLite dev environment with `uv`.
- No additional datasets required.
- Basic Django testing familiarity (`TestCase`, `RequestFactory`, `client`).

---

## How to use this tutorial

- Cite ADR and briefs (with links) in each section’s context.
- Anchor “why it matters” to PRD §4 F-011 and NF-004.
- For each brief area: context → steps → code excerpt with file path → commands → verification (URLs/tests/expected outputs) → troubleshooting.
- Reference docs: Django, Python stdlib (`unittest.mock`), plus HTMX/Bootstrap if UI touches.

---

## Section 1 — Test infrastructure and base classes (Brief 01)

**Context:** [brief-ADR-1.0.11-01-test-infrastructure.md](../../travelmathlite/briefs/adr-1.0.11/brief-ADR-1.0.11-01-test-infrastructure.md)  
**Why it matters:** INV-1 determinism; shared helpers reduce duplication across apps.

**Steps**
- Use `BaseTestCase` for common setup, `MockingTestCase` for HTTP mocks, `TimeTestCase` for time freezing.
- RequestFactory helpers keep view tests fast; `_ensure_requests_module` protects mocks when `requests` isn’t installed.

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
- Tests should pass; no external HTTP calls made.
- If you see ImportError for `requests`, ensure `_ensure_requests_module` is present (already implemented).

**Troubleshooting**
- If mocks leak, ensure `_mocks` is cleared in `tearDown` (built into the base class).

---

## Section 2 — Calculator unit tests (Brief 02)

**Context:** [brief-ADR-1.0.11-02-calculator-tests.md](../../travelmathlite/briefs/adr-1.0.11/brief-ADR-1.0.11-02-calculator-tests.md)  
**Why it matters:** FR-F-011-1 requires calculator correctness (distance, cost, cache behavior).

**Steps**
- Cover pure functions (`test_geo.py`, `test_costs.py`) and caching utilities.
- Use deterministic inputs; assert numeric outputs and units.

**Key code** (`travelmathlite/apps/calculators/tests/test_geo.py`):
```python
class GeoTests(TestCase):
    def test_haversine_distance(self) -> None:
        dist = haversine_distance((32.8998, -97.0403), (33.9416, -118.4085))
        self.assertGreater(dist, 0)
```

**Commands**
```bash
uv run python travelmathlite/manage.py test calculators
```

**Verification**
- All calculator tests should pass; no network calls expected.

**Troubleshooting**
- If floats differ slightly, use approximate assertions (e.g., `assertAlmostEqual`) as in existing tests.

---

## Section 3 — View tests (Brief 03)

**Context:** [brief-ADR-1.0.11-03-view-tests.md](../../travelmathlite/briefs/adr-1.0.11/brief-ADR-1.0.11-03-view-tests.md)  
**Why it matters:** Ensure templates render and routes resolve (stable UX, F-011).

**Steps**
- Use Django test client/RequestFactory to hit calculator views.
- Assert status codes, templates used, and context keys.

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
- Pages render 200; templates match expectations.

**Troubleshooting**
- If URLs fail, verify `apps/calculators/urls.py` is included in `core/urls.py`.

---

## Section 4 — Search tests (Brief 04)

**Context:** [brief-ADR-1.0.11-04-search-tests.md](../../travelmathlite/briefs/adr-1.0.11/brief-ADR-1.0.11-04-search-tests.md)  
**Why it matters:** Search is user-facing; ensure queries and pagination are stable.

**Steps**
- Hit `/search/` with/without query; assert 200 and template usage.
- Check pagination links and highlighted fields.

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
- No query → help text; query → results list and pagination when applicable.

**Troubleshooting**
- If highlighting fails, review `apps/search/templatetags/highlight.py`.

---

## Section 5 — Auth tests (Brief 05)

**Context:** [brief-ADR-1.0.11-05-auth-tests.md](../../travelmathlite/briefs/adr-1.0.11/brief-ADR-1.0.11-05-auth-tests.md)  
**Why it matters:** Login/logout/signup/profile are core flows (FR-F-011-1).

**Steps**
- Cover login happy path, logout redirect, signup creates user, protected routes redirect anon to login with `next`.

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
- Login returns 302 to home; logout 302 to home; profile requires auth and redirects anon.

**Troubleshooting**
- If status is 301 in local dev, ensure `SECURE_SSL_REDIRECT=0` in local settings.

---

## Section 6 — Health and import tests (Brief 06)

**Context:** [brief-ADR-1.0.11-06-health-and-import-tests.md](../../travelmathlite/briefs/adr-1.0.11/brief-ADR-1.0.11-06-health-and-import-tests.md)  
**Why it matters:** NF-004 reliability; health endpoint and import logic must be stable.

**Steps**
- Run health check tests to ensure `/health/` returns 200 and JSON payload.
- Import-related tests (if present) should mock external data; see `core/tests/test_health.py`.

**Commands**
```bash
uv run python travelmathlite/manage.py test core.tests.test_health
```

**Verification**
- Health returns 200 with `{"status": "ok"}` and includes `X-Request-ID`.

**Troubleshooting**
- If health fails in prod-like settings, check ALLOWED_HOSTS and middleware order.

---

## Section 7 — Mocking and time helpers (Brief 07)

**Context:** [brief-ADR-1.0.11-07-mocking-and-time-tests.md](../../travelmathlite/briefs/adr-1.0.11/brief-ADR-1.0.11-07-mocking-and-time-tests.md)  
**Why it matters:** Determinism (INV-1) requires controlled time/network.

**Steps**
- Use `MockingTestCase` to patch `requests.get/post`; use `TimeTestCase` to freeze time.
- Examples live in `apps/base/tests/test_mocking_examples.py`.

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
- Tests pass; repeated `timezone.now()` returns frozen time; HTTP mocks return deterministic payloads.

**Troubleshooting**
- Ensure `freezegun` is not used (course norm); rely on provided helpers.

---

## Section 8 — Visual checks integration (Brief 08)

**Context:** [brief-ADR-1.0.11-08-visual-checks-integration.md](../../travelmathlite/briefs/adr-1.0.11/brief-ADR-1.0.11-08-visual-checks-integration.md)  
**Why it matters:** Visual smoke complements unit tests (optional but recommended).

**Steps**
- Use Playwright scripts under `travelmathlite/scripts/` (see docs/security/testing guides) to capture flows; keep screenshots under `travelmathlite/screenshots/`.
- Not required for CI; run locally for UI sanity.

**Commands (example)**
```bash
# Calculators HTMX visual checks
uv run python travelmathlite/scripts/visual_check_htmx_calculators.py
```

**Verification**
- Screenshots saved under `travelmathlite/screenshots/...`; flows complete without errors.

**Troubleshooting**
- If Playwright browser not installed: `uvx playwright install chromium`.

---

## Verification summary (quick run)

```bash
# Core suites
uv run python travelmathlite/manage.py test calculators search core.tests.test_auth core.tests.test_health

# Mocking/time helpers
uv run python travelmathlite/manage.py test apps.base.tests.test_mocking_examples
```

Expected: all pass; no external network calls; redirects match assertions.

---

## References

- [Understand Django (Matt Layman)](https://www.mattlayman.com/understand-django/)
- [Django documentation](https://docs.djangoproject.com/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [HTMX documentation](https://htmx.org/docs/)
- [Bootstrap documentation](https://getbootstrap.com/docs/)
