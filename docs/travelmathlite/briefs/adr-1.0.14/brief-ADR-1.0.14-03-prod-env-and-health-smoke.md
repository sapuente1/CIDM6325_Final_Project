# BRIEF: Build prod env + health smoke slice

Goal

- Define required prod env vars and a health-check smoke test for deployments, addressing PRD §12 and ADR-1.0.14.

Scope (single PR)

- Files to touch: `docs/ops/deploy.md`, possibly `.env.example` or README snippet.
- Behavior: List required env vars (SECRET_KEY, ALLOWED_HOSTS, PORT, DATABASE_URL, SECURE_* if overriding), and a smoke command (`curl -f http://localhost:${PORT}/health/` or staging URL).
- Non-goals: Full monitoring stack, uptime checks.

Standards

- Commits: conventional style (docs/chore).
- Keep commands copy-pasteable; use `uv run` where appropriate.

Acceptance

- User flow: Operator can set envs, start app, and confirm `/health/` returns 200.
- Docs include a minimal env checklist and smoke command.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Add env var checklist and health curl command to deploy docs."
- "Note DJANGO_SETTINGS_MODULE=core.settings.prod and REQUEST_LOG_LEVEL override if needed."
