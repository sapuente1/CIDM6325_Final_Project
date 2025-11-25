# BRIEF: Build security documentation and toggles slice

Goal

- Document security controls, env toggles, and operational guidance addressing PRD §7 NF-003 and ADR-1.0.12.

Scope (single PR)

- Files to touch: `docs/security.md`, `docs/travelmathlite/testing.md` (links), `docs/travelmathlite/briefs/gh-commands-adr-1.0.0.md` (if command snippets need an ADR-1.0.12 section), project README link.
- Behavior: Provide clear instructions for enabling/disabling rate limiting, secure cookies, HSTS, and sanitization; include GH CLI snippet to open issues for ADR-1.0.12 briefs mirroring existing commands file.
- Non-goals: Rewriting PRD/ADR text; implementing controls (handled in other briefs).

Standards

- Commits: conventional style (docs/chore).
- No secrets; env via settings.
- Keep docs concise and actionable; link to ADR-1.0.12 and relevant briefs.

Acceptance

- User flow: Developers can follow docs to enable/verify security controls and run security tests.
- GH CLI snippet for ADR-1.0.12 briefs lives with existing commands doc (or a new section) and references each brief file.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Update docs/security.md with toggles for rate limiting, security headers, sanitization; include test commands."
- "Add GH CLI issue-creation snippets for ADR-1.0.12 briefs alongside existing commands file."
- "Add links from README/testing docs to the security guide."
