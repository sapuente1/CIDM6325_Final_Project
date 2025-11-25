# BRIEF: Build gunicorn + WhiteNoise run command slice

Goal

- Document and wire a production run command (gunicorn + WhiteNoise) using `core.settings.prod`, addressing PRD §12 and ADR-1.0.14.

Scope (single PR)

- Files to touch: `Procfile` or deploy docs snippet, `docs/ops/deploy.md`, `travelmathlite/core/settings/prod.py` (env reminders if needed).
- Behavior: Show a working run command (e.g., `gunicorn core.wsgi:application --bind 0.0.0.0:${PORT:-8000}`) relying on WhiteNoise for static. Ensure `DJANGO_SETTINGS_MODULE=core.settings.prod`.
- Non-goals: Container orchestration, NGINX config.

Standards

- Commits: conventional style (docs/chore).
- Use `uv run` for local validation if needed.
- Keep instructions minimal and copy-pasteable.

Acceptance

- User flow: A deploy operator can run the command with env vars set and get a 200 on `/health/`.
- Docs include the exact command and required env vars.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Add gunicorn run command (prod settings) to docs/ops/deploy.md using WhiteNoise."
- "Remind deployers to set DJANGO_SETTINGS_MODULE=core.settings.prod and PORT."
