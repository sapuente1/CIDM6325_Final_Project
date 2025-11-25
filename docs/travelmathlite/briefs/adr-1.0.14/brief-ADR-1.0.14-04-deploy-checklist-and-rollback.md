# BRIEF: Build deploy checklist and rollback slice

Goal

- Provide a concise deploy/rollback checklist for the gunicorn + WhiteNoise approach, addressing PRD §12 and ADR-1.0.14.

Scope (single PR)

- Files to touch: `docs/ops/deploy.md`, possibly README quickstart link.
- Behavior: Checklist covering env prep, collectstatic, run command, smoke test, and rollback (stop process, revert env, clear static if needed).
- Non-goals: Detailed CI/CD pipeline, blue/green deploys.

Standards

- Commits: conventional style (docs/chore).
- Keep steps concise and ordered; include rollback triggers.

Acceptance

- User flow: Operator can follow checklist to deploy and roll back; smoke passes.
- Checklist includes log locations and how to quiet logs (`REQUEST_LOG_LEVEL`).
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Add deploy/rollback checklist to docs/ops/deploy.md (env, collectstatic, run, smoke, rollback)."
- "Include log-tail tips and where to find static files."
