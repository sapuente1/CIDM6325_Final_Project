# BRIEF: Build custom error templates slice

Goal

- Create user-friendly 404/500 pages with logging alignment addressing PRD §4 F-015 and ADR-1.0.13.

Scope (single PR)

- Files to touch: `travelmathlite/templates/404.html`, `travelmathlite/templates/500.html`, shared layout if needed, `docs/ops/logging-and-errors.md`.
- Behavior: Custom 404/500 templates extend base layout; surface support links; optionally show request_id when DEBUG=False (friendly message only).
- Non-goals: Custom error views beyond templates, full UX redesign.

Standards

- Commits: conventional style (feat/fix/docs/chore).
- Use `uv run` for Django commands; lint/format with Ruff.
- Django tests: use Django TestCase (no pytest).

Acceptance

- User flow: 404 and 500 render branded templates; response carries security headers per settings.
- Tests assert templates used and include friendly copy; may surface request_id placeholder for correlation.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Add 404.html and 500.html extending base with support link and request_id placeholder."
- "Write tests that trigger 404 and verify template/strings."
- "Document how to preview error pages (DEBUG off) in docs/ops/logging-and-errors.md."
