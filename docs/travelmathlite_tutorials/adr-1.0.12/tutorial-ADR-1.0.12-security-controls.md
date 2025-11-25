# Tutorial: ADR-1.0.12 Security Controls

Goal

- Explain and guide the security controls delivered by ADR-1.0.12 using its briefs and implemented settings, middleware, filters, and tests.

How to use this tutorial

- Cite ADR and briefs (with links) in overview/context.
- Anchor “why it matters” to PRD §4 (F-012/F-014) and NF-003 noted in ADR.
- For each brief area: context → steps → code excerpt with file path → commands to run → verification (URLs/tests/expected outputs) → troubleshooting.
- Reference docs: Django, Python stdlib (unittest/mock), and libraries used (bleach).

Context

- ADR: `docs/travelmathlite/adr/adr-1.0.12-security-controls.md`
- Briefs: `docs/travelmathlite/briefs/adr-1.0.12/` (01 security settings, 02 auth rate limiting, 03 input sanitization, 04 security tests, 05 security docs/toggles)

Prerequisites

- Working TravelMathLite dev environment with uv
- No additional datasets required
- Ability to run Django tests and `curl` locally

Overview (why it matters)

- PRD §4 F-012/F-014 require hardened security headers, cookies, CSRF, and auth rate limiting.
- ADR-1.0.12 opts for Django built-ins + bleach + optional rate limiting to keep risk low and configuration simple (NF-003 traceability).

Section 1 — Security settings hardening (Brief 01)

- Key files: `travelmathlite/core/settings/base.py`, `travelmathlite/core/settings/prod.py`
- Steps:
  - Ensure `SecurityMiddleware` present early in `MIDDLEWARE`.
  - Set secure cookies, HSTS, referrer policy, X-Frame-Options with DEBUG-aware defaults.
  - Document toggles in `docs/security.md`.
- Code excerpt (`core/settings/base.py`):
  ```python
  SECURE_REFERRER_POLICY = env("SECURE_REFERRER_POLICY", default="strict-origin-when-cross-origin")
  X_FRAME_OPTIONS = env("X_FRAME_OPTIONS", default="DENY")
  SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=not DEBUG)
  SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=not DEBUG)
  SECURE_HSTS_SECONDS = int(env("SECURE_HSTS_SECONDS", default="31536000" if not DEBUG else "0"))
  ```
- Commands:
  ```bash
  uv run python travelmathlite/manage.py check
  ```
- Verification:
  - Curl an endpoint (prod-like): `curl -I https://<host>/` → expect `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`.
  - Run prod settings test: `uv run python travelmathlite/manage.py test core.tests.test_settings_prod`
- Troubleshooting:
  - If redirects block local dev, set `SECURE_SSL_REDIRECT=0` (local settings already do this).

Section 2 — Auth rate limiting (Brief 02)

- Key files: `travelmathlite/apps/accounts/mixins.py`, `travelmathlite/apps/accounts/views.py`, `travelmathlite/apps/accounts/urls.py`, `core/settings/base.py` (`RATE_LIMIT_AUTH_*`)
- Steps:
  - Introduce `RateLimitMixin` that tracks POST attempts per IP/username via cache.
  - Apply to LoginView/SignupView; add env toggles for enabled/max/window.
- Code excerpt (`apps/accounts/mixins.py`):
  ```python
  class RateLimitMixin:
      def get_rate_limit_config(self) -> tuple[bool, int, int]:
          enabled = getattr(settings, "RATE_LIMIT_AUTH_ENABLED", False)
          max_requests = int(getattr(settings, "RATE_LIMIT_AUTH_MAX_REQUESTS", 5))
          window = int(getattr(settings, "RATE_LIMIT_AUTH_WINDOW", 60))
          return enabled, max_requests, window
  ```
- Commands:
  ```bash
  uv run python travelmathlite/manage.py test apps.accounts.tests.test_rate_limit
  ```
- Verification (manual):
  - With defaults, three bad logins from same IP should yield 429 on the third POST.
  - Toggle off quickly by setting `RATE_LIMIT_AUTH_ENABLED=0`.
- Troubleshooting:
  - Ensure cache backend is available (locmem default). If running in multi-process setup, use a shared cache.

Section 3 — Input sanitization (Brief 03)

- Key files: `apps/base/utils/sanitize.py`, `apps/base/templatetags/sanitize.py`, `core/settings/base.py` (BLEACH_*), `apps/trips/templates/trips/saved_list.html`
- Steps:
  - Centralize `sanitize_html` using bleach allowlists and expose as template filter.
  - Apply to user-rendered fields (saved calculations preview).
- Code excerpt (`apps/base/utils/sanitize.py`):
  ```python
  def sanitize_html(value: str | None) -> str:
      cleaned = bleach.clean(
          value or "",
          tags=settings.BLEACH_ALLOWED_TAGS,
          attributes=settings.BLEACH_ALLOWED_ATTRIBUTES,
          protocols=settings.BLEACH_ALLOWED_PROTOCOLS,
          strip=settings.BLEACH_STRIP,
          strip_comments=settings.BLEACH_STRIP_COMMENTS,
      )
      return mark_safe(cleaned)
  ```
- Commands:
  ```bash
  uv run python travelmathlite/manage.py test core.tests.test_sanitization apps.trips.tests.test_sanitization
  ```
- Verification:
  - Seed a saved calculation with `<script>alert(1)</script><b>ok</b>`; page should show `alert(1)` as text, keep `<b>ok</b>`, and strip `<script>`.
  - Env toggles allow adjusting allowed tags/attributes/protocols.
- Troubleshooting:
  - If bleach not installed, ensure `bleach` dependency present (declared in requirements/pyproject).

Section 4 — Security tests (Brief 04)

- Key files: `core/tests/test_security.py`, `apps/accounts/tests/test_rate_limit.py` (shared with Section 2), `docs/security.md`
- Steps:
  - Assert security headers present under prod-like settings.
  - Verify CSRF token presence and enforcement.
  - Confirm rate-limit 429 after threshold.
- Commands:
  ```bash
  uv run python travelmathlite/manage.py test core.tests.test_security apps.accounts.tests.test_rate_limit
  ```
- Verification:
  - Tests should pass; warnings may show 403/429 during negative scenarios (expected).
- Troubleshooting:
  - If SECRET_KEY/ALLOWED_HOSTS missing in tests, ensure `override_settings` or env patching mirrors existing tests.

Section 5 — Security docs and toggles (Brief 05)

- Key file: `docs/security.md`
- Steps:
  - Document all env toggles (SECURE_*, BLEACH_*, RATE_LIMIT_*) and operational guidance.
  - Provide test commands and manual verification notes.
- Commands:
  - Docs only; no code commands. Run tests as above for validation.
- Verification:
  - Confirm the guide lists toggles and references tests/commands.
- Troubleshooting:
  - Keep docs in sync when toggles change; update `docs/travelmathlite/README.md` links if new guides are added.

Verification summary (quick run)

```bash
# Headers, CSRF, and rate limits
uv run python travelmathlite/manage.py test core.tests.test_security apps.accounts.tests.test_rate_limit

# Sanitization
uv run python travelmathlite/manage.py test core.tests.test_sanitization apps.trips.tests.test_sanitization
```

References

- [Understand Django (Matt Layman)](https://www.mattlayman.com/understand-django/)
- [Django documentation](https://docs.djangoproject.com/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [bleach documentation](https://bleach.readthedocs.io/en/latest/)
- [HTMX documentation](https://htmx.org/docs/)
