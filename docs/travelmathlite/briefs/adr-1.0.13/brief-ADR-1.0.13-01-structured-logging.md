# BRIEF: Build structured logging slice

Goal

- Implement JSON logging with request metadata (request_id, path, status, duration) addressing PRD §4 F-015/F-009 and ADR-1.0.13.

Scope (single PR)

- Files to touch: `travelmathlite/core/logging.py`, `travelmathlite/core/settings/base.py` (LOGGING), `core/middleware` if needed, `docs/ops/logging-and-errors.md`.
- Behavior: Emit JSON log lines with request_id, path, method, status, duration, and correlation-friendly fields. Ensure log format is default in prod; keep DEBUG-friendly console in dev if desired.
- Non-goals: Third-party log collectors, full APM.

Standards

- Commits: conventional style (feat/fix/docs/chore).
- Use `uv run` for Django commands; lint/format with Ruff.
- Django tests: use Django TestCase (no pytest).

Acceptance

- User flow: Requests emit JSON logs including request_id and status; request_id comes from RequestIDMiddleware.
- Tests cover log format and fields (e.g., structured dict or parsed JSON).
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Add JSON logger that includes request_id/path/status/duration and wire into LOGGING config."
- "Write tests asserting log records contain request_id and status for a sample request."
- "Document logging fields and sample output in docs/ops/logging-and-errors.md."
