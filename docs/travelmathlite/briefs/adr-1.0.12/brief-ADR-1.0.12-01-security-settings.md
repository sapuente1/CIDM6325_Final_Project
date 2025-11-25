# BRIEF: Build security settings hardening slice

Goal

- Harden security settings (headers, secure cookies, CSRF posture) addressing PRD §4 F-012/F-014 and ADR-1.0.12.

Scope (single PR)

- Files to touch: `travelmathlite/core/settings/base.py`, `travelmathlite/core/settings/prod.py`, `docs/security.md`.
- Behavior: Ensure `SecurityMiddleware` is active, secure cookie flags are set in prod, HSTS/X-Content-Type-Options/X-Frame-Options configured, CSRF enabled with secure cookie in prod.
- Non-goals: Rate limiting (separate brief), view-level changes, CSP deep tuning beyond safe defaults.

Standards

- Commits: conventional style (feat/fix/docs/chore).
- Use `uv run` for Django commands; lint/format with Ruff.
- Django tests: use Django TestCase (no pytest).

Acceptance

- User flow: Requests in prod emit security headers (HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy). CSRF cookie is secure/HttpOnly in prod.
- Settings flags documented with env toggles and safe defaults.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Add security header settings and secure cookie flags to base/prod settings; keep DEBUG-safe defaults."
- "Document security settings and env toggles in docs/security.md."
- "Explain changes and propose commit messages."
