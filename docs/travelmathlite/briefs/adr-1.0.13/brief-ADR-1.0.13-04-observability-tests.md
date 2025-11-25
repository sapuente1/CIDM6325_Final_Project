# BRIEF: Build observability tests slice

Goal

- Add tests for logging fields, error pages, and Sentry toggle hooks addressing PRD §4 F-015/F-009 and ADR-1.0.13.

Scope (single PR)

- Files to touch: `travelmathlite/core/tests/test_logging.py` (or new `test_observability.py`), `travelmathlite/core/tests/test_error_pages.py`, `docs/ops/logging-and-errors.md` (test commands).
- Behavior: Tests assert JSON log fields include request_id/status/path; 404/500 templates render; Sentry init called when DSN set and skipped otherwise.
- Non-goals: Load/perf testing, integration with external Sentry.

Standards

- Commits: conventional style (test/docs/chore).
- Use `uv run` for Django commands; lint/format with Ruff.
- Django tests: use Django TestCase (no pytest).

Acceptance

- User flow: `uv run python manage.py test core.tests.test_observability` passes (or equivalent split files).
- Tests cover log field presence, 404/500 template usage, and Sentry init guard.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Add test that captures log output and asserts request_id/status/path in JSON."
- "Add tests that trigger 404/500 and confirm custom templates."
- "Add test that patches SENTRY_DSN and asserts init called once, and no-op when missing."
