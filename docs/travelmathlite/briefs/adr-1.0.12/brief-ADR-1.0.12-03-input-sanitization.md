# BRIEF: Build input sanitization slice

Goal

- Ensure user-rendered content is sanitized (bleach/autoescape) addressing PRD §4 F-014 and ADR-1.0.12.

Scope (single PR)

- Files to touch: `travelmathlite/apps/*` templates that render user input (e.g., accounts/profile, future rich text), `travelmathlite/core/settings/base.py` for bleach allowlists if needed, `docs/security.md`.
- Behavior: Sanitize any HTML-bearing fields with bleach; ensure templates rely on Django autoescape by default; document where sanitization is applied and allowlists.
- Non-goals: Building rich-text editors, CSP rollout, rate limiting (separate).

Standards

- Commits: conventional style (feat/fix/docs/chore).
- Use `uv run` for Django commands; lint/format with Ruff.
- Django tests: use Django TestCase (no pytest).

Acceptance

- User flow: Any user-provided HTML rendered in templates is escaped or sanitized; no raw HTML rendering without bleach.
- Tests cover sanitization (e.g., `<script>` stripped/escaped) or template autoescape behavior.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Identify templates rendering user input and ensure autoescape or bleach.clean with allowlists."
- "Add unit tests demonstrating `<script>` is removed/escaped in rendered output."
- "Document sanitization rules and allowlists in docs/security.md."
