# BRIEF: Build ops docs and runbook slice

Goal

- Document deployment steps, env toggles, and operational tips for ADR-1.0.14 in a single runbook.

Scope (single PR)

- Files to touch: `docs/ops/deploy.md`, `docs/travelmathlite/README.md` (link), `docs/travelmathlite/testing.md` (test commands if needed).
- Behavior: Provide a cohesive runbook: env checklist, collectstatic, run command, smoke test, log tail, rollback notes, and links to observability/security docs.
- Non-goals: Cloud provider-specific guides, CI pipeline details.

Standards

- Commits: conventional style (docs/chore).
- Keep instructions copy-pasteable; link to ADR/briefs.

Acceptance

- User flow: A reader can follow runbook to deploy and verify the app with prod settings.
- Runbook links to observability and security guides for headers/logs checks.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Write a deploy runbook (docs/ops/deploy.md) covering envs, collectstatic, gunicorn run, smoke test, rollback, and log tailing."
- "Add links from README to the deploy runbook."
