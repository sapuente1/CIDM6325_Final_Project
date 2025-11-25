# Tutorial: ADR-1.0.13 Observability and Error Handling

**Date:** November 25, 2025  
**ADR Reference:** [ADR-1.0.13 Observability and Error Handling](../../travelmathlite/adr/adr-1.0.13-observability-and-error-handling.md)  
**Briefs:** [adr-1.0.13 briefs](../../travelmathlite/briefs/adr-1.0.13/)  
**PRD trace:** §4 F-015/F-009, §11 (metrics)  
**Acceptance hooks:** FR-F-015-1 (structured logs, error pages), FR-F-009-1 (request_id), NF-003 (operational docs)

---

## Overview

ADR-1.0.13 establishes observability primitives: structured JSON logging with correlation fields, branded error pages (404/500), an optional Sentry toggle, and an observability test suite plus runbook. This tutorial mirrors the depth of ADR-1.0.10 (caching) with per-brief walkthroughs, sample outputs, manual verifications, and troubleshooting/rollback guidance.

**Learning Objectives**
- Emit JSON logs with request_id, path, method, status_code, and duration via middleware + formatter.
- Render and preview custom 404/500 pages in DEBUG-off mode with request_id hints.
- Enable Sentry safely when `SENTRY_DSN` is present; keep disabled by default and guard when SDK is absent.
- Run observability tests (logging, error pages, Sentry guard) and interpret their outputs.
- Operate toggles and rollback paths (log levels, middleware ordering, Sentry envs).

**Prerequisites**
- Working TravelMathLite dev environment with `uv`.
- Ability to run Django tests and `curl`.
- No additional datasets required.

---

## How to use this tutorial

- Cite ADR and briefs explicitly in each section.  
- For each brief: context → why it matters → concepts → steps → code excerpt (path) → commands → verification (tests/URLs/expected outputs) → troubleshooting → rollback notes.  
- Reference docs: Django, Python stdlib (`unittest.mock`), Sentry SDK.  
- Keep parity with the 1.0.10 caching tutorial in depth and structure.

---

## Section 1 — Structured logging (Brief 01)

**Context:** [brief-ADR-1.0.13-01-structured-logging.md](../../travelmathlite/briefs/adr-1.0.13/brief-ADR-1.0.13-01-structured-logging.md)  
**Why it matters:** FR-F-015-1 requires logs that can be correlated by request_id; PRD §11 requires measurable signals (path, status, duration).

### Concepts
- Request correlation: request_id propagated from middleware into logs.
- Rich context: path, method, status_code, duration_ms captured per request.
- Logger isolation: dedicated `request` logger to avoid chatty `django.request`.

### Steps
1) **Middleware order**: ensure `RequestIDMiddleware` precedes `RequestLoggingMiddleware`.  
2) **Formatter**: extend JSON formatter with path/method/status_code.  
3) **Logger**: add `request` logger in settings with env-controlled level.

### Key code
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
- Logger (`travelmathlite/core/settings/base.py`):
```python
"request": {
    "handlers": ["console"],
    "level": env("REQUEST_LOG_LEVEL", default="INFO"),
    "propagate": False,
},
```

### Commands
```bash
# Observability suite (covers logging)
uv run python travelmathlite/manage.py test core.tests.test_observability

# Tail logs during dev
uv run python travelmathlite/manage.py runserver 2>&1 | tee /tmp/logs.json
tail -f /tmp/logs.json | jq 'select(.path=="/" and .status_code==200)'
```

### Verification
- Expect JSON entries like:
```json
{"timestamp":"...","level":"INFO","module":"middleware","message":"request completed","request_id":"abcd-123","duration_ms":18.3,"path":"/accounts/login/","method":"POST","status_code":429}
```
- Manual: hit `/` or `/accounts/login/`; logs should show correct status (200/302/429).

### Troubleshooting / Rollback
- Missing fields: confirm middleware order and that `RequestLoggingMiddleware` is in `MIDDLEWARE`.
- Too noisy: set `REQUEST_LOG_LEVEL=WARNING` or temporarily remove middleware (revert afterward).

---

## Section 2 — Custom error templates (Brief 02)

**Context:** [brief-ADR-1.0.13-02-error-templates.md](../../travelmathlite/briefs/adr-1.0.13/brief-ADR-1.0.13-02-error-templates.md)  
**Why it matters:** FR-F-015-1 requires user-friendly errors; correlation via request_id.

### Concepts
- Django uses `404.html` and `500.html` at project root (`travelmathlite/templates/`).
- DEBUG must be False to render 500 template.

### Steps
1) Create `404.html` and `500.html` extending `base.html` with support copy and request_id hint.  
2) Keep tone concise; link back to home.

### Key code
- `travelmathlite/templates/404.html`:
```html
<h1>Page not found</h1>
<p>The page you’re looking for doesn’t exist or may have moved.</p>
<p class="text-muted">If you need help, include the request ID from the response headers.</p>
```
- `travelmathlite/templates/500.html`:
```html
<h1>Something went wrong</h1>
<p>We hit an unexpected error. Please try again in a moment.</p>
<p class="text-muted">Include the request ID from the response headers if you contact support.</p>
```

### Commands
```bash
# Preview with DEBUG off
DJANGO_SETTINGS_MODULE=core.settings.prod SECRET_KEY=dev ALLOWED_HOSTS=localhost \
uv run python travelmathlite/manage.py runserver
```

### Verification
- `http://localhost:8000/does-not-exist/` → custom 404.
- Introduce a controlled exception in a view (remove after) → 500 template shows.
- Automated: `core.tests.test_observability` asserts 404/500 templates.

### Troubleshooting / Rollback
- Default Django error page showing? Ensure templates in `travelmathlite/templates/` and DEBUG=False for 500 preview.
- If a change breaks layout, revert to previous template revision.

---

## Section 3 — Optional Sentry toggle (Brief 03)

**Context:** [brief-ADR-1.0.13-03-sentry-toggle.md](../../travelmathlite/briefs/adr-1.0.13/brief-ADR-1.0.13-03-sentry-toggle.md)  
**Why it matters:** Optional error monitoring without forcing third-party deps.

### Concepts
- Guarded initialization: no-op when `SENTRY_DSN` missing or SDK absent.
- Integrations: DjangoIntegration; traces_sample_rate default 0.0 unless set.

### Steps
1) Implement `init_sentry` in `core/sentry.py` with guards.  
2) Call `init_sentry()` from `core/wsgi.py`.

### Key code
- `travelmathlite/core/sentry.py`:
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

### Commands
```bash
# Observability suite covers DSN guard
uv run python travelmathlite/manage.py test core.tests.test_observability

# Optional enable locally (requires sentry-sdk installed)
export SENTRY_DSN=https://example.ingest.sentry.io/123
export SENTRY_ENV=local
uv run python travelmathlite/manage.py runserver
```

### Verification
- Without DSN: app runs, no init errors.
- With DSN + SDK: Sentry initializes (no startup errors); observability tests still pass.

### Troubleshooting / Rollback
- Missing SDK: install `sentry-sdk[django]` or remove DSN to skip init.
- To disable: unset `SENTRY_DSN` (no code change).

---

## Section 4 — Observability tests (Brief 04)

**Context:** [brief-ADR-1.0.13-04-observability-tests.md](../../travelmathlite/briefs/adr-1.0.13/brief-ADR-1.0.13-04-observability-tests.md)  
**Why it matters:** Validates logs, error pages, and Sentry guard as a package.

### Concepts
- Tests simulate requests to capture logs and error templates.
- Sentry guard tested via patched env/imports.

### Steps
- `core/tests/test_observability.py` assertions:
  - Formatter includes request_id/path/method/status_code/duration_ms.
  - Middleware emits log records.
  - 404/500 templates render under DEBUG=False.
  - Sentry init runs only when DSN is present.

### Key code
- Formatter test:
```python
payload = json.loads(formatter.format(record))
self.assertEqual(payload["request_id"], "req-123")
self.assertEqual(payload["path"], "/health/")
self.assertEqual(payload["status_code"], 200)
```
- Error templates:
```python
resp = self.client.get("/does-not-exist/")
self.assertTemplateUsed(resp, "404.html")
```

### Commands
```bash
uv run python travelmathlite/manage.py test core.tests.test_observability
```

### Verification
- Expect 6 tests passing; console shows WARNING/ERROR for simulated 404/500 (expected).
- Manual: `curl -I http://localhost:8000/does-not-exist/` → 404 + `X-Request-ID`; induce a temporary 500 to view template.

### Troubleshooting / Rollback

- If 500 test fails, ensure DEBUG=False (tests use override_settings).  
- Logging assertions fail → verify middleware and formatter fields.  
- To reduce noise, raise `REQUEST_LOG_LEVEL` temporarily.

---

## Section 5 — Logging/error docs and runbook (Brief 05)

**Context:** [brief-ADR-1.0.13-05-logging-docs-and-runbook.md](../../travelmathlite/briefs/adr-1.0.13/brief-ADR-1.0.13-05-logging-docs-and-runbook.md)  
**Why it matters:** NF-003 requires operational guidance and rollback steps.

### Steps
- Maintain `docs/travelmathlite/ops/logging-and-errors.md` with:
  - Log field definitions, sample entry, and tail commands.
  - Error-page preview steps (DEBUG off).
  - Sentry enable/disable instructions and envs.
  - Rollback (quiet request logger, remove middleware, unset SENTRY_DSN).

### Commands
- Docs only. Validation via observability suite:
```bash
uv run python travelmathlite/manage.py test core.tests.test_observability
```

### Verification
- Runbook lists toggles and sample log. Links to tests and manual previews.

### Troubleshooting / Rollback
- If settings change (new fields/toggles), update runbook + tests in sync.

---

## Manual smoke walkthrough (mirrors tests)

1) Start server (dev): `uv run python travelmathlite/manage.py runserver 2>&1 | tee /tmp/logs.json`  
2) Hit `/` and `/accounts/login/`; watch logs for JSON entries with path/method/status.  
3) Visit `/does-not-exist/` → custom 404.  
4) (Optional) Introduce a temporary `raise Exception("boom")` in a safe view, hit the page with DEBUG=False to see 500 template; remove after.  
5) If enabling Sentry, export DSN/env and restart; ensure no startup errors.

---

## Verification summary (quick run)

```bash
# Observability suite (logging, 404/500 templates, Sentry guard)
uv run python travelmathlite/manage.py test core.tests.test_observability

# Targeted logging/health (optional)
uv run python travelmathlite/manage.py test core.tests.test_logging core.tests.test_health
```

Expected: all pass; simulated 404/500 warnings in output are normal. Manual checks: tail logs during `runserver`, load `/does-not-exist/`, and (optionally) a controlled 500 to view templates.

---

## References

- [Django documentation](https://docs.djangoproject.com/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Sentry Python SDK](https://docs.sentry.io/platforms/python/guides/django/)
- [HTMX documentation](https://htmx.org/docs/)
- [Understand Django (Matt Layman)](https://www.mattlayman.com/understand-django/)
