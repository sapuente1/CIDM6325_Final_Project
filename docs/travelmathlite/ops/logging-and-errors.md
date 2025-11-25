# Logging and Error Handling Guide (ADR-1.0.13)

**Status:** In progress (logging implemented; error templates/Sentry toggle to be wired via ADR-1.0.13 briefs)  
**Links:** ADR-1.0.13 · PRD §4 (F-015/F-009) · PRD §11 (metrics)

## Overview
- Structured JSON logging with request metadata (request_id, path, status, duration) — see `core.logging.JSONFormatter` and `RequestIDMiddleware`.
- Error handling: custom 404/500 templates planned under `travelmathlite/templates/`; preview steps below.
- Optional Sentry: enable only when `SENTRY_DSN` is set; keep disabled by default.

## Logging
- Format: JSON lines with `timestamp`, `level`, `module`, `message`, `request_id`, `duration_ms`, optional `exc_info`.
- Env toggles:
  - `LOG_LEVEL` (root, default INFO)
  - `DJANGO_LOG_LEVEL` (Django loggers, default INFO)
- Quick tail:
  ```bash
  uv run python travelmathlite/manage.py runserver 2>&1 | tee /tmp/logs.json
  tail -f /tmp/logs.json | jq 'select(.level=="ERROR")'
  ```
- Tests: `uv run python travelmathlite/manage.py test core.tests.test_logging core.tests.test_health`

## Error pages (404/500)
- Templates to live at `travelmathlite/templates/404.html` and `travelmathlite/templates/500.html`, extending `base.html` with support links and request_id hint for correlation.
- Preview locally with DEBUG off:
  ```bash
  DJANGO_SETTINGS_MODULE=core.settings.prod \
  SECRET_KEY=dev-secret \
  ALLOWED_HOSTS=localhost \
  uv run python travelmathlite/manage.py runserver
  ```
  - 404: visit `http://localhost:8000/does-not-exist/`
  - 500: temporarily raise in a view or use a test-only endpoint; revert after verification.

## Optional Sentry (guarded)
- When SDK and DSN are configured, initialize Sentry with DjangoIntegration:
  - `SENTRY_DSN` (set to enable)
  - `SENTRY_ENV` (e.g., `local`, `staging`, `prod`)
  - `SENTRY_RELEASE` (git SHA or tag)
- Keep disabled by default; ensure code guards initialization when `SENTRY_DSN` is missing.
- Recommended SDK: `sentry-sdk[django]`; pin in `pyproject.toml`/`requirements.txt` when enabling.

## Verification checklist
- Logs emit JSON with `request_id` and `duration_ms` (see `core.tests.test_logging`).
- Health endpoint passes (`core.tests.test_health`).
- 404/500 templates render (after brief-02 implementation).
- Sentry init guarded by DSN (after brief-03 implementation).
