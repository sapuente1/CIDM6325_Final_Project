# Tutorial: ADR-1.0.12 Security Controls

**Date:** November 25, 2025  
**ADR Reference:** [ADR-1.0.12 Security Controls](../../travelmathlite/adr/adr-1.0.12-security-controls.md)  
**Briefs:** [adr-1.0.12 briefs](../../travelmathlite/briefs/adr-1.0.12/)  
**PRD trace:** §4 F-012/F-014 (FR-F-012-1, FR-F-014-1), NF-003

---

## Overview

ADR-1.0.12 hardens the app: security headers/cookies, auth rate limiting, input sanitization, targeted security tests, and documentation of toggles. This guide walks each brief with steps, code, commands, verification, and troubleshooting so you can extend or debug safely.

**Learning Objectives**
- Configure security headers, secure cookies, and HSTS with DEBUG-aware defaults.
- Apply auth rate limiting with env toggles.
- Sanitize user-rendered HTML via bleach with allowlists.
- Run security test suites (headers/CSRF/rate limits/sanitization) and interpret outputs.
- Use docs/toggles to enable/disable controls in different environments.

**Prerequisites**
- Working TravelMathLite dev environment with `uv`.
- Ability to run Django tests and `curl` locally.
- No extra datasets required.

---

## How to use this tutorial
- Cite ADR and briefs in each section.
- For each brief: context → why it matters → steps → code excerpt (with path) → commands → verification (tests/URLs/expected outputs) → troubleshooting.
- Reference docs: Django, Python stdlib (`unittest.mock`), bleach.

---

## Section 1 — Security settings hardening (Brief 01)

**Context:** [brief-ADR-1.0.12-01-security-settings.md](../../travelmathlite/briefs/adr-1.0.12/brief-ADR-1.0.12-01-security-settings.md)  
**Why it matters:** FR-F-012-1 and FR-F-014-1 require secure headers/cookies; NF-003 demands documented toggles.

**Steps**
- Keep `SecurityMiddleware` near the top of `MIDDLEWARE`.
- Set secure cookies, HSTS, referrer policy, X-Frame-Options, nosniff with DEBUG-aware defaults.
- Document toggles in `docs/security.md`.

**Key code** (`travelmathlite/core/settings/base.py`):
```python
SECURE_REFERRER_POLICY = env("SECURE_REFERRER_POLICY", default="strict-origin-when-cross-origin")
X_FRAME_OPTIONS = env("X_FRAME_OPTIONS", default="DENY")
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=not DEBUG)
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=not DEBUG)
SECURE_HSTS_SECONDS = int(env("SECURE_HSTS_SECONDS", default="31536000" if not DEBUG else "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=not DEBUG)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool("SECURE_CONTENT_TYPE_NOSNIFF", default=not DEBUG)
```

**Commands**
```bash
# Sanity check settings
uv run python travelmathlite/manage.py check
# Prod settings test
uv run python travelmathlite/manage.py test core.tests.test_settings_prod
```

**Verification**
- Curl prod/staging: `curl -I https://<host>/` → expect `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`.
- Local dev should not force HTTPS: `SECURE_SSL_REDIRECT=0` in `core/settings/local.py`.

**Troubleshooting**
- Redirect loops locally → set `SECURE_SSL_REDIRECT=0`.  
- Missing HSTS in staging → ensure `DEBUG=False` and `SECURE_HSTS_SECONDS>0`.

---

## Section 2 — Auth rate limiting (Brief 02)

**Context:** [brief-ADR-1.0.12-02-auth-rate-limiting.md](../../travelmathlite/briefs/adr-1.0.12/brief-ADR-1.0.12-02-auth-rate-limiting.md)  
**Why it matters:** Mitigates brute force on login/signup (FR-F-014-1).

**Steps**
- Add `RateLimitMixin` using cache to count POST attempts per IP/username.
- Apply to login/signup views; expose toggles `RATE_LIMIT_AUTH_ENABLED/MAX_REQUESTS/WINDOW`.

**Key code** (`apps/accounts/mixins.py`):
```python
class RateLimitMixin:
    def get_rate_limit_config(self) -> tuple[bool, int, int]:
        enabled = getattr(settings, "RATE_LIMIT_AUTH_ENABLED", False)
        max_requests = int(getattr(settings, "RATE_LIMIT_AUTH_MAX_REQUESTS", 5))
        window = int(getattr(settings, "RATE_LIMIT_AUTH_WINDOW", 60))
        return enabled, max_requests, window

    def check_rate_limit(self, request: HttpRequest) -> HttpResponse | None:
        # increments per request.path + identifier; returns 429 after threshold
```

**Commands**
```bash
uv run python travelmathlite/manage.py test apps.accounts.tests.test_rate_limit
```

**Verification**
- Automated: tests expect 429 on third bad login/signup attempt with defaults.  
- Manual: post 3 bad logins from same IP to `/accounts/login/` → 429 on third; set `RATE_LIMIT_AUTH_ENABLED=0` to disable quickly.

**Troubleshooting**
- In multi-process setups, use a shared cache (Redis/Memcached); locmem is single-process.
- If 429 arrives too early/late, adjust env: `RATE_LIMIT_AUTH_MAX_REQUESTS`, `RATE_LIMIT_AUTH_WINDOW`.

---

## Section 3 — Input sanitization (Brief 03)

**Context:** [brief-ADR-1.0.12-03-input-sanitization.md](../../travelmathlite/briefs/adr-1.0.12/brief-ADR-1.0.12-03-input-sanitization.md)  
**Why it matters:** Prevent XSS when rendering user input (FR-F-012-1).

**Steps**
- Centralize bleach allowlists and a `sanitize_html` helper; expose as template filter.
- Apply to user-rendered fields (saved calculations preview).
- Keep autoescape for other templates; use filter only where HTML is expected.

**Key code** (`apps/base/utils/sanitize.py`):
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

**Commands**
```bash
uv run python travelmathlite/manage.py test core.tests.test_sanitization apps.trips.tests.test_sanitization
```

**Verification**
- Automated: tests assert `<script>` stripped, `<b>` preserved, script text rendered as text.
- Manual: seed saved calc inputs with `<script>alert(1)</script><b>ok</b>` and visit `/trips/saved/`; expect no `<script>`, text “alert(1)”, and bold “ok”.

**Troubleshooting**
- Missing bleach? ensure dependency present (declared in requirements).  
- Need richer HTML? Adjust `BLEACH_ALLOWED_TAGS/ATTRIBUTES/PROTOCOLS` envs and update docs/tests accordingly.

---

## Section 4 — Security tests (Brief 04)

**Context:** [brief-ADR-1.0.12-04-security-tests.md](../../travelmathlite/briefs/adr-1.0.12/brief-ADR-1.0.12-04-security-tests.md)  
**Why it matters:** Proves headers/CSRF/rate limits behave under prod-like settings.

**Steps**
- Header/CSRF tests in `core/tests/test_security.py`; rate limit tests reuse `apps.accounts.tests.test_rate_limit`.
- Use `override_settings` to simulate prod and enforce CSRF.

**Key code** (`core/tests/test_security.py`):
```python
@override_settings(
    DEBUG=False,
    ALLOWED_HOSTS=["testserver"],
    SECURE_HSTS_SECONDS=31536000,
    SECURE_CONTENT_TYPE_NOSNIFF=True,
    SECURE_REFERRER_POLICY="strict-origin-when-cross-origin",
    X_FRAME_OPTIONS="DENY",
)
class SecurityHeaderTests(TestCase):
    def test_security_headers_present_on_secure_request(self) -> None:
        resp = Client().get("/", secure=True)
        self.assertEqual(resp.headers.get("Strict-Transport-Security"), "max-age=31536000; includeSubDomains")
```

**Commands**
```bash
uv run python travelmathlite/manage.py test core.tests.test_security apps.accounts.tests.test_rate_limit
```

**Verification**
- Tests pass; warnings for expected 403/429 may appear in logs (negative scenarios).
- Manual: `curl -I https://<host>/` for headers; attempt repeated bad logins for 429.

**Troubleshooting**
- If SECRET_KEY/ALLOWED_HOSTS errors appear, mimic test env patches; ensure `DEBUG=False` when checking headers.

---

## Section 5 — Security docs and toggles (Brief 05)

**Context:** [brief-ADR-1.0.12-05-security-docs-and-toggles.md](../../travelmathlite/briefs/adr-1.0.12/brief-ADR-1.0.12-05-security-docs-and-toggles.md)  
**Why it matters:** NF-003 requires documented toggles and operational guidance.

**Steps**
- Maintain toggles and commands in `docs/security.md`; link from README/testing guides.
- Include how to disable/relax controls safely (e.g., rate limits off, HTTPS redirect off locally).

**Key doc** (`docs/security.md`):
- Lists `SECURE_*`, `BLEACH_*`, `RATE_LIMIT_*` defaults and verification commands.

**Verification**
- Docs mention test commands and manual curl checks; toggles match settings files.

**Troubleshooting**
- When toggles change in code, update docs and tests in sync.

---

## Verification summary (quick run)

```bash
# Headers, CSRF, rate limits
uv run python travelmathlite/manage.py test core.tests.test_security apps.accounts.tests.test_rate_limit

# Sanitization
uv run python travelmathlite/manage.py test core.tests.test_sanitization apps.trips.tests.test_sanitization
```

Expected: all pass; 403/429 warnings may appear (negative cases). For manual checks: `curl -I https://<host>/` and try 3 bad logins for 429.

---

## References

- [Django documentation](https://docs.djangoproject.com/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [bleach documentation](https://bleach.readthedocs.io/en/latest/)
- [HTMX documentation](https://htmx.org/docs/)
- [Understand Django (Matt Layman)](https://www.mattlayman.com/understand-django/)
