# BRIEF: UI docs, patterns, and screenshots

Goal

- Document the Bootstrap 5 + HTMX UI stack, component patterns, and provide screenshots/snippets to satisfy ADR-1.0.17 attestation.

Scope (single PR)

- Files to touch: `docs/ux/ui-stack.md` (new or updated), add screenshots under `docs/travelmathlite/ui/` (or existing docs path), optionally link from README. Include HTML snippets showing navbar, forms, pagination, alerts, and HTMX partial conventions.
- Behavior: Write a concise UI stack guide: asset sources/pins, includes (navbar/footer/alerts/pagination), form/button/pagination patterns, HTMX usage guidelines, and how to add overrides. Capture screenshots of key pages (home, calculators, search, airports) showing Bootstrap styling and responsive navbar.
- Non-goals: New UI features; restyling beyond documentation.

Standards

- Commits: conventional (docs).
- No secrets; env via settings.
- Django tests: N/A (docs/screenshots only).

Acceptance

- User flow: Contributors can read the UI guide to understand how to use Bootstrap/HTMX, where includes live, and how to keep styles consistent; screenshots exist for attestation.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Draft UI stack docs covering Bootstrap/HTMX assets, includes, form/button/pagination patterns, and HTMX partial guidelines; add screenshots."
- "Link the UI guide from README or relevant docs index."
