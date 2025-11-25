# Tutorial: ADR-1.0.11 Testing Strategy

Goal

- Explain and guide the testing strategy delivered by ADR-1.0.11 using its briefs and the implemented tooling.

Context

- ADR: `docs/travelmathlite/adr/adr-1.0.11-testing-strategy.md`
- Briefs: `docs/travelmathlite/briefs/adr-1.0.11/` (base test classes, calculator tests, search tests, mocking/time helpers, auth flows)

Prerequisites

- Working TravelMathLite dev environment
- `uv` available for running Django commands
- No additional datasets required

Steps (guided by briefs)

1) Summary of decisions and scope from ADR
- Use Django `TestCase` (no pytest) with custom base classes for determinism.
- Provide mocking/time helpers and consistent fixtures.
- Cover calculators/search/auth flows with deterministic tests.

2) Key files to touch or review
- Base test classes: `travelmathlite/apps/base/tests/base.py`
- Mocking/time examples: `travelmathlite/apps/base/tests/test_mocking_examples.py`
- Auth flow tests: `travelmathlite/core/tests/test_auth.py`
- Calculator/search tests: see `travelmathlite/apps/calculators/tests/` and `travelmathlite/apps/search/tests/`
- Docs: `docs/travelmathlite/testing.md` (security/observability test entry points included)

3) Minimal, copy-pasteable commands
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

4) Minimal code snippets with links to source files
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

5) Verification
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
- [Bootstrap documentation](https://getbootstrap.com/docs/)
- [HTMX documentation](https://htmx.org/docs/)
