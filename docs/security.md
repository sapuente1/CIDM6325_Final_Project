# Travelmathlite security settings

Links: ADR-1.0.12, PRD §4 (F-012/F-014), NF-003.

## Defaults
- `SecurityMiddleware` and `XFrameOptionsMiddleware` stay enabled in all environments.
- Production defaults: HTTPS redirect on, secure+HttpOnly session and CSRF cookies, HSTS (31536000s) with subdomains, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`.
- Development defaults: secure cookie flags and HSTS disabled when `DJANGO_DEBUG=true`; headers remain configurable via env vars.

## Environment toggles (base/prod)
- `SESSION_COOKIE_SECURE` (default: `!DEBUG`)
- `SESSION_COOKIE_HTTPONLY` (default: `true`)
- `CSRF_COOKIE_SECURE` (default: `!DEBUG`)
- `CSRF_COOKIE_HTTPONLY` (default: `true`)
- `SECURE_SSL_REDIRECT` (default: `!DEBUG`)
- `SECURE_HSTS_SECONDS` (default: `0` when `DEBUG` else `31536000`)
- `SECURE_HSTS_INCLUDE_SUBDOMAINS` (default: `!DEBUG`; prod default `true`)
- `SECURE_HSTS_PRELOAD` (default: `false`)
- `SECURE_CONTENT_TYPE_NOSNIFF` (default: `!DEBUG`)
- `SECURE_REFERRER_POLICY` (default: `strict-origin-when-cross-origin`)
- `X_FRAME_OPTIONS` (default: `DENY`)
- `USE_WHITENOISE` (prod default: `true`)
- `BLEACH_ALLOWED_TAGS` (default: `p, br, strong, em, b, i, u, a, ul, ol, li`)
- `BLEACH_ALLOWED_ATTRIBUTES` (default: `{"a": ["href", "title", "rel"]}`)
- `BLEACH_ALLOWED_PROTOCOLS` (default: `http, https, mailto`)
- `BLEACH_STRIP` (default: `true`)
- `BLEACH_STRIP_COMMENTS` (default: `true`)
- `RATE_LIMIT_AUTH_ENABLED` (default: `true`)
- `RATE_LIMIT_AUTH_MAX_REQUESTS` (default: `5`)
- `RATE_LIMIT_AUTH_WINDOW` (default: `60` seconds)

## Operational toggles and quick actions
- Disable login/signup rate limiting temporarily: `RATE_LIMIT_AUTH_ENABLED=0` (restart app).
- Relax or tighten limits: set `RATE_LIMIT_AUTH_MAX_REQUESTS` and `RATE_LIMIT_AUTH_WINDOW` (seconds); defaults are 5 in 60s.
- Enforce HTTPS redirects/HSTS: ensure `SECURE_SSL_REDIRECT=1` and `SECURE_HSTS_SECONDS>0`; set `SECURE_HSTS_INCLUDE_SUBDOMAINS=1` in prod.
- Local dev without redirects: `SECURE_SSL_REDIRECT=0` in `core/settings/local.py`.
- Adjust sanitization allowlist: override `BLEACH_ALLOWED_TAGS/ATTRIBUTES/PROTOCOLS`; defaults allow basic text and links only.

## Input sanitization
- `apps/base/utils/sanitize.py` centralizes `sanitize_html` using bleach allowlists.
- Template filter `{% load sanitize %} {{ value|sanitize_html }}` sanitizes user-provided HTML while preserving allowed tags.
- Applied in `trips/templates/trips/saved_list.html` for saved calculation inputs; search/results rely on Django autoescape + safe highlight filter.
- Tests: `core/tests/test_sanitization.py` (utility/filter) and `apps/trips/tests/test_sanitization.py` (saved calculations render sanitized).

## Security test commands
- Headers and CSRF: `uv run python travelmathlite/manage.py test core.tests.test_security`
- Rate limiting: `uv run python travelmathlite/manage.py test apps.accounts.tests.test_rate_limit`

## Verification
- Automated: `core.tests.test_settings_prod.ProdSettingsTest` checks secure cookie flags and header defaults.
- Manual: send an HTTPS request in production (e.g., `curl -I https://<host>/`) and confirm `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`, and `Referrer-Policy` headers are present.
