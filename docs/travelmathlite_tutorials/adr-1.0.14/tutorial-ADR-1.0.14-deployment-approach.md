# Tutorial: ADR-1.0.14 Deployment Approach

**Date:** November 27, 2025  
**ADR Reference:** [ADR-1.0.14 Deployment approach](../../travelmathlite/adr/adr-1.0.14-deployment-approach.md)  
**Briefs:** [adr-1.0.14 briefs](../../travelmathlite/briefs/adr-1.0.14/)  
**PRD trace:** §12 Rollout and release plan (F-012, F-010, F-015)  
**Acceptance hooks:** FR-F-012-1 (prod settings + headers), FR-F-010-1 (collectstatic + hashed assets), FR-F-015-1 (structured logs usable in demos)

---

## Overview

ADR-1.0.14 locks in a demo-friendly deployment: gunicorn as the WSGI server, WhiteNoise for static files, environment-driven prod settings, and a concise runbook with smoke/rollback steps. This tutorial matches the depth of ADR-1.0.10 (caching): each brief becomes a section with concepts, doc excerpts, step-by-step commands, code excerpts, verification, and troubleshooting/rollback guidance.

**Learning Objectives**
- Run TravelMathLite with `gunicorn` + WhiteNoise under `core.settings.prod`.
- Execute `collectstatic` with manifest storage and understand hashed asset outputs.
- Configure required production environment variables and perform a `/health/` smoke test.
- Follow an ordered deploy and rollback checklist with log tailing.
- Use the ops runbook as the single source of truth.

**Prerequisites**
- TravelMathLite repo checked out; `uv` installed.
- Ability to run shell commands and `curl` on the deploy target (local VM or PaaS).
- Basic familiarity with Django settings and environment variables.

**How to use this tutorial**
- Keep `docs/travelmathlite/ops/deploy.md` open; this tutorial expands every step with context and verification.
- Follow sections in order (Brief 01 → 05). Copy/paste commands, then run the verification block before moving on.
- When in doubt, run `uv run python travelmathlite/manage.py check --deploy` to spot missing prod settings.

---

## Section 1 — Gunicorn + WhiteNoise run command (Brief 01)

**Context:** [brief-ADR-1.0.14-01-gunicorn-run-command.md](../../travelmathlite/briefs/adr-1.0.14/brief-ADR-1.0.14-01-gunicorn-run-command.md)  
**Why it matters:** Establishes the production entrypoint for FR-F-012-1; prod settings turn on security middleware and logging from ADR-1.0.13.

### Concepts and doc excerpts
- **Gunicorn:** Django’s deploy docs list gunicorn as a common WSGI choice. Gunicorn docs: “Gunicorn is a pre-fork worker model. The master process manages worker processes and handles web requests.” Good fit for a single VM/PaaS demo.
- **WhiteNoise:** WhiteNoise docs: “serve its own static files… deploy anywhere without relying on nginx.” Works because `whitenoise.middleware.WhiteNoiseMiddleware` is already in `MIDDLEWARE` (see `travelmathlite/core/settings/base.py`).
- **Prod settings:** `DJANGO_SETTINGS_MODULE=core.settings.prod` enforces `DEBUG=False`, required `SECRET_KEY`/`ALLOWED_HOSTS`, and security headers (`SECURE_*`).

### Steps
1) Confirm WhiteNoise is enabled in middleware: `whitenoise.middleware.WhiteNoiseMiddleware` appears near the top of `travelmathlite/core/settings/base.py`.
2) Export production settings selection: `DJANGO_SETTINGS_MODULE=core.settings.prod`.
3) Run gunicorn with a bind that works locally and on PaaS: `0.0.0.0:${PORT:-8000}` and keep access logs visible.

### Commands (copy/paste)
From repo root:

```bash
DJANGO_SETTINGS_MODULE=core.settings.prod \
uv run gunicorn core.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --access-logfile -
```

### Expected output (sample)
```
[INFO] Starting gunicorn 21.x
[INFO] Listening at: http://0.0.0.0:8000
[INFO] Using worker: sync
[INFO] Booting worker with pid: 12345
```

### Verification
1) With gunicorn running, hit health:
   ```bash
   curl -f http://localhost:${PORT:-8000}/health/
   ```
   Expect `{"status": "ok"}` and header `X-Request-ID`.
2) Tail access logs (stdout) and confirm 200 status for `/health/`.

### Troubleshooting / rollback
- Port conflict → change `PORT` or stop the other process.
- 500 or missing headers → verify `DJANGO_SETTINGS_MODULE=core.settings.prod` and required env vars (see Section 3).
- Rollback: stop gunicorn, restore prior env file, rerun with known-good settings.

---

## Section 2 — Collectstatic and static pipeline (Brief 02)

**Context:** [brief-ADR-1.0.14-02-collectstatic-and-static-pipeline.md](../../travelmathlite/briefs/adr-1.0.14/brief-ADR-1.0.14-02-collectstatic-and-static-pipeline.md)  
**Why it matters:** FR-F-010-1 mandates hashed assets. Manifest storage + WhiteNoise give cache-busting filenames without extra infra.

### Concepts and doc excerpts
- **Django collectstatic:** Django docs: “collects static files from each of your applications into a single location that can easily be served in production.”
- **ManifestStaticFilesStorage:** Django docs: “If the file changes, its name will change, so you don’t need to change your templates to invalidate the cache.”
- **WhiteNoise + manifest:** WhiteNoise serves the hashed files directly when debug is off; no nginx/CDN needed for demos.

### Steps
1) Check paths: `STATIC_ROOT` defaults to `travelmathlite/staticfiles` (`travelmathlite/core/settings/base.py`).
2) Optional cleanup: remove stale artifacts before collecting.
3) Collect with prod settings so manifest hashing is on.
4) Spot-check hashed outputs and headers.

### Commands
```bash
# (optional) clear old staticfiles
rm -rf travelmathlite/staticfiles

# collect with manifest storage (prod settings)
DJANGO_SETTINGS_MODULE=core.settings.prod \
uv run python travelmathlite/manage.py collectstatic --noinput --clear
```

### Expected output (sample)
```
Copying '/.../static/admin/css/base.css'
Post-processed 'admin/css/base.css' as 'admin/css/base.45f0c1e2cc5b.css'
```

### Verification
1) List a few files to confirm hashes:
   ```bash
   ls travelmathlite/staticfiles | head
   ```
2) When the app is running, curl a known asset:
   ```bash
   curl -I http://localhost:${PORT:-8000}/static/admin/css/base.css
   ```
   Expect `200 OK` with `Cache-Control` and `ETag` from WhiteNoise.
3) Load a page in the browser; static assets should render without 404s.

### Troubleshooting / rollback
- 404 on static → rerun collectstatic; ensure `STATIC_ROOT` is writable.
- Missing hashes → ensure `DEBUG=False` or `USE_MANIFEST_STATIC=1`.
- Corrupted static → delete `staticfiles` and rerun collectstatic from the last good commit.

---

## Section 3 — Prod env vars and health smoke (Brief 03)

**Context:** [brief-ADR-1.0.14-03-prod-env-and-health-smoke.md](../../travelmathlite/briefs/adr-1.0.14/brief-ADR-1.0.14-03-prod-env-and-health-smoke.md)  
**Why it matters:** Prod settings require certain envs (FR-F-012-1) and observability (FR-F-015-1); the health check confirms the app is up with correct headers.

### Core env vars (what/why)
- `SECRET_KEY` (required) — prod raises if missing (`travelmathlite/core/settings/prod.py`).
- `ALLOWED_HOSTS` (required) — prevents host header abuse.
- `PORT` — bind target for gunicorn/PaaS.
- `DATABASE_URL` — override sqlite when using a managed DB.
- Optional security: `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`.
- Logging: `LOG_LEVEL`, `REQUEST_LOG_LEVEL`.
- Sentry (optional): `SENTRY_DSN`, `SENTRY_ENV`, `SENTRY_RELEASE`.

### Steps
1) Create a small env file for deploys.
2) Source the env and run Django’s deploy checks.
3) Start gunicorn (Section 1) and run the smoke test.

### Commands
```bash
# sample env file — adjust secrets before use
cat > /tmp/travelmathlite.deploy.env <<'EOF'
SECRET_KEY=change-me
ALLOWED_HOSTS=localhost,127.0.0.1
PORT=8000
DATABASE_URL=sqlite:///travelmathlite/db.sqlite3
DJANGO_SETTINGS_MODULE=core.settings.prod
REQUEST_LOG_LEVEL=INFO
EOF

set -a && source /tmp/travelmathlite.deploy.env && set +a

# sanity check prod settings
uv run python travelmathlite/manage.py check --deploy
```

Smoke test (after gunicorn is running):
```bash
curl -f http://localhost:${PORT}/health/
```

### Expected output
```json
{"status": "ok"}
```
Headers should include `X-Request-ID` (from ADR-1.0.13 middleware).

### Verification
- `check --deploy` exits 0 (warnings reveal missing security headers or hosts).
- `/health/` returns 200 with request ID; logs show path, method, status_code.

### Troubleshooting / rollback
- 400/500 on health → recheck `ALLOWED_HOSTS`, DB connectivity, and `SECRET_KEY`.
- Missing `X-Request-ID` → ensure `core.middleware.RequestIDMiddleware` and `RequestLoggingMiddleware` are in `MIDDLEWARE` (base settings).
- Rollback: stop gunicorn, restore previous env file, restart, re-run smoke.

---

## Section 4 — Deploy checklist and rollback (Brief 04)

**Context:** [brief-ADR-1.0.14-04-deploy-checklist-and-rollback.md](../../travelmathlite/briefs/adr-1.0.14/brief-ADR-1.0.14-04-deploy-checklist-and-rollback.md)  
**Why it matters:** Keeps deployments consistent and gives an immediate rollback path if smoke fails.

### Deploy checklist (ordered)
1) Env prep: set `SECRET_KEY`, `ALLOWED_HOSTS`, `PORT`, `DATABASE_URL` (or sqlite), optional `LOG_LEVEL`/`REQUEST_LOG_LEVEL`, optional `SENTRY_*`.
2) Static prep: `DJANGO_SETTINGS_MODULE=core.settings.prod uv run python travelmathlite/manage.py collectstatic --noinput --clear`.
3) Start app: `DJANGO_SETTINGS_MODULE=core.settings.prod uv run gunicorn core.wsgi:application --bind 0.0.0.0:${PORT:-8000} --access-logfile -`.
4) Smoke: `curl -f http://localhost:${PORT:-8000}/health/` → expect 200 + `{"status": "ok"}` + `X-Request-ID`.
5) Tail logs for errors (swap in your process/log path):
   ```bash
   tail -f /tmp/logs.json | jq 'select(.level=="ERROR")'
   ```

### Rollback checklist
- Stop gunicorn (kill process or scale-to-zero on PaaS).
- Revert env or code to last known-good (restore previous `.env` or release).
- If static is broken, restore the previous `staticfiles` directory or rerun collectstatic from last good commit.
- Restart with the known-good env and re-run the health smoke test.

### Verification
- All deploy steps complete without errors.
- Health and static checks pass post-deploy and post-rollback rehearsal.
- Logs are quiet at `REQUEST_LOG_LEVEL=INFO` (or lower if throttled).

### Troubleshooting
- Smoke fails but app running → inspect logs for DB/auth errors; ensure `ALLOWED_HOSTS` covers your host.
- Static 404s after deploy → rerun collectstatic; confirm WhiteNoise is enabled and `STATIC_ROOT` is readable.

---

## Section 5 — Ops docs and runbook (Brief 05)

**Context:** [brief-ADR-1.0.14-05-ops-docs-and-runbook.md](../../travelmathlite/briefs/adr-1.0.14/brief-ADR-1.0.14-05-ops-docs-and-runbook.md)  
**Why it matters:** Centralizes commands and links so operators do not need to chase details across ADRs or settings files.

### Runbook highlights
- Source of truth: `docs/travelmathlite/ops/deploy.md` bundles run command, env checklist, collectstatic, smoke, log tail, and rollback notes.
- Related docs: logging/health (ADR-1.0.13) and security headers (`docs/security.md`) for quick checks on `SECURE_*` flags.
- Commands use `uv run` for parity between local validation and deploy.

### How to apply
1) Keep `docs/travelmathlite/ops/deploy.md` open while executing this tutorial; confirm commands match.
2) Link the runbook from `docs/travelmathlite/README.md` (per ADR plan) for discoverability.
3) Capture evidence post-deploy: console transcript + screenshot of the running app to satisfy ADR attestation.

### Verification
- A new operator can follow the runbook plus this tutorial to achieve a healthy deploy.
- Links resolve (deploy, security, logging/health).
- Smoke/log steps in the runbook match the commands you rehearsed.

### Troubleshooting / keep-in-sync
- If env requirements or commands change, update both this tutorial and `deploy.md` together.
- Maintain a short “known issues” block in the runbook for platform quirks (ports, file permissions).

---

## Summary and next steps

- You now have a demo-ready deployment path: gunicorn + WhiteNoise, manifest static assets, prod envs, `/health/` smoke, and rollback drills.
- Next steps:
  1) Rehearse the deploy on a VM/PaaS using these commands.
  2) Capture evidence (transcript + screenshot) for ADR attestation.
  3) If scaling beyond demos, pair with ADR-1.0.13 observability toggles and front gunicorn with a reverse proxy/CDN.

---

## References

- Django deployment checklist: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/
- Django static files and collectstatic: https://docs.djangoproject.com/en/stable/howto/static-files/deployment/
- Django ManifestStaticFilesStorage: https://docs.djangoproject.com/en/stable/ref/contrib/staticfiles/#manifeststaticfilesstorage
- Gunicorn docs: https://docs.gunicorn.org/en/stable/run.html
- WhiteNoise docs: https://whitenoise.readthedocs.io/en/stable/
