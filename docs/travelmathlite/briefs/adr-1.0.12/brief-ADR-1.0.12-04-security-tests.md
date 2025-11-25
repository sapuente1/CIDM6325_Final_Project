# BRIEF: Build security tests slice

Goal

- Add tests verifying security headers, CSRF enforcement, and rate limiting addressing PRD §4 F-012/F-014 and ADR-1.0.12.

Scope (single PR)

- Files to touch: `travelmathlite/core/tests/test_security.py` (new), `travelmathlite/apps/accounts/tests/test_rate_limit.py` (or similar), `travelmathlite/core/settings/prod.py` (test hooks/env toggles), `docs/security.md` (test commands).
- Behavior: Tests assert security headers in prod settings, CSRF token presence on forms, rate-limit 429 behavior for auth endpoints when enabled.
- Non-goals: Pen tests, fuzzing, CSP validation.

Standards

- Commits: conventional style (test/docs/chore).
- Use `uv run` for Django commands; lint/format with Ruff.
- Django tests: use Django TestCase (no pytest).

Acceptance

- User flow: `uv run python manage.py test core.tests.test_security apps.accounts.tests.test_rate_limit` passes.
- Header tests cover HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy in prod settings.
- Rate-limit tests demonstrate 429 after exceeding threshold; CSRF tests verify token presence/validation.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Add prod-settings security header tests in core/tests/test_security.py using override_settings."
- "Add auth rate-limit tests that simulate multiple POSTs and assert 429."
- "Document how to run the new security test modules in docs/security.md."
