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

## Verification
- Automated: `core.tests.test_settings_prod.ProdSettingsTest` checks secure cookie flags and header defaults.
- Manual: send an HTTPS request in production (e.g., `curl -I https://<host>/`) and confirm `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`, and `Referrer-Policy` headers are present.
