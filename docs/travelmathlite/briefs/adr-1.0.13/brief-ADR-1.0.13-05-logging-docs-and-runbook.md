# BRIEF: Build logging/error docs and runbook slice

Goal

- Document logging fields, error page behavior, Sentry toggle steps, and verification commands addressing PRD §7 NF-003 and ADR-1.0.13.

Scope (single PR)

- Files to touch: `docs/ops/logging-and-errors.md` (new or expanded), `docs/travelmathlite/README.md` (link), `docs/travelmathlite/testing.md` (commands).
- Behavior: Clear guidance for enabling/disabling Sentry, interpreting JSON logs (fields), previewing 404/500, and running observability tests. Include rollback notes.
- Non-goals: Rewriting PRD/ADR; deep APM setup.

Standards

- Commits: conventional style (docs/chore).
- Use `uv run` for Django commands; lint/format with Ruff.
- Django tests: use Django TestCase (no pytest).

Acceptance

- User flow: Developer can follow docs to enable Sentry, view structured logs, and preview error pages with DEBUG off.
- Test commands listed for observability suites.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Write logging-and-errors.md covering JSON fields, request_id correlation, Sentry enable/disable, and 404/500 preview steps."
- "Add links from README/testing docs to the logging-and-errors guide."
- "Include rollback note for reverting to console formatter."
