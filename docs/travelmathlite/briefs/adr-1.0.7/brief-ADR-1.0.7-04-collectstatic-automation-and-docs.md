# BRIEF: Automate collectstatic and operator docs

Goal

- Document and script the steps required to run `collectstatic` across local, CI, and deployment workflows so hashed assets are always present before WhiteNoise serves them (PRD §7 NF-004).

Scope (single PR)

- Files to touch: `scripts/` (add `uv run` helper for `collectstatic`), `docs/travelmathlite/ops/static-and-media.md`, `README.md` deployment section, checklist seeds referencing ADR-1.0.7.
- Tasks: create a reusable shell script or `make`-style task (e.g., `scripts/run_collectstatic.sh`) that activates virtualenv via `uv run`; ensure script exports `DJANGO_SETTINGS_MODULE=core.settings` and fails loudly; update documentation with a "Before deploy" checklist covering `STATIC_ROOT` cleanup, asset hashing verification, and artifact attachment expectations.
- Non-goals: Container builds, CDN upload automation, Windows batch parity (optional but nice to call out).

Standards

- Commits: `chore/docs` style; include Issue refs.
- Scripts should use `bash` + `set -euo pipefail`, rely on `uv run` (no `python` directly); keep instructions reproducible.
- Tests: include at least one CI-friendly smoke test invoking the script with `--dry-run` or `COLLECTSTATIC_SKIP_UPLOAD=1` flag to ensure it stays green.

Acceptance

- A single documented command (e.g., `bash scripts/collectstatic.sh`) runs `uv run python manage.py collectstatic --noinput` and stores output under `travelmathlite/staticfiles/`.
- Docs include troubleshooting tips (permissions, missing manifest) and tie back to ADR acceptance evidence requirements.
- CHECKLIST seeds updated with a "Manifest storage enabled / WhiteNoise configured" verification box referencing this script.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Create `scripts/collectstatic.sh` that calls `uv run python manage.py collectstatic --noinput` and accepts `--dry-run` / `--clear` flags, ensuring the script exits on errors."
- "Update `docs/travelmathlite/ops/static-and-media.md` with a section describing how to run the new script locally and in CI, including environment variables (`USE_MANIFEST_STATIC=1`)."
- "Add a README deployment snippet showing the collectstatic command in the release checklist."

---
ADR: adr-1.0.7-static-media-and-asset-pipeline.md
PRD: §7 NF-004
Requirements: NF-004
