# Deployment quickstart (ADR-1.0.14)

**Run target:** gunicorn + WhiteNoise using `core.settings.prod`  
**Use case:** demo/staging on a small VM or PaaS (no container orchestration required)

## Run command

From repo root:

```bash
# Ensure env vars are set (see below), then:
DJANGO_SETTINGS_MODULE=core.settings.prod \
uv run gunicorn core.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --access-logfile -
```

Notes:
- WhiteNoise serves static assets; no NGINX required for demos.
- `PORT` defaults to 8000 if not provided by the platform.
- To quiet request logs, set `REQUEST_LOG_LEVEL=WARNING`.

## Required/expected environment

- `SECRET_KEY` (required)
- `ALLOWED_HOSTS` (comma-separated; required)
- `DATABASE_URL` (recommended; defaults to sqlite if unset)
- `PORT` (platform-provided or set manually)
- Security (optional overrides): `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, etc. (see `docs/security.md`)
- Logging (optional): `LOG_LEVEL`, `REQUEST_LOG_LEVEL`
- Sentry (optional): `SENTRY_DSN`, `SENTRY_ENV`, `SENTRY_RELEASE`
- Health endpoint check: `/health/` returns 200 with JSON `{"status": "ok"}` and `X-Request-ID` header.

## Static assets

Run collectstatic before serving:

```bash
# Optional: clear old files, then collect
uv run python travelmathlite/manage.py collectstatic --noinput --clear
```

Defaults:
- `STATIC_ROOT` = `travelmathlite/staticfiles` (override via env)
- Manifest/hashed assets enabled when `USE_MANIFEST_STATIC=1` or `DEBUG=False`
- Storage: `ManifestStaticFilesStorage` when enabled; hashed filenames for cache busting.

## Smoke test

After starting gunicorn, verify health:

```bash
curl -f http://localhost:${PORT:-8000}/health/
```

Expected: HTTP 200 with `{"status": "ok"}` and `X-Request-ID` header.

## Troubleshooting / rollback

- Missing headers or prod flags: confirm `DJANGO_SETTINGS_MODULE=core.settings.prod` and required env vars are set.
- Static 404s: ensure `collectstatic` ran and `STATIC_ROOT` is writable.
- To roll back quickly: stop the gunicorn process, revert env changes, and restart with known-good settings.
