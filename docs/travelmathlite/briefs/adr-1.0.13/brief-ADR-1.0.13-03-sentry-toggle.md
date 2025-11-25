# BRIEF: Build optional Sentry toggle slice

Goal

- Add optional Sentry integration hooks addressing PRD §4 F-015 and ADR-1.0.13.

Scope (single PR)

- Files to touch: `travelmathlite/core/settings/base.py` (env toggles), `travelmathlite/core/wsgi.py` or `core/__init__.py` for init block, `requirements.txt`/`pyproject.toml` if SDK needed, `docs/ops/logging-and-errors.md`.
- Behavior: Initialize Sentry only when `SENTRY_DSN` is set; include Django integration and sample release/env tags; keep disabled by default.
- Non-goals: Mandating Sentry in dev/test; adding performance traces/APM.

Standards

- Commits: conventional style (feat/fix/docs/chore).
- Use `uv run` for Django commands; lint/format with Ruff.
- Django tests: use Django TestCase (no pytest).

Acceptance

- User flow: App runs unchanged without `SENTRY_DSN`; with DSN, Sentry init occurs with DjangoIntegration and release/env tags.
- Tests: settings guard ensures import/init not called when DSN missing; import safe if SDK absent unless enabled.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Add SENTRY_DSN and SENTRY_ENV/RELEASE toggles; guard initialization in core/wsgi.py."
- "Write test that patches SENTRY_DSN and asserts init called; another that no-ops when missing."
- "Document enable/disable steps in docs/ops/logging-and-errors.md."
