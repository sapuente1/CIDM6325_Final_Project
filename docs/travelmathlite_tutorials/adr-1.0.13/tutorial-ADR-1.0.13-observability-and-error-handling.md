# Tutorial: ADR-1.0.13 Observability and Error Handling

**Date:** November 25, 2025  
**ADR Reference:** [ADR-1.0.13 Observability and Error Handling](../../travelmathlite/adr/adr-1.0.13-observability-and-error-handling.md)  
**Briefs:** [adr-1.0.13 briefs](../../travelmathlite/briefs/adr-1.0.13/)  
**PRD trace:** §4 F-015/F-009, §11 (metrics)

---

## Overview

ADR-1.0.13 delivers structured JSON logging with request metadata, branded 404/500 templates, optional Sentry integration, and an observability test suite with documentation. This tutorial walks each brief with steps, code, commands, verification, and troubleshooting so you can extend or debug safely.

**Learning Objectives**
- Emit JSON logs with request_id/path/method/status/duration using middleware + formatter.
- Render custom 404/500 pages and preview them in DEBUG-off mode.
- Enable Sentry safely when `SENTRY_DSN` is provided; keep disabled by default.
- Run observability tests (logs, error pages, Sentry guard) and interpret outputs.
- Use the logging/error runbook for operations and rollback.

**Prerequisites**
- Working TravelMathLite dev environment with `uv`.
- Ability to run Django tests and `curl` locally.
- No extra datasets required.

---

## How to use this tutorial
- Cite ADR and briefs in each section.
- For each brief: context → why it matters → steps → code excerpt (with path) → commands → verification (tests/URLs/expected outputs) → troubleshooting.
- Reference docs: Django, Python stdlib (`unittest.mock`), Sentry SDK docs.

---

## Section 1 — Structured logging (Brief 01)

**Context:** [brief-ADR-1.0.13-01-structured-logging.md](../../travelmathlite/briefs/adr-1.0.13/brief-ADR-1.0.13-01-structured-logging.md)  
**Why it matters:** FR-F-015-1 requires structured logs with request correlation (request_id, path, status, duration).

**Steps**
- Use `RequestIDMiddleware` to stamp request_id/duration_ms; add `RequestLoggingMiddleware` to emit per-request logs.
- Extend `core.logging.JSONFormatter` to include path/method/status_code.
- Wire a `request` logger in `LOGGING`.

**Key code**
- Middleware (`travelmathlite/core/middleware.py`):
```python
class RequestLoggingMiddleware:
    logger = logging.getLogger("request")

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start = time.perf_counter()
        response = self.get_response(request)
        duration_ms = getattr(request, "duration_ms", None) or (time.perf_counter() - start) * 1000.0
        self.logger.info(
            "request completed",
            extra={
                "request_id": getattr(request, "request_id", "-"),
                "duration_ms": duration_ms,
                "path": request.path,
                "method": request.method,
                "status_code": response.status_code,
            },
        )
        return response
```
- Formatter (`travelmathlite/core/logging.py`):
```python
log_entry = {
    "timestamp": datetime.now(UTC).isoformat(),
    "level": record.levelname,
    "module": record.module,
    "message": record.getMessage(),
    "request_id": request_id,
    "duration_ms": duration_ms,
    "path": getattr(record, "path", None),
    "method": getattr(record, "method", None),
    "status_code": getattr(record, "status_code", None),
}
```
- Logger (`core/settings/base.py`):
```python
"request": {"handlers": ["console"], "level": env("REQUEST_LOG_LEVEL", default="INFO"), "propagate": False},
```

**Commands**
```bash
# Observability suite covers logging
uv run python travelmathlite/manage.py test core.tests.test_observability

# Quick tail during dev
uv run python travelmathlite/manage.py runserver 2>&1 | tee /tmp/logs.json
tail -f /tmp/logs.json | jq 'select(.level=="INFO" and .path=="/")'
```

**Verification**
- Expect per-request JSON logs with request_id/path/method/status_code/duration_ms.
- Manual: hit `/` and `/accounts/login/`; check logs show 200/302 (or 429 under rate limit tests).

**Troubleshooting**
- Missing fields: ensure middleware order has `RequestIDMiddleware` before `RequestLoggingMiddleware`.
- No logs: confirm `REQUEST_LOG_LEVEL` not set above INFO; logger name is `request`.

---

## Section 2 — Custom error templates (Brief 02)

**Context:** [brief-ADR-1.0.13-02-error-templates.md](../../travelmathlite/briefs/adr-1.0.13/brief-ADR-1.0.13-02-error-templates.md)  
**Why it matters:** FR-F-015-1 calls for user-friendly error pages with correlation hints.

**Steps**
- Create branded `404.html` and `500.html` under `travelmathlite/templates/`, extending `base.html`.
- Include request_id hint in copy (via response headers).

**Key code** (`travelmathlite/templates/404.html`):
```html
<h1>Page not found</h1>
<p>The page you’re looking for doesn’t exist or may have moved.</p>
<p class="text-muted">If you need help, include the request ID from the response headers.</p>
```

**Commands**
```bash
# Preview in prod-like mode
DJANGO_SETTINGS_MODULE=core.settings.prod SECRET_KEY=dev ALLOWED_HOSTS=localhost \
uv run python travelmathlite/manage.py runserver
```

**Verification**
- Visit `/does-not-exist/` → custom 404 renders.
- Induce 500 (temporary raise in a view) → custom 500 renders. Tests also cover this in `core.tests.test_observability`.

**Troubleshooting**
- If default Django pages appear, ensure templates are placed at `travelmathlite/templates/` and DEBUG=False for 500 preview.

---

## Section 3 — Optional Sentry toggle (Brief 03)

**Context:** [brief-ADR-1.0.13-03-sentry-toggle.md](../../travelmathlite/briefs/adr-1.0.13/brief-ADR-1.0.13-03-sentry-toggle.md)  
**Why it matters:** Opt-in error monitoring without mandatory third-party deps.

**Steps**
- Add guarded init in `core/sentry.py`; call from `core/wsgi.py`.
- Respect envs: `SENTRY_DSN`, `SENTRY_ENV`, `SENTRY_RELEASE`, `SENTRY_TRACES_SAMPLE_RATE`.

**Key code** (`travelmathlite/core/sentry.py`):
```python
def init_sentry() -> None:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
    except Exception:
        return
    sentry_sdk.init(
        dsn=dsn,
        integrations=[DjangoIntegration()],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")),
        environment=os.getenv("SENTRY_ENV", "local"),
        release=os.getenv("SENTRY_RELEASE"),
    )
```

**Commands**
```bash
# Observability suite covers DSN guard
uv run python travelmathlite/manage.py test core.tests.test_observability

# Optional enable locally (if SDK installed)
export SENTRY_DSN=https://example.ingest.sentry.io/123
export SENTRY_ENV=local
uv run python travelmathlite/manage.py runserver
```

**Verification**
- Without DSN: no errors, app runs.
- With DSN + SDK: Sentry initializes (logs show no failures); observability test should still pass.

**Troubleshooting**
- Missing SDK: install `sentry-sdk[django]` before enabling.
- If init raises, ensure env vars are set and imports succeed.

---

## Section 4 — Observability tests (Brief 04)

**Context:** [brief-ADR-1.0.13-04-observability-tests.md](../../travelmathlite/briefs/adr-1.0.13/brief-ADR-1.0.13-04-observability-tests.md)  
**Why it matters:** Validates logs, error pages, and Sentry guard behave as designed.

**Steps**
- Tests in `core/tests/test_observability.py` assert:
  - JSON formatter includes request_id/path/method/status_code.
  - Request logging middleware emits records.
  - 404/500 templates render under DEBUG=False.
  - Sentry init runs only when DSN is set.

**Commands**
```bash
uv run python travelmathlite/manage.py test core.tests.test_observability
```

**Verification**
- Expect 6 tests passing; logs may show WARNING/ERROR lines for simulated 404/500 (expected).
- Manual: `curl -I http://localhost:8000/does-not-exist/` (404) and check `X-Request-ID`; induce a controlled 500 to see template.

**Troubleshooting**
- If 500 test fails due to DEBUG, ensure override settings or run with `DEBUG=False`.
- If logging assertions fail, confirm middleware/formatter updates are present.

---

## Section 5 — Logging/error docs and runbook (Brief 05)

**Context:** [brief-ADR-1.0.13-05-logging-docs-and-runbook.md](../../travelmathlite/briefs/adr-1.0.13/brief-ADR-1.0.13-05-logging-docs-and-runbook.md)  
**Why it matters:** NF-003 requires operational guidance and rollback steps.

**Steps**
- Keep runbook at `docs/travelmathlite/ops/logging-and-errors.md` updated with log fields, samples, error-page preview, Sentry enable/disable, and rollback (log level/middleware toggles).

**Commands**
- Docs only; run observability tests for validation: `uv run python travelmathlite/manage.py test core.tests.test_observability`.

**Verification**
- Docs list toggles and sample log output; references tests and manual previews.

**Troubleshooting**
- If settings change (new log fields, toggles), update runbook and tests together.

---

## Verification summary (quick run)

```bash
# Observability suite (logs, 404/500, Sentry guard)
uv run python travelmathlite/manage.py test core.tests.test_observability

# Optional targeted logging/health
uv run python travelmathlite/manage.py test core.tests.test_logging core.tests.test_health
```

Expected: all pass; warnings for simulated 404/500 are expected. Manual checks: tail logs during `runserver` and hit `/does-not-exist/` (404) and a controlled 500 to confirm templates.

---

## References

- [Django documentation](https://docs.djangoproject.com/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Sentry Python SDK](https://docs.sentry.io/platforms/python/guides/django/)
- [HTMX documentation](https://htmx.org/docs/)
- [Understand Django (Matt Layman)](https://www.mattlayman.com/understand-django/)
