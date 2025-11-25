# BRIEF: Build collectstatic and static pipeline slice

Goal

- Ensure collectstatic/hashed assets are documented and runnable for prod, addressing PRD §12 and ADR-1.0.14.

Scope (single PR)

- Files to touch: `docs/ops/deploy.md`, optional `Procfile`/script snippet, `core/settings/prod.py` notes for STATIC_ROOT/USE_MANIFEST_STATIC if needed.
- Behavior: Provide commands to run `uv run python travelmathlite/manage.py collectstatic --noinput`, note hashed filenames with ManifestStaticFilesStorage (already wired), and location of `STATIC_ROOT`.
- Non-goals: CDN/NGINX configuration, asset versioning beyond Django manifest.

Standards

- Commits: conventional style (docs/chore).
- Keep instructions concise and copy-pasteable.

Acceptance

- User flow: Operator can run collectstatic and serve hashed assets via WhiteNoise; docs state where files land and how to clean them.
- Tests not required; manual command suffices.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Add collectstatic section to deploy docs with ManifestStaticFilesStorage and STATIC_ROOT notes."
- "Document clean-up steps (removing old staticfiles) if needed."
