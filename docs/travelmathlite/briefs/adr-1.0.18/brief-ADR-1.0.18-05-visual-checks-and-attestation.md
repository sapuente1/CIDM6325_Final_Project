# BRIEF: Visual checks and attestation for ADR-1.0.18

Goal

- Capture screenshots and verification notes proving templates follow the Bootstrap catalogue (base/search/app index) with no custom CSS, satisfying ADR-1.0.18 acceptance.

Scope (single PR)

- Files to touch: `docs/travelmathlite/ui/` screenshots (replace placeholders), attestation notes in a short doc or added to `docs/ux/templates-bootstrap-catalogue.md` or `docs/ux/ui-stack.md`.
- Non-goals: Template changes unless required to fix visual gaps.

Standards

- Commits: conventional (docs/chore).
- No secrets; env via settings.
- Tests: N/A (visual evidence).

Acceptance

- User flow: Reviewer sees current screenshots for base, search (with pagination), and at least one app page (e.g., calculators or airports) matching the Bootstrap catalogue; notes mention zero custom CSS added for this ADR.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "List the screenshots to capture (base/search/calculators/airports) and where to store them; note that no custom CSS was added."
- "Append an attestation note to the UI docs referencing the captured images."
