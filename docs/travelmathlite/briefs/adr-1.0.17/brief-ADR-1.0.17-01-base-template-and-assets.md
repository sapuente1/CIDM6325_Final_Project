# BRIEF: Build base template with Bootstrap 5 + HTMX includes

Goal

- Stand up the base template loading pinned Bootstrap 5 (CSS/JS) and HTMX globally, matching ADR-1.0.17. Ensure responsive navbar toggle, proper script placement, and accessibility defaults.

Scope (single PR)

- Files to touch: `travelmathlite/templates/base.html`, `travelmathlite/templates/includes/head.html` (if added), static overrides file (if needed), settings for static paths if required.
- Behavior: Base template loads Bootstrap 5 CSS (CDN or vendored) and HTMX, defers JS appropriately, and wires navbar collapse for mobile. Ensure integrity/crossorigin attributes on CDN. HTMX available sitewide. Keep `{% load static %}` for local overrides.
- Non-goals: Component-specific styling (covered in other briefs); SPA frameworks; build pipelines.

Standards

- Commits: conventional (feat/chore/docs).
- No secrets; env via settings.
- Django tests: template render smoke test acceptable; primary verification is manual (asset load + navbar toggle).

Acceptance

- User flow: Base page renders with Bootstrap styling; navbar collapses/expands on mobile; HTMX script present.
- Include migration? no
- Update docs & PR checklist.

Prompts for Copilot

- "Update base.html to load pinned Bootstrap 5 CSS/JS and HTMX with integrity tags; ensure navbar toggle works."
- "Keep HTMX script after body content; ensure static override CSS (if any) loads after Bootstrap."
