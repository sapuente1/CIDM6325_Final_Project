# BRIEF: Build auth rate limiting slice

Goal

- Apply `django-ratelimit` to auth-sensitive endpoints (login, signup) addressing PRD §4 F-014 and ADR-1.0.12.

Scope (single PR)

- Files to touch: `travelmathlite/apps/accounts/urls.py`, `travelmathlite/apps/accounts/views.py` (or decorators), `travelmathlite/core/settings/base.py`, `travelmathlite/core/settings/prod.py`, `requirements.txt`/`pyproject.toml` (if dependency wiring needed), `docs/security.md`.
- Behavior: Rate-limit login and signup views with sensible defaults (e.g., 5/min per IP or username), return HTTP 429 on abuse, allow toggling via settings/env.
- Non-goals: Global throttling for all views, captcha integration (separate brief), custom middleware.

Standards

- Commits: conventional style (feat/fix/docs/chore).
- Use `uv run` for Django commands; lint/format with Ruff.
- Django tests: use Django TestCase (no pytest).

Acceptance

- User flow: Repeated login attempts over the threshold receive 429 with clear message; normal login works.
- Settings expose rate-limit keys (enabled flag, limits) and are documented.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Wire django-ratelimit to LoginView/SignupView with per-IP and/or per-username keys and 5/min limit."
- "Add settings/env toggles for rate limiting defaults; document in docs/security.md."
- "Create tests asserting 200 for normal login, 429 after exceeding limit."
