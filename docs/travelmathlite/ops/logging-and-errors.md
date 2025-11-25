# Logging and Error Handling Guide (ADR-1.0.13)

**Status:** Implemented  
**Links:** ADR-1.0.13 · PRD §4 (F-015/F-009) · PRD §11 (metrics)

## Overview
- Structured JSON logging with request metadata (request_id, path, method, status, duration) — via `RequestIDMiddleware`, `RequestLoggingMiddleware`, and `core.logging.JSONFormatter`.
- Error handling: custom 404/500 templates in `travelmathlite/templates/`.
- Optional Sentry: opt-in when `SENTRY_DSN` is set; disabled by default with safe guard if SDK missing.

## Logging
- Format: JSON lines with `timestamp`, `level`, `module`, `message`, `request_id`, `duration_ms`, `path`, `method`, `status_code`, optional `exc_info`.
  - Example request log:
    ```json
    {"timestamp": "...", "level": "INFO", "module": "middleware", "message": "request completed", "request_id": "abcd-1234", "duration_ms": 18.3, "path": "/accounts/login/", "method": "POST", "status_code": 429}
    ```
- Env toggles:
  - `LOG_LEVEL` (root, default INFO)
  - `DJANGO_LOG_LEVEL` (Django loggers, default INFO)
  - `REQUEST_LOG_LEVEL` (request logger, default INFO)
- Quick tail:
  ```bash
  uv run python travelmathlite/manage.py runserver 2>&1 | tee /tmp/logs.json
  tail -f /tmp/logs.json | jq 'select(.level=="ERROR")'
  ```
- Notes:
  - `RequestLoggingMiddleware` emits per-request logs; keep it after `RequestIDMiddleware`.
  - To quiet noisy logs temporarily: `REQUEST_LOG_LEVEL=WARNING` (see Rollback below).
- Tests: `uv run python travelmathlite/manage.py test core.tests.test_logging core.tests.test_health`

## Error pages (404/500)
- Templates live at `travelmathlite/templates/404.html` and `travelmathlite/templates/500.html`, extending `base.html` with support links and request_id hint for correlation.
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
- When SDK and DSN are configured, Sentry initializes via `core.sentry.init_sentry()` (called from `core.wsgi`):
  - `SENTRY_DSN` (set to enable)
  - `SENTRY_ENV` (e.g., `local`, `staging`, `prod`)
  - `SENTRY_RELEASE` (git SHA or tag)
- Keep disabled by default; ensure code guards initialization when `SENTRY_DSN` is missing.
- Recommended SDK: `sentry-sdk[django]`; pin in `pyproject.toml`/`requirements.txt` when enabling.
- Enable locally (opt-in):
  ```bash
  export SENTRY_DSN=https://example.ingest.sentry.io/123
  export SENTRY_ENV=local
  uv run python travelmathlite/manage.py runserver
  ```
- Disable: unset `SENTRY_DSN` or leave blank; init short-circuits and app runs normally.

## Verification checklist
- Logs emit JSON with `request_id`, `duration_ms`, `path`, `method`, `status_code` (see `core.tests.test_logging` and `core.tests.test_observability`).
- Health endpoint passes (`core.tests.test_health`).
- Observability suite: `uv run python travelmathlite/manage.py test core.tests.test_observability` (logs, 404/500 templates, Sentry guard).
- 404/500 templates render (covered in observability suite).
- Sentry init guarded by DSN (covered in observability suite).

## Rollback
- To quiet structured request logs temporarily, set `REQUEST_LOG_LEVEL=WARNING` or remove `RequestLoggingMiddleware` from `MIDDLEWARE` (revert afterward).
- To disable Sentry, remove/unset `SENTRY_DSN`; no code change required.
